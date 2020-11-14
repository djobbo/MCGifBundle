from pathlib import Path
from getNearestColor import getNearestColor
from progressbar import printProgressBar

def writeOutputFile(url, data):
    f = open(url, 'w')
    f.write(data)
    f.close()


def getBundleData(frame, uniqueId = 'test123'):
    output = '\\"Items\\":['

    for y in range(frame.size[1]):
        for x in range(frame.size[0]):
            mcName = getNearestColor(frame.getpixel((x, y)))
            output += '{id:\\"minecraft:' + mcName + '_stained_glass_pane\\",Count:1b},'

    output += '],gifbundle:\\"' + uniqueId + '\\"'
    return output


def getMCFunction(frames, delay = 5, uniqueId = 'test123'):
    print('Creating datapack structure...')

    Path('dist/gifbundle_' + uniqueId).mkdir(exist_ok=True)

    writeOutputFile('dist/gifbundle_' + uniqueId + '/pack.mcmeta', '{"pack":{"pack_format": 6,"description": "GIF Bundles!"}}')
    print('Created \'dist/gifbundle/' + uniqueId + '/pack.mcmeta\'.')

    outputFolder = 'dist/gifbundle_' + uniqueId + '/data'

    Path(outputFolder).mkdir(exist_ok=True)
    Path(outputFolder + '/gifbundle').mkdir(exist_ok=True)
    Path(outputFolder + '/gifbundle/functions').mkdir(exist_ok=True)
    Path(outputFolder + '/gifbundle/item_modifiers').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft/tags').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft/tags/functions').mkdir(exist_ok=True)

    print('Building datapack functions...')

    initOutput = 'scoreboard objectives add '+ uniqueId + ' dummy\n'
    initOutput += 'give @a minecraft:bundle{gifbundle:"' + uniqueId + '"}'

    writeOutputFile(outputFolder + '/gifbundle/functions/init.mcfunction', initOutput)
    filesize = Path(outputFolder + '/gifbundle/functions/init.mcfunction').stat().st_size
    print('Created Init file \'' + outputFolder + '/gifbundle/functions/init.mcfunction\' [' + str(filesize/1000) + 'kB]')

    writeOutputFile(outputFolder + '/minecraft/tags/functions/load.json', '{"values": ["gifbundle:init"]}')
    writeOutputFile(outputFolder + '/minecraft/tags/functions/tick.json', '{"values": ["gifbundle:main"]}')

    output = 'scoreboard players add @a[scores={' + uniqueId + '=1..}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=..1}, nbt={Inventory:[{id:"minecraft:bundle",tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=1..}, nbt=!{Inventory:[{id:"minecraft:bundle",tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 0\n'

    totalFileSize = 0

    for i in range(len(frames)):
        frame = frames[i]

        itemModifierOutput = '{"function":"set_nbt","tag":"{'
        itemModifierOutput += getBundleData(frame, uniqueId)
        itemModifierOutput += '}"}'

        writeOutputFile(outputFolder + '/gifbundle/item_modifiers/frame_' + str(i) + '.json', itemModifierOutput)
        totalFileSize += Path(outputFolder + '/gifbundle/item_modifiers/frame_' + str(i) + '.json').stat().st_size

        for slot in range(9):
            output += 'item entity @a[scores={' + uniqueId + '=' + str((i + 1) * delay + 1) + '},'
            output += 'nbt={Inventory:[{id:"minecraft:bundle", tag:{gifbundle:"' + uniqueId + '"},'
            output += 'Count: 1b, Slot: ' + str(slot) + 'b}]}] container.' + str(slot) + ' modify gifbundle:frame_' + str(i) + '\n'
        
        printProgressBar(i + 1, len(frames), prefix = 'Created Frame ' + str(i + 1) + '/' + str(len(frames)), suffix = 'Complete [' + str(totalFileSize/1000) + ' kB]', length = 50)

    output += 'scoreboard players set @a[scores={' + uniqueId + '=' + str((len(frames) * delay + 1)) + '..}] ' + uniqueId + ' 1'

    writeOutputFile(outputFolder + '/gifbundle/functions/main.mcfunction', output)

    filesize = Path(outputFolder + '/gifbundle/functions/main.mcfunction').stat().st_size
    print('Created Main Loop file \'' + outputFolder + '/gifbundle/functions/main.mcfunction\' [' + str(filesize/1000) + 'kB]')