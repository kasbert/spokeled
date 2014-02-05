#

import sys
import argparse
from PIL import Image

parser = argparse.ArgumentParser(description='Pack spokeled image.')
parser.add_argument('file', nargs='+')
parser.add_argument('-d', dest='debug', action='store_true', default=False)
parser.add_argument('-w', dest='binfile')
parser.add_argument('-s', dest='height', type=int, choices=(11,16,32), default=32)
args = parser.parse_args()

if args.height > 16:
    word = 4
    bits = (19,0,23,1,27,3,31,2,18,4,22,5,26,7,30,6,17,8,21,9,25,11,29,10,16,12,20,13,24,15,28,14)
else:
    word = 2
    bits = (0,1,3,2,4,5,7,6,8,9,11,10,12,13,15,14)

print args.file
for file in args.file:
    print file
    img = Image.open(file)
    for m in range(args.height):
        row = []
        print m,
        for l in range(img.size[0]):
            if img.getpixel ((l,m)):
                row.append("#")
            else:
                row.append(".")
        print ("%02d" % m), "".join(row)
