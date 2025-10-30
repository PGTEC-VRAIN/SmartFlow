import cdsapi


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

# --- CONFIGURACIÓN BÁSICA DEL DAG ---
default_args = {
    'owner': 'AlexPGTEC',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}
DATAPATH = Path("./data/EFAS")
DATAPATH.mkdir(exist_ok=True)


dataset = "efas-historical"
request = {
    "system_version": ["version_5_0"],
    "variable": [
        "river_discharge_in_the_last_6_hours",
        "runoff_water_equivalent",
        "snow_depth_water_equivalent",
        "soil_wetness_index",
        "elevation",
        "upstream_area"
    ],
    "model_levels": "surface_level",
    "hyear": ["2025"],
    "hmonth": ["10"],
    "hday": ["26"],
    "time": [
        "00:00", "06:00", "12:00",
        "18:00"
    ],
    "data_format": "netcdf",
    "download_format": "zip",
    "area": [39.6, -1, 38, 1]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()