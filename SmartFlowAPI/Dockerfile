# Dockerfile

# Usa una imagen base oficial de Python (ligera y optimizada para la web)
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos e instala las dependencias
# Esto ayuda a la caché de Docker si solo cambian los scripts
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./data /data

# Copia todos tus scripts de Python al contenedor
# Asegúrate de copiar también tus archivos NetCDF (.nc) si son pequeños, 
# o montar un volumen si son muy grandes.
COPY . .

# Expone el puerto por defecto de Uvicorn/FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación con Uvicorn.
# El 'main:app' hace referencia al archivo main.py y el objeto app.
# El --host 0.0.0.0 es crucial para que sea accesible fuera del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]