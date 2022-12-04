#!/usr/bin/env python3
# Compress bitmaps using clever encoding
# Works only with 128x32 (512 bytes long) BMPs for now.

import textwrap
import argparse

# Arg parser
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', action='store', help='file to run the squeeze-o compression algorithm on [default = input_bytes.tmp]', default='input_bytes.tmp', type=str)
args = parser.parse_args()

indent = '    '
my_wrap = textwrap.TextWrapper(width = 95, initial_indent=indent, subsequent_indent=indent)

# TODO: This could also be modified to work with other dominant bytes: 0xFF for example.
# There would need to be a flag on the firwmare side to make this work right.
BYTE_ZERO = '0x00'

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

# Read into individual bytes
with open(args.file) as fo:
    bytes_raw = fo.read()

# Clean
bytes_raw = bytes_raw.lower()
bytes_list = bytes_raw.split(',')

# Check the length and throw a warning.
if len(bytes_list) > 512:
    print("Bitmap too large! Max size: 128x32 (512 bytes)")

# Iterate over bytes and generate block map
block_map = ''
block_list = []
for x in range(len(bytes_list)):
    # Clean each raw byte
    raw_byte = bytes_list[x]
    raw_byte = raw_byte.strip()
    raw_byte = raw_byte.strip('\n')

    # Build the block map: 0 if the whole byte is zero, the raw byte otherwise.
    if BYTE_ZERO in raw_byte:
        block_map += '0'
    else:
        block_map += '1'
        block_list.append(raw_byte)

# Finalize and write to string
block_map_list = list(chunkstring(block_map, 8))
block_map_str = ''

for part in block_map_list:
    part_flipped = part[::-1]
    chunk = int(part_flipped, 2)
    block_map_str += f"0x{chunk:02x}, "

# NEW: Block maps and block lists are now encapsulated in a struct, compressed_oled_frame_t.
# This makes it easier to integrate into the keyboard firmware.
typedef_header = """
// Compressed oled data structure
// This must be included ONCE along with the compressed data
typedef struct {
    const uint16_t data_len;
    const char* block_map;
    const char* block_list;
} compressed_oled_frame_t;
"""

if 'input_bytes' in args.file:
    frame_name = 'frame'
else:
    # Include input file names if not using the default
    frame_name = args.file

    # Sanitize - remove dots
    frame_name = frame_name.split('.')[0] if '.' in frame_name else frame_name
    # Sanitize - remove forward/backward slashes
    frame_name = frame_name.split('/')[-1] if '/' in frame_name else frame_name
    frame_name = frame_name.split('\\')[-1] if '\\' in frame_name else frame_name

block_map_str = block_map_str.rstrip(', ')
print(typedef_header)
print(f"static const char PROGMEM {frame_name}_map[] = {{ ")
print(f"{my_wrap.fill(text = block_map_str)}")
print("};")
print(f"static const char PROGMEM {frame_name}_list[] = {{ ")
print(f"{my_wrap.fill(text = ', '.join(block_list))}")
print("};")
print(f"static const compressed_oled_frame_t PROGMEM {frame_name} = {{{len(bytes_list)}, {frame_name}_map, {frame_name}_list}};")
# Calculate some statistics
compression_ratio = (1-(len(block_map_list) + len(block_list))/len(bytes_list))*100
print(f"// Input was {len(bytes_list)} bytes, deflated block list is now {len(block_list)} bytes + {len(block_map_list)} bytes overhead")
print(f"// Space savings: {compression_ratio:.2f}%")
