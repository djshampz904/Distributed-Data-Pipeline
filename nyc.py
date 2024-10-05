#!/usr/bin/env python3

import requests
import csv

url = "https://data.cityofnewyork.us/resource/w7w3-xahh.csv"

rows = 1000
offset = 0
headers_fetched = False
headers = []
header_inserted = False

while True:
    response = requests.get(url, params={"$limit": rows, "$offset": offset})
    if response.status_code == 200:
        data = response.text
        if headers_fetched == False:
            data_lines = data.splitlines()
            headers = [header.strip('"') for header in data_lines[0].split(',')]

            print(headers)
            headers_fetched = True


        if not data:
            # no data found
            break

        data_modified = [[field.strip('"') for field in line.split(',')] for line in data_lines[1:]]


        with open('nyc.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            if header_inserted == False:
                writer.writerow(headers)
                header_inserted = True

            writer.writerows(data_modified)


        offset += rows
        print(f"Fetched {len(data)} records")


    else:

        print("Failed to fetch data")
        break

print(f"Total records retrieved {len(all_data)}")

