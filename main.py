from rich.console import Console
import requests
from rich.console import Console
from datetime import datetime, timezone
from rich.table import Table
import pytz
import math

console = Console()
url = "https://v6.bvg.transport.rest/stops/${}/departures?pretty=true&suburban=true&subway=true&tram=true&bus=true&ferry=false&express=false&regional=true"
stations = []
requests.packages.urllib3.util.connection.HAS_IPV6 = False
a = {
    'tripId': '1|64221|2|86|4062024',
    'stop': {
        'type': 'stop',
        'id': '900120014',
        'name': 'Grünberger Str./Warschauer Str. (Berlin)',
        'location': {'type': 'location', 'id': '900120014', 'latitude': 52.512402, 'longitude': 13.452393},
        'products': {'suburban': False, 'subway': False, 'tram': True, 'bus': True, 'ferry': False, 'express': False, 'regional': False},
        'stationDHID': 'de:11000:900120014'
    },
    'when': '2024-06-04T20:36:00+02:00',
    'plannedWhen': '2024-06-04T20:31:00+02:00',
    'delay': 300,
    'platform': None,
    'plannedPlatform': None,
    'prognosisType': 'prognosed',
    'direction': 'S+U Warschauer Str.',
    'provenance': None,
    'line': {
        'type': 'line',
        'id': 'm10',
        'fahrtNr': '20466',
        'name': 'M10',
        'public': True,
        'adminCode': 'BVT---',
        'productName': 'Tram',
        'mode': 'train',
        'product': 'tram',
        'operator': {'type': 'operator', 'id': 'berliner-verkehrsbetriebe', 'name': 'Berliner Verkehrsbetriebe'}
    },
    'remarks': [{'type': 'hint', 'code': 'FK', 'text': 'Bicycle conveyance'}],
    'origin': None,
    'destination': {
        'type': 'stop',
        'id': '900120004',
        'name': 'S+U Warschauer Str. (Berlin)',
        'location': {'type': 'location', 'id': '900120004', 'latitude': 52.505768, 'longitude': 13.449157},
        'products': {'suburban': True, 'subway': True, 'tram': True, 'bus': True, 'ferry': False, 'express': False, 'regional': False},
        'stationDHID': 'de:11000:900120004'
    },
    'currentTripPosition': {'type': 'location', 'latitude': 52.533239, 'longitude': 13.439206},
    'occupancy': 'low'
}

def getStationData(stationId):
    print(url.replace("${}",stationId))
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
            if ((c.seconds/60) > 0 and (c.seconds/60) < 1):
                deltaString = f"In less than a minute"
            elif (c.seconds/60) > 0:
                deltaString = f"In [bold]{math.floor(c.seconds/60)}[/bold] minute(s)"
            elif (c == 0):
                deltaString = "[green]Right now![/green]"
            table.add_row(str(departure["line"]["product"])[0].upper()+str(departure["line"]["product"])[1:] + " nach " + departure['destination']["name"], f"{deltaString}")

    console.print(table)
getStationData("900193002")
getStationData("900120014")
getStationData("900120001")
getStationData("900120025")



