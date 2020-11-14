import sys
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

gifFrames = getFramesFromGIF(filename)
getMCFunction(gifFrames, 1, uniqueId)