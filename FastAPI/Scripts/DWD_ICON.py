from fastapi import APIRouter
from typing import Optional

# Crea una instancia del Router
router = APIRouter(
    prefix="/DWD_ICON",  # Todas las rutas aquí comenzarán con /DWD_ICON
    tags=["DWD ICON"] # Agrupa las rutas en Swagger UI
)

from fastapi import APIRouter, HTTPException
from typing import Optional
import pandas as pd
import glob
import os

# Define la ruta base donde Airflow guarda los archivos
# (Asegúrate de que esta ruta esté montada en Docker)
DATA_DIR = "./data" 

# ... [Definición del router] ...
router = APIRouter(
    prefix="/DWD_ICON",
    tags=["DWD ICON"]
)
# ... [Definición de find_latest_csv] ...

def find_latest_csv(directory_path: str, filename_pattern: str) -> str:
    """Encuentra la ruta completa al archivo CSV más reciente 
    por fecha de modificación en un directorio."""
    
    # 1. Encontrar todos los archivos que coinciden con el patrón
    # Ejemplo de patrón: './data/DWD_ICON_*.csv'
    search_pattern = os.path.join(directory_path, filename_pattern)
    list_of_files = glob.glob(search_pattern)
    
    if not list_of_files:
        # Si no se encuentra ningún archivo, lanza un error HTTP 404
        raise HTTPException(status_code=404, detail=f"No se encontraron archivos con el patrón: {search_pattern}")

    # 2. Encontrar el archivo con el tiempo de modificación más reciente
    # La función 'max' utiliza 'key=os.path.getmtime' para comparar los archivos 
    # por su tiempo de modificación.
    latest_file = max(list_of_files, key=os.path.getmtime)
    
    return latest_file

@router.get("/data/coordinates")
async def get_dwd_icon_data(
    lat: float,
    lon: float,
    date: Optional[str] = "latest"
):
    """
    Endpoint para obtener datos FWI de la fuente DWD ICON.
    """
    try:
        # 1. Encontrar el archivo CSV más reciente
        latest_file_path = find_latest_csv(DATA_DIR, "DWD_ICON_*.csv")

        # 2. Leer el archivo más reciente
        # Ahora pasamos una ruta de archivo válida a pd.read_csv()
        df = pd.read_csv(latest_file_path) 
        
        # 3. Aquí iría tu lógica de interpolación con el DataFrame 'df'
        
        return {
            "source": "DWD ICON",
            "file_read": latest_file_path, # Añadido para verificar
            "lat": lat,
            "lon": lon,
            "value": 5.23  # Sustituir con el valor interpolado real
        }
        
    except HTTPException as e:
        # Re-lanzar el error 404 si no se encuentran archivos
        raise e
    except Exception as e:
        # Manejar otros posibles errores de lectura/procesamiento
        raise HTTPException(status_code=500, detail=f"Error interno al procesar datos: {str(e)}")