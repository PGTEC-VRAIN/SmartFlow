from __future__ import annotations
import cdsapi
import requests
import pandas as pd
from pathlib import Path
import numpy as np
from SmartDataModels.WeatherForecastSeries import WeatherForecastSeries
import geopandas as gpd
from shapely.geometry import Point
from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta
import datetime as dt
import logging
import xarray as xr
import os
import json
import zipfile

# Configuración básica para el logger (necesario dentro de un operador)
log = logging.getLogger(__name__)

# --- CONFIGURACIÓN BÁSICA DEL DAG ---
default_args = {
    'owner': 'AlexPGTEC',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}
DATA_DIR = "SmartFlowAPI/data/EFFIS/"
MODELO = "EFFIS"

def ejecutar_descarga_EFFIS():
    """
    Función que simula la ejecución de tu script de descarga, 
    ahora recibiendo la fecha de destino.
    """
    
    # Airflow ya se encarga de calcular el salto de mes/año con {{ tomorrow_ds }}
    # Aquí puedes construir el diccionario de request como hicimos antes, 
    # pero ahora dentro de la función callable.

    target_date = datetime.today() - timedelta(days=31)
    print(target_date)
    
    year_str = str(target_date.year)
    month_str = f"{target_date.month:02d}"
    day_str = f"{target_date.day:02d}"
    download_time = datetime.now().isoformat()
    print("🕒 Fecha de descarga:", download_time)
    dataset = "sis-tourism-fire-danger-indicators"
    request = {
    "time_aggregation": "daily_indicators",
    "product_type": "single_model",
    "variable": ["daily_fire_weather_index"],
    "gcm_model": [
        "cnrm_cm5",
        # "ec_earth",
        # "ipsl_cm5a_mr",
        # "hadgem2_es",
        # "mpi_esm_lr",
        # "noresm1_m"
    ],
    "experiment": "rcp8_5",
    "version": "v2_0",
    "period": [
        "2025",
        # "2026",
        # "2027",
        # "2028",
        # "2029",
        # "2030",
        # "2031",
        # "2032",
        # "2033",
        # "2034",
        # "2035",#deja hasta 2098
    ]
}

    client = cdsapi.Client(key="26032064-cdae-4843-9bbb-c6e11f89149c", url=" https://cds.climate.copernicus.eu/api")
    file = client.retrieve(dataset, request).download()
    
    log.info(f"Descargando datos de EFFIS para la fecha dinámica: {year_str}-{month_str}-{day_str}")
    return file, download_time

def json_serial(obj):
    """Convierte objetos datetime a string ISO 8601."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def procesar_effis():
    zip_path, download_time = ejecutar_descarga_EFFIS()
    print(f"📦 ZIP descargado: {zip_path}")

    # 📂 Carpeta donde se descomprime (mismo directorio)
    extract_dir = DATA_DIR

    # 🔓 Descomprimir directamente
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Mostrar contenido
        print("Contenido del ZIP:")
        for name in zip_ref.namelist():
            print(" -", name)
        # Extraer todo (solo un .nc)
        zip_ref.extractall(extract_dir)

    # 🔍 Buscar el archivo .nc recién extraído
    nc_file = next(
        (os.path.join(extract_dir, f)
         for f in os.listdir(extract_dir)
         if f.endswith(".nc")),
        None
    )

    if nc_file is None:
        raise FileNotFoundError(f"No se encontró ningún archivo .nc dentro de {zip_path}")

    print(f"✅ Archivo NetCDF encontrado: {nc_file}")

    df = xr.open_dataset(nc_file, engine="netcdf4").to_dataframe().reset_index()
    print(df.head())
    print(df.columns)
    
    df.to_csv(f"FastAPI/data/EFFIS/PrediccionesEFFIS_{download_time}.csv")

    # df["valid_time"] = df["valid_time"].astype(str) 
    # grouped = df.groupby(["lat", "lon"])

    # forecasts_list = []

    # for (lat, lon), group_df in grouped:
    #     daily_fire_weather_index = group_df["daily_fire_weather_index"].dropna().tolist()

    #     # 👇 Saltar puntos sin datos
    #     if not river_discharge:
    #         continue

    #     point_forecast = WeatherForecastSeries(
    #         id=f"{MODELO}_{lat}_{lon}_{download_time}",
    #         dateIssued=download_time,
    #         lat=lat,
    #         lon=lon,
    #         timestamp=group_df["valid_time"].dropna().tolist(),
    #         fireWeatherIndex=daily_fire_weather_index,
    #     )
    #     forecasts_list.append(point_forecast.model_dump())

    # final_data_dict = {
    #     "id": f"{MODELO}_{download_time}",
    #     "dateIssued": download_time,
    #     "forecasts": forecasts_list,  
    # }

    # os.makedirs(DATA_DIR, exist_ok=True)
    # filename = f"{MODELO}_{download_time.replace(':', '-')}.json"
    # file_path = os.path.join(DATA_DIR, filename)

    # with open(file_path, "w") as f:
    #     json.dump(final_data_dict, f, indent=4, default=json_serial)

    print(f"Datos del modelo {MODELO} descargados correctamente ({len(forecasts_list)} puntos guardados).")
    print("\n FIN")


with DAG(
    dag_id='EFFIS_Forecast_Copernicus_EWDS',
    default_args=default_args,
    description='Descarga y procesamiento de predicciones de EFFIS de Copernicus EWDS para la Comunidad Valenciana',
    schedule='@daily',  # Cada día
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['EFFIS', 'Copernicus', 'meteorología', 'EWDS'],
) as dag:
    
    # La clave es usar op_kwargs para inyectar el macro de Airflow
    EFFIS = PythonOperator(
        task_id='Procesar_EFFIS_Forecast',
        python_callable=procesar_effis,
    )
    EFFIS
