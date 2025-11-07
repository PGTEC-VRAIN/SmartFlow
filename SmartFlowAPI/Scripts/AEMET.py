from fastapi import APIRouter,Depends, Query,HTTPException
from typing import Optional,List, Dict, Any
import pandas as pd
import glob
import os
import json
from functools import lru_cache
from SmartDataModels.WeatherForecastSeries import WeatherForecastSeries
import math
# Crea una instancia del Router
router = APIRouter(
    prefix="/Harmonie-AROME-AEMET",  # Todas las rutas aquí comenzarán con /AIFS_ECMWF
    tags=["Harmonie-AROME-AEMET"] # Agrupa las rutas en Swagger UI
)

# Define la ruta base donde Airflow guarda los archivos
# (Asegúrate de que esta ruta esté montada en Docker)
DATA_DIR = "/data/HARMONIE" 
MODELO = "HARMONIE"

# ... [Definición de find_latest_json] ...
def find_latest_json_path(directory_path: str, filename_pattern: str) -> str:
    """Encuentra la ruta completa al archivo JSON más reciente."""
    
    search_pattern = os.path.join(directory_path, f"{filename_pattern}*.json")
    list_of_files = glob.glob(search_pattern)
    
    if not list_of_files:
        # Lanza un error HTTP 404 (o 503 si el servicio no está disponible)
        raise HTTPException(status_code=503, detail=f"Datos del modelo Harmonie-AROME no disponibles. No se encontraron archivos.")

    # Encuentra el archivo más reciente por tiempo de modificación
    latest_file = max(list_of_files, key=os.path.getmtime)
    
    return latest_file

@lru_cache(maxsize=1) # 🔑 ¡Caché crucial! Solo carga los datos una vez
def get_cached_forecast_data() -> Dict[str, Any]:
    """
    Dependencia que carga y valida el archivo JSON más reciente.
    Retorna el diccionario completo, incluyendo los metadatos y la lista de objetos PointForecast validados.
    """
    latest_file_path = find_latest_json_path(DATA_DIR, MODELO)
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
async def get_AIFS_data(
    # Usamos la dependencia para obtener los datos
    data: Dict[str, Any] = Depends(get_cached_forecast_data),
    # Parámetros de consulta
    lat: float = Query(..., description="Latitud del punto a consultar. Se interpola si la coordenada no está disponible"),
    lon: float = Query(..., description="Longitud del punto a consultar.Se interpola si la coordenada no está disponible"),
):
    
    # Extraemos la lista de objetos WeatherForecastSeries validados
    collection_forecasts: List[WeatherForecastSeries] = data["forecasts"]

    # 1. Búsqueda por Coincidencia Exacta
    # Usamos una tolerancia mínima para errores de coma flotante
    TOLERANCE = 0.0001 
    
    filtered_forecasts = [
        point for point in collection_forecasts 
        if abs(point.lat - lat) < TOLERANCE and abs(point.lon - lon) < TOLERANCE
    ]
    
    if filtered_forecasts:
        # Se encontró el punto exacto o uno muy cercano
        return filtered_forecasts
    
    # --- 2. Lógica del Vecino Más Cercano (Nearest Neighbor) ---

    # Si no hay coincidencia exacta, buscamos el punto más cercano
    
    # Inicialización con una distancia imposiblemente grande
    min_distance_sq = float('inf')
    closest_point = None

    for point in collection_forecasts:
        # Calculamos la distancia euclidiana al cuadrado para evitar la costosa raíz cuadrada
        # Distancia = (lat_modelo - lat_consulta)^2 + (lon_modelo - lon_consulta)^2
        distance_sq = (point.lat - lat)**2 + (point.lon - lon)**2
        
        if distance_sq < min_distance_sq:
            min_distance_sq = distance_sq
            closest_point = point

    if closest_point:
        # Si encontramos el punto más cercano, lo devolvemos
        
        # Opcional: Puedes calcular la distancia real (en grados) para el mensaje
        min_distance = math.sqrt(min_distance_sq)
        
        print(f"Punto exacto no encontrado. Devolviendo el más cercano en lat={closest_point.lat}, lon={closest_point.lon}. Distancia: {min_distance:.4f} grados.")
        
        # Devolvemos el punto más cercano en una lista (para mantener la consistencia del endpoint)
        return [closest_point]
    
    # Si la colección de pronósticos está vacía (nunca debería pasar si get_cached_forecast_data funciona)
    raise HTTPException(
        status_code=404,
        detail=f"No hay datos de pronóstico disponibles para el modelo ."
    )