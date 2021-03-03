import time
from multiprocessing import Pool
import os
from pathlib import Path
from getNearestColor import getNearestColor
from progressbar import printProgressBar
from multiprocess import MyPool

def writeOutputFile(url, data):
    f = open(url, 'w')
    f.write(data)
    f.close()


def getBundleItem(r, g, b):
    return '{id:\\"minecraft:' + getNearestColor(r, g, b) + '\\",Count:1b},'


def getBundleData(frame, uniqueId = 'test123'):
    output = '\\"Items\\":['

    pool = Pool(os.cpu_count())
    result = [pool.apply(getBundleItem, args=(frame.getpixel((x, y)))) for y in range(frame.size[1]) for x in range(frame.size[0])]
    output += ''.join(result)
    output += '],gifbundle:\\"' + uniqueId + '\\"'
    return output


def getBundleFrame(frames, i, uniqueId):
    # printProgressBar(i, len(frames), prefix = 'Generating Frame ' + str(i + 1) + '/' + str(len(frames)), suffix = 'Complete', length = 50)
    data = getBundleData(frames[i], uniqueId)
    return data


def getMCFunction(frames, delay = 5, uniqueId = 'test123'):
    print('Creating datapack structure...')

    uniqueGifbundle = '/gifbundle_' + uniqueId
    Path('dist' + uniqueGifbundle).mkdir(exist_ok=True)


    writeOutputFile('dist' + uniqueGifbundle + '/pack.mcmeta', '{"pack":{"pack_format": 6,"description": "GIF Bundles!"}}')
    filesize = Path('dist' + uniqueGifbundle + '/pack.mcmeta').stat().st_size
    print('Created McMeta file \'dist' + uniqueGifbundle + '/pack.mcmeta\'  [' + str(filesize/1000) + 'kB]')

    outputFolder = 'dist' + uniqueGifbundle + '/data'

    Path(outputFolder).mkdir(exist_ok=True)
    Path(outputFolder + uniqueGifbundle).mkdir(exist_ok=True)
    Path(outputFolder + uniqueGifbundle + '/functions').mkdir(exist_ok=True)
    Path(outputFolder + uniqueGifbundle + '/item_modifiers').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft/tags').mkdir(exist_ok=True)
    Path(outputFolder + '/minecraft/tags/functions').mkdir(exist_ok=True)

    print('Building datapack functions...')

    initOutput = 'scoreboard objectives add '+ uniqueId + ' dummy\n'
    initOutput += 'give @a minecraft:bundle{gifbundle:"' + uniqueId + '"}'

    writeOutputFile(outputFolder + uniqueGifbundle + '/functions/init.mcfunction', initOutput)
    filesize = Path(outputFolder + uniqueGifbundle + '/functions/init.mcfunction').stat().st_size
    print('Created Init file \'' + outputFolder + uniqueGifbundle + '/functions/init.mcfunction\' [' + str(filesize/1000) + 'kB]')

    writeOutputFile(outputFolder + '/minecraft/tags/functions/load.json', '{"values":["gifbundle_' + uniqueId + ':init"]}')
    writeOutputFile(outputFolder + '/minecraft/tags/functions/tick.json', '{"values":["gifbundle_' + uniqueId + ':main"]}')

    output = 'scoreboard players add @a[scores={' + uniqueId + '=1..}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=..1}, nbt={Inventory:[{id:"minecraft:bundle",tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 1\n'
    output += 'scoreboard players set @a[scores={' + uniqueId + '=1..}, nbt=!{Inventory:[{id:"minecraft:bundle",tag:{gifbundle:"' + uniqueId + '"}}]}] ' + uniqueId + ' 0\n'

    totalFileSize = 0

    print('Generating bundle frames...')
    startBundleFrames = time.time()
    pool = MyPool(os.cpu_count()) 
    print(frames)
    bundleFrames = [pool.apply(getBundleData, args=(frame, uniqueId)) for frame in frames]
    endBundleFrames = time.time()
    printProgressBar(len(frames), len(frames), prefix = 'Created Frame ' + str(len(frames)) + '/' + str(len(frames)), suffix = 'Complete [' + '%.2f' % (endBundleFrames - startBundleFrames) + 's]', length = 50)
    pool.close()

    print('Creating item_modifiers files...')
    for i in range(len(bundleFrames)):

        itemModifierOutput = '{"function":"set_nbt","tag":"{'
        itemModifierOutput += bundleFrames[i]
        itemModifierOutput += '}"}'

        writeOutputFile(outputFolder + uniqueGifbundle + '/item_modifiers/frame_' + str(i) + '.json', itemModifierOutput)
        totalFileSize += Path(outputFolder + uniqueGifbundle + '/item_modifiers/frame_' + str(i) + '.json').stat().st_size

        for slot in range(9):
            output += 'item entity @a[scores={' + uniqueId + '=' + str((i + 1) * delay + 1) + '},'
            output += 'nbt={Inventory:[{id:"minecraft:bundle",tag:{gifbundle:"' + uniqueId + '"},'
            output += 'Count: 1b,Slot: ' + str(slot) + 'b}]}] container.' + str(slot) + ' modify gifbundle_' + uniqueId + ':frame_' + str(i) + '\n'
        
        printProgressBar(i + 1, len(frames), prefix = 'Created Frame ' + str(i + 1) + '/' + str(len(frames)) + ' file', suffix = 'Complete [' + str(totalFileSize/1000) + ' kB]', length = 50)

    output += 'scoreboard players set @a[scores={' + uniqueId + '=' + str((len(frames) * delay + 1)) + '..}] ' + uniqueId + ' 1'

    writeOutputFile(outputFolder + uniqueGifbundle + '/functions/main.mcfunction', output)

    filesize = Path(outputFolder + uniqueGifbundle + '/functions/main.mcfunction').stat().st_size
    print('Created Main Loop file \'' + outputFolder + uniqueGifbundle + '/functions/main.mcfunction\' [' + str(filesize/1000) + 'kB]')