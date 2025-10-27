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
  <a href="https://pgtec.webs.upv.es/">
    <img src="https://pgtec.webs.upv.es/images/logo_PGTEC.svg" alt="PGTEC Logo" width="80"/>
  </a>

  <h3 align="center">Smart data pipelines</h3>

  <p align="center">
    Repository containing Python scripts to ingest data from multiple sources, transform it into FIWARE Smart Data Models, and build Airflow DAGs to orchestrate automated data pipelines.
    <br />
    <a href="https://pgtec.webs.upv.es/"><strong>See the web page »</strong></a>
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
      <a href="#about-the-project">About The Project</a>
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

This README provides an overview of the project’s purpose, setup instructions, usage examples, and references for further development.

<!-- ABOUT THE PROJECT -->
## About The Project

Its main objective is to describe and provide the infrastructure required to deploy a data space using <a href="https://www.fiware.org/">FIWARE</a> technology, offering a detailed and easy-to-follow guide for different environments.

This repository is part of the tasks developed within the <a href="https://pgtec.webs.upv.en/">PGTEC</a> project. Its main objective is to describe and provide the infrastructure required to deploy a data space using  <a href="https://www.fiware.org/">FIWARE</a> technologies, offering a detailed and easy-to-follow guide adaptable to different environments.

The goal of PGTEC is to build a data platform that periodically retrieves historical and forecasted climate and weather data from multiple APIs, standardizes them using Smart Data Models, and stores them in a FIWARE Context Broker with historical persistence — enabling the development of machine learning and deep learning models.

This repository specifically contains the Python scripts used to:

- Retrieve data from multiple climate data sources such as AEMET, CHJ, Open-Meteo, and Copernicus.

- Convert the raw data into FIWARE Smart Data Models to standardize the format.

- The creation of automated Airflow DAGs for pipeline execution.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

The project is built using the following main components:

<div align="center">

  | <!-- -->                                   | <!-- -->             | <!-- -->            |
  |:-------------------------------------------:|:--------------------:|:-------------------:|
  | [![Python][Python]][Python-url]             | [![Airflow][Airflow]][Airflow-url]   | [![Smart-data-models][Smart-data-models]][Smart-Data-models-url] |


</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
### Getting Started 

To get a local copy up and running follow these simple steps in ubuntu command line:

1. Clone the repo and navigate to the project folder
   ```sh
   git clone https://github.com/PGTEC-VRAIN/SmartFlow
   cd SmartFlow
   ``` 

2. Create a virtual environment
   ```sh
   python -m venv venv
   source venv/bin/activate 
   ```

3. Install the required packages
   ```sh
   pip install -r requirements.txt
   ```

4. Initialize Airflow
   ```sh
   airflow standalone
   ```

Here is a brief explanation of the Python scripts:

- `AEMET_HARMONIE_AROME.py`: This script retrieves weather forecast data from the AEMET website and processes it into a standardized format defined by the `WeatherForecastSeries.py` Smart Data Model.
The input data are GeoTIFF (.tif) files containing weather variables encoded as color values.
Using a color scale provided by AEMET, the script converts these color codes (RGBA) into real physical values such as temperature, wind speed, and precipitation.

No API key is required for execution as we are downloading public data from AEMET website.
Run this script hourly to ensure the latest forecasts are always retrieved and processed.

- `ARPEGE-AROME.py`: This script retrieves weather forecast data for the model ARPEGE-AROME from the MeteoFrance website and processes it into a standardized format defined by the `WeatherForecastSeries.py` Smart Data Model.

Data format xxxx
API Key xxxx
Run script xxxx
 
- `Open-Meteo.py`: This script retrieves weather data from the Open-Meteo API and processes it into a standardized format using `WeatherForecastSeries.py` Smart Data Model. The input data are JSON files. Here are the weather models that we are currently using:

- ICON-EU DWD (`dwd_icon_eu`)
- ARPEGE MétéoFrance (`meteofrance_arpege_europe`)
- HRES/IFS 9km Resolution ECMWF  (`ecmwf_ifs`)
- GFS NOAA (`ncep_gfs013`o `ncep_gfs025`)
- AIFS ECMWF (modelo de IA) (`ecmwf_aifs025`)
- GEPS_ENS CMC (`cmc_gem_geps`)
- SEAS5_ECMWF Copernicus (`ecmwf_seas5_6hourly`)

No API key is required for execution.
Run this script hourly to ensure the latest forecasts are always retrieved and processed.

- `Copernicus.py`: This script retrieves weather forecast data from the Copernicus Climate Data Store (CDS) API and Early Warning Data Store (EWDS) and processes it into a standardized format defined by the `WeatherForecastSeries.py` Smart Data Model. The input data are NetCDF (.nc) files containing various weather variables. The weather models currently used are:

- EFFIS (a través del EWDS de Copernicus, no hay tiempo real, Catalogue — CEMS Early Warning Data Store) 
- EFAS (a través del EWDS de Copernicus, no hay tiempo real, Catalogue — CEMS Early Warning Data Store)

An API key is required for execution. To get an API key, you need to register on the Copernicus Climate Data Store website: https://cds.climate.copernicus.eu

Run this script daily to ensure the latest forecasts are always retrieved and processed.

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

This is an example to use the environment using the scripts to download data and convert to Smart Data Models format:

To fill...
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
[Python]: https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Airflow]: https://img.shields.io/badge/airflow-2.x-darkblue.svg?logo=apacheairflow&logoColor=white
[Airflow-url]: https://airflow.apache.org/
[Smart-data-models]: https://img.shields.io/badge/smartdata-models-fiware
[Smart-Data-models-url]: https://github.com/smart-data-models/dataModel.Weather
