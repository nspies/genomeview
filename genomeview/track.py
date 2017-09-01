class Track:
    def __init__(self, name):
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
        name = self.name
        # if self.scale.pixel_width < 400:
        #     name = name[:
        yield from renderer.text_with_background(5, 14, name, anchor="start", size=18)

        
class TrackLabel:
    def __init__(self, name):
        self.name = name + "_label"
        self.label = name
        self.height = 35

    def layout(self, *args):
        pass

    def render(self, renderer):
        yield from renderer.text(5, 20, self.label, anchor="start", size=24, **{"font-weight":"bold"})
