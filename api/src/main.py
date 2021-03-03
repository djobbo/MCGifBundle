import sys
import time
from pathlib import Path
from getFramesFromGIF import getFramesFromGIF
from getMCFunction import getMCFunction
from clearOutDir import clearOutDir
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Lesgoooo'

@app.route('/gif', methods=["POST"])
def handleGif():
    return 'GIF'

@app.errorhandler(404)
def page_not_found(error):
    return "Page not found"

# if len(sys.argv) < 3:
#     print('Missing argument. Correct usage: make [gifPath] [uniqueID]')
#     sys.exit(1)

# clearOutDir()

# filename = sys.argv[1]
# uniqueId = sys.argv[2]

# start = time.time()

# gifFrames = getFramesFromGIF(filename)
# getMCFunction(gifFrames, 1, uniqueId)

# end = time.time()

# print('Generated datapack in', '%.2f' % (end - start) + 's')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)