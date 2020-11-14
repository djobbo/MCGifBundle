from pathlib import Path
import shutil
from PIL import Image, ImageSequence
from math import sqrt

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


def getNearestColor(rgb):
    r, g, b = rgb
    color_diffs = []
    for (mcName, color) in COLORS:
        cr, cg, cb = color
        color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
        color_diffs.append((color_diff, mcName))
    return min(color_diffs)[1]
    

def getBundleData(frame, uniqueId = 'test123'):
    output = '\\"Items\\":['

    for y in range(frame.size[1]):
        for x in range(frame.size[0]):
            mcName = getNearestColor(frame.getpixel((x, y)))
            output += '{id:\\"minecraft:' + mcName + '_stained_glass_pane\\",Count:1b},'

    output += '], gifbundle:\\"' + uniqueId + '\\"'
    return output


def writeOutputFile(url, data):
    f = open(url, 'w')
    f.write(data)
    f.close()


def getMCFunction(frames, delay = 5, uniqueId = 'test123'):

    Path('dist/gifbundle').mkdir(exist_ok=True)

    writeOutputFile('dist/gifbundle/pack.mcmeta', '{"pack": {"pack_format": 6,"description": "GIF Bundles!"}}')

    outputFolder = 'dist/gifbundle/data'

    Path(outputFolder).mkdir(exist_ok=True)
    Path(outputFolder + '/gifbundle').mkdir(exist_ok=True)
    Path(outputFolder + '/gifbundle/functions').mkdir(exist_ok=True)
    Path(outputFolder + '/gifbundle/item_modifiers').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft/tags').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft/tags/functions').mkdir(exist_ok=True)

    initOutput = 'scoreboard objectives add '+ uniqueId + ' dummy\n'
    initOutput += 'give @a minecraft:bundle{gifbundle:"' + uniqueId + '"}'

    writeOutputFile(outputFolder + '/gifbundle/functions/init.mcfunction', initOutput)

    writeOutputFile(outputFolder + '/minecraft/tags/functions/load.json', '{"values": ["gifbundle:init"]}')
    writeOutputFile(outputFolder + '/minecraft/tags/functions/tick.json', '{"values": ["gifbundle:main"]}')

    output = 'scoreboard players add @a[scores={' + uniqueId + '=1..}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=..1}, nbt={Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=1..}, nbt=!{Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 0\n'

    for i in range(len(frames)):
        frame = frames[i]

        itemModifierOutput = '{"function": "set_nbt","tag": "{'
        itemModifierOutput += getBundleData(frame, uniqueId)
        itemModifierOutput += '}"}'

        writeOutputFile(outputFolder + '/gifbundle/item_modifiers/frame_' + str(i) + '.json', itemModifierOutput)

        for slot in range(9):
            output += 'item entity @a[scores={' + uniqueId + '=' + str((i + 1) * delay + 1) + '},'
            output += 'nbt={Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"},'
            output += 'Count: 1b, Slot: ' + str(slot) + 'b}]}] container.' + str(slot) + ' modify gifbundle:frame_' + str(i) + '\n'
    
    output += 'scoreboard players set @a[scores={' + uniqueId + '=' + str((len(frames) * delay + 1)) + '..}] ' + uniqueId + ' 1'

    writeOutputFile(outputFolder + '/gifbundle/functions/main.mcfunction', output)


def getFramesFromGIF(url):
    try:
        im = Image.open(url)
    except IOError:
        print ("Cant load", url)
        sys.exit(1)

    i = 0
    frames = []
    try:
        while 1:

            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im)
            frames.append(background)

            i += 1
            im.seek(im.tell() + 1)

    except EOFError:
        return frames


gifFrames = getFramesFromGIF('./gifs/pepe.gif')

try:
    shutil.rmtree('dist')
except:
    pass

Path('dist').mkdir(exist_ok=True)

getMCFunction(gifFrames, 1, 'pepe')