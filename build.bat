@echo off
REM ─────────────────────────────────────────────
REM اسکریپت ساخت نسخه‌ی exe برنامه‌ی مدیریت ساختمان
REM ─────────────────────────────────────────────

echo ═══════════════════════════════════════
echo ساخت نسخه‌ی exe
echo ═══════════════════════════════════════

echo.
echo پاک کردن build های قبلی...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q "BuildingManager.spec" 2>nul

REM ─── چک آماده بودن Tesseract و EasyOCR ───
if not exist "Tesseract-OCR\tesseract.exe" (
    echo.
    echo Tesseract-OCR آماده نیست!
    echo    اول این رو اجرا کن: python prepare_bundle.py
    echo.
    pause
    exit /b 1
)

if not exist "EasyOCR_models" (
    echo.
    echo EasyOCR_models آماده نیست!
    echo    اول این رو اجرا کن: python prepare_bundle.py
    echo.
    pause
    exit /b 1
)

echo Tesseract-OCR آماده‌ست
echo EasyOCR_models آماده‌ست

REM ─── فعال کردن venv پروژه ───
if exist ".venv311\Scripts\activate.bat" (
    echo فعال‌سازی venv311...
    call ".venv311\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo فعال‌سازی venv...
    call ".venv\Scripts\activate.bat"
) else (
    echo venv پیدا نشد
)

echo.
echo در حال ساخت exe...
echo توجه: این build سنگینه (torch + easyocr)
echo    ممکنه ۱۰-۲۰ دقیقه طول بکشه. صبر کن.
echo.

pyinstaller --name "BuildingManager" ^
  --windowed ^
  --icon=app_icon.ico ^
  --add-data "fonts;fonts" ^
  --collect-all flet ^
  --collect-all flet_runtime ^
  --collect-all easyocr ^
  --collect-all torch ^
  --collect-all torchvision ^
  --collect-all pytesseract ^
  --collect-all cv2 ^
  --collect-all numpy ^
  --collect-all reportlab ^
  --collect-all matplotlib ^
  --collect-all cryptography ^
  --collect-all bidi ^
  --collect-all arabic_reshaper ^
  --hidden-import win10toast ^
  --hidden-import plyer.platforms.win.notification ^
  --hidden-import pystray._win32 ^
  --hidden-import PIL._tkinter_finder ^
  --hidden-import sqlalchemy.sql.default_comparator ^
  --hidden-import jdatetime ^
  --hidden-import receipt_parser ^
  --hidden-import chart_generator ^
  --hidden-import pdf_generator ^
  --hidden-import bill_parser ^
  --hidden-import services ^
  --hidden-import models ^
  --hidden-import database ^
  --hidden-import sms_service ^
  --hidden-import tray ^
  --hidden-import notify ^
  --hidden-import check_db ^
  --hidden-import migrate_add_images ^
  app.py

echo.
if not exist "dist\BuildingManager\BuildingManager.exe" (
    echo ساخت exe ناموفق بود!
    pause
    exit /b 1
)

echo exe ساخته شد.
echo.
echo در حال کپی Tesseract و EasyOCR به dist...
echo.

REM ─── کپی Tesseract و EasyOCR به dist ───
xcopy /E /I /Y /Q "Tesseract-OCR" "dist\BuildingManager\Tesseract-OCR" >nul
if errorlevel 1 (
    echo خطا در کپی Tesseract!
    pause
    exit /b 1
)

xcopy /E /I /Y /Q "EasyOCR_models" "dist\BuildingManager\EasyOCR_models" >nul
if errorlevel 1 (
    echo خطا در کپی EasyOCR!
    pause
    exit /b 1
)

echo Tesseract-OCR کپی شد
echo EasyOCR_models کپی شد

echo.
echo ═══════════════════════════════════════
echo همه چیز آماده‌ست!
echo خروجی: dist\BuildingManager\
echo ═══════════════════════════════════════
echo.
echo حالا setup.iss رو کامپایل کن
echo.
pause