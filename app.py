# coding:utf-8

import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())
printx(plist)
printx(plist[0])
printx(plist[0][0])
printx(plist[0][1])
printx(plist[0][2])

if len(plist) < 0:
    printx("没有发现端口！")
else:
    plist_0 = list(plist[0])
    serial_name = plist_0[0]
    serial_fd = serial.Serial(serial_name, 9600, timeout=60)
    printx("可用端口名>>>", serial_fd.name)
