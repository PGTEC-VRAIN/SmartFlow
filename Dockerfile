FROM apache/airflow:3.0.6

# 1. Definir ARG al inicio (necesario para que el valor se aplique a los pasos de RUN)
# ARG DOCKER_GID=1001
# ARG HOST_UID=1000
# ARG HOST_GID=1000

# Instala dependencias adicionales si las tienes
COPY requirements.txt /requirements.txt
# Instalamos la librería 'docker' en requirements.txt
# La instalación de dependencias debe hacerse como usuario 'airflow'
USER airflow
RUN pip install --no-cache-dir -r /requirements.txt

# 2. Instalar el binario Docker (Se necesita root)
USER root
RUN apt-get update && apt-get install -y docker.io

# RUN groupdel docker || true
# RUN groupadd -r -g ${DOCKER_GID} docker
# RUN usermod -aG docker $USER

# 3. SINCRONIZACIÓN DE PERMISOS (CRÍTICO)
# Esta es la lógica final que asegura que el grupo 'docker' tiene el GID del host.
# RUN groupmod -g ${DOCKER_GID} docker
# RUN groupadd -f -g ${HOST_GID} hostgroup
# RUN usermod -u ${HOST_UID} -g ${HOST_GID} -o -m airflow 
# RUN usermod -aG docker airflow

# 4. Volver al usuario de ejecución de Airflow
USER airflow
