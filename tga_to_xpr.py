import math
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image

# Loop through each TGA file in /tga
# For each file, change TGA name to 'strname.tga' and move to root
# Then, run bundler "filename.rdf" -o "xpr/output.xpr" via command line and delete strname.tga

CWD = os.getcwd()
RDF = os.path.abspath(os.path.join(CWD, 'main.rdf'))
MIPS = False

def make_rdf(tga):
    print('Making RDF')
    tree = ET.parse(RDF)
    texture = tree.find('Texture')
    levels_max = max(tga['size'])
    
    attributes = {
        'Name': 'strName',
        'Source': 'strName.tga',
        'Format': 'D3DFMT_DXT5' if tga['alpha'] else 'D3DFMT_DXT1',
        'Width': str(tga['size'][0]),
        'Height': str(tga['size'][1]),
        'Levels': str(math.floor(math.log(levels_max)/math.log(2)) + 1 if MIPS else 1)
    }
    
    for attr in attributes:
        texture.set(attr, attributes[attr])
    
    tree.write(RDF, "utf-8", True)

def get_image_size_and_alpha(tga):
    print('Getting image size and alpha')
    im = Image.open(tga)
    return { 'size': im.size, 'alpha': True if im.mode == 'RGBA' else False }

for f in os.scandir(os.path.abspath(os.path.join(CWD, 'tga'))):
    if (f.path.endswith(".tga")) and f.is_file():
        f_name = f.name[:-4]
        print(f'Converting: {f_name}')
        
        tga_meta = get_image_size_and_alpha(f.path)
        make_rdf(tga_meta)

        shutil.move(f.path, os.path.abspath(os.path.join(CWD, 'strName.tga')))

        output = os.path.abspath(os.path.join(CWD, 'xpr', f'{f_name}.xpr'))
        process = subprocess.run(f'bundler \"{RDF}\" -o \"{output}\"')
        if process.returncode == 1:
            print(f'Failed converting {f_name}')
        os.remove(os.path.abspath(os.path.join(CWD, 'strName.tga')))
