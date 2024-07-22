import requests
import pandas as pd

# Define variables for the URL parameters and filename
tz_date = 'Europe%2FBerlin'
beginning_date = '2023-02-27'
end_date = '2023-07-22'
latitude = 52.425394
longitude = 9.867977
units = 'dwd'
excel_filename = 'weather_data.xlsx'

# Construct the URL using the defined variables
url = f'https://api.brightsky.dev/weather?date={beginning_date}&last_date={end_date}&lat={latitude}&lon={longitude}&tz={tz_date}&units={units}'
headers = {'Accept': 'application/json'}

# Make the GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Extract relevant data
    weather_data = data.get('weather', [])

    # Create a DataFrame from the weather data
    df = pd.DataFrame(weather_data)

    # Save the DataFrame to an Excel file
    df.to_excel(excel_filename, index=False)
    print(f"Weather data saved to {excel_filename}")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
