'''

'''
from WeatherForecastSeries import WeatherForecastSeries
import os
import re
import pandas as pd
import rasterio
import numpy as np
import glob
import json
import os
import requests
import tarfile
from io import BytesIO
import datetime


# Carpeta de datos
data_path = "./Datos/HARMONIE/"

# Diccionario de variables y sufijos de archivo
variables_sufijos = {
    "temperatura": "_11.tif",
    "viento": "_32.tif",
    "prec_1h": "_61_1HH.tif",
    # "prec_3h": "_61_3HH.tif",
    # "prec_6h": "_61_6HH.tif",
    # "nubosidad": "_71.tif",
    # "descargas_electricas": "_207.tif",
    # "descargas_electricas3h": "_207_3HH.tif",
    # "racha_maxima_viento": "_228.tif",
    # "racha_maxima_viento3h": "_228_3HH.tif"
}


def download_harmonie_pb(output_dir):
    """
    Descarga el archivo ZIP del modelo HARMONIE PB desde AEMET,
    lo guarda en disco y lo descomprime.

    Args:
        output_dir (str): Carpeta donde guardar los datos.

    Returns:
        list: Lista de rutas de los archivos descomprimidos.
    """
    url = "https://www.aemet.es/es/api-eltiempo/modelos/download/harmonie/PB"
    # Si existe, eliminar archivos antiguos
    if os.path.exists(output_dir):
        print("🗑️ Limpiando archivos antiguos en: ", output_dir)
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))

    os.makedirs(output_dir, exist_ok=True)
 
    print("📡 Descargando datos desde AEMET...")
    response = requests.get(url, timeout=60)
    print(response.status_code, response.headers.get("content-type"))

    # guardamos la fecha de la descarga:
    download_time = datetime.datetime.now().isoformat()
    print("🕒 Fecha de descarga:", download_time)
    if response.status_code != 200:
        raise Exception(f"❌ Error {response.status_code} al descargar desde AEMET")

    content_type = response.headers.get("content-type", "")
    if "tar" not in content_type and "gzip" not in content_type:
        raise Exception(f"❌ El contenido no parece ser un archivo TAR/GZIP: {content_type}")

    # Abrir el TAR en memoria
    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
        tar.extractall(output_dir)
        files = tar.getnames()

    print(f"✅ Descarga y extracción completada: {len(files)} archivos guardados en {os.path.abspath(output_dir)}")

    return [os.path.join(output_dir, f) for f in files], download_time


def tif_to_dataframe_realvalues(filepath, variable):
    """
    Convierte un archivo GeoTIFF RGBA (procedente de AEMET HARMONIE) en un DataFrame 
    con coordenadas, timestamp y valores físicos (temperatura, viento, precipitación, etc.).

    La función interpreta la paleta de colores contenida en los metadatos `ESCALA`
    para transformar los valores de color RGBA en magnitudes físicas reales mediante
    interpolación lineal entre los puntos de la escala.

    Parámetros
    ----------
    filepath : str
        Ruta completa al archivo .tif descargado desde AEMET.
    variable : str
        Nombre de la variable (por ejemplo, 'temperatura', 'viento', 'precipitacion').

    Devuelve
    -------
    df : pandas.DataFrame
        DataFrame con columnas:
            - lat : latitud (°)
            - lon : longitud (°)
            - valor : valor físico interpolado
            - timestamp : fecha/hora obtenida del nombre del archivo
            - variable : nombre de la variable correspondiente
    """
    
    with rasterio.open(filepath) as src:
        # Leer array RGBA (4 bandas)
        if src.count < 4:
            raise ValueError("Se esperaban 4 bandas RGBA en el TIF.")
        array_index = src.read()
        # print("array_INDEX",array_index.shape)
        imagen_rgba = np.moveaxis(array_index, 0, -1).astype(np.uint8)
        tags = src.tags()
        escala_str = tags.get('ESCALA')
        if not escala_str:
            raise ValueError(f"No se encontró ESCALA en metadatos de {filepath}")
        
        escala_dict = json.loads(escala_str.replace("'", '"'))
        alto, ancho, _  = imagen_rgba.shape

        puntos_clave_list = []

    for entry in escala_dict["Lista RGBA"]:
        # 1. Extraer Temperatura Máxima
        # Convertir a flotante, ignorando el string vacío '' (si existe)
        valores_numericos = [float(v) for v in entry["Valores"] if v != '']
        
        # Si hay valores, T_max es el máximo del intervalo.
        if valores_numericos:
            T_max = max(valores_numericos)
        else:
            # Manejar el caso si 'Valores' es ['',''] (improbable, pero seguro)
            continue 
        
        # 2. Extraer R, G, B
        # El cuarto valor es 'A' (Alpha), que generalmente es 255.
        R, G, B = [int(c) for c in entry["RGBA"][:3]]
        
        # 3. Construir el punto clave [T_max, R, G, B]
        puntos_clave_list.append([T_max, R, G, B])

    # Convertir la lista a un array de NumPy para el procesamiento
    puntos_clave = np.array(puntos_clave_list, dtype=np.float32)
    Temperaturas = puntos_clave[:, 0]
    Colores = puntos_clave[:, 1:]
    # print("Temperaturas",Temperaturas)
    # print("Colores",Colores)
    # Inicializar matriz de temperaturas recuperadas
    temperaturas_recuperadas = np.full((alto, ancho), np.nan, dtype=np.float32)

    # Flatten de la imagen para procesar cada píxel RGBA
    pixeles = imagen_rgba.reshape(-1, 4)[:, :3] # Solo nos interesa RGB (las 3 primeras columnas)
    # print(imagen_rgba.shape)
    # print("pixeles",pixeles)
    # --- Proceso de Interpolación (Vectorizado en lo posible) ---

    # 1. Calcular la distancia euclidiana de CADA PÍXEL a CADA PUNTO CLAVE
    # (N_pixeles, 3) - (N_puntos, 3) -> (N_pixeles, N_puntos, 3)
    diff = pixeles[:, None, :] - Colores[None, :, :]
    # Distancia euclidiana: sqrt(sum(diff**2)) -> (N_pixeles, N_puntos)
    distancias = np.sqrt(np.sum(diff**2, axis=2))

    # 2. Encontrar los dos puntos clave más cercanos para CADA PÍXEL
    # Obtener los índices de las dos distancias más pequeñas
    indices_cercanos = np.argsort(distancias, axis=1)[:, :2]

    # 3. Aplicar interpolación lineal

    # Distancias a P1 y P2
    d_P1 = distancias[np.arange(len(pixeles)), indices_cercanos[:, 0]]
    d_P2 = distancias[np.arange(len(pixeles)), indices_cercanos[:, 1]]

    # Temperaturas de P1 y P2
    T_P1 = Temperaturas[indices_cercanos[:, 0]]
    T_P2 = Temperaturas[indices_cercanos[:, 1]]

    # Casos especiales: Si la distancia es casi cero (coincidencia exacta), evita división por cero
    denominador = d_P1 + d_P2
    denominador[denominador == 0] = 1e-9 

    # Cálculo de alfa y la temperatura interpolada
    # Asumimos que T_P1 < T_P2, si no, es (T_P2 - T_P1) * (d_P1 / denominador) + T_P1
    # O más simplemente: (T_1 * d_2 + T_2 * d_1) / (d_1 + d_2)
    # Esto es una interpolación ponderada por la inversa de la distancia
    T_recuperada_plana = (T_P1 * d_P2 + T_P2 * d_P1) / denominador

    # Reconstruir la matriz 2D
    temperaturas_recuperadas = T_recuperada_plana.reshape(alto, ancho)

    # Transformamos a coordenadas (x,y)
    rows, cols = np.indices(temperaturas_recuperadas.shape)
    lons, lats = rasterio.transform.xy(src.transform, rows, cols)

    # Convertir listas de listas a arrays planos
    lons = np.array(lons).flatten()
    lats = np.array(lats).flatten()
    valores = temperaturas_recuperadas.flatten()

    # Timestamp desde el nombre de archivo
    match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2})", filepath)
    timestamp = datetime.datetime.strptime(match.group(1), "%Y-%m-%dT%H") if match else None
    # print("TIMESTAMP: ",timestamp)
    # print("LATS: ",lats)
    # print("LONS: ",lons)
    # # print("temperaturas: ",temperaturas_recuperadas)
    # print(len(lats), len(lons), len(valores))
    # Deberían ser iguales: alto * ancho
    # print(alto * ancho)
    df = pd.DataFrame({
        "lat": lats,
        "lon": lons,
        "valor": valores,
        "timestamp": timestamp,
        "variable": variable
    })
        
    return df

