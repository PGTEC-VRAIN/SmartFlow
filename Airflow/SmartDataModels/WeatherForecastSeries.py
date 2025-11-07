# Reemplaza toda la clase WeatherForecastSeries con esto:
from datetime import datetime
import json
from typing import List, Optional, Dict, Any, Union # Necesario para la compatibilidad con Pydantic
from pydantic import BaseModel # 👈 ¡NUEVA IMPORTACIÓN CLAVE!

class WeatherForecastSeries(BaseModel):
    """ 
    Descripción harmonizada de una Serie de Pronóstico del Tiempo,
    basada en el esquema Smart Data Models, usando Pydantic para
    validación y serialización.
    """
    
    # --- PROPIEDADES REQUERIDAS y BÁSICAS ---
    id: str
    dateIssued: datetime
    type: str = 'WeatherForecastSeries' # Valor fijo
    
    # --- LOCALIZACIÓN (Asegúrate de incluir lat y lon para el router) ---
    # NOTA: Agrego lat y lon que usas en el router de FastAPI,
    # asumiendo que vienen en los datos JSON.
    lat: float
    lon: float
    location: Optional[Dict] = None
    address: Optional[Dict] = None
    
    # --- PROPIEDADES DE PRONÓSTICO (Alineadas con Pydantic y tu JSON) ---
    weatherType: Optional[str] = None
    visibility: Optional[List[Union[str, float]]] = None
    windDirection: Optional[List[float]] = None
    windSpeed: Optional[List[float]] = None
    gustSpeed: Optional[List[float]] = None
    refPointOfInterest: Optional[str] = None
    atmosphericPressure: Optional[List[float]] = None
    illuminance: Optional[List[float]] = None
    temperature: Optional[List[float]] = None
    feelsLikeTemperature: Optional[List[float]] = None
    relativeHumidity: Optional[List[float]] = None # Range [0, 1]
    
    # Pydantic puede manejar la conversión de ISO string a datetime automáticamente
    timestamp: Optional[List[datetime]] = None 
    
    dateRetrieved: Optional[datetime] = None
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    uVIndexMax: Optional[List[float]] = None
    precipitation: Optional[List[float]] = None
    precipitationProbability: Optional[List[Optional[float]]] = None
    solarRadiation: Optional[List[Optional[float]]] = None
    riverDischarge: Optional[List[Optional[float]]] = None
    fireWeatherIndex: Optional[List[Optional[float]]] = None

    # --- CONFIGURACIÓN DE PYDANTIC ---
    class Config:
        # Permite que la clase acepte atributos adicionales
        extra = "allow"
        # Permite la serialización/deserialización de objetos datetime
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }