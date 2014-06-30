#!/usr/bin/python
import struct
from sys import argv, exit

def ensure(condition, message, exitCode=0):
    if not condition:
        print(message)
        exit(exitCode)

# Check argument existence
ensure(len(argv) > 1,
'''
    swatch.py - Adobe ASE swatch reader

    Usage: swatch.py <in_file>

    https://github.com/rschiang/swatch-tool
''')

f = open(argv[1], 'r')

# Check ASE signature
ensure(f.read(4) == 'ASEF', 'ERROR: Signature mismatch')

buf = f.read()
f.close()

def unpack(fmt):
    global buf
    val = struct.unpack_from(fmt, buf)
    buf = buf[struct.calcsize(fmt):]
    return val if len(val) > 1 else val[0]

# Check file version
version = unpack('>hh')
if version != (1, 0):
    print('WARNING: File version mismatch (%d.%d)' % version)

# Read blocks
blocks = unpack('>i')
for i in range(blocks):
    block_type = unpack('>H')
    if block_type not in [0xc001, 0xc002, 0x0001]:
        print('WARNING: Unknown block type %d' % block_type)

    block_len = unpack('>i')

    if block_type == 0xc002:
        print('[GROUP END]')
        ensure(block_len == 0, 'ERROR: Invalid block size')
        continue
    else:
        ensure(block_len > 0, 'ERROR: Invalid block size')

    name_len = unpack('>H')
    ensure(0 < name_len < block_len, 'ERROR: Invalid name string length')
    block_len -= 2

    name = u''
    for j in range(name_len):
        val = unpack('>H')
        name += unichr(val)
    block_len -= 2 * name_len

    if block_type == 0xc001:
        # Group start
        print('[GROUP %s]' % name)

    elif block_type == 0x0001:
        # Color swatch
        print('COLOR %s' % name)

        color_mode = unpack('4s')
        block_len -= 4

        if color_mode == 'CMYK':
            C, M, Y, K = unpack('4f')
            block_len -= 16

        elif color_mode == 'RGB ':
            R, G, B = unpack('3f')
            block_len -= 12

        elif color_mode == 'LAB ':
            R, G, B = unpack('3f')
            block_len -= 12

        elif color_mode == 'Gray':
            B = unpack('f')
            block_len -= 4

        else:
            ensure(False, 'ERROR: Invalid color mode')

        ensure(block_len > 0, 'ERROR: Invalid block size')

        color_type = unpack('>h')
        block_len -= 2

    ensure(block_len == 0, 'ERROR: Block size mismatch')
