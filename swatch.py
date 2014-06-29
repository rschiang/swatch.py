#!/usr/bin/python
import struct
from sys import argv, exit

if len(argv) <= 1:
    print('''
    swatch.py - Adobe ASE swatch reader

    Usage: swatch.py <in_file>

    https://github.com/rschiang/swatch-tool
    ''')
    exit()

f = open(argv[1], 'r')
