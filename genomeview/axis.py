import math

from genomeview.track import Track

class Axis(Track):
    def __init__(self, name=None):
        self.name = name
        self.scale = None

        self.height = 50
        self.font_size = 16

    def render(self, renderer):
        start, end = self.scale.start, self.scale.end
        yield from renderer.line(self.scale.topixels(start), 5, self.scale.topixels(end), 5)
        
        ticks = get_ticks(start, end, max(1,self.scale.pixel_width/120))
        prev_right = -1e6

        for i, (tick, label) in enumerate(ticks):
            x = self.scale.topixels(tick)
            if x < 0 or x > self.scale.pixel_width: continue

            yield from renderer.line(x, 0, x, 20)
            anchor = "middle"
            cur_left = x - len(label) / 2 * self.font_size * 0.8

            if x < 50 and i == 0:
                anchor = "start"
                x = min(x, 5)
                cur_left = x
            elif x > self.scale.pixel_width-50 and i == len(ticks)-1:
                anchor = "end"
                x = max(x, self.scale.pixel_width-5)
                cur_left = x - len(label) * self.font_size * 0.8

            # make sure we don't clobber label text we've already rendered
            if cur_left > prev_right:
                yield from renderer.text(x, 35, label, anchor=anchor, size=self.font_size)

                if anchor == "start":
                    prev_right = x + len(label) * self.font_size * 0.8
                elif anchor == "middle":
                    prev_right = x + len(label) / 2 * self.font_size * 0.8
                else:
                    prev_right = x

def get_ticks(start, end, target_n_labels=10):
    ticks = []
    start = int(start)
    end = int(end)
    width = end - start

    res = (10 ** round(math.log10(end - start))) / (10**math.floor(math.log10(target_n_labels)))

    if width / res > target_n_labels*2:
        res *= 5
    elif width / res > target_n_labels*1.5:
         res *= 2.5
    elif width / res < target_n_labels*0.15:
        res /= 10.0
    elif width / res < target_n_labels*0.25:
        res /= 8.0
    elif width / res < target_n_labels*0.5:
        res /= 4.0
    elif width / res < target_n_labels*0.8:
        res /= 2.0

    roundStart = start - (start%res)
    res = max(1, int(res))
    
    for i in range(int(roundStart), end, res):
        res_digits = math.log10(res)
        if res_digits >= 6:
            label = "{}mb".format(i / 1e6)
        elif res_digits >= 3:
            label = "{:,}kb".format(i / 1e3)
        else:
            label = "{:,}".format(i)

        ticks.append((i, label))

    return ticks


if __name__ == '__main__':
    params = [(10000, 11060, 10),
              (0, 10311, 10),
              (0, 143600, 10),
              (0, 1002552, 10)]

    for param in params:
        print(params)
        print(get_ticks(*param))
        print("")
