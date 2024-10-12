#!/usr/bin/env python3

import requests

def fetch_coin_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data")
        return None

def display_coin_info(data):
    if data:
        print(f"Token Address: {data['tokenAddress']}")
        print(f"Description: {data['description']}")
        print(f"Website: {data['links'][0]['url']}")
        # Add more fields as needed

def main():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    data = fetch_coin_data(url)
    display_coin_info(data)
    # Add logic to determine when to buy based on price or other conditions

if __name__ == "__main__":
    main()
