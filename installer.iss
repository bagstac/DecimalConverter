; Inno Setup script for Decimal Convertor
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
; Run build.bat first to produce dist\DecimalConvertor.exe

#define AppName      "Decimal Convertor"
#define AppVersion   "1.0"
#define AppPublisher "Brian"
#define AppExeName   "DecimalConvertor.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppVerName={#AppName} {#AppVersion}

; Default install location: C:\Program Files\Decimal Convertor
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}

; Installer output
OutputDir=installer_output
OutputBaseFilename=DecimalConvertorSetup

; Compression
Compression=lzma2/ultra64
SolidCompression=yes

; Require Windows 10 or later
MinVersion=10.0

; Visual
WizardStyle=modern
WizardSizePercent=100

; The installer does not need admin rights for per-user installs,
; but writing to Program Files requires them.
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; \
  Description: "Create a &desktop shortcut"; \
  GroupDescription: "Additional shortcuts:"; \
  Flags: unchecked

[Files]
; Main executable produced by PyInstaller
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";           Filename: "{app}\{#AppExeName}"
; Uninstall entry in Start Menu
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
; Optional desktop shortcut (only if the user ticked the task above)
Name: "{commondesktop}\{#AppName}";   Filename: "{app}\{#AppExeName}"; \
  Tasks: desktopicon

[Run]
; Offer to launch the app at the end of installation
Filename: "{app}\{#AppExeName}"; \
  Description: "Launch {#AppName}"; \
  Flags: nowait postinstall skipifsilent
