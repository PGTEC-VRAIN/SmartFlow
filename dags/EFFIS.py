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
DATAPATH = Path("./data/EFFIS")
DATAPATH.mkdir(exist_ok=True)

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

def procesar_EFFIS():
    file, download_time = ejecutar_descarga_EFFIS()

    df = xr.open_dataset(file, engine="netcdf4").to_dataframe().reset_index()
    print(df.tail())
    print(df.columns)
    

    df["valid_time"] = df["valid_time"].astype(str)

    datos = WeatherForecastSeries(
        id="EFFIS_" + download_time,
        dateIssued=download_time,
        timestamp = df["valid_time"].tolist(),
        lat = df["latitude"].tolist(),
        lon = df["longitude"].tolist(),
        fireWeatherIndex = df["daily_fire_weather_index"].to_list(),
    )
    datos_dict = datos._to_dict()
    print("Variables del JSON: ",datos_dict.keys())
    print("Cantidad de datos de riesgo de incendios descargados: ",datos_dict)
    print("FIN DEL PROCESO DE DESCARGA DE PREDICCIONES DE EFFIS.")


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
        python_callable=procesar_EFFIS,
    )
    EFFIS
