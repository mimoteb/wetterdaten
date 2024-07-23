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
    data = response.json()
    weather_data = data.get('weather', [])
    df = pd.DataFrame(weather_data)

    # Drop specified columns
    columns_to_drop = ['wind_direction', 'cloud_cover', 'dew_point', 'pressure_msl', 'sunshine']
    df.drop(columns=columns_to_drop, inplace=True)

    # Convert date format to dd.MM.yyyy
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.strftime('%d.%m.%Y')

    df.to_excel(excel_filename, index=False)
    print(f"Weather data saved to {excel_filename}")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
