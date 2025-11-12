<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!--
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Unlicense License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
-->


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://airflow.apache.org/">
    <img src="Airflow/images/airflow.png" alt="Airflow Logo" width="80"/>
  </a>

  <h3 align="center">Airflow</h3>

  <p align="center">
    Repository containing Python scripts to ingest data from multiple climate models, transform it into FIWARE Smart Data Model WeatherForecastSeries, and build Airflow DAGs to orchestrate automated data pipelines.
    <br />
    <a href="https://pgtec-vrain.github.io/welcome/"><strong>See the PGTEC web page »</strong></a>
    <br />
    <!--<br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    &middot;
    <a href="https://github.com/othneildrew/Best-README-Template/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/othneildrew/Best-README-Template/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>-->
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Service</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <!--<li><a href="#prerequisites">Prerequisites</a></li>-->
        <!--<li><a href="#cheatsheet">Cheatsheet</a></li>-->
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <!--<li><a href="#roadmap">Roadmap</a></li>-->
    <!--<li><a href="#contributing">Contributing</a></li>-->
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#references">References</a></li>
  </ol>
</details>


<!-- ABOUT THE SERVICE -->
## About The service 

Apache Airflow is a service that enables the programmatic execution of different tasks. In this project, Airflow's objective is to periodically execute Python scripts that access multiple weather forecast model data sources to extract the most recent forecasts and store them. Using Airflow makes it possible to automatically obtain the most recent model forecasts once the frequency of model execution is known.

The prediction models of interest in the project are as follows:

- ARPEGE from MeteoFrance
- ICON_EU from the German Meteorological Service (DWD)
- GFS from the US agency (NOAA)
- IFS from the European agency (ECMWF)
- AIFS from the European agency (ECMWF)
- GEPS from the Canadian agency (CNC)
- Seas5 from Copernicus (ECMWF)
- Harmonie-Arome from AEMET
- EFAS from Copernicus 
- EFFIS from Copernicus

The predictions of all models except the last three can be accessed from the <a href="https://open-meteo.com/">Open-Meteo</a> API. The Harmonie-Arome model predictions can be accessed via the official website. The EFAS and EFFIS predictions can be accessed via the Copernicus Climate Data Store (CDS).

### Built With

The service is built using the following main components:

<div align="center">

| | | | |
|:-------------------------------------------:|:--------------------:|:-------------------:|:---------------------:|
| [![Python][Python]][Python-url] | [![Airflow][Airflow]][Airflow-url] | [![Smart-data-models][Smart-data-models]][Smart-Data-models-url] | [![Docker][Docker]][Docker-url] |


</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
### Getting Started 

Here is a brief explanation of the Python scripts:

- `AEMET_HARMONIE_AROME.py`: Python script that retrieves weather forecast data from the AEMET website and processes it programatically using airflow sintaxis

  - **Data**: All the data is processed into a standardized format defined by the `WeatherForecastSeries.py` Smart Data Model. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Wind Speed 

  - **Raw Data**: The input data are GeoTIFF (.tif) files containing weather variables encoded as color values. Using a color scale provided by AEMET, the script converts these color codes (RGBA) into real physical values such as temperature, wind speed, and precipitation.

  - **API Key**: No API key is required for execution as we are downloading public data from AEMET website.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.
 
All the following scripts retrieve data from OpenMeteo API:

- `AIFS_ECMWF.py`: Python script that retrieves weather data from the Open-Meteo API programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Wind Speed

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.

- `ARPEGE.py`: Python script that retrieves weather data from the Open-Meteo API programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Relative Humidity
    - Solar Radiation

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.

- `DWD_ICON_EU.py`: Python script that retrieves weather data from the Open-Meteo API programmatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.

- `GEPS_ENS_CNC.py`: Python script that retrieves weather data from the Open-Meteo API programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Wind Speed

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.

- `GFS_NOAA.py`: Python script that retrieves weather data from the Open-Meteo API programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Wind Speed
    - Solar Radiation

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.


- `IFS9km_ECMWF.py`: Python script that retrieves weather data from the Open-Meteo API programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Wind Speed

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.

- `Seas5_ECWMF_copernicus.py`: Python script that retrieves weather data from the Open-Meteo API programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are JSON files. The variables we are currently using are:
    - Temperature 
    - Precipitation
    - Wind Speed
    - Solar Radiation

  - **API Key**: No API key is required for execution as we are downloading public data from Open-Meteo API.

  - **Run script**: Run hourly to ensure the latest forecasts are always retrieved and processed.

The last two scrips retrieve data from Copernicus Climate Data Store (CDS) API and Early Warning Data Store (EWDS):