def pivotar_y_recortar_datos_a_comunidad_valenciana(df):
    """
    Pivota los datos para tener las variables cada una en una columna diferente y luego recorta el DataFrame para coger solo puntos de la Comunidad Valenciana.

    Parámetros
    ----------
    df : pandas.DataFrame
        DataFrame con columnas 'lat' y 'lon'.

    Devuelve
    -------
    df_recortado : pandas.DataFrame
        DataFrame filtrado para la Comunidad Valenciana.
    """

    ### 1º: PIVOTE
    # Pivotar para que cada variable sea columna (dehago el pd.concat previo)
    df_wide = df.pivot_table(
        index=["lat", "lon", "timestamp"],
        columns="variable",
        values="valor"
    ).reset_index()

    df_wide.columns.name = None #quitar multi index del nombre de las columnas
    
    ### 2º: RECORTE
    cv_bounds = {
        "lat_min": 38.0,
        "lat_max": 40.3,
        "lon_min": -1.0,
        "lon_max": 0.5
    }
    df_recortado = df_wide[
        (df_wide["lat"] >= cv_bounds["lat_min"]) &
        (df_wide["lat"] <= cv_bounds["lat_max"]) &
        (df_wide["lon"] >= cv_bounds["lon_min"]) &
        (df_wide["lon"] <= cv_bounds["lon_max"])
    ]
    return df_recortado

def main():
    _ ,download_time = download_harmonie_pb("./Datos/HARMONIE")

    dfs = []
    for var, suf in variables_sufijos.items():
        for f in sorted(glob.glob(f"{data_path}/*{suf}")):
            dfs.append(tif_to_dataframe_realvalues(f, var))


    df_final = pd.concat(dfs, ignore_index=True)

    df_cv = pivotar_y_recortar_datos_a_comunidad_valenciana(df_final)
 
    df_cv["timestamp"] = df_cv["timestamp"].astype(str)

    datos = WeatherForecastSeries(
        id="Harmonie-Arome_AEMET_CV_001",
        dateIssued=download_time,
        timestamp = df_cv["timestamp"].tolist(),
        lat = df_cv["lat"].tolist(),
        lon = df_cv["lon"].tolist(),
        precipitation = df_cv["prec_1h"].to_list(),
        windSpeed = df_cv["viento"].to_list()
    )
    datos_dict = datos._to_dict()
    print("Variables del JSON: ",datos_dict.keys())
    print("Cantidad de datos de termperatura descargados: ",len(datos_dict["precipitation"]))
    print("FIN DEL PROCESO DE DESCARGA DE PREDICCIONES HARMONIE-AROME DE AEMET.")

if __name__ == "__main__":
    main()