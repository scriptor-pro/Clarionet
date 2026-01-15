#define MyAppName "Clarionet"
#define MyAppVersion "__VERSION__"
#define MyAppPublisher "Clarionet"
#define MyAppURL ""
#define MyAppExeName "clarionet.exe"

[Setup]
AppId={{A09AFA07-EE3E-4D96-BE74-35A6F6D0E1E1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=__SOURCE_DIR__\dist
OutputBaseFilename=clarionet-setup
Compression=lzma
SolidCompression=yes
SetupIconFile=__SOURCE_DIR__\assets\icons\clarionet.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons"; Flags: unchecked

[Files]
Source: "__SOURCE_DIR__\dist\clarionet\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