- `EFFIS.py`: Python script that retrieves weather data from the dataset (https://cds.climate.copernicus.eu/datasets/sis-tourism-fire-danger-indicators?tab=overview) and download data programamatically using airflow sintaxis. 

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are NetCDF (.nc) files containing various weather variables:
    - Daily fire weather index

  - **API Key**: An API key is required for execution. To get an API key, you need to register on the Copernicus Climate Data Store website: https://cds.climate.copernicus.eu

  - **Run script**: Run this script daily because Copernicus updates the data once a day. It has been configured to automatically detect the latest available forecast.

- `EFAS.py`: Python script that retrieves weather data from the EWDS dataset (https://ewds.climate.copernicus.eu/datasets/efas-forecast?tab=overview) and download data programamatically using airflow sintaxis.

  - **Data**: processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. 

  - **Raw Data**: The input data are NetCDF (.nc) files containing the following weather variable:
    - River discharge last 6 hours

  - **API Key**: An API key is required for execution. To get an API key, you need to register on the Copernicus Climate Data Store website: https://cds.climate.copernicus.eu

  - **Run script**: Run this script daily because Copernicus updates the data once a day. It has been configured to automatically detect the latest available forecast.

<!--
### Prerequisites

These are the necessary requirements to be able to execute the project:

|                    Software                              | Version / Notes |
| --------------------------------------------------------:|:------- |
| [Python](https://www.python.org/) | 3.x.x  |
| [Airflow](https://airflow.apache.org/) | 2.x  |


### Cheatsheet

* Python (Recommended to create an environment from anaconda / miniconda)
  ```bash
    # Download Miniconda installer (Linux x86_64)
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

    # Run the installer
    bash ~/miniconda.sh

    # Follow the prompts (accept license, choose install path, initialize conda)

    # Initialize conda for bash
    source ~/.bashrc

    # Create a project environment (Python 3.12.3)
    conda create -n pgtec_env python=3.12.3 -y
    conda activate pgtec_env
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

-->

<!-- USAGE EXAMPLES -->
## Usage

This section describes how to deploy and use the Airflow service through a guided example.

To deploy the service:

The first step in deploying the environment is to clone the GitHub repository onto your computer. To do this, follow these instructions in an Ubuntu terminal:

1. Clone the repo and navigate to the service folder
```sh
   git clone https://github.com/PGTEC-VRAIN/SmartFlow
   cd SmartFlow/Airflow
   ``` 

The second step is to launch the Docker service, which must be installed on your computer beforehand.

2. Initialise Docker:
```sh
sudo systemctl start docker
```

The third and final step is to initialise the containers by first building them with `--build` and then launching them with `up`. All of this can be done on the same line. To avoid execution logs, use the `-d` parameter.

3. Initialise Docker containers
```sh
docker compose up --build -d
```

To use the service:

The first step is to access the local web page where Airflow is running. The service is designed to run on localhost on port 8080. Therefore, you must access the following URL to enter Airflow:

1. Access the Airflow URL:
```sh
http:localhost:8080
```
The following credentials have been set in the Airflow service configuration to access Airflow:

2. Login credentials:
```sh
user: airflow
password:airflow
```

Once you have accessed the website, the next step is to access a DAG. To do this, search for the model you are interested in and access the DAG by clicking on it. The following screenshot shows the DAGs available on the Airflow website:

<div align="center">

<img src="images/dags.png" alt="Airflow dags" width="700"/>

</div>

When accessing the DAG, the following window will appear. To activate the DAG, click on the `Trigger` button located in the upper right corner, as shown in the following image:

<div align="center">

<img src="images/dag_DWD_ICON.png" alt="Airflow dags" width="700"/>

</div>

Once the DAG is running, a new window opens showing the status of the DAG execution in real time. In this window, we recommend accessing the task that is being executed by clicking on it. The next window is much more comprehensive. It shows the execution time, the progress of the execution, the code being executed and the logs. To verify that the DAG has been executed correctly, you can access the logs and check that the model data has been downloaded correctly. Below is a screenshot of the DWD_ICON model logs:

<div align="centre">

<img src="images/dag_exec.png" alt="Airflow dags" width="700"/>

</div>

The screenshot shows that the script has run without any problems and that the predictions from the ICON_EU model have been saved in JSON format following the WeatherForecastSeries Smart Data Model.

<!-- ROADMAP 
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->


<!-- CONTRIBUTING 
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
-->
<!---
### Top contributors:

<a href="https://github.com/othneildrew/Best-README-Template/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=othneildrew/Best-README-Template" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

-->

<!-- LICENSE -->
## License

Distributed under the AGPL-3.0 License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/PGTEC-VRAIN](https://github.com/PGTEC-VRAIN)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- References -->
## References

* [Readme Template](https://github.com/othneildrew/Best-README-Template)
* Smart Data Models [Weather Smart Data Model - Fiware](https://github.com/smart-data-models/dataModel.Weather)


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python]: https://img.shields.io/badge/python-3.12.11+-blue.svg?logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Airflow]: https://img.shields.io/badge/airflow-3.0.6-green.svg?logo=apacheairflow&logoColor=white
[Airflow-url]: https://airflow.apache.org/
[Smart-data-models]: https://img.shields.io/badge/SmartDataModels-purple.svg
[Smart-Data-models-url]: https://github.com/smart-data-models/dataModel.Weather
[Docker-url]: https://www.docker.com/
[Docker]: https://img.shields.io/badge/docker-44.4.3+-red.svg?logo=python&logoColor=white
