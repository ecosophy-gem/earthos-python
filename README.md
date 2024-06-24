# Ecosophy EarthOS API Python bindings

These are open API bindings for Ecosophy's EarthOS API. You must have an EarthOS account
in order to use the bindings.

## Installation

Try:
```
pip install earthos-python
```

Or, if you have cloned this from a git repository, you can also:
```
python setup.py install
```

## Getting started

First, log in to [EarthOS](https://earthos.ai/) and generate an API key in your organization 
settings dialog. 

Then, in Python:

```python
from earthos import EarthOS
APIKEY = 'your api key here'
eo = EarthOS(APIKEY)
```

With this in place, you can start fetching and working with the data, for example:

```
myformula = EOVar('gfs.relative_humidity')/100.0
data = eo.get_region(north=90.0, south=-90.0, east=180.0, west=-180.0, formula=myformula)
data.show()
```

See `tests` for further examples.

# License

This library is copyright © Ecosophy ehf 2024. It is released under the terms of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

Use of the EarthOS API is subject to end user license conditions, which can be seen at https://earthos.ai/api-license

