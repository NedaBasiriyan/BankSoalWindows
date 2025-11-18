[Setup]
AppName=BankSoalApp
AppVersion=1.0
DefaultDirName={pf}\BankSoalApp
DefaultGroupName=BankSoalApp
OutputDir=dist
OutputBaseFilename=BankSoalApp_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\BankSoalApp.exe"; DestDir: "{app}\"; Flags: ignoreversion

[Run]
Filename: "{app}\BankSoalApp.exe"; Description: "{cm:LaunchProgram, BankSoalApp}"; Flags: nowait postinstall
