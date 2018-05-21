
```
pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com  

python gui.py
```

```
pyinstaller --onefile --windowed gui.spec
```

```
1、登录：          AA 4A 4C 0C 00 81 02 00 01 11 11 22 22 02 04 01 01
2、开始试验：      AA 4A 4C 05 00 84 02 00 01 47
3、结束试验：      AA 4A 4C 05 00 84 02 00 01 4F
4、蜂鸣器频率设置：AA 4A 4C 09 00 84 02 00 01 41 34 05 00 00
5、蜂鸣器开关：    AA 4A 4C 06 00 84 02 00 01 42 88
6、灯光开关：	   AA 4A 4C 06 00 84 02 00 01 4C 88
7、加电开关：	   AA 4A 4C 06 00 84 02 00 01 45 88
8、重力数据返回：  AA 4A 4C 04 00 86 0F 00 01
```
