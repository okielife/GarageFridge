from json import dumps
from requests import get
from sys import argv, exit
from time import sleep
from typing import Tuple

url = argv[1]
ifttt_event = argv[2]
ifttt_token = argv[3]


def get_temps() -> Tuple[float, float]:
    try:
        r = get(url)
    except Exception as e:  # could be a connection timeout, unknown schema, bad address, etc.
        print(f"Encountered error trying to connect: {str(e)}")
        exit(1)
    data = r.json()
    print(f"Received data response from temperature sensor: {dumps(data)}")
    return data['fridge_temp'], data['freezer_temp']


fridge_temp_limit = 3
freezer_temp_limit = -10
print(f"Limits defined as: {fridge_temp_limit=}, {freezer_temp_limit=}")

fridge_temp, freezer_temp = get_temps()
if freezer_temp < freezer_temp_limit and fridge_temp < fridge_temp_limit:
    print("Temps in range, success, leaving, bye!")
    exit(0)

print("Got an out of range temp, sleeping for two minutes and trying again")
sleep(120)

fridge_temp, freezer_temp = get_temps()
if freezer_temp > freezer_temp_limit or fridge_temp > fridge_temp_limit:
    print("Temps out of range again! Aborting to trigger action failure")
    exit(1)