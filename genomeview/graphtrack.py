import collections
import numpy

from genomeview.track import Track
from genomeview.axis import get_ticks

COLORS = ["blue", "red", "green", "black"]

class Series:
    def __init__(self, x, y, color=None, label=None):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        
class GraphTrack(Track):
    def __init__(self, name="graph", x=None, y=None):
        super().__init__()
        self.name = name

        self.series = collections.OrderedDict()
        
        self.min_y = 0
        self.max_y = 0
        
        if x is not None:
            self.add_series(x, y)

        self.height = 100
        self.ymargin = 5
        
    def add_series(self, x, y, color=None, label=None):
        if label is None:
            label = "series_{}".format(len(self.series))
            
        assert label not in self.series

        x = numpy.asarray(x)
        y = numpy.asarray(y)

        if color is None:
            color = COLORS[len(self.series) % len(COLORS)]
            
        self.series[label] = Series(x, y, color, label)

        self.min_y = min(self.min_y, y[numpy.isfinite(y)].min())
        self.max_y = max(self.max_y, y[numpy.isfinite(y)].max())

    def ytopixels(self, yval):
        height = self.max_y - self.min_y
        return self.height - ((yval - self.min_y) / height * (self.height-2*self.ymargin) + self.ymargin)
        
    def render(self, renderer):
        for label, series in self.series.items():
            for i in range(len(series.x)-1):
                if any(numpy.isnan(series.x[i:i+2])) or any(numpy.isnan(series.y[i:i+2])):
                    continue
                x1 = self.scale.topixels(series.x[i])
                x2 = self.scale.topixels(series.x[i+1])
                y1 = self.ytopixels(series.y[i])
                y2 = self.ytopixels(series.y[i+1])
                                         
                yield from renderer.line(x1, y1, x2, y2, **{"stroke-width":1, "stroke":series.color})

        # since the labels are drawn at the top of the ticks, let's make sure the top tick/label is 
        # more than 12 pixels from the top of the track so it doesn't get clipped
        # TODO: this ignores the margin, as of now
        axis_max_y = self.min_y + (self.max_y - self.min_y) * (1-7/self.height)
        ticks = get_ticks(self.min_y, axis_max_y, 4)

        yield from renderer.line(1, self.ytopixels(ticks[0][0]), 1, self.ytopixels(ticks[-1][0]), **{"stroke-width":2, "stroke":"gray"})
        for tick, label in ticks:
            y = self.ytopixels(tick)
            yield from renderer.line(1, y, 10, y, **{"stroke-width":2, "stroke":"gray"})
            yield from renderer.text(14, y, label, anchor="start", fill="gray")
            
