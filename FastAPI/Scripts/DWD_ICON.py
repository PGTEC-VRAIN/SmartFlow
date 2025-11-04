from fastapi import APIRouter,Depends, Query,HTTPException
from typing import Optional,List, Dict, Any
import pandas as pd
import glob
import os
import json
from functools import lru_cache
from SmartDataModels.WeatherForecastSeries import WeatherForecastSeries

# Crea una instancia del Router
router = APIRouter(
    prefix="/DWD_ICON",  # Todas las rutas aquí comenzarán con /DWD_ICON
    tags=["DWD ICON"] # Agrupa las rutas en Swagger UI
)

# Define la ruta base donde Airflow guarda los archivos
# (Asegúrate de que esta ruta esté montada en Docker)
DATA_DIR = "./data" 
MODELO = "DWD_ICON"
# ... [Definición del router] ...
router = APIRouter(
    prefix="/DWD_ICON",
    tags=["DWD ICON"]
)
# ... [Definición de find_latest_json] ...
def find_latest_json_path(directory_path: str, filename_pattern: str) -> str:
    """Encuentra la ruta completa al archivo JSON más reciente."""
    
    search_pattern = os.path.join(directory_path, filename_pattern)
    # Cambiamos la extensión a .json
    search_pattern = search_pattern.replace(".csv", ".json") 
    list_of_files = glob.glob(search_pattern)
    
    if not list_of_files:
        # Lanza un error HTTP 404 (o 503 si el servicio no está disponible)
        raise HTTPException(status_code=503, detail=f"Datos del modelo ICON no disponibles. No se encontraron archivos.")

    # Encuentra el archivo más reciente por tiempo de modificación
    latest_file = max(list_of_files, key=os.path.getmtime)
    
    return latest_file

@lru_cache(maxsize=1) # 🔑 ¡Caché crucial! Solo carga los datos una vez
def get_cached_forecast_data() -> Dict[str, Any]:
    """
    Dependencia que carga y valida el archivo JSON más reciente.
    Retorna el diccionario completo, incluyendo los metadatos y la lista de objetos PointForecast validados.
    """
    latest_file_path = find_latest_json_path(DATA_DIR, f"{MODELO}_*.json")
    
    try:
        with open(latest_file_path, 'r') as f:
            full_data = json.load(f)
            
        if 'forecasts' not in full_data or not isinstance(full_data['forecasts'], list):
             raise HTTPException(status_code=500, detail="El archivo JSON no tiene la clave 'forecasts' o no es una lista.")

        # Validar CADA elemento de la lista 'forecasts' usando el modelo WeatherForecastSeries
        validated_forecasts = []
        for raw_point in full_data['forecasts']:
            # Pydantic valida y convierte el diccionario en un objeto WeatherForecastSeries
            validated_forecasts.append(WeatherForecastSeries(**raw_point))
            
        # Reemplazar la lista cruda del diccionario por los objetos validados
        full_data['forecasts'] = validated_forecasts
        
        return full_data
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al decodificar el archivo JSON. Estructura inválida.")
    except Exception as e:
        # Esto captura errores de validación de Pydantic
        raise HTTPException(status_code=500, detail=f"Error al cargar/validar los datos: {e}")

@router.get(
    "/data/coordinates",
    response_model=List[WeatherForecastSeries], # La respuesta es una lista de pronósticos
    summary="Obtiene el pronóstico más reciente, filtrado por coordenadas."
)
async def get_dwd_icon_data(
    # Usamos la dependencia para obtener los datos
    data: Dict[str, Any] = Depends(get_cached_forecast_data),
    # Parámetros de consulta
    lat: float = Query(..., description="Latitud exacta del punto a consultar."),
    lon: float = Query(..., description="Longitud exacta del punto a consultar."),
    # El parámetro 'date' ya no es necesario si siempre se busca el 'latest'
    # date: Optional[str] = "latest" 
):

    # Extraemos la lista de objetos WeatherForecastSeries validados
    collection_forecasts: List[WeatherForecastSeries] = data["forecasts"]

    # Buscamos el punto exacto
    filtered_forecasts = [
        point for point in collection_forecasts 
        if abs(point.lat - lat) < 0.0001 and abs(point.lon - lon) < 0.0001
    ]
    
    if not filtered_forecasts:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró pronóstico para la coordenada lat={lat}, lon={lon}."
        )
            
    # Devolvemos la lista (que contendrá 0 o 1 elemento)
    return filtered_forecasts