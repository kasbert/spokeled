import usb.core
import usb.util
from array import array

#
# Chip in question is AT24C04 (or bigger)
# 
# USB programmer vendor_id = 0x1d57, product_id = 0x0005
#
# Vendor and product strings are utf-8 encoded, probably in chinese
# Vendor name: b"'\xe5\x8c\x80\xe4\x88\x80\\u2000\xe4\xb4\x80\xe6\xbc\x80\xe7\x94\x80\xe7\x8c\x80\xe6\x94\x80\xe7\xbc\x80\xe8\x86\x80\xe8\x8e\x82\xe8\x96\x84\xe8\x9e\x86'"
# Product name: b"'\xe5\x8c\x80\xe4\x88\x80\\u2000\xe4\xb4\x80\xe6\xbc\x80\xe7\x94\x80\xe7\x8c\x80\xe6\x94\x80\xe7\xbc\x80\xe8\x86\x80\xe8\x8e\x82\xe8\x96\x84\xe8\x9e\x86'"
#
# Eeprom address
# 0 contains count of patterns
# 1 flags ?
# 2 + n*3 address high byte
# 3 + n*3 address low byte
# 4 + n*3 pattern size (50)
#
# Bitmap is 50 columns, right to left, each column is 16 bits (2 bytes), low endian first.
# Bit 0 is bottom and bit 11 is up
# Bits 2(4) and 3(8), 6(64) and 7(128), 10(0x400) and 11(0x800), 14(0x4000) and 15(0x8000) are swapped
# Unused bits are set to 1, thus empty is 0xf400
# 1111x1xx xxxxxxxx
# ^^  ^^   ^^  ^^    swaoped


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
        print (msg)
        assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)
        addr += 4

def read_eeprom (addr):
    if (addr & 7) != 0:
        raise "Address must be aligned to 8 bytes"
    msg =  [ 0, 0, 0, 0, (addr & 0xff), (addr >> 8), 0, 0x10 ]
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
    #print repr(data)
    return data

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
    print ("discard", repr(data))
except:
    pass

print (repr(read_eeprom(0)))

# write
#msg = [1,2,3,4, 0xf0,0x01,0,0x70]
#print msg
#assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)
#msg = [5,6,7,8, 0xf0,0x01,0,0x74]
#print msg
#assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)
#msg = [9,10,11,12, 0xf0,0x01,0,0x78]
#print msg
#assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)
#msg = [13, 14, 15, 16, 0xf0,0x01,0,0x7c]
#print msg
#print 
#assert device.ctrl_transfer(0x21, 9, 0x200, 0, msg) == len(msg)

#write_eeprom (0x1e0, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
#print (repr(read_eeprom(0x1e0)))
#print (repr(read_eeprom(0x1e8)))


#print (repr(read_eeprom(0x1f0)))
#print (repr(read_eeprom(0x1f8)))
#write_eeprom (0x1f0, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
#print (repr(read_eeprom(0x1f0)))
#print (repr(read_eeprom(0x1f8)))
#write_eeprom (0x1f0, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

f=open("out-orig.bin", "rb")
try:
    i = 0;
    while i < 65536:
        data = f.read(16)
        if len (data) == 0:
            break
        # has to be read first ?
        read_eeprom(i)
        print ("before", repr(read_eeprom(i)))
        write_eeprom (i, [ ord(x) for x in data ])
        print (i, data)
        print ("after", repr(read_eeprom(i)))
        i += 16
finally:
    f.close()

print
f=open("out.bin", "wb")

i = 0;
while i < 512:
    data = read_eeprom(i)
    f.write(data)
    print (i, data)
    i += 8
f.close()



#ret = device.ctrl_transfer(0x21, 9, 0x200, 0, 9)
#sret = ''.join([chr(x) for x in ret])
#print ret


#device.write(array)
#result = device.controlMsg(
#    usb.ENDPOINT_OUT + usb.TYPE_CLASS + usb.RECIP_INTERFACE,
#    usb.REQ_SET_CONFIGURATION, buf, value=0x200, timeout=50)
#if result != len(buf):
#    raise IOError('pywws.device_libusb.USBDevice.write_data failed')


