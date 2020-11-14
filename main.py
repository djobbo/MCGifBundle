from pathlib import Path
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

PURE_COLORS = [
    ('white', (255, 255, 255)),
    ('light_gray', (170, 170, 170)),
    ('gray', (80, 80, 80)),
    ('black', (0, 0, 0)),

    ('brown',(170, 80, 40)),
    ('red', (170, 40, 40)),
    ('orange', (255, 128, 0)),
    ('yellow',(255, 255, 0)),
    ('lime',(128, 255, 0)),
    ('green',(80, 128, 0)),
    ('cyan', (0, 170, 170)),
    ('light_blue',(0, 170, 255)),
    ('blue', (40, 40, 170)),
    ('purple', (128, 40, 170)),
    ('magenta', (200, 80, 200)),
    ('pink', (255, 128, 170)),
]

MAX_COMMAND_LENGTH = 30000

def getNearestColor(rgb):
    r, g, b = rgb
    color_diffs = []
    for (mcName, color) in COLORS:
        cr, cg, cb = color
        color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
        color_diffs.append((color_diff, mcName))
    return min(color_diffs)[1]
    
def getBundleData(frame, commandBlock = False, uniqueId = 'test123'):
    

    command = 'bundle{Items:['

    for y in range(frame.size[1]):
        for x in range(frame.size[0]):
            mcName = getNearestColor(frame.getpixel((x, y)))
            if commandBlock:
                command += '{id:\\\\\\"minecraft:' + mcName + '_stained_glass_pane\\\\\\",Count:1b},'
            else:
                command += '{id:"minecraft:' + mcName + '_stained_glass_pane",Count:1b},'

    command += '], gifbundle:"' + uniqueId + '"}'
    return command

def getBundleGif(frames, delay = 5, slot = 'container.8', uniqueId = 'time123'):
    outputIndex = 0

    output = getInitCommands(outputIndex)

    output += '{id:command_block_minecart,Command:"scoreboard objectives add '+ uniqueId + ' dummy"},'

    output += '{id:command_block_minecart,Command:"setblock ~ ~-3 ~-1 repeating_command_block[facing=north]"},'
    output += '{id:command_block_minecart,Command:"data merge block ~ ~-3 ~-1 {auto:1,Command:\\"scoreboard players add @e[scores={' + uniqueId + '=1..}] ' + uniqueId + ' 1\\"}"},'

    for i in range(len(frames)):
        frame = frames[i]
        newCommands = '{id:command_block_minecart,Command:"setblock ~ ~-3 ~' + str(-2 - i) + ' chain_command_block[facing=north]"},'
        newCommands += '{id:command_block_minecart,Command:"data merge block ~ ~-3 ~' + str(-2 - i) + ' {auto:1,Command:\\"'
        newCommands += 'item entity @p[scores={' + uniqueId + '=' + str((i + 1) * delay + 1) + '}] ' + slot + ' replace ' + getBundleData(frame, True)
        newCommands += '\\"}"},'

        if (len(output) + len(newCommands) + len(getCleanupCommands())) >= MAX_COMMAND_LENGTH:
            output += getCleanupCommands()
            writeOutputFile(output, uniqueId, outputIndex)
            outputIndex += 1
            output = getInitCommands(outputIndex)
        
        output += newCommands
    
    output += '{id:command_block_minecart,Command:"setblock ~ ~-3 ~' + str(-2 - len(frames)) + ' chain_command_block[facing=north]"},'
    output += '{id:command_block_minecart,Command:"data merge block ~ ~-3 ~' + str(-2 - len(frames)) + ' {auto:1,Command:\\"scoreboard players set @e[scores={' + uniqueId + '=' + str((len(frames) * delay + 1)) + '..}] ' + uniqueId + ' 1\\"}"},'

    output += getCleanupCommands()

    writeOutputFile(output, uniqueId, outputIndex)

def getInitCommands(outputIndex):
    output = 'summon falling_block ~' + str(outputIndex) + ' ~1 ~ {BlockState:{Name:stone},Time:1,Passengers:['
    output += '{id:"armor_stand",Health:0,Passengers:['
    output += '{id:falling_block,BlockState:{Name:redstone_block},Time:1,DropItem:0,Passengers:['
    output += '{id:"armor_stand",Health:0,Passengers:['
    output += '{id:falling_block,BlockState:{Name:activator_rail},Time:1,Passengers:['
    return output

def getCleanupCommands():
    output = '{id:command_block_minecart,Command:"setblock ~ ~ ~1 command_block{Command:\\"fill ~ ~-3 ~-1 ~ ~ ~ air\\"}"},'
    output += '{id:command_block_minecart,Command:"setblock ~ ~-1 ~1 redstone_block"},'
    output += '{id:command_block_minecart,Command:"kill @e[type=command_block_minecart,distance=..1]"}'
    output += ']}]}]}]}]}'
    return output

def writeOutputFile(data, uniqueId, index = 0):
    f = open('dist/' + uniqueId + '/output.' + str(index) + '.txt', 'w')
    f.write(data)
    f.close()

def getMCFunction(frames, delay = 5, uniqueId = 'test123'):
    
    Path('dist/' + uniqueId).mkdir(exist_ok=True)

    initOutput = 'scoreboard objectives add '+ uniqueId + ' dummy\n'
    initOutput += 'give @a minecraft:bundle{gifbundle:"' + uniqueId + '"}'

    f = open('dist/' + uniqueId + '/init.mcfunction', 'w')
    f.write(initOutput)
    f.close()

    output = 'scoreboard players add @a[scores={' + uniqueId + '=1..}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=..1}, nbt={Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=1..}, nbt=!{Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 0\n'

    for i in range(len(frames)):
        frame = frames[i]
        for slot in range(9):
            output += 'item entity @a[scores={' + uniqueId + '=' + str((i + 1) * delay + 1) + '},'
            output += 'nbt={Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"},'
            output += 'Count: 1b, Slot: ' + str(slot) + 'b}]}] container.' + str(slot) + ' replace ' + getBundleData(frame, False, uniqueId) + '\n'
    
    output += 'scoreboard players set @a[scores={' + uniqueId + '=' + str((len(frames) * delay + 1)) + '..}] ' + uniqueId + ' 1'

    f = open('dist/' + uniqueId + '/main.mcfunction', 'w')
    f.write(output)
    f.close()

def getFrameFromUrl(url):
    return Image.open(url)

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

# gifFrames = [getFrameFromUrl('Mobs/' + str(i + 1) + '.png') for i in range(4)]

gifFrames = getFramesFromGIF('./gifs/pepe.gif')
print(gifFrames)

# getBundleGif(gifFrames, 3, 'container.2', 'pepe2')

Path('dist').mkdir(exist_ok=True)

getMCFunction(gifFrames, 1, 'pepe')