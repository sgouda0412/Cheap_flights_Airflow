# Search of cheap flights with Airflow

This repository is part of a project of the Data Engineering course of the Master's Degree in Data Science of the Universidad de Sonora.

<p align="center">
  <img src="https://github.com/josemal98/Cheap_flights_Airflow/assets/90294947/8e5592f9-0cb2-4dd0-ab1e-88647e20576e" alt="Logo Unison" width="20%" height="20%">
  <img src="https://github.com/josemal98/Cheap_flights_Airflow/assets/90294947/559ccb14-a5d8-4861-9f82-df1a9f4ea62a" alt="Logo MCD" width="20%" height="20%">
</p>

In general terms, the project consists of developing and implementing a data pipeline on the Airflow platform. More specifically, the goal of my project is to automate the search for cheap flights. For this I developed a Dag in Airflow with the following tasks:

1.- **Search_flights:** extracts information about available flights from a predetermined origin and to a predetermined destination. This is performed by means of a request to the free API: [Travelpayouts Data API](https://travelpayouts-data-api.readthedocs.io/en/latest/). These data are then preprocessed to obtain a tidy structure.
 
2.- **Evaluate_flight_prices:** the prices of these flights are evaluated with respect to a predetermined threshold.
 
3a.- **Send_email:** this task is executed only when the second task has found one or more flights whose price is below the threshold. It consists of sending a notification by mail with the information of cheap flights.

3b.- **Do_nothing:** this is a dummy task that does nothing and is executed only when the second task has found no flight whose price is below the threshold.
