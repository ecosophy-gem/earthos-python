from earthos import EarthOS, EOColorScale, COLORSCALES, EOVar
import os

APIKEY = os.environ.get('EARTHOS_APIKEY', None)
if not APIKEY:
    raise ValueError("Please set EARTHOS_APIKEY environment variable")
eo = EarthOS(APIKEY)

def test_point():
    # Hafnarhaus, Reykjavik, Iceland:
    lat = 64.149141
    lon = -21.940747
    # Relative humidity in Reykjavik, Iceland on June 24, 2024 at 16:30 UTC:
    humidity = 84.7
    points = eo.get_point(lat, lon, timestamp='2024-06-24T16:30:00Z', formula='gfs.relative_humidity')
    assert(type(points) == dict)
    assert('result' in points)
    assert(type(points['spacetime']) == dict)
    assert('time' in points['spacetime'])
    assert('latitude' in points['spacetime'])
    assert('longitude' in points['spacetime'])
    assert('error' in points)
    assert(points['error']['type'] == "NoError")
    assert(abs(points['spacetime']['latitude'] - lat) < 0.0001)
    assert(abs(points['spacetime']['longitude'] - lon) < 0.0001)
    assert(points['spacetime']['time'] == 1719246600)
    assert(abs(points['result'] - humidity) < 0.1)

