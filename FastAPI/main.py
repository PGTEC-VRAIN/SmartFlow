from fastapi import FastAPI
from Scripts import DWD_ICON # Importa el router que creaste

app = FastAPI(
    title="SmartFlow Global API",
    description="Acceso a múltiples datos geográficos resultantes de modelos predicción (EFFIS, Copernicus, Open.).",
    version="1.0.0"
)

# Registra los routers
app.include_router(DWD_ICON.router)
# Si tuvieras otra fuente (ej. Copernicus)
# from routers import copernicus
# app.include_router(copernicus.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API global en funcionamiento. Visite /docs"}