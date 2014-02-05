#
# Eeprom addresses:
# 0 count of patterns
# 1 flags
#  bit 2(4) == background led, 
#  bit 3(8) == led order ? Set with 11 leds, clear with 32 leds
# 2 + n*3 address high byte
# 3 + n*3 address low byte
# 4 + n*3 pattern size
# 5 + n*3 first pattern
# 
# Pattern is n columns, right to left, each column is 16 bits (2 bytes) or 32 bits (4 bytes), low endian.

# 11 Led version
# bits = (0,1,3,2,4,5,7,6,8,9,11,10,12,13,15,14)
# Bit 0 is bottom and bit 11 is up
# Bits 2(4) and 3(8), 6(64) and 7(128), 10(0x400) and 11(0x800), 14(0x4000) and 15(0x8000) are swapped
# Unused bits are set to 1, thus empty is 0xf400
# 1111x1xx xxxxxxxx
# ^^  ^^   ^^  ^^    swapped

# 32 led version
# bits = (19,0,23,1,27,3,31,2,18,4,22,5,26,7,30,6,17,8,21,9,25,11,29,10,16,12,20,13,24,15,28,14)

import sys
import argparse

parser = argparse.ArgumentParser(description='Unpack spokeled image.')
parser.add_argument('file')
parser.add_argument('-d', dest='debug', action='store_true', default=False)
parser.add_argument('-b', dest='bitmap', action='store_true', default=False)
parser.add_argument('-p', dest='outprefix', default='out')
parser.add_argument('-l', dest='leds', type=int, choices=(11,16,32), default=32)
args = parser.parse_args()

if args.bitmap:
    from PIL import Image

f=open(args.file, "rb")
try:
    i = 0;
    data = f.read()
    if args.debug:
        print (i, data)
finally:
    f.close()

if args.leds > 16:
    word = 4
    bits = (19,0,23,1,27,3,31,2,18,4,22,5,26,7,30,6,17,8,21,9,25,11,29,10,16,12,20,13,24,15,28,14)
else:
    word = 2
    bits = (0,1,3,2,4,5,7,6,8,9,11,10,12,13,15,14)

count = ord(data[0])
flags = ord(data[1])
if args.debug:
    print ("Count", count)
    print ("Flags", flags)
for i in range (count):
    offset = ord(data[2+i*3])*256 + ord(data[3+i*3])
    length = ord(data[4+i*3])
    print
    if args.debug:
        print (i, offset, length)
    if args.bitmap:
        img=Image.new("1", (length, args.leds))
    for m in range(args.leds):
        row = []
        for l in range(length):
            k = (length - 1 - l) * word + bits[m] / 8
            if ord(data[offset + k]) & (1 << (bits[m] % 8)):
                if args.bitmap:
                    img.putpixel((l, m), 1)
                row.append("#")
            else:
                row.append(".")
        print ("%02d" % m), "".join(row)
    if args.bitmap:
        filename = "{1}-{0:02d}.bmp".format(i, args.outprefix)
        img.save(filename)
        print filename, "saved"
