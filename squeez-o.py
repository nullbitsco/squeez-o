#!/usr/bin/env python3
# Compress bitmaps using clever encoding
# Works only with 128x32 (512 bytes long) BMPs for now.

from ast import arg
import textwrap
import argparse

# Arg parser
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', action='store', help='file to run the squeeze-o compression algorithm on [default = input_bytes.tmp]', default='input_bytes.tmp', type=str)
args = parser.parse_args()

my_wrap = textwrap.TextWrapper(width = 95)

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
    block_map_str += F"0x{chunk:02x}, "

'''
Block maps and block lists look like this:

static const char PROGMEM block_map[] = {
    0x80, 0x03, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00, 0x70, 0x00, 0x00,
    0x00, 0xc0, 0x0f, 0x00, 0x00, 0xff, 0x19, 0x00, 0xfc, 0xf1, 0x1d, 0x00, 0x38, 0x00, 0xf3, 0x0f,
    0xe0, 0x83, 0x0d, 0x0f, 0x00, 0xfe, 0xff, 0x03, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x00, 0x00, 0x18,
    0x00, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static const char PROGMEM block_list[] = {
    0x07, 0x78, 0x80, 0x07, 0xf8, 0x1f, 0xe0, 0x01, 0x1e, 0xe0, 0x01, 0x1e, 0xe0, 0x80, 0x80, 0x80,
    0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0xc2, 0xc1, 0x01, 0xc0, 0x3f, 0xe0, 0x10, 0x08, 0x08, 0x04,
    0x02, 0x01, 0x18, 0x18, 0x03, 0x43, 0xc0, 0x03, 0x7c, 0x80, 0x03, 0x7c, 0x80, 0x13, 0x0c, 0x07,
    0x38, 0x40, 0x20, 0x20, 0x20, 0x20, 0xc0, 0x07, 0x18, 0x20, 0x40, 0x80, 0x03, 0x03, 0x1e, 0x1e,
    0x80, 0x60, 0x18, 0x07, 0x1f, 0x20, 0x40, 0x40, 0x20, 0x20, 0x10, 0x10, 0x10, 0x20, 0x40, 0x40,
    0x40, 0x80, 0x80, 0x9f, 0xe0, 0x01, 0x3e, 0xc0, 0x07, 0xf8, 0x1f, 0xe0, 0x03, 0x7c
};
'''

block_map_str = block_map_str.rstrip(', ')
print("static const char PROGMEM block_x_map[] = {")
print(F"{my_wrap.fill(text = block_map_str)}")
print("};")
print()
print("static const char PROGMEM block_x_list[] = {")
print(F"{my_wrap.fill(text = ', '.join(block_list))}")
print("};")

# Calculate some statistics
compression_ratio = (1-(len(block_map_list) + len(block_list))/len(bytes_list))*100
print(F"Input was {len(bytes_list)} bytes, deflated block list is now {len(block_list)} bytes + {len(block_map_list)} bytes overhead")
print(F"Space savings: {compression_ratio:.2f}%")
