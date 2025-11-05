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

MODELO = "EFAS"
DATA_DIR = "FastAPI/data/EFAS"

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

def ejecutar_descarga_EFAS():
    """
    Función que simula la ejecución de tu script de descarga, 
    ahora recibiendo la fecha de destino.
    """
    
    target_date = datetime.today() - timedelta(days=31) # descargamos datos de un mes antes ya que son los últimos datos gratis
    print(target_date)
    
    year_str = str(target_date.year)
    month_str = f"{target_date.month:02d}"
    day_str = f"{target_date.day:02d}"
    download_time = datetime.now().isoformat()
    print("🕒 Fecha de descarga:", download_time)
    dataset = "efas-forecast"
    request = {
        "system_version": ["operational"],
        "originating_centre": "ecmwf",
        "product_type": ["control_forecast"],
        "variable": [
            "river_discharge_in_the_last_6_hours",
            # "runoff_water_equivalent",
            # "snow_depth_water_equivalent",
            # "soil_wetness_index",
            # "elevation_v5_0",
            # "upstream_area_v5_0"
        ],
        "model_levels": "surface_level",
        "year": [year_str],
        "month": [month_str],
        "day": [day_str],
        "time": ["00:00", "12:00"],
        "leadtime_hour": [
            "6",
            "12",
            "18",
            "24",
            "30",
            "36",
            "42",
            "48",
            "54",
            "60",
            "66",
            "72",
            "78",
            "84",
            "90",
            "96",
            "102",
            "108",
            "114",
            "120",
            "126",
            "132",
            "138",
            "144",
            "150",
            "156",
            "162",
            "168",
            "174",
            "180",
            "186",
            "192",
            "198",
            "204",
            "210",
            "216",
            "222",
            "228",
            "234",
            "240",
            "246",
            "252",
            "258",
            "264",
            "270",
            "276",
            "282",
            "288",
            "294",
            "300",
            "306",
            "312",
            "318",
            "324",
            "330",
            "336",
            "342",
            "348",
            "354",
            "360"
        ],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [40.3, -1, 38.0, 0.5]
    }

    client = cdsapi.Client(key="26032064-cdae-4843-9bbb-c6e11f89149c", url="https://ewds.climate.copernicus.eu/api")
    file = client.retrieve(dataset, request).download()
    
    log.info(f"Descargando datos de EFAS para la fecha dinámica: {year_str}-{month_str}-{day_str}")
    return file, download_time

def json_serial(obj):
    """Convierte objetos datetime a string ISO 8601."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def procesar_efas():
    file, download_time = ejecutar_descarga_EFAS()
    df = xr.open_dataset(file, engine="netcdf4").to_dataframe().reset_index()

    df["valid_time"] = df["valid_time"].astype(str) 
    grouped = df.groupby(["latitude", "longitude"])

    forecasts_list = []

    for (lat, lon), group_df in grouped:
        river_discharge = group_df["dis06"].dropna().tolist()

        # 👇 Saltar puntos sin datos
        if not river_discharge:
            continue

        point_forecast = WeatherForecastSeries(
            id=f"{MODELO}_{lat}_{lon}_{download_time}",
            dateIssued=download_time,
            lat=lat,
            lon=lon,
            timestamp=group_df["valid_time"].dropna().tolist(),
            riverDischarge=river_discharge,
        )
        forecasts_list.append(point_forecast.model_dump())

    final_data_dict = {
        "id": f"{MODELO}_{download_time}",
        "dateIssued": download_time,
        "forecasts": forecasts_list,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"{MODELO}_{download_time.replace(':', '-')}.json"
    file_path = os.path.join(DATA_DIR, filename)

    with open(file_path, "w") as f:
        json.dump(final_data_dict, f, indent=4, default=json_serial)

    print(f"Datos del modelo {MODELO} descargados correctamente ({len(forecasts_list)} puntos guardados).")
    print("\n FIN")

with DAG(
    dag_id='EFAS_Forecast_Copernicus_EWDS',
    default_args=default_args,
    description='Descarga y procesamiento de predicciones de EFAS de Copernicus EWDS para la Comunidad Valenciana',
    schedule='@daily',  # Cada día
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['EFAS', 'Copernicus', 'meteorología', 'EWDS'],
) as dag:
    
    # La clave es usar op_kwargs para inyectar el macro de Airflow
    EFAS = PythonOperator(
        task_id='Procesar_EFAS_Forecast',
        python_callable=procesar_efas,
    )
    EFAS
