import asyncio
import aiohttp
from rich.console import Console
import requests
from rich.console import Console
from datetime import datetime, timezone
from rich.table import Table
import pytz
import math
import time
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, ListView, Static, DataTable

console = Console()
url = "https://v6.bvg.transport.rest/stops/${}/departures?pretty=true&suburban=true&subway=true&tram=true&bus=true&ferry=false&express=false&regional=true"
stations = ["900193002","900120014","900120001","900120025"]
berlin_tz = pytz.timezone("Europe/Berlin")
requests.packages.urllib3.util.connection.HAS_IPV6 = False

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

async def parse_destinations(stations):
    filtered_departures = []
    berlin_tz = pytz.timezone("Europe/Berlin")
    urls = [f"https://v6.bvg.transport.rest/stops/{station}/departures?pretty=false&suburban=true&subway=true&tram=true&bus=true&ferry=false&express=false&regional=true" for station in stations]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            for departure in response["departures"]:
                if "when" in departure and departure["when"] is not None and "direction" in departure and "direction"!="Fahrt endet hier" and  "name" in departure["line"]:
                    filtered_departures.append({
                        "line_name": departure["line"]["name"],
                        "direction": departure["direction"],
                        "minutes": math.floor((datetime.strptime(departure["when"], "%Y-%m-%dT%H:%M:%S%z")-datetime.now(berlin_tz)).seconds/60)
                    })
    return filtered_departures

async def asyncGetFilteredDepartures():
    stations = ["900193002","900120014","900120001","900120025"]
#    stations = ["900120025"]
    filtered_departures = await parse_destinations(stations)
    return sorted(filtered_departures, key=lambda x: x['minutes'])



class ArrivalKiosk(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "vert.tcss"

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Line", "Direction", "departure")
        self.set_interval(3,self.get_stations)

    async def get_stations(self) -> None:
        table = self.query_one(DataTable)
        # newRow = []
        # newRow = getFilteredDepartures(stations[1])[0]
        newRows = await asyncGetFilteredDepartures()
        for newRow in newRows:
            table.add_row(newRow["line_name"],newRow["direction"],newRow["minutes"])

app = ArrivalKiosk()

def getFilteredDepartures(stationId):
    r = requests.get(url.replace("${}", stationId))
    filtered_departures = []

    for departure in r.json()["departures"]:
        if "when" in departure and "direction" in departure and  "name" in departure["line"]:
            filtered_departures.append({
                "line_name": departure["line"]["name"],
                "direction": departure["direction"],
                "minutes": math.floor((datetime.strptime(departure["when"], "%Y-%m-%dT%H:%M:%S%z")-datetime.now(berlin_tz)).seconds/60)
            })
    return filtered_departures

def getStationData(stationId):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "*/*","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    r = requests.get(url.replace("${}",stationId), headers=headers)

    table = Table(show_header=True, header_style="bold magenta", title="Transportation stop")
    table.add_column("Mode of Transport", width=20)
    table.add_column("Departure Time", width=20)

    for departure in r.json()["departures"]:
        when = None
        plannedWhen = None
        try:
            when = datetime.strptime(departure["when"], "%Y-%m-%dT%H:%M:%S%z")
        except:
            pass
        plannedWhen = datetime.strptime(departure["plannedWhen"], "%Y-%m-%dT%H:%M:%S%z")
        if when == None:
            table.add_row(str(departure["line"]["product"])[0].upper()+str(departure["line"]["product"])[1:] + " nach " + departure['destination']["name"], "[red]Cancelled[/red]")
        else: 
            berlin_tz = pytz.timezone("Europe/Berlin")
            c = plannedWhen - datetime.now(berlin_tz)
            print(c.seconds, plannedWhen, datetime.now(berlin_tz))
            if ((c.seconds/60) > 0 and (c.seconds/60) < 1):
                deltaString = f"In less than a minute"
            elif (c.seconds/60) > 0:
                deltaString = f"In [bold]{math.floor(c.seconds/60)}[/bold] minute(s)"
            elif (c == 0):
                deltaString = "[green]Right now![/green]"
            elif (c < 0):
                deltaString = f"[red][bold]{math.floor(c.seconds/60)}[/bold] minute(s) ago[/red]"
            table.add_row(str(departure["line"]["product"])[0].upper()+str(departure["line"]["product"])[1:], "" + " nach " + departure['destination']["name"], f"{deltaString}")

if __name__ == "__main__":
    app.run()
