import itertools

class GraphicsBackend:
    pass
    
def _addOptions(kwdargs, defaults=None):
    if defaults is None: defaults = {}
    options = []
    defaults.update(kwdargs)
    for key, arg in defaults.items():
        if arg is not None and arg != "":
            options.append("""{key}="{arg}" """.format(key=key, arg=arg))
    return "".join(options)

class SVG(GraphicsBackend):
    _filter_id = 0

    def text(self, x, y, text, size=10, anchor="middle", family="Helvetica", **kwdargs):
        defaults = {}
        assert anchor in ["start", "middle", "end"]
        yield """<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-family="{family}" text-anchor="{anchor}" {more}>{text}</text>""".format(
            x=x, y=y, size=size, family=family, anchor=anchor, more=_addOptions(kwdargs, defaults), text=text)

    def text_with_background(self, x, y, text, size=10, anchor="middle", text_color="black", bg="white", **kwdargs):
        self._filter_id += 1

        text_filter = [
            """<defs>""",
            """    <filter x="0" y="0" width="1" height="1" id="solid{}">""".format(self._filter_id),
            """        <feFlood flood-opacity="0.8" flood-color="{}"/>""".format(bg),
            """        <feComposite in="SourceGraphic"/>""",
            """    </filter>""",
            """</defs>"""]
        for line in text_filter:
            yield line

        # this is a stoopid hack to get the filter to be fully behind the text, without making it blurry
        kwdargs["fill"] = bg
        kwdargs["filter"] = "url(#solid{})".format(self._filter_id)
        yield from self.text(x, y, text, size, anchor, **kwdargs)

        kwdargs["fill"] = text_color
        del kwdargs["filter"]
        yield from self.text(x, y, text, size, anchor, **kwdargs)



    def rect(self, x, y, width, height, **kwdargs):
        defaults = {"fill":"white", "stroke":"black"}
        tag = """<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" {more}/>""".format(
            x=x, y=y, w=width, h=height, more=_addOptions(kwdargs, defaults))
        yield tag

    def line(self, x1, y1, x2, y2, arrowhead=None, **kwdargs):
        defaults = {"stroke":"black"}
        yield """<line x1="{x1:.2f}" x2="{x2:.2f}" y1="{y1:.2f}" y2="{y2:.2f}" {more} />""".format(
            x1=x1, x2=x2,  y1=y1, y2=y2, more=_addOptions(kwdargs, defaults))

    def line_with_arrows(self, x1, y1, x2, y2, n=5, direction="right", color="black", arrowKwdArgs=None, **kwdargs):
        self.n = n
        self.direction = direction
        self.arrowKwdArgs = arrowKwdArgs
        
        defaults = {"stroke":color}
        defaults.update(kwdargs)
        
        yield from self.line(x1, y1, x2, y2, **defaults)
        if arrowKwdArgs is None: arrowKwdArgs = {}

        for i in range(1, self.n+1):
            x_arrow = x1+float(x2-x1)*i/n
            y_arrow = y1+float(y2-y1)*i/n
            yield from self.arrow(x_arrow, y_arrow, direction, 
                color=color, scale=arrowKwdArgs.get("stroke-width", 1), **arrowKwdArgs)

    def arrow(self, x, y, direction, color="black", scale=1.0, **kwdargs):
        more = _addOptions(kwdargs)

        if direction == "right":
            a = """<path d="M {x0} {y0} L {x1} {y1} L {x2} {y2} z" fill="{color}" xcenter="{xcenter}" {more}/>""".format(
                x0=(x-10*scale), y0=(y-5*scale), 
                x1=(x), y1=y, 
                x2=(x-10*scale), y2=(y+5*scale),
                color=color,
                xcenter=x,
                more=more)
        elif direction == "left":
            a = """<path d="M {x0} {y0} L {x1} {y1} L {x2} {y2} z" fill="{color}" xcenter="{xcenter}" {more}/>""".format(
                x0=(x+10*scale), y0=(y-5*scale), 
                x1=(x), y1=y, 
                x2=(x+10*scale), y2=(y+5*scale),
                color=color,
                xcenter=x,
                more=more)
        yield a
        
    def start_clipped_group(self, x, y, width, height, name):
        yield """<clipPath id="clip_path_{}"><rect x="{}" y="{}" width="{}" height="{}" /></clipPath>""".format(
            name, x, y, width, height)
        yield """<g clip-path="url(#clip_path_{})">""".format(name)
        
    def stop_clipped_group(self):
        yield "</g>"
    

class Renderer:
    newid = itertools.count()
    
    def __init__(self, backend, x, y, width, height):
        self.backend = backend
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = next(Renderer.newid)
    
    def text(self, x, y, *args, **kwdargs):
        yield from self.backend.text(x+self.x, y+self.y, *args, **kwdargs)
        
    def text_with_background(self, x, y, *args, **kwdargs):
        yield from self.backend.text_with_background(x+self.x, y+self.y, *args, **kwdargs)
        
    def rect(self, x, y, *args, **kwdargs):
        yield from self.backend.rect(x+self.x, y+self.y, *args, **kwdargs)
    
    def line(self, x1, y1, x2, y2, *args, **kwdargs):
        yield from self.backend.line(x1+self.x, y1+self.y, x2+self.x, y2+self.y, *args, **kwdargs)
    
    def line_with_arrows(self, x1, y1, x2, y2, *args, **kwdargs):
        yield from self.backend.line_with_arrows(x1+self.x, y1+self.y, x2+self.x, y2+self.y, *args, **kwdargs)

    def arrow(self, x, y, *args, **kwdargs):
        yield from self.backend.arrow(x+self.x, y+self.y, *args, **kwdargs)

    def render(self, element):
        yield "<!-- {} -->".format(element.name)
        yield from self.backend.start_clipped_group(self.x, self.y, self.width, self.height, self.id)
        # yield self.backend.rect(self.x, self.y, self.width, self.height, fill="blue")
        try:
            for subelement in element.prerender(self):
                yield "   " + subelement
        except AttributeError:
            pass
        
        for subelement in element.render(self):
            yield "   " + subelement

        try:
            for subelement in element.postrender(self):
                yield "   " + subelement
        except AttributeError:
            pass

        yield from self.backend.stop_clipped_group()
        
    def subrenderer(self, x=0, y=0, width=None, height=None):
        if width is None: width = self.width
        if height is None: height = self.height

        assert width <= self.width
        assert height <= self.height, "{} {}".format(height, self.height)

        x += self.x
        y += self.y
        
        renderer = Renderer(self.backend, x, y, width, height)

        return renderer
