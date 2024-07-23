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

    # Keep only specified columns
    columns_to_keep = ['timestamp', 'temperature', 'precipitation']
    df = df[columns_to_keep]

    # Convert timestamp to datetime and filter by time range
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df[(df['timestamp'].dt.hour >= 5) & (df['timestamp'].dt.hour <= 14)]

    # Group by date and aggregate data
    df['date'] = df['timestamp'].dt.strftime('%d.%m.%Y')
    grouped = df.groupby('date').agg({
        'temperature': lambda x: ','.join(map(str, x)),
        'precipitation': lambda x: ','.join(map(str, x))
    }).reset_index()

    # Add column for temperature under 5 degrees
    grouped['temperature_under_5'] = grouped['temperature'].apply(
        lambda x: 'Ja' if any(float(temp) < 5 for temp in x.split(',')) else 'Nein'
    )

    # Add column for rain in two hours
    df['precipitation_rain'] = df['precipitation'] > 0
    rain_agg = df.groupby('date').agg({
        'precipitation_rain': lambda x: 'Ja' if x.sum() >= 2 else 'Nein'
    }).reset_index()

    # Merge the rain_agg with grouped
    grouped = grouped.merge(rain_agg, on='date')

    # Rename the column to match the specification
    grouped.rename(columns={'precipitation_rain': 'rained_for_2_hours'}, inplace=True)

    # Save to Excel
    grouped.to_excel(excel_filename, index=False)
    print(f"Weather data saved to {excel_filename}")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
