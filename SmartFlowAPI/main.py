from fastapi import FastAPI
from Scripts import DWD_ICON, ARPEGE, GFS_NOAA,AIFS_ECMWF,GEPS_ENS_CNC,IFS9km_ECMWF,Seas5_ECMWF_copernicus,AEMET,EFAS

app = FastAPI(
    title="SmartFlow Global API",
    description= (
    "Esta API ha sido desarrollada como parte del proyecto PGTEC para tener un **punto de acceso unificado y preprocesado** a series de tiempo "
    "geoespaciales de múltiples modelos de predicción meteorológica (AEMET, DWD, NOAA, etc.). "
    "Su objetivo central es facilitar la ejecución y el entrenamiento del **modelo hidrológico TETIS**, "
    "eliminando la complejidad del manejo de datos brutos.\n\n"
    
    "### Funcionalidad Central\n"
    "* **Normalización de Datos:** Todos los datos se sirven estrictamente en el formato estandarizado **`WeatherForecastSeries`** (un Smart Data Model), garantizando la homogeneidad de variables (temperatura, precipitación, etc.).\n"
    "* **Abstracción de Fuente:** La API actúa como una capa de abstracción, obteniendo datos de su servidor local **Open-Meteo** (modelos como ICON, GFS, AROME) y de fuentes externas directas (como **AEMET**).\n\n"
    
    "### Búsqueda Inteligente (Interpolación)\n"
    "Para asegurar la continuidad de las simulaciones de TETIS en cualquier coordenada, la API gestiona la interpolación de la siguiente manera:\n"
    "* **Modelos Open-Meteo (DWD, NOAA, ECMWF, etc.):** La **propia API local de Open-Meteo** realiza la lógica de **Vecino Más Cercano (Nearest Neighbor)** o interpolación en el *backend*, asegurando que el pronóstico devuelto ya es el más relevante para la coordenada solicitada.\n"
    "* **Modelos Externos (AEMET y Copernicus (EFAS y EFFIS)):** Cuando la fuente no ofrece interpolación nativa, esta API aplica una lógica de **Vecino Más Cercano (Nearest Neighbor)** a los datos del *grid* para devolver el pronóstico más relevante."
    ),
    version="1.0.0"
)

# Registra los routers
app.include_router(DWD_ICON.router)
app.include_router(ARPEGE.router)
app.include_router(GFS_NOAA.router)
app.include_router(AIFS_ECMWF.router)
app.include_router(GEPS_ENS_CNC.router)
app.include_router(IFS9km_ECMWF.router)
app.include_router(Seas5_ECMWF_copernicus.router)
app.include_router(EFAS.router)
# app.include_router(EFFIS.router)
app.include_router(AEMET.router)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "API global en funcionamiento. Visite /docs"}