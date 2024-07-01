import requests
import json
import sys
import os
from earthos import EarthOS

EARTHOS_APIKEY  = os.environ.get('EARTHOS_APIKEY', '')
EARTHOS_ENGINE_HOST = os.environ.get('EARTHOS_ENGINE_HOST', 'https://engine.earthos.ai')
url = f'{EARTHOS_ENGINE_HOST}/points/'

if EARTHOS_APIKEY == '':
    print("You must set EARTHOS_APIKEY before you use this script.")
    sys.exit(-1)

eo = EarthOS(EARTHOS_APIKEY)

payload = {
    "defaults": {
        "formula": "gfs.air_temperature",
        "timestamp": 1679933282,
        "altitude": 2,
        "latitude": -20
    },
    "points": [
        {
            "id": "1",
            "latitude": 66.0,
            "longitude": 23.0
        },
        {
            "id": "2",
            "latitude": 67.0,
            "longitude": 22.0
        },
        {
            "id": "3",
            "latitude": 60.0,
            "longitude": 20.0
        }
    ]
}

response = eo.get_points(payload)
# response = requests.post(url, data=json.dumps(payload), headers=headers)
print("Response: ", response)
# print(response.json())
