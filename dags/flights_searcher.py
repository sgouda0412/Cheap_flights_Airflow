# Import libraries
import datetime
import requests
import pandas as pd
import logging
import os
import sys

# Dictionary of airlines IATA codes
dict_airlines = {"AM": "Aeromexico", "Y4": "Volaris", "VB": "VivaAerobus"}

# Dictionary of cities IATA codes
dict_cities = {
    "CUN": "Cancún",
    "MEX": "Mexico City",
    "SJD": "San José del Cabo",
    "PVR": "Puerto Vallarta",
    "GDL": "Guadalajara",
    "MTY": "Monterrey",
    "HMO": "Hermosillo",
    "ACA": "Acapulco",
    "TIJ": "Tijuana",
    "CZM": "Cozumel",
    "MID": "Mérida",
    "MLM": "Morelia",
    "BJX": "Silao",
    "VER": "Veracruz",
    "CUU": "Chihuahua",
    "ZIH": "Ixtapa",
    "VSA": "Villahermosa",
    "MZT": "Mazatlán",
    "SLP": "San Luis Potosí",
    "TRC": "Torreón",
    "QRO": "Querétaro",
    "ZLO": "Manzanillo",
    "AGU": "Aguascalientes",
    "CUL": "Culiacán",
    "ZCL": "Zacatecas",
    "PBC": "Puebla",
    "OAX": "Oaxaca",
    "TLC": "Toluca",
    "TAM": "Tampico",
    "TGZ": "Tuxtla Gutiérrez",
}


def search_flights(origin, destination, api_token):

    # Get the current date
    current_date = datetime.date.today() - datetime.timedelta(days=1)

    # Calculate the day of the week of the current date (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    current_day = current_date.weekday()

    # If the current date is Friday, Saturday, or Sunday, consider the next Friday and Sunday of the following week
    if current_day >= 4:  # Friday (4), Saturday (5), Sunday (6)
        days_to_next_friday = 7 - (current_day - 4)
        days_to_next_sunday = 9 - current_day
    else:
        # Calculate the number of days to reach the next Friday
        days_to_next_friday = (4 - current_day) % 7

        # Calculate the number of days to reach the next Sunday
        days_to_next_sunday = (6 - current_day) % 7

    # Get the date of the next Friday by adding the corresponding days to the current date
    next_friday = current_date + datetime.timedelta(days=days_to_next_friday)

    # Get the date of the next Sunday by adding the corresponding days to the current date
    next_sunday = current_date + datetime.timedelta(days=days_to_next_sunday)

    # Empty list to store results of each request
    rows = []

    # Loop through all the remaining Fridays and Sundays of the month
    # (If I want to do iterate through all the Fridays and Sundays of the year, replace "month" by "year")
    while (current_date.year == next_friday.year) and (
        current_date.year == next_sunday.year
    ):

        # API request
        url = "https://api.travelpayouts.com/v1/prices/direct"
        querystring = {
            "origin": "HMO",
            "destination": "MEX",
            "depart_date": next_friday.strftime("%Y-%m-%d"),
            "return_date": next_sunday.strftime("%Y-%m-%d"),
            "currency": "MXN",
        }
        headers = {"x-access-token": api_token}
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()

        # Check if the response is not empty
        if data["data"]:

            # Extract relevant data from request response
            origin = dict_cities[querystring["origin"]]
            destination = dict_cities[querystring["destination"]]
            flight_number = data["data"][querystring["destination"]]["0"][
                "flight_number"
            ]
            airline = dict_airlines[
                data["data"][querystring["destination"]]["0"]["airline"]
            ]
            departure_date = data["data"][querystring["destination"]]["0"][
                "departure_at"
            ].split("T")[0]
            departure_times_temp = (
                data["data"][querystring["destination"]]["0"]["departure_at"]
                .split("T")[1]
                .split("-")
            )
            departure_times = (
                departure_times_temp[0][:5] + "-" + departure_times_temp[1][:5]
            )
            return_date = data["data"][querystring["destination"]]["0"][
                "return_at"
            ].split("T")[0]
            return_times_temp = (
                data["data"][querystring["destination"]]["0"]["return_at"]
                .split("T")[1]
                .split("-")
            )
            return_times = return_times_temp[0][:5] + "-" + return_times_temp[1][:5]
            price_expiration_utc = str(
                data["data"][querystring["destination"]]["0"]["expires_at"]
            )[:-1]

            # Create dictionary with extracted relevant data
            new_row = {
                "Origin": origin,
                "Destination": destination,
                "Flight_number": flight_number,
                "Airline": airline,
                "Departure_date": departure_date,
                "Departure_times": departure_times,
                "Return_date": return_date,
                "Return_times": return_times,
                "Price_mxn": data["data"][querystring["destination"]]["0"]["price"],
                "Price_expiration_UTC+0": price_expiration_utc.replace("T", " "),
            }

            # Add dictionary to list
            rows.append(new_row)

        # Increase date to next friday
        next_friday += datetime.timedelta(days=7)

        # Increase date to next sunday
        next_sunday += datetime.timedelta(days=7)

        # Create DataFrame from list of dictionaries
    df = pd.DataFrame(rows)

    # Reorder columns
    # df = df[['Origin', 'Destination', 'Flight_number', 'Airline', 'Departure_date', 'Departure_times', 'Return_date', 'Return_times', 'Price_mxn', 'Price_expiration_UTC+0']]

    # Print Dataframe
    return df
