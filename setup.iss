; ═══════════════════════════════════════════════════════
; اسکریپت Inno Setup برای «مدیریت ساختمان»
; ═══════════════════════════════════════════════════════

#define MyAppName "مدیریت ساختمان"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "شرکت شما"
#define MyAppExeName "BuildingManager.exe"

[Setup]
AppId={{B1E1A2F0-0000-0000-0000-000000000001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=BuildingManager_Setup_{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
SetupIconFile=app_icon.ico
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "ساخت آیکون روی دسکتاپ"; GroupDescription: "آیکون‌های اضافی:"
Name: "startupicon"; Description: "اجرای خودکار برنامه هنگام روشن شدن ویندوز"; GroupDescription: "گزینه‌های اجرا:"; Flags: unchecked

[Files]
; ⭐ همه‌ی محتوای dist (شامل exe، _internal، Tesseract، EasyOCR)
Source: "dist\BuildingManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\حذف {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; توجه: عمداً دیتابیس/لوگو/بکاپ‌ها اینجا نیستن
; Type: filesandordirs; Name: "{app}\logos"
; Type: filesandordirs; Name: "{app}\reports"
; Type: files; Name: "{app}\building_manager.db"