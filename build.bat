@echo off
REM ─────────────────────────────────────────────
REM اسکریپت ساخت نسخه‌ی exe برنامه‌ی مدیریت ساختمان
REM این فایل رو کنار app.py بذار و دابل‌کلیک کن یا
REM از داخل .venv فعال‌شده اجرا کن.
REM
REM نکته: عمداً اسم خروجی (BuildingManager) انگلیسیه، نه فارسی.
REM دلیلش: وقتی اسم فارسیِ فایل exe رو تو چند جای مختلف (اینجا،
REM بعداً تو اسکریپت نصاب) جدا تایپ/کپی می‌کنیم، به‌خاطر
REM کاراکترهای نامرئی جهت متن (RTL mark) که ادیتورها/ویندوز گاهی
REM خودشون اضافه می‌کنن، ممکنه از نظر بایت یکی نباشن و ویندوز
REM موقع اجرا بگه «فایل رو پیدا نکردم» — دقیقاً همون خطایی که
REM قبلاً گرفتی. اسم انگلیسی این ریسک رو کامل از بین می‌بره.
REM عنوان پنجره‌ی برنامه (چیزی که واقعاً می‌بینی) همچنان فارسیه
REM و از app.py میاد، این فقط اسم فایله.
REM ─────────────────────────────────────────────

echo در حال پاک کردن build های قبلی...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q "BuildingManager.spec" 2>nul

echo.
echo در حال ساخت exe...
echo.

pyinstaller --name "BuildingManager" ^
  --windowed ^
  --icon=app_icon.ico ^
  --add-data "fonts;fonts" ^
  --hidden-import win10toast ^
  --hidden-import plyer.platforms.win.notification ^
  --hidden-import pystray._win32 ^
  --hidden-import PIL._tkinter_finder ^
  --hidden-import sqlalchemy.sql.default_comparator ^
  --hidden-import jdatetime ^
  --collect-all reportlab ^
  --collect-all matplotlib ^
  --collect-all cryptography ^
  app.py

echo.
if exist "dist\BuildingManager\BuildingManager.exe" (
    echo ✅ ساخت با موفقیت انجام شد.
    echo خروجی: dist\BuildingManager\
) else (
    echo ❌ ساخت ناموفق بود. پیام‌های بالا رو بررسی کن.
)
echo.
pause
