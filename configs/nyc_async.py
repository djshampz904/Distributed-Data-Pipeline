#!/usr/bin/env python3
import asyncio
import json

import aiohttp

MAX_ITEMS = 100000
BASE_URL = "https://data.cityofnewyork.us/resource/w7w3-xahh.json"
ROWS_PER_REQUEST = 1000


async def fetch_data(session: aiohttp.ClientSession, url: str, ) -> str:
    """ Fetch Data From URL """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching data from {url}: {e}")
        return []


async def get_total_count(session: aiohttp.ClientSession) -> int:
    """ Get Total Count of Records """
    url = f"{BASE_URL}?$select=count(*)"

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return int(data[0]['count'])
    except (aiohttp.ClientError, KeyError, IndexError, ValueError) as e:
        print(f"Error fetching data from {url}: {e}")
        return MAX_ITEMS


async def fetch_data_from_api():

    async with aiohttp.ClientSession() as session:
        total_count = min(await get_total_count(session), MAX_ITEMS)
        urls = [f"{BASE_URL}?$limit={ROWS_PER_REQUEST}&$offset={offset}" for offset in
                range(0, total_count, ROWS_PER_REQUEST)]

        tasks = [fetch_data(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)

        all_data = [item for sublist in responses for item in json.loads(sublist)]

        # print length of dataset
        print(f"Total records retrieved {sum([len(response) for response in responses])}")

        if all_data:
            print(len(all_data))

        return all_data


async def run_async():
    all_data =  await fetch_data_from_api()
    return all_data