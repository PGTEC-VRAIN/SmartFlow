from fastapi import FastAPI
from Scripts import DWD_ICON, ARPEGE, GFS_NOAA,AIFS_ECMWF,GEPS_ENS_CNC,IFS9km_ECMWF,Seas5_ECMWF_copernicus,AEMET,EFAS

app = FastAPI(
    title="SmartFlow Global API",
    description="Esta API ha sido desarrollada como un **punto de acceso unificado y preprocesado** a series de tiempo geoespaciales de múltiples modelos de predicción meteorológica (AEMET, DWD, NOAA, etc.). El objetivo central es facilitar la ejecución y el entrenamiento del **modelo hidrológico TETIS**, eliminando la complejidad del manejo de datos brutos y asegurando que TETIS reciba datos limpios y listos para usar en un formato estandarizado. \n\n"
    "La funcionalidad clave reside en la **normalización del dato** y la **búsqueda inteligente**. Los datos se sirven estrictamente en el formato **`WeatherForecastSeries`** (un Smart Data Model) para garantizar la homogeneidad de variables (temperatura, precipitación, etc.). Además, si TETIS solicita datos para coordenadas sin coincidencia exacta, la API aplica una lógica de **Vecino Más Cercano (Nearest Neighbor)** para devolver el pronóstico más relevante, asegurando la continuidad de las simulaciones.",
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