; Inno Setup script: BreakMyWallet installer
[Setup]
AppName=BreakMyWallet
AppVersion=1.0.0
DefaultDirName={autopf}\BreakMyWallet
DefaultGroupName=BreakMyWallet
OutputDir=installer\output
OutputBaseFilename=breakmywallet_installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\bmw_maint_tracker.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BreakMyWallet"; Filename: "{app}\bmw_maint_tracker.exe"
Name: "{commondesktop}\BreakMyWallet"; Filename: "{app}\bmw_maint_tracker.exe"
