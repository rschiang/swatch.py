#!/usr/bin/python
import struct
from sys import argv, exit

def ensure(condition, message, exitCode=-1):
    if not condition:
        print(message if exitCode != -1 else 'ERROR: %s' % message)
        exit(exitCode)

def warn_if(condition, message, args=None):
    if condition:
        print('WARNING: %s' % (message if args is None else message % args))

# Check argument existence
ensure(len(argv) > 1,
'''
    swatch.py - Adobe ASE swatch reader

    Usage: swatch.py <in_file>

    https://github.com/rschiang/swatch.py
''', 0)

f = open(argv[1], 'r')

# Check ASE signature
ensure(f.read(4) == 'ASEF', 'Signature mismatch')

buf = f.read()
f.close()

def unpack(fmt):
    global buf
    val = struct.unpack_from(fmt, buf)
    buf = buf[struct.calcsize(fmt):]
    return val if len(val) > 1 else val[0]

# Check file version
version = unpack('>hh')
warn_if(version != (1, 0), 'File version mismatch (%d.%d)', version)

# Read blocks
blocks = unpack('>i')
indent = 0
for i in range(blocks):
    block_type = unpack('>H')
    warn_if(block_type not in [0xc001, 0xc002, 0x0001], 'Unknown block type %d', block_type)

    block_len = unpack('>i')

    if block_type == 0xc002:
        ensure(block_len == 0, 'Invalid block size')
        indent -= 1
        continue
    else:
        ensure(block_len > 0, 'Invalid block size')

    name_len = unpack('>H')
    ensure(0 < name_len < block_len, 'Invalid name string length')
    block_len -= 2

    name = u''
    for j in range(name_len):
        val = unpack('>H')
        name += unichr(val)
    block_len -= 2 * name_len

    if block_type == 0xc001:
        # Group start
        print('[GROUP %s]' % name)
        indent += 1

    elif block_type == 0x0001:
        # Color swatch
        color_mode = unpack('4s')
        block_len -= 4

        processing = {
            'CMYK': '>4f',
            'RGB ': '>3f',
            'LAB ': '>3f',
            'Gray': '>f',
        }

        ensure(color_mode in processing, 'Unrecognized color mode %s' % color_mode)

        fmt = processing[color_mode]
        colors = unpack(fmt)

        block_len -= struct.calcsize(fmt)
        ensure(block_len > 0, 'Invalid block size')

        color_type = unpack('>h')
        block_len -= 2

        color_types = {
            0: 'GLOBAL',
            1: 'SPOT',
            2: 'NORMAL',
        }
        ensure(color_type in color_types, 'Unknown color type %d' % color_type)

        print('%sCOLOR %s %s (%s) %s' % (
            indent * '\t',
            name,
            color_mode.strip(),
            ', '.join([str(k) for k in colors]),
            color_types[color_type]
        ))

    ensure(block_len == 0, 'Block size mismatch')
