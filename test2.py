import asyncio
import aiohttp
import math
import time
from datetime import datetime, timezone
import pytz

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    berlin_tz = pytz.timezone("Europe/Berlin")
    stations = ["900193002","900120014","900120001","900120025"]
    urls = [f"https://v6.bvg.transport.rest/stops/{station}/departures?pretty=false&suburban=true&subway=true&tram=true&bus=true&ferry=true" for station in stations]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)

        filtered_departures = [
            {
                "line_name": departure["line"]["name"],
                "direction": departure["direction"],
                "minutes": math.floor((datetime.strptime(departure["when"], "%Y-%m-%dT%H:%M:%S%z") - datetime.now(berlin_tz)).total_seconds() / 60)
            }
            for response in responses
            for departure in response["departures"]
            if "when" in departure and "direction" in departure and "name" in departure["line"]
        ]

        print(filtered_departures)

asyncio.run(main())
