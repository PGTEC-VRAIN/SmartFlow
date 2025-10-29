from datetime import datetime
import json

class WeatherForecastSeries:
    """
    A harmonised description of a Weather Forecast Series, based on the 
    Smart Data Models WeatherForecast schema, tailored to exclude daily min/max 
    properties and enforce the 'WeatherForecast' type, using modern Python 
    type hint syntax (PEP 585 and PEP 604).
    """

    def __init__(
        self,
        # Required Properties
        id: str,
        dateIssued: datetime,
        
        # Location-Commons (Inferred from schema structure)
        location = None,
        address: dict | None = None,
        
        # Weather-specific Properties
        weatherType: str | None = None,
        visibility: list[str] | list[float] | None = None,
        windDirection: list[float] | None = None,
        windSpeed: list[float] | None = None,
        gustSpeed: list[float] | None = None,
        refPointOfInterest: str | None = None,
        atmosphericPressure: list[float] | None = None,
        illuminance: list[float] | None = None,
        temperature: list[float] | None = None,
        feelsLikeTemperature: list[float] | None = None,
        relativeHumidity: list[float] | None = None, # Range [0, 1]
        timestamp: list[datetime] | None = None, # Lista de fechas 
        dateRetrieved: datetime | None = None,
        validFrom: datetime | None = None,
        validTo: datetime | None = None,
        uVIndexMax: list[float] | None = None,
        precipitation: list[float] | None = None,
        precipitationProbability: list[float] | None = None,
        solarRadiation: list[float] | None = None,        
        # GSMA-Commons (For any other metadata)
        **kwargs
    ) -> None:
        # Required
        self.id = id
        self.dateIssued = dateIssued
        
        # Hardcoded Type
        self.type: str = 'WeatherForecastSeries'
        
        # Location-Commons
        self.location = location
        self.address = address

        # Weather-specific
        self.weatherType = weatherType
        self.visibility = visibility
        self.windDirection = windDirection
        self.windSpeed = windSpeed
        self.gustSpeed = gustSpeed
        self.refPointOfInterest = refPointOfInterest
        self.atmosphericPressure = atmosphericPressure
        self.illuminance = illuminance
        self.temperature = temperature
        self.feelsLikeTemperature = feelsLikeTemperature
        self.relativeHumidity = relativeHumidity
        self.timestamp = timestamp
        self.dateRetrieved = dateRetrieved
        self.validFrom = validFrom
        self.validTo = validTo
        self.uVIndexMax = uVIndexMax
        self.precipitation = precipitation
        self.precipitationProbability = precipitationProbability,
        self.solarRadiation = solarRadiation
        
        # Store any extra attributes from kwargs
        self._extra_attrs = kwargs

    def _to_dict(self) -> dict:
        """Converts the object to a dictionary, handling datetime and filtering None values."""
        data = {}
        
        # Properties to exclude (private, derived, or explicitly requested for removal)
        #EXCLUDE_KEYS = ['_extra_attrs', 'dayMaximum', 'dayMinimum']
        
        # Iterate over all attributes
        for key, value in self.__dict__.items():
            if key.startswith('_')  or value is None: #or key in EXCLUDE_KEYS
                continue

            # Handle datetime objects: convert to ISO 8601 string
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            else:
                data[key] = value

        # Add any extra attributes captured by **kwargs
        data.update(self._extra_attrs)
        
        return data

    def __repr__(self) -> str:
        """Outputs a JSON string containing the serialized object."""
        return json.dumps(self._to_dict(), indent=4)