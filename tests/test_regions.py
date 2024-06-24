from datetime import datetime
import os
from earthos import EarthOS, EOVar

APIKEY = os.environ.get('EARTHOS_APIKEY', None)
if not APIKEY:
    raise ValueError("Please set EARTHOS_APIKEY environment variable")
eo = EarthOS(APIKEY)

def test_region():
    data = eo.get_region(90, -90, 180, -180, datetime.now(), "gfs.air_temperature", 1000, 500)
    assert(data.resolution() == (1000, 500))
    assert(data._data.size == 500000)   

def test_tile():
    data = eo.get_tile(0, 0, 0, datetime.now(), "gfs.air_temperature")
    assert(data.resolution() == (256, 256))
    assert(data._data.size == 65536)

def test_formula_tile():
    # Difference in air temperature from 24 hours ago
    airtemp_past = EOVar('gfs.air_temperature').offset(time=-(3600*24))
    airtemp_now = EOVar('gfs.air_temperature')
    airtemp_diff = airtemp_now - airtemp_past
    tile = eo.get_tile(0, 0, 0, timestamp=datetime.now(), formula=airtemp_diff)
    assert(str(airtemp_diff) == '(gfs.air_temperature - gfs.air_temperature[time: -86400])')
    assert(tile.resolution() == (256, 256))
    assert(tile._data.size == 65536)
    assert(tile._original_format == 'pfpng')
