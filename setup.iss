[Files]
Source: "C:\Users\Jeff\pycom\src"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Application"; Filename: "{app}\WinPython\python-3.7.0b3.amd64\pythonw.exe"; WorkingDir: "{app}"; Parameters: """WinPython\python-3.7.0b3.amd64\Lib\site-packages\PyComApp\gui.py""";  IconFilename: "{app}\favicon.ico"

[Run]
Filename: "C:\Users\Jeff\pycom\PyComApp\WinPython\python-3.7.0b3.amd64\python.exe"; WorkingDir: "{app}"; Parameters: """{app}\postinstall.py"""; Flags: runhidden

[Setup]
SetupIconFile=C:\Users\Jeff\pycom\favicon.ico
WizardImageFile=wizard.bmp
WizardImageStretch=no
WizardSmallImageFile=wizard-small.bmp
WizardImageBackColor=$ffffff
AppName=PyComApp
AppVersion=1.0.0
DefaultDirName=C:\PyComApp

