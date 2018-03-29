# coding:utf-8

import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())
print(plist)
print(plist[0])
print(plist[0][0])
print(plist[0][1])
print(plist[0][2])

if len(plist) < 0:
    print("没有发现端口！")
else:
    plist_0 = list(plist[0])
    serial_name = plist_0[0]
    serial_fd = serial.Serial(serial_name, 9600, timeout=60)
    print("可用端口名>>>", serial_fd.name)
