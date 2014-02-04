

f=open("out-orig.bin", "rb")
try:
    i = 0;
    data = f.read()
    print (i, data)
finally:
    f.close()

count = ord(data[0])
flags = ord(data[1])
print ("count", count)
print ("flags", flags)
for i in range (count):
    offset = ord(data[2+i*3])*256 + ord(data[3+i*3])
    length = ord(data[4+i*3])
    print (i, offset, length)
    for j in (0,1,3,2,4,5,7,6,8,9,11): #  11,9,8,6,7,5,4,2,3,1,0
        for k in range(length * 2 - 2, -1, -2):
            value = ord(data[offset + k]) + ord(data[offset + k + 1])*256 
            if (value & (1<<j)) != 0:
                print ("#"),
            else:
                print ("."),
        print
