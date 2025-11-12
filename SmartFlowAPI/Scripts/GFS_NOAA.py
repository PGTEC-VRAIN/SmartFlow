from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any
import requests 
from functools import lru_cache
from SmartDataModels.WeatherForecastSeries import WeatherForecastSeries
from datetime import datetime, timezone

router = APIRouter(
    prefix="/GFS_NOAA_OpenMeteo",
    tags=["GFS_NOAA_OpenMeteo"]
)

OPEN_METEO_API_URL = "http://open-meteo-api:8080/v1/forecast" 
MODELO = "ncep_gfs013"
VARIABLES_OM = "temperature_2m,precipitation" 


@lru_cache(maxsize=1) # memoria caché que guarda el último get hecho. si el usuario pide otras coords se modifica la caché con las nuevas coords y values
def get_raw_forecast_from_om(lat: float, lon: float) -> Dict[str, Any]:
    """
    Función que consulta el servidor Open-Meteo local para obtener datos en JSON.
    El resultado es el JSON original devuelto por Open-Meteo.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": VARIABLES_OM,
        "models": MODELO
    }
    
    try:
        response = requests.get(OPEN_METEO_API_URL, params=params, timeout=10)
        response.raise_for_status() 
        raw_data = response.json()
        return raw_data
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error al conectar o consultar el servidor Open-Meteo local: {e}"
        )


def om_to_smartdatamodel(om_data: Dict[str, Any], model_name: str) -> List[Any]:
    """
    Transforma el JSON de Open-Meteo (OM) en el smart data model WeatherForecastSeries 
    que contiene las listas de datos, filtrando los valores nulos.
    """
    
    hourly_data = om_data.get('hourly', {})
    if not hourly_data:
        return [] 
        
    raw_times = hourly_data.get('time', [])
    raw_temp_series = hourly_data.get('temperature_2m', [])
    raw_prec_series = hourly_data.get('precipitation', [])
    
    filtered_times = []
    filtered_temps = []
    filtered_precs = []
    
    for i in range(len(raw_times)):
        current_temp = raw_temp_series[i]
        current_prec = raw_prec_series[i]
        
        
        if current_temp is not None and current_prec is not None: # Eliminamos valores nulos
            filtered_times.append(raw_times[i])
            
            
            filtered_temps.append(current_temp) 
            filtered_precs.append(current_prec)


    date_issued = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    lat_model = om_data.get('latitude', 0.0)
    lon_model = om_data.get('longitude', 0.0)
    
    if not filtered_times:
        return []

    try:
        forecast_entity = WeatherForecastSeries(
            id=f"urn:ngsi-ld:WeatherForecastSeries:{model_name}:{lat_model},{lon_model}",
            type="WeatherForecastSeries",
            dateObserved=filtered_times[0], 
            dateIssued=date_issued,
            lat=lat_model,
            lon=lon_model,
            timestamp=filtered_times, 
            temperature=filtered_temps,
            precipitation=filtered_precs, 
            
        )
        
        return [forecast_entity]
    
    except Exception as e:
        # Si falla aquí, es por un error de tipo Pydantic no resuelto (ej. 'timestamp' vs 'time')
        raise RuntimeError(f"Fallo al mapear a WeatherForecastSeries. Revise los tipos: {e}")

@router.get(
    "/data/coordinates",
    response_model=List[WeatherForecastSeries],
    summary="Obtiene el pronóstico más reciente, filtrado por coordenadas (usando OM local)."
)
async def get_gfs_data(
    lat: float = Query(..., description="Latitud del punto a consultar."),
    lon: float = Query(..., description="Longitud del punto a consultar."),
):
    
    # 1. Obtener los datos del servidor OM local (con caché)
    raw_om_data = get_raw_forecast_from_om(lat, lon) 
    
    # 2. Transformar el JSON de OM al formato Smart Data Model
    collection_forecasts = om_to_smartdatamodel(raw_om_data,MODELO)
    
    if not collection_forecasts:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos de pronóstico disponibles para el modelo {MODELO} en esa ubicación."
        )
        
    # --- 3. Lógica de Respuesta ---
    # El servidor devuelve los datos para el punto de consulta (interpolado o el más cercano), ya no hace falta crear el algoritmo de k-neighbors
    
    return collection_forecasts