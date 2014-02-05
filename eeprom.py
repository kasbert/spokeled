#
# Chip in question is AT24C04, 1024 or 2048 kiB
# 
# USB programmer vendor_id = 0x1d57, product_id = 0x0005
# This is identified as some kind of mouse
#
# Vendor and product strings are utf-8 encoded, probably in chinese
# Vendor name: b"'\xe5\x8c\x80\xe4\x88\x80\\u2000\xe4\xb4\x80\xe6\xbc\x80\xe7\x94\x80\xe7\x8c\x80\xe6\x94\x80\xe7\xbc\x80\xe8\x86\x80\xe8\x8e\x82\xe8\x96\x84\xe8\x9e\x86'"
# Product name: b"'\xe5\x8c\x80\xe4\x88\x80\\u2000\xe4\xb4\x80\xe6\xbc\x80\xe7\x94\x80\xe7\x8c\x80\xe6\x94\x80\xe7\xbc\x80\xe8\x86\x80\xe8\x8e\x82\xe8\x96\x84\xe8\x9e\x86'"
#

import usb.core
import usb.util
from array import array
import argparse
import sys

VENDOR_ID = 0x1d57
PRODUCT_ID = 0x0005

def write_eeprom (addr, data):
    if (addr & 3) != 0:
        raise "Address must be aligned to 4 bytes"
    if (len(data) & 3) != 0:
        raise "Data must be chunks of 4 bytes"
    for i in range (0, len(data), 4):
        cmd = (addr & 0xc) + 0x70
        msg = [ data[i], data[i+1], data[i+2], data[i+3], 
               (addr & 0xf0), (addr >> 8), 0, cmd]
        if args.debug:
            print ("ctrl msg:", repr(msg))
        assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)
        addr += 4

def read_eeprom (addr):
    if (addr & 7) != 0:
        raise "Address must be aligned to 8 bytes"
    msg =  [ 0, 0, 0, 0, (addr & 0xff), (addr >> 8), 0, 0x10 ]
    if args.debug:
        print ("ctrl msg:", repr(msg))
    assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)
    data = read_data_packet()
    #print (repr(data))
    return data

def read_data_packet():
    attempts = 10
    data = None
    while data is None and attempts > 0:
        try:
            data = device.read(endpoint.bEndpointAddress,
                           endpoint.wMaxPacketSize, timeout=100)
        except usb.core.USBError as e:
            data = None
            attempts -= 1
            if e.args == ('Operation timed out',):
                continue
    if args.debug:
        print ("Read data:", repr(data))
    return data

#
#
#

parser = argparse.ArgumentParser(description='Eeprom reader/programmer.')
parser.add_argument('-w', dest='writefile')
parser.add_argument('-r', dest='readfile')
parser.add_argument('-s', dest='size', type=int, choices=(512,1024,2048,4096), default=2048)
parser.add_argument('-d', dest='debug', action='store_true', default=False)
args = parser.parse_args()

# find the USB device
device = usb.core.find(idVendor=VENDOR_ID,
                       idProduct=PRODUCT_ID)

if device.is_kernel_driver_active(0) is True:
   device.detach_kernel_driver(0)

# use the first/default configuration
device.set_configuration()
# first endpoint
endpoint = device[0][(0,0)][0]

# discard old data
try:
    data = device.read(endpoint.bEndpointAddress,
                           endpoint.wMaxPacketSize, timeout=100)
    if args.debug:
        print ("Discard", repr(data))
except:
    pass

assert len (read_eeprom(0)) == 8

#
if args.readfile is not None:
    f=open(args.readfile, "wb")
    try:
        for i in range (0, args.size, 8):
            data = read_eeprom(i)
            f.write(data)
            if args.debug:
                print (i, data)
            i += 8
    finally:
        f.close()

#
if args.writefile is not None:
    f=open(args.writefile, "rb")
    try:
        for i in range (0, args.size, 16):
            data = f.read(16)
            if len (data) == 0:
                break
            # has to be read first ?
            read_eeprom(i)
            if args.debug:
                print ("Before", repr(read_eeprom(i)))
            write_eeprom (i, [ ord(x) for x in data ])
            if args.debug:
                print (i, data)
    finally:
        f.close()
    f=open(args.writefile, "rb")
    c = 0
    read_eeprom(0)
    try:
        for i in range (0, args.size, 8):
            data = f.read(8)
            if len (data) == 0:
                break
            data2 = read_eeprom(i)
            for j in range(8):
                assert data2[j] == ord(data[j]), (c + j, data2[j], data[j])
            c = c + 8
    finally:
        f.close()

