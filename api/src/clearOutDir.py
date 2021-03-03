from pathlib import Path
from shutil import rmtree

def clearOutDir():
    print('Clearing output directory...')
    try:
        rmtree('dist')
    except:
        pass

    Path('dist').mkdir(exist_ok=True)