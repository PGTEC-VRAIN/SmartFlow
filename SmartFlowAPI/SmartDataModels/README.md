# SmartDataModels

We've defined SmartDataModels to standardize the way information is shared in our project.

## WeatherForcastSeries

Is a modification of the existing [WeatherForcast](https://smart-data-models.github.io/dataModel.Weather/WeatherForecast/schema.json)
where most variable types have been turned into an array of their previous type. This way we can represent a series of weather forecasts
in a single object.

Some of the variables whose types that have been change where defined by reference in [Weather-Commons](https://smart-data-models.github.io/dataModel.Weather/weather-schema.json#/definitions/Weather-Commons).
Now they are defined in the WeatherForcastSeries' schema.

A variable timestamps has been added to indicate the moment each prediction of the series refers to.
