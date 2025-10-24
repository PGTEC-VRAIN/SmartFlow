"""
Script python para la automatización de descarga de predicciones meteorológicas mediante el uso de Airflow

Este script coge otro script python y lo ejecuta de forma programática con Airflow

Para ejecutar más scripts se pueden añadir más bashOperators con los nuevos scripts.

Para que le funcione a otra persona se debe modificar el comando Bash con las rutas de los archivos (airflow.py y venv) 

Author: Alex Chaume

Date: 24/10/2025

Versión: demo

"""

from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.standard.operators.bash import BashOperator

# --- CONFIGURACIÓN BÁSICA DEL DAG ---
default_args = {
    'owner': 'AlexPGTEC',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

# --- DEFINICIÓN DEL DAG ---
with DAG(
    dag_id='AEMET_HARMONIE_AROME',
    default_args=default_args,
    description='Descarga automática de predicciones HARMONIE-AROME de AEMET',
    schedule='0 */1 * * *',  # Cada 1 hora
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['aemet', 'harmonie', 'meteorología', 'arome'],
) as dag:

    # --- TAREA 1: Ejecutar el script Python ---
    ejecutar_descarga = BashOperator(
        task_id='ejecutar_harmonie_script',
        bash_command='source /home/alex/SmartFlow/venv/bin/activate && python3 /home/alex/SmartFlow/SmartFlow/AEMET_HARMONIE_AROME.py', 
        #primero inyecto el entorno virtual venv con los paquetes necesarios y luego ya ejecuto el script aemet
    )

    ejecutar_descarga