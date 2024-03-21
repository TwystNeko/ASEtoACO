# converts Adobe Swatch Exchange (ASE) files to Adobe Color (ACO) format. 

import os
import struct
import sys
from pathlib import Path

# commandline args: -aco (or blank) for .ACO output, -png for 8x8px swatches, -txt for text, -hex for hexcode list
try:
    cmd = sys.argv[1]
except:
    cmd = "-aco"
    
class Color:
    def __init__(self,name,red,green,blue) -> None:
        self.name = name.decode("UTF-16BE")[:-1]
        self.rawname = name
        self.red = int(red*255)
        self.float_red = red
        self.green = int(green*255)
        self.float_green = green
        self.blue = int(blue*255)
        self.float_blue = blue

directory = os.path.join(os.path.dirname(__file__),"palettes\\")
print("Looking for ASE files in "+ directory)
for file in os.listdir(directory):
    pal_file = os.path.join(directory,file)
    if pal_file.endswith(".ase"):
        filename = Path(pal_file).stem
        #reading ASE file
        pf = open(pal_file,"rb")
        header, majver, minver, total_blocks = struct.unpack_from('>4shhi', pf.read(12))
        palette = []
        for block in range(total_blocks):
            block_id, block_length= struct.unpack_from('>hi', pf.read(6))
            block_data = pf.read(block_length)
            if block_id == 1: #it's a color, we want it!
                name_len = struct.unpack_from('>h',block_data[:2])
                name_len, name, color_space,red,green,blue,mode  = struct.unpack_from('>h' + str(name_len[0] *2)+'s4sfffh', block_data)
                c = Color(name,red,green,blue)
                palette.append(c)
        pf.close()

        #decide what to output
        if cmd == "-aco":
            #writing ACO file
            format = "ACO"
            outfile = os.path.join(directory, filename + ".aco")
            of = open(outfile, "wb")
            of.write(struct.pack('>hh',1,len(palette)))
            for c in palette:
                of.write(struct.pack('>hBBBBBBh', 0,c.red,c.red,c.green, c.green, c.blue, c.blue, 0))
            of.close()
        elif cmd == "-txt":
            #writing text file: Name, R, G, B
            format = "TXT"
            outfile = os.path.join(directory, filename + ".txt")
            of = open(outfile, "w")
            of.write(";Palette Name: "+filename+" -- "+str(len(palette))+" colors.\n")
            for c in palette:
                of.write(c.name + ": "+str(c.red)+","+str(c.green)+","+str(c.blue)+"\n")
            of.close()
        elif cmd == "-hex":
            #writing hex file: colors in HEX format. 
            format = "HEX"
            outfile = os.path.join(directory, filename + ".hex")
            of = open(outfile, "w")
            of.write(";Palette Name: "+filename+" -- "+str(len(palette))+" colors.\n")
            for c in palette:
                of.write("#"+f"{c.red:0{2}X}")
                of.write(f"{c.green:0{2}X}")
                of.write(f"{c.blue:0{2}X}"+"\n")
            of.close()
        
        print("Converted "+ Path(pal_file).stem + " to "+format+" format.  " + str(len(palette)) + " colors in palette")