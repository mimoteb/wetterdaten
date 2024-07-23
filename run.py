import json

import arrow
import xlsxwriter


def run():
    # Read in data
    with open("./data.json", "r") as f:
        data = json.loads(f.read())

    # Gather Weather Stations
    stations = {}
    for station in data["sources"]:
        name = station["station_name"]
        lat = station["lat"]
        lon = station["lon"]
        stations[station["id"]] = f"{name} ({lat}, {lon})"

    # Filter and Prepare Data
    output_data = {}
    for entry in data["weather"]:
        timestamp = arrow.get(entry["timestamp"])
        timestamp = timestamp.to("Europe/Berlin")
        entry_date = timestamp.format("DD.MM.YYYY")
        start = timestamp.replace(hour=5)
        end = timestamp.replace(hour=14)
        if timestamp >= start and timestamp <= end:
            try:
                entries = output_data[entry_date]
            except KeyError:
                entries = []
                output_data[entry_date] = entries

            entries.append(
                (entry["temperature"], entry["precipitation"], entry["source_id"])
            )

    # Write Excel File
    headers = [
        "Datum (05:00–14:00)",
        "Temperaturen (°C)",
        "Niederschläge (mm)",  # Total precipitation during previous 60 minutes
        "2 Stunden hintereinander geregnet",
        "Unter 5°C",
        "Stationen (Koordinaten)",
    ]
    workbook = xlsxwriter.Workbook("output.xlsx", {"remove_timezone": False})
    worksheet = workbook.add_worksheet(name="Blatt 1")
    worksheet.write_row(0, 0, headers)
    row_id = 1
    for entry_date, entries in output_data.items():
        temperatures = [e[0] for e in entries]
        percipitations = [e[1] for e in entries]
        stations_entries = set([stations[e[2]] for e in entries])
        temp_cell = ", ".join([f"{x:.2f}" for x in temperatures])
        perc_cell = ", ".join([f"{x:.2f}" for x in percipitations])
        station_cell = ", ".join(stations_entries)
        has_rained = False
        rained_count = 0
        for p in percipitations:
            if p > 0:
                rained_count += 1
            else:
                rained_count = 0

            if rained_count == 2:
                has_rained = True
                break
        under_5_degrees = min(temperatures) < 5.0
        rained_cell = "Ja" if has_rained else "Nein"
        under_5_degrees_cell = "Ja" if under_5_degrees else "Nein"

        columns = [
            entry_date,
            temp_cell,
            perc_cell,
            rained_cell,
            under_5_degrees_cell,
            station_cell,
        ]
        worksheet.write_row(row_id, 0, columns)
        row_id += 1

    workbook.close()


if __name__ == "__main__":
    run()
