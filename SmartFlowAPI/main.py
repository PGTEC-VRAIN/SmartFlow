from fastapi import FastAPI
from Scripts import DWD_ICON, ARPEGE, GFS_NOAA,AIFS_ECMWF,GEPS_ENS_CNC,IFS9km_ECMWF,Seas5_ECMWF_copernicus,AEMET,EFAS
import os, yaml

DESCRIPCIONES = {
    'AEMET': (
    "Esta API ha sido desarrollada como parte del proyecto PGTEC para tener un **punto de acceso unificado y preprocesado** a series de tiempo "
    "geoespaciales de múltiples modelos de predicción meteorológica (AEMET, DWD, NOAA, etc.). "
    "Su objetivo central es facilitar la ejecución y el entrenamiento del **modelo hidrológico TETIS**, "
    "eliminando la complejidad del manejo de datos brutos.\n\n"
    
    "### Funcionalidad Central\n"
    "* **Normalización de Datos:** Todos los datos se sirven estrictamente en el formato estandarizado **`WeatherForecastSeries`** (un Smart Data Model), garantizando la homogeneidad de variables (temperatura, precipitación, etc.).\n"
    "* **Conversión de colores a valores:** Los datos brutos son imágenes TIFF con colores y con metadatos sobre la escala de color y se realiza una conversión a valores numéricos mediante la interpolación lineal de la escala de color.\n\n"
    
    "### Búsqueda Inteligente (Interpolación)\n"
    "Esta API aplica una lógica de **Vecino Más Cercano (Nearest Neighbor)** a los datos de la malla (*grid*) para devolver el pronóstico más cercano al solicitado por el usuario."
    ),
    'Open-Meteo': (
    "Esta API ha sido desarrollada como parte del proyecto PGTEC para tener un **punto de acceso unificado y preprocesado** a series de tiempo "
    "geoespaciales de múltiples modelos de predicción meteorológica (AEMET, DWD, NOAA, etc.). "
    "Su objetivo central es facilitar la ejecución y el entrenamiento del **modelo hidrológico TETIS**, "
    "eliminando la complejidad del manejo de datos brutos.\n\n"
    
    "### Funcionalidad Central\n"
    "* **Normalización de Datos:** Todos los datos se sirven estrictamente en el formato estandarizado **`WeatherForecastSeries`** (un Smart Data Model), garantizando la homogeneidad de variables (temperatura, precipitación, etc.).\n"
    "* **Abstracción de Fuente:** La API actúa como una capa de abstracción, obteniendo datos de su servidor local **Open-Meteo** (modelos como ICON, GFS, AROME) y de fuentes externas directas (como **AEMET**).\n\n"
    
    "### Búsqueda Inteligente (Interpolación)\n"
    "En este caso, la API local de **Open-Meteo** realiza la lógica de interpolación en el *backend*, asegurando que el pronóstico devuelto es el más cercano para la coordenada solicitada.\n"
    ),
    'Copernicus': (
    "Esta API ha sido desarrollada como parte del proyecto PGTEC para tener un **punto de acceso unificado y preprocesado** a series de tiempo "
    "geoespaciales de múltiples modelos de predicción meteorológica (AEMET, DWD, NOAA, etc.). "
    "Su objetivo central es facilitar la ejecución y el entrenamiento del **modelo hidrológico TETIS**, "
    "eliminando la complejidad del manejo de datos brutos.\n\n"
    
    "### Funcionalidad Central\n"
    "* **Normalización de Datos:** Todos los datos se sirven estrictamente en el formato estandarizado **`WeatherForecastSeries`** (un Smart Data Model), garantizando la homogeneidad de variables (temperatura, precipitación, etc.).\n"
    
    "### Búsqueda Inteligente (Interpolación)\n"
    "Esta API aplica una lógica de **Vecino Más Cercano (Nearest Neighbor)** a los datos de la malla (*grid*) para devolver el pronóstico más cercano al solicitado por el usuario."
    ),
    None: # Para el caso por defecto si no se define MODELO_ACTIVO
        "Esta es la API Global sin modelo activo. Inicie un conector específico (AEMET, Open-Meteo, etc.) para ver la documentación completa."
}

MODELO_ACTIVO = os.environ.get("MODELO_ACTIVO")
#Permitimos que se puedan pedir más de 1 modelo:
if MODELO_ACTIVO:
    MODELOS_ACTIVOS_LIST = [m.strip() for m in MODELO_ACTIVO.split(',') if m.strip()]
else:
    MODELOS_ACTIVOS_LIST = []

with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

active_description = DESCRIPCIONES.get(MODELO_ACTIVO, DESCRIPCIONES[None])

app = FastAPI(
    title="SmartFlow Global API",
    description=active_description,
    version="1.0.0"
)

ROUTER_MAP = {
    'AEMET': [AEMET.router],
    'Open-Meteo': [
        DWD_ICON.router, 
        ARPEGE.router, 
        GFS_NOAA.router, 
        GEPS_ENS_CNC.router, 
        IFS9km_ECMWF.router
        # Las líneas comentadas deben importarse primero si se quieren incluir
    ],
    'Copernicus': [
        # EFAS.router, # Debes descomentar/añadir la importación primero
        # EFFIS.router
    ]
}

# Lógica de carga (mucho más limpia)
for modelo in MODELOS_ACTIVOS_LIST:
    if modelo in ROUTER_MAP:
        print(f"Cargando solo endpoints para el modelo: {modelo}")
        for router in ROUTER_MAP[modelo]:
            app.include_router(router)
    elif modelo is not None:
        # Esto manejaría casos donde el modelo está en env pero no en ROUTER_MAP
        print(f"Modelo '{modelo}' no reconocido o no configurado.")
    elif modelo is None:
        print(f"Como no se ha elegido modelo, se usa Open-Meteo por defecto")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API global en funcionamiento. Visite /docs"}