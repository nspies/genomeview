
class Track:
    def __init__(self):
        self.name = None
        self.scale = None
        self.height = 100
        
    def layout(self, scale):
        self.scale = scale
        
    def render(self, renderer):
        yield from renderer.rect(5, 5, self.scale.pixel_width-10, self.height-10)
        yield from renderer.rect(35, 25, self.scale.pixel_width+20, self.height+20, fill="lightblue")
        yield from renderer.line(25, 55, 400, 200)
        yield from renderer.line_with_arrows(250, 55, 400, 55)
        
        



