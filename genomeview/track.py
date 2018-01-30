class Track:
    def __init__(self, name=None):
        self.name = name
        self.scale = None
        self.height = 100
        
    def layout(self, scale):
        self.scale = scale
        
    def render(self, renderer):
        yield from renderer.rect(5, 5, self.scale.pixel_width-10, self.height-10)
        yield from renderer.rect(35, 25, self.scale.pixel_width+20, self.height+20, fill="lightblue")
        yield from renderer.line(25, 55, 400, 200)
        yield from renderer.line_with_arrows(250, 55, 400, 55)
        
    def render_label(self, renderer):
        if self.name is not None:
            yield from renderer.text_with_background(5, 14, self.name, anchor="start", size=18, bg_opacity=0.9)

        
class TrackLabel:
    def __init__(self, name=None):
        self.name = name
        self.label = name
        self.height = 35

    def layout(self, *args):
        pass

    def render(self, renderer):
        yield from renderer.text(5, 20, self.label, anchor="start", size=24, **{"font-weight":"bold"})
