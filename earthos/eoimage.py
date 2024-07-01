
from copy import deepcopy
import numpy


class EOData:
    def __init__(self, data, region={'north': 0, 'south': 0, 'east': 0, 'west': 0}):
        self._data = data
        self._region = region
        self._width = 0
        self._height = 0
        self._original_format = 'unknown'

    def save(self, path, colorscale=None):
        if colorscale:
            from PIL import Image
            from io import BytesIO

            image = Image.new('RGB', (self._width, self._height))
            for y in range(self._height):
                for x in range(self._width):
                    value = self._data[y * self._width + x]
                    color = colorscale.get_color(value)
                    image.putpixel((x, y), color)
            image.save(path)
        else:
            with open(path, 'wb') as f:
                f.write(self._data)

    def show(self, colorscale):
        from PIL import Image
        from io import BytesIO

        image = Image.new('RGB', (self._width, self._height))
        for y in range(self._height):
            for x in range(self._width):
                value = self._data[y * self._width + x]
                color = colorscale.get_color(value)
                image.putpixel((x, y), color)

        image.show()

    def min(self):
        return numpy.nanmin(self._data)
    
    def max(self):
        return numpy.nanmax(self._data)
    
    def mean(self):
        return numpy.nansum(self._data) / self._data.size 
    
    def resolution(self):
        return self._width, self._height

    def __repr__(self):
        return f'<EOImage>'
    
    @staticmethod
    def from_pfpng(data, region):
        from PIL import Image
        from io import BytesIO
        from struct import unpack

        image = Image.open(BytesIO(data))
        pixel_data = image.getdata()

        # Unpack the pixel data into a flat list of floats. Each pixel is stuffed
        # with 4 bytes which are a Float32 value.
        array_data = numpy.array([unpack('f', bytes(pixel))[0] for pixel in pixel_data])

        eodata = EOData(array_data, region)
        eodata._width, eodata._height = image.size
        eodata._original_format = 'pfpng'

        return eodata


class EOColorScale:
    def __init__(self, colors=[], offsets=[], min=0.0, max=1.0, data: EOData = None):
        self.colors = colors
        self.offsets = offsets
        self.min = min
        self.max = max
        if data:
            self.set_minmax(data)

    @staticmethod
    def from_json(data):
        colors = data.get('colors', [])
        offsets = data.get('offsets', [])
        min = data.get('min', 0.0)
        max = data.get('max', 1.0)

        colorscale = EOColorScale(colors, offsets, min, max)
        return colorscale
    
    def set_minmax(self, data: EOData):
        self.min = data.min()
        self.max = data.max()

    def add_color(self, color, offset):
        self.colors.append(color)
        self.offsets.append(offset)

    def to_json(self):
        return {
            'colors': self.colors,
            'offsets': self.offsets,
            'min': self.min,
            'max': self.max,
        }
    
    def _interpolate(self, color1, color2, t):
        r1, g1, b1, a1 = color1
        r2, g2, b2, a2 = color2

        r = int(r1 + t * (r2 - r1))
        g = int(g1 + t * (g2 - g1))
        b = int(b1 + t * (b2 - b1))
        a = int(a1 + t * (a2 - a1))

        return r, g, b, a

    def get_color(self, value, rescale=True):
        if rescale:
            value = (value - self.min) / (self.max - self.min)

        if value <= self.min:
            return self.colors[0]
        if value >= self.max:
            return self.colors[-1]

        for i in range(len(self.offsets) - 1):
            if self.offsets[i] <= value <= self.offsets[i + 1]:
                t = (value - self.offsets[i]) / (self.offsets[i + 1] - self.offsets[i])
                return self._interpolate(self.colors[i], self.colors[i + 1], t)
            
        return self.colors[-1]
            
COLORSCALES = {
    'black-white': EOColorScale(colors=[(0, 0, 0, 255), (255, 255, 255, 255)], offsets=[0.0, 1.0]),
    'red-green': EOColorScale(colors=[(255, 0, 0, 255), (0, 255, 0, 255)], offsets=[0.0, 1.0]),
    'blue-yellow': EOColorScale(colors=[(0, 0, 255, 255), (255, 255, 0, 255)], offsets=[0.0, 1.0]),
    'blue-red': EOColorScale(colors=[(0, 0, 255, 255), (255, 0, 0, 255)], offsets=[0.0, 1.0]),
    'blue-green': EOColorScale(colors=[(0, 0, 255, 255), (0, 255, 0, 255)], offsets=[0.0, 1.0]),
    'waves': EOColorScale(colors=[(0, 0, 255, 255), (0, 255, 255, 255), (255, 255, 255, 255), (255, 0, 255, 255), (0, 0, 255, 255)], offsets=[0.0, 0.25, 0.5, 0.75, 1.0]),
}