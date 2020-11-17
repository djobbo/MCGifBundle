import sys
import time
from pathlib import Path
from getFramesFromGIF import getFramesFromGIF
from getMCFunction import getMCFunction
from clearOutDir import clearOutDir

if len(sys.argv) < 3:
    print('Missing argument. Correct usage: make [gifPath] [uniqueID]')
    sys.exit(1)

clearOutDir()

filename = sys.argv[1]
uniqueId = sys.argv[2]

start = time.time()

gifFrames = getFramesFromGIF(filename)
getMCFunction(gifFrames, 1, uniqueId)

end = time.time()

print('Generated datapack in', '%.2f' % (end - start) + 's')