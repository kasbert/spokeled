#

import sys
import argparse
from array import array
from PIL import Image

parser = argparse.ArgumentParser(description='Pack spokeled image.')
parser.add_argument('file', nargs='+')
parser.add_argument('-d', dest='debug', action='store_true', default=False)
parser.add_argument('-i', dest='inverse', action='store_true', default=False)
parser.add_argument('-s', dest='size', type=int, choices=(512,1024,2048,4096), default=2048)
parser.add_argument('-w', dest='binfile')
parser.add_argument('-l', dest='leds', type=int, choices=(11,16,32), default=32)
args = parser.parse_args()

if args.leds > 16:
    word = 4
    bits = (19,0,23,1,27,3,31,2,18,4,22,5,26,7,30,6,17,8,21,9,25,11,29,10,16,12,20,13,24,15,28,14)
else:
    word = 2
    bits = (0,1,3,2,4,5,7,6,8,9,11,10,12,13,15,14)

data = [ 0 for i in range(args.size) ]
count = len(args.file)
data[0] = count
if args.leds > 16:
    data[1] = 0x4
else:
    data[1] = 0xc
offset = count * 3 + 2

for i in range(count):
    file = args.file[i]
    print file
    img = Image.open(file)
    length = img.size[0]
    if args.debug:
        print (i, offset, length)
    data[2 + i*3] = offset >> 8;
    data[3 + i*3] = offset & 0xff;
    data[4 + i*3] = length;

    for m in range(args.leds):
        row = []
        for l in range(length):
            if (img.getpixel ((l,m)) != 0) ^ args.inverse:
                row.append("#")
                k = (length - 1 - l) * word + bits[m] / 8
                if offset + k < len(data):
                    data[offset + k] = data[offset + k] | (1 << (bits[m] % 8))
            else:
                row.append(".")
        print ("%02d" % m), "".join(row)
    offset = offset + length * word
if args.debug:
    print (data)
data = [ chr(x) for x in data]

if args.binfile is not None:
    f=open(args.binfile, "wb")
    try:
        f.write("".join(data))
    finally:
        f.close()

