# ============================================================
# 🛰️ Open-Meteo Data Collector
# ============================================================

import requests
import pandas as pd
import time
from pathlib import Path
import numpy as np
import subprocess
from SmartDataModels.WeatherForecastSeries import WeatherForecastSeries
import geopandas as gpd
from shapely.geometry import Point
from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta
import datetime as dt
import os
import json

DATA_DIR = Path("/opt/airflow/data/IFS/")
DATA_DIR.mkdir(exist_ok=True)
MODELO = "ecmwf_ifs"#"gfs_global" #"meteofrance_arpege_europe" #"ecmwf_ifs"
VARIABLES = ["temperature_2m","precipitation","wind_speed_10m"]

# --- CONFIGURACIÓN BÁSICA DEL DAG ---
default_args = {
    'owner': 'AlexPGTEC',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}
# Configuración del endpoint y parámetros
API_URL = "https://api.open-meteo.com/v1/forecast"#"http://openmeteo-api:8080/v1/forecast"

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

def json_serial(obj):
    """Convierte objetos datetime a string ISO 8601."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def fetch_forecast(lats, lons):
    """
    Descarga datos de la API interna de Open-Meteo para todas las variables
    y puntos a la vez. El servidor OpenMeteo gestiona la descarga y el cacheo.
    """
    print(f"🔄 Llamando al servicio API en la red interna de Docker: {API_URL} ...")
    start_time = time.time()
    
    # Lista que almacenará los DataFrames combinados por punto (lat, lon)
    all_data = [] 
    
    # Fecha de descarga para el metadato (ahora se calcula antes de los loops)
    download_time = datetime.now(dt.UTC).isoformat() 
    
    variables_str = ",".join(VARIABLES)
    # start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # end_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    
    # Variables de seguimiento de progreso
    i = 0 
    
    # 1. Bucle por cada punto de la cuadrícula
    for lat in lats:
        for lon in lons:
            i += 1
            
            # PARÁMETROS FINALES para la llamada HTTP
            PARAMS = {
                "latitude": lat,
                "longitude": lon,
                "models": MODELO,
                "hourly": variables_str, # <--- Se piden TODAS las variables aquí
                # "start_date": start_date,
                # "end_date": end_date
            }
            
            try:
                print(f"  ➡️ Solicitando datos para lat={lat:.2f}, lon={lon:.2f}")

                # La llamada HTTP reemplaza al docker run
                r = requests.get(API_URL, params=PARAMS, timeout=300) 
                r.raise_for_status()
                data = r.json()
                hourly_data = data.get("hourly", {})
                
                # 2. Validación de Datos (Comprobamos la variable de tiempo)
                if not hourly_data or "time" not in hourly_data or not hourly_data["time"]:
                    print(f"⚠️ No se obtuvieron datos de tiempo para lat={lat:.2f}, lon={lon:.2f}.")
                    # No lanzamos error, simplemente ignoramos este punto
                    continue 

                # 3. Creación del DataFrame combinando todas las variables
                combined_df = pd.DataFrame({
                    "time": hourly_data["time"],
                })
                
                # Añadir TODAS las variables (las pedidas en variables_str)
                for var in VARIABLES:
                    if var in hourly_data:
                        combined_df[var] = hourly_data[var]
                    else:
                        print(f"   ❌ Advertencia: '{var}' falta en la respuesta JSON para este punto.")
                
                # 4. Añadir metadatos
                combined_df["time"] = pd.to_datetime(combined_df["time"])
                combined_df["latitude"] = lat
                combined_df["longitude"] = lon
                combined_df["downloaded_at"] = download_time # Usamos la hora de inicio de la ejecución
                
                all_data.append(combined_df)
                
            except requests.exceptions.RequestException as e:
                # Captura errores de red o HTTP (4xx, 5xx)
                print(f"❌ Error al consultar API para lat={lat:.2f}, lon={lon:.2f}: {e}")
                continue # Continúa al siguiente punto si falla la llamada
            except Exception as e:
                # Captura cualquier otro error (JSON malformado, etc.)
                print(f"❌ Error inesperado para lat={lat:.2f}, lon={lon:.2f}: {e}")
                continue
                
            time.sleep(0.2) # Mantener el retardo para no saturar la API

        if (i % 100 == 0):
            print(f"Progreso: {i} puntos de latitud procesados.")

    # --- RESULTADO FINAL ---
    total_time = time.time() - start_time
    print(f"\n🏁 Descarga completada en {total_time:.2f} s ({total_time/60:.2f} min)")

    if all_data:
        result_df = pd.concat(all_data, ignore_index=True)
        print(f"📦 Total registros: {len(result_df)}")
        # Devolvemos el DataFrame final y el timestamp, como en tu código original
        return result_df, download_time 
    else:
        print("❌ No se obtuvieron datos.")
        return pd.DataFrame(), download_time


def ejecutar_descarga_ifs():
    lats, lons = sacar_limite_CV("/opt/airflow/data/F162C175_Demarcacion.geojson")

    df, download_time = fetch_forecast(lats, lons)

    grouped = df.groupby(['latitude', 'longitude'])
        
    forecasts_list = []
        
    # 2. Iterar sobre cada grupo y crear objetos WeatherForecastSeries
    for (lat, lon), group_df in grouped:
            
        point_forecast = WeatherForecastSeries(
        id= MODELO + "_" + download_time,
        dateIssued=download_time,
        lat=lat,
        lon=lon,
        timestamp = group_df["time"].dropna().tolist(),
        precipitation = group_df["precipitation"].dropna().to_list(),
        temperature = group_df["temperature_2m"].dropna().to_list(),
        windSpeed = group_df["wind_speed_10m"].dropna().to_list(),

)
        forecasts_list.append(point_forecast.model_dump())
    
    final_data_dict = {
    "id": f"{MODELO}_{download_time}",
    "dateIssued": download_time,
    "forecasts": forecasts_list  # Lista de diccionarios de pronósticos
    }

    # 4. Guardar el archivo (lógica de Airflow)
    os.makedirs(DATA_DIR, exist_ok=True)
    print("💾 Guardando datos en archivo JSON en ", DATA_DIR)
    filename = f"{MODELO}_{download_time.replace(':', '-')}.json"
    file_path = os.path.join(DATA_DIR, filename)

    with open(file_path, 'w') as f:
        json.dump(final_data_dict, f, indent=4,default=json_serial)

    print(f"Datos del modelo {MODELO} descargados correctamente.")
    print("\n FIN")

with DAG(
    dag_id='IFS9km_ECMWF_CV',
    default_args=default_args,
    description='Descarga y procesamiento de predicciones IFS de ECMWF para la Comunidad Valenciana',
    schedule='0 */1 * * *',  # Cada 1 hora
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['IFS', 'ECMWF', 'meteorología', 'HRES'],
) as dag:
    
    # 1. Tarea para ejecutar el procesamiento y descarga
    procesar_ifs_ecmwf = PythonOperator(
        task_id='procesar_ifs_ecmwf',
        python_callable=ejecutar_descarga_ifs, # Llama a la función Python
    )
    procesar_ifs_ecmwf
