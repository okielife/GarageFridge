from json import dumps
from requests import get, post
from sys import argv

url = argv[1]
ifttt_event = argv[2]
ifttt_token = argv[3]

r = get(url)
data = r.json()
fridge_temp = data['fridge_temp']
freezer_temp = data['freezer_temp']

fridge_temp_limit = 2
freezer_temp_limit = -10

if freezer_temp > freezer_temp_limit or fridge_temp > fridge_temp_limit:
    ifttt_response = post(
        f"https://maker.ifttt.com/trigger/{ifttt_event}/json/with/key/{ifttt_token}",
        headers={'content-type': 'application/json'},
        data=dumps({
            'fridge': f"Current temp = {fridge_temp}; Limit = {fridge_temp_limit}",
            'freezer': f"Current temp = {freezer_temp}; Limit = {freezer_temp_limit}"
        })
    )
