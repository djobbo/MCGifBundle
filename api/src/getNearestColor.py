from math import sqrt
import json


COLORS = [
    ('white', (249, 255, 255)),
    ('light_gray', (156, 157, 151)),
    ('gray', (71, 79, 82)),
    ('black', (29, 28, 33)),
    ('brown',(130, 84, 50)),
    ('red', (176, 46, 38)),
    ('orange', (249, 128, 29)),
    ('yellow',(255, 216, 61)),
    ('lime',(128, 199, 31)),
    ('green',(93, 124, 21)),
    ('cyan', (22, 156, 157)),
    ('light_blue',(58, 179, 218)),
    ('blue', (60, 68, 169)),
    ('purple', (137, 50, 183)),
    ('magenta', (198, 79, 189)),
    ('pink', (243, 140, 170)),
]

def getNearestColor(r, g, b):
    with open('./src/item_colors.json') as json_file:
        colors = json.load(json_file)

        color_diffs = []
        for (mcName, color) in colors:
            cr, cg, cb, a = color
            _r = (cr + r) / 2

            dr, dg, db = r - cr, g - cg, b - cb

            color_diff = sqrt((2 + _r / 256)*dr**2 + 4*dg**2 + (2 + (255 - _r) / 256)*db**2)
            color_diffs.append((color_diff, mcName))
        return min(color_diffs)[1]