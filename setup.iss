; ═══════════════════════════════════════════════════════
; اسکریپت Inno Setup برای «مدیریت ساختمان»
;
; قبل از استفاده، فقط این یه مورد رو عوض کن:
;   خط Source توی بخش [Files] → مسیر واقعی پوشه‌ی خروجی
;   pyinstaller روی سیستم خودت (همون dist\مدیریت ساختمان)
;
; نکته‌ی مهم درباره‌ی PrivilegesRequired=lowest:
; برنامه دیتابیس/لوگو/آیکون/بکاپ رو مستقیم کنار exe (توی همون
; پوشه‌ی نصب) ذخیره می‌کنه. اگه نصاب رو با دسترسی ادمین و توی
; Program Files معمولی نصب کنیم، برنامه موقع اجرا اجازه‌ی
; نوشتن نداره و کرش می‌کنه. برای همین اینجا از {autopf} +
; PrivilegesRequired=lowest استفاده شده که خودش هوشمندانه یه
; مسیر قابل‌نوشتن (زیر پوشه‌ی کاربر، بدون نیاز به ادمین) انتخاب
; می‌کنه. این تنظیمات رو دست نزن مگر مطمئن باشی.
; ═══════════════════════════════════════════════════════

#define MyAppName "مدیریت ساختمان"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "شرکت شما"
; نکته: اسم فایل exe عمداً انگلیسیه (BuildingManager)، نه فارسی —
; همون دلیلی که تو build.bat توضیح داده شده (جلوگیری از خطای
; "CreateProcess failed; code 2" به‌خاطر ناهماهنگی نامرئیِ
; کاراکترهای RTL بین فایل‌های مختلف). AppName و اسم میانبرها
; همچنان فارسی می‌مونن، فقط اسم فایل exe عوض شده.
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
Compression=lzma
SolidCompression=yes
; دستور رو تغییر نده، دلیلش بالای فایل توضیح داده شده
PrivilegesRequired=lowest
WizardStyle=modern
; نکته: SetupIconFile به فایل app_icon.ico توی ریشه‌ی پروژه (همون
; فایلی که به pyinstaller با --icon دادیم) اشاره می‌کنه، نه به
; داخل پوشه‌ی dist — چون --icon فقط آیکون رو داخل خودِ exe
; می‌ذاره و فایل .ico رو جدا کپی نمی‌کنه، پس همچین فایلی توی
; dist اصلاً وجود نداره (همون چیزی که باعث خطای کامپایل شد).
; اگه اصلاً app_icon.ico توی ریشه‌ی پروژه نداری، کل این خط رو
; پاک کن یا با سمی‌کالن کامنتش کن — نصاب با آیکون پیش‌فرض
; Inno Setup ساخته می‌شه، مشکلی نیست.
SetupIconFile=app_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "ساخت آیکون روی دسکتاپ"; GroupDescription: "آیکون‌های اضافی:"
Name: "startupicon"; Description: "اجرای خودکار برنامه هنگام روشن شدن ویندوز"; GroupDescription: "گزینه‌های اجرا:"; Flags: unchecked

[Files]
; این مسیر رو با مسیر واقعی پوشه‌ی خروجی pyinstaller عوض کن
Source: "C:\Users\amire\PycharmProjects\building_manager"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\حذف {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; توجه: عمداً دیتابیس/لوگو/بکاپ‌ها اینجا نیستن، پس با حذف برنامه
; پاک نمی‌شن. اگه می‌خوای موقع Uninstall کامل پاک بشن، این خطوط
; رو از حالت کامنت دربیار (سمی‌کالن اول خط رو حذف کن):
; Type: filesandordirs; Name: "{app}\logos"
; Type: filesandordirs; Name: "{app}\reports"
; Type: files; Name: "{app}\building_manager.db"
