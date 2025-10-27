# ============================================================
# 🛰️ Open-Meteo Data Collector
# ============================================================

import requests
import pandas as pd
import datetime
import time
from pathlib import Path
import numpy as np
import subprocess
from WeatherForecastSeries import WeatherForecastSeries
import geopandas as gpd
from shapely.geometry import Point

# Configuración del endpoint y parámetros
API_URL = "http://127.0.0.1:8081/v1/forecast"

def sacar_limite_CV(file_path: str):
    # 1. Cargar el GeoJSON
    gdf = gpd.read_file(file_path)

    # 2. Seleccionar la demarcación Júcar (por si hay más de una)
    cuenca = gdf[gdf["Demarcacio"] == "Júcar"].geometry.iloc[0]

    # 3. Crear una cuadrícula de puntos dentro del bounding box de la cuenca
    minx, miny, maxx, maxy = cuenca.bounds
    step = 1  # grados, ajusta según resolución deseada

    lats = np.arange(miny, maxy, step)
    lons = np.arange(minx, maxx, step)

    # 4. Filtrar solo los puntos que están dentro del polígono
    puntos_dentro = [
        (lat, lon)
        for lat in lats
        for lon in lons
        if cuenca.contains(Point(lon, lat))
    ]

    # 5. Separar latitudes y longitudes
    lats_in, lons_in = map(list, zip(*puntos_dentro))

    return lats_in, lons_in

# # Límites rectangulares aproximados de la comunitat valenciana
# lat_min, lat_max = 37.698098, 40.885909
# lon_min, lon_max = -1.953683, 1.100229

# # Crear malla de puntos con paso, por ejemplo, 0.1°
# step = 1#0.1
# lats = np.arange(lat_min, lat_max + 1e-6, step)
# lons = np.arange(lon_min, lon_max + 1e-6, step)

# Carpeta donde guardar los datos (CSV temporal)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MODELO = "dwd_icon_eu"#"gfs_global" #"meteofrance_arpege_europe" #"ecmwf_ifs"
VARIABLES = ["temperature_2m","precipitation"]
now = datetime.datetime.now()  # o .utcnow() si quieres UTC
filename = now.strftime("%Y%m%d_%H%M") +"_"+ MODELO+".csv"
DATA_FILE = DATA_DIR / filename


def fetch_forecast(lats, lons):
    """Descarga datos de Open-Meteo y verifica que las variables existan."""
    print(f"🔄 Descargando datos de {API_URL} ...")
    start_time = time.time()
    all_data = []

    #PASO 1º: DESCARGAMOS LOS DATOS DE LA VARIABLE AL CONTENEDOR 
    download_time = datetime.datetime.now().isoformat()
    for var in VARIABLES:
        print(f"⬇️ Descargando {var} del Bucket S3 de AWS...")
        subprocess.run([
            "docker", "run", "--rm", "-v", "open-meteo-data:/app/data",
            "ghcr.io/open-meteo/open-meteo", "sync", MODELO, var
        ], check=True)  # check=True lanza error si falla
    i=0
    j=0
    for lat in lats:
        i+=1
        for lon in lons:
            j+=1
            combined_df = pd.DataFrame()

            for var in VARIABLES:

                PARAMS = {
                    "latitude": lat,
                    "longitude": lon,
                    "models": MODELO,  # usar el modelo correcto
                    "hourly": var
                }
                # PASO 2º: ACCEDEMOS A LOS DATOS DESCARGADOS DEL CONTENEDOR A TRAVES DE LA URL LOCALHOST Y CREAMOS EL DATAFRAME
                try:
                    r = requests.get(API_URL, params=PARAMS)
                    r.raise_for_status()
                    data = r.json()

                    # 🔹 Validación: la variable debe existir y contener datos
                    if var not in data.get("hourly", {}) or all(v is None for v in data["hourly"][var]):
                        message = (
                            f"⚠️ La variable '{var}' no contiene datos para "
                            f"lat={lat}, lon={lon}.\n"
                            "Primero debes descargar los datos en el volumen "
                            "con Docker, por ejemplo:\n"
                            "docker run -it --rm -v open-meteo-data:/app/data "
                            "ghcr.io/open-meteo/open-meteo sync " + MODELO + " " + var
                        )
                        raise ValueError(message)

                    df = pd.DataFrame({
                        "time": data["hourly"]["time"],
                        var: data["hourly"][var]
                    })

                    if combined_df.empty:
                        combined_df = df
                    else:
                        combined_df = pd.merge(combined_df, df, on="time", how="outer")

                except Exception as e:
                    print(e)
                    continue

                time.sleep(0.2)

            if not combined_df.empty:
                combined_df["time"] = pd.to_datetime(combined_df["time"])
                combined_df["latitude"] = lat
                combined_df["longitude"] = lon
                combined_df["downloaded_at"] = datetime.datetime.now(datetime.UTC)
                all_data.append(combined_df)
            if (i % 100 == 0) and (j % 100 == 0):
                print(f"Progreso: lat={lat}, lon={lon}")

    total_time = time.time() - start_time
    print(f"\n🏁 Descarga completada en {total_time:.2f} s ({total_time/60:.2f} min)")

    if all_data:
        result_df = pd.concat(all_data, ignore_index=True)
        print(f"📦 Total registros: {len(result_df)}")
        return result_df, download_time
    else:
        print("❌ No se obtuvieron datos.")
        return pd.DataFrame(), download_time


def append_forecast(df):
    """Guarda los datos en CSV (append si ya existe)"""
    if DATA_FILE.exists() and df.shape[0]>0:
        old_df = pd.read_csv(DATA_FILE, parse_dates=["time", "downloaded_at"])
        df = pd.concat([old_df, df]).drop_duplicates(subset=["time"]).reset_index(drop=True)
    else:
        pass
    return df 

def main():
    lats, lons = sacar_limite_CV("./F162C175_Demarcacion.geojson")

    df, download_time = fetch_forecast(lats, lons)

    df = append_forecast(df)

    datos = WeatherForecastSeries(
    id= MODELO + "_" + download_time,
    dateIssued=download_time,
    timestamp = df["time"].tolist(),
    lat = df["latitude"].tolist(),
    lon = df["longitude"].tolist(),
    precipitation = df["precipitation"].to_list(),
    windSpeed = df["temperature_2m"].to_list()
)
    datos_dict = datos._to_dict()
    print("Variables del JSON: ",datos_dict.keys())
    print("Cantidad de datos de precipitación descargados: ",len(datos_dict["precipitation"]))
    print("FIN DEL PROCESO DE DESCARGA DE PREDICCIONES HARMONIE-AROME DE AEMET.")
    print("\n FIN")

if __name__ == "__main__":
    main()
