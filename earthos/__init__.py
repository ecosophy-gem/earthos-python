import math
import requests
import os
from datetime import datetime

from .eoformula import EOFormula, EOVar, EOOffset
from .eoimage import EOData, EOColorScale, COLORSCALES

EARTHOS_ENGINE_HOST = os.environ.get('EARTHOS_ENGINE_HOST', 'https://engine.earthos.ai')
EARTHOS_APIKEY = os.environ.get('EARTHOS_APIKEY', None)

def num2deg(xtile, ytile, zoom):
    n = 1 << zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

class EarthOSAPIError(Exception):
    def __init__(self, message, response=None):
        self.message = message
        self.response = response

    def __str__(self):
        if self.response is None:
            return self.message
        return f"{self.message} ({self.response.status_code}): {self.response.text}"

class EarthOS:
    def __init__(self, api_key=EARTHOS_APIKEY):
        if not api_key:
            raise ValueError("API key is required. Provide it as a parameter or set the EARTHOS_APIKEY environment variable.")
        if not EARTHOS_ENGINE_HOST:
            raise ValueError("EARTHOS_ENGINE_HOST environment variable is required.")
        self.api_key = api_key
        self._varcache = None

    def _get(self, path, params={}, **kwargs):
        url = f'{EARTHOS_ENGINE_HOST}/{path}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        response = requests.get(url, headers=headers, params=params, **kwargs)
        if response.status_code != 200:
            self._show_error(response)
            return None

        return response
    
    def _post(self, path, data, **kwargs):
        url = f'{EARTHOS_ENGINE_HOST}/{path}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        response = requests.post(url, headers=headers, json=data, **kwargs)
        if response.status_code != 200:
            self._show_error(response)
            return None

        return response
    
    def _normalize_timestamp(self, timestamp) -> float:
        if isinstance(timestamp, str):
            return int(datetime.fromisoformat(timestamp).timestamp())
        
        if isinstance(timestamp, datetime):
            return int(timestamp.timestamp())
    
        if isinstance(timestamp, int):
            return timestamp
        
        if isinstance(timestamp, float):
            return int(timestamp)
        
        raise ValueError("Invalid timestamp format.")

    def get_engine_version(self):
        return self._get('version/').json()
    
    def get_variables(self):
        if not self._varcache:
            self._varcache = {}
            sets = self._get('variables/').json()
            for _set in sets:
                for var in _set['variables']:
                    self._varcache[f"{var['namespace']}.{var['name']}"] = var

        return self._varcache
    
    def get_variable(self, namespace, name):
        vars = self.get_variables()
        return EOVar(f'{namespace}.{name}', info=vars.get(f'{namespace}.{name}', None))
    
    def get_variable(self, name):
        vars = self.get_variables()
        return EOVar(name, info=vars.get(name, None))

    def get_point(self, lat, lon, alt, time, formula):
        if isinstance(formula, EOFormula):
            formula = str(formula)

        format = 'json'

        params = {
            'time': self._normalize_timestamp(time),
            'formula': formula,
            'format': format,
            'latitude': lat,
            'longitude': lon,
            'altitude': alt,
        }

        response = self._get('point/', params)
        return response.json()

    def get_points(self, query):
        response = self._post('points/', query)
        return response.json()

    def get_tile(self, x, y, z, timestamp, formula):
        if isinstance(formula, EOFormula):
            formula = str(formula)

        format = 'pfpng'

        params = {
            'timestamp': self._normalize_timestamp(timestamp),
            'formula': formula,
            'format': format,
        }
        region = self.tile_to_region(x, y, z)

        response = self._get(f'map/{x}/{y}/{z}/', params)
        
        return EOData.from_pfpng(response.content, region)

    
    def get_region(self, north: float, south: float, east: float, west: float, timestamp, formula, width: int = 2000, height: int = 1000):
        if isinstance(formula, EOFormula):
            formula = str(formula)

        format = 'pfpng'

        region = {
            'north': north,
            'south': south,
            'east': east,
            'west': west,
        }

        params = {
            'timestamp': self._normalize_timestamp(timestamp),
            'formula': formula,
            'format': format,
            'width': width,
            'height': height,
        }
        params.update(region)

        response = self._get(f'map/', params)
        
        return EOData.from_pfpng(response.content, region)
    

    def tile_to_region(self, x, y, z):
        # Convert Slippy Map tile coordinates to region coordinates.
        # The region coordinates are the bounding box of the tile.
        # The bounding box is in the format (north, south, east, west).
        # The tile coordinates are in the format (x, y, z).
        north, west = num2deg(x, y, z)
        south, east = num2deg(x + 1, y + 1, z)

        return {
            'north': north,
            'south': south,
            'east': east,
            'west': west,
        }
    
    def _show_error(self, response):
        if response.status_code == 204:
            raise EarthOSAPIError("No data available for this region and time.", response)
        elif response.status_code == 400:
            raise EarthOSAPIError("Bad request", response)
        elif response.status_code == 500:
            raise EarthOSAPIError("Internal server error.", response)
        elif response.status_code == 401:
            raise EarthOSAPIError("Unauthorized. Is your API key correct?", response)
        elif response.status_code == 403:
            raise EarthOSAPIError("Forbidden. Are you allowed to access this resource?", response)
        elif response.status_code == 404:
            raise EarthOSAPIError("Not found.", response)
        else:
            raise EarthOSAPIError(f"Unknown error.", response)


__all__ = ['EarthOS', 'EOData', 'EOColorScale', 'EOFormula', 'COLORSCALES', 'EOVar', 'EOOffset']
