# converts Adobe Swatch Exchange (ASE) files to Adobe Color (ACO) format. 

import os
import struct
from pathlib import Path

directory = os.path.join(os.path.dirname(__file__),"palettes/")
print("Looking for ASE files in "+ directory)
for file in os.listdir(directory):
    pal_file = os.path.join(directory,file)

    if pal_file.endswith(".ase"):
        
        outfile = os.path.join(directory,Path(pal_file).stem + ".aco")
 
        pf = open(pal_file,"rb")
        of = open(outfile, "wb")
        
        header_chunk = pf.read(12) #header is 12 bytes: 4 / 2 / 2 / 4. 
        header, majver, minver, total_blocks = struct.unpack_from('>4shhi', header_chunk)
        aco_header = struct.pack('>hh',1,total_blocks)
        of.write(aco_header)

        for block in range(total_blocks):
            block_header_chunk = pf.read(6) #block header is 6 bytes: id, blocklen
            block_id, block_length= struct.unpack_from('>hi', block_header_chunk)
            block_data = pf.read(block_length)
            if block_id == 1: #it's a color, we want it!
                name_len = struct.unpack_from('>h',block_data[:2])
                n_len = name_len[0]*2
                format_string = '>h' + str(n_len)+'s4sfffh'
                name_len, name, color_space,red,green,blue,mode  = struct.unpack_from(format_string, block_data)
                out_len = name_len - 1
                red = int(red * 255)
                green = int(green * 255)
                blue = int(blue * 255)
                aco_color = struct.pack('>hBBBBBBh', 0,red,red,green, green, blue, blue, 0)
                of.write(aco_color)
        pf.close()
        of.close()
        print("Converted "+ Path(pal_file).stem + " to .ACO format.")