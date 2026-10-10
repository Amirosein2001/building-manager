# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

import os
import sys
import random
import jdatetime
import shutil
from datetime import datetime
import webbrowser
import flet as ft
import asyncio
import time

ft.Dropdown = ft.DropdownM2
ft.dropdown = ft.dropdownm2

# ═══════════ نکات آموزشیِ لودینگ ═══════════
# موقع جابجایی بین صفحات، یکی از این‌ها به‌صورت رندوم نمایش داده
# می‌شه تا کاربر کم‌کم با امکانات برنامه آشنا بشه.
APP_TIPS = [
    "💡 از بخش «تنظیمات» می‌تونید لوگوی اختصاصیِ ساختمان رو بسازید و همه‌جای برنامه نمایش داده بشه.",
    "💡 با زدن روی زنگوله‌ی بالای سایدبار، آخرین اعلان‌ها و یادآوری‌ها رو ببینید.",
    "💡 توی بخش «قبوض»، می‌تونید مبلغ قبض آب/برق/گاز رو بین واحدها بر اساس نفرات یا متراژ تقسیم کنید.",
    "💡 از بخش «گزارش مالی» می‌تونید خروجی PDF کامل از وضعیت مالی ساختمان بگیرید.",
    "💡 توی «یادداشت‌ها» می‌تونید یادآوری تنظیم کنید تا سر وقت به شما یادآوری بشه.",
    "💡 با تغییر واحد پول یا حالت روشن/تاریک در تنظیمات، همون لحظه بدون ری‌استارت اعمال می‌شه.",
    "💡 برای هر واحد می‌تونید چند پرداخت جداگانه (حتی پرداخت پله‌ای) ثبت کنید.",
    "💡 با بستن پنجره از دکمه‌ی ضربدر، می‌تونید انتخاب کنید برنامه مینیمایز بشه یا کامل بسته بشه.",
    "💡 برنامه یه بکاپ خودکار از دیتابیس موقع خروج می‌سازه.",
    "💡 از بخش تنظیمات می‌تونید هر وقت خواستید یه بکاپ دستی هم بگیرید یا بکاپ قبلی رو بازیابی کنید.",
    "💡 توی «شارژ و پرداخت»، با زدن روی آیکون تاریخچه، همه‌ی پرداخت‌های قبلیِ هر واحد رو می‌بینید.",
    "💡 وقتی یه قبض جدید ثبت می‌کنید، به‌صورت خودکار هم به لیست هزینه‌ها اضافه می‌شه.",
    "💡 توی «هزینه‌ها» یه نمودار دایره‌ای می‌بینید که نشون می‌ده هزینه‌ها بین چه دسته‌هایی تقسیم شده.",
    "💡 از بخش «پیامک»، می‌تونید برای یک یا چند واحد هم‌زمان پیامک ارسال کنید.",
    "💡 یادداشت‌ها رنگ‌بندی و اولویت‌بندی دارن؛ مهم‌ترین‌ها رو می‌تونید پین کنید تا بالای لیست بمونن.",
    "💡 موقع فراموشی رمز عبور، می‌تونید با پاسخ به سؤال امنیتی‌تون رمز رو بازیابی کنید.",
    "💡 با فعال کردن System Tray در تنظیمات، برنامه به‌جای بسته شدن کامل، کنار ساعت ویندوز مینیمایز می‌شه.",
    "💡 اگه یه واحد چند نفر ساکن داشته باشه، تقسیم قبض آب به‌صورت خودکار بر اساس تعداد نفرات محاسبه می‌شه.",
    "💡 برای شارژهای دیرکرد، وضعیت واحد به‌صورت خودکار به «معوق» تغییر می‌کنه تا راحت پیگیری کنید.",
    "💡 می‌تونید برای هر واحد اطلاعات ساکن (مالک/مستأجر) و شماره تماس رو ثبت کنید.",
    "💡 توی داشبورد، خلاصه‌ی وضعیت مالی، موجودی صندوق و بدهکارها رو یک‌جا می‌بینید.",
    "💡 هر بار که لوگو رو از نو می‌سازید، همه‌جای برنامه (سایدبار، صفحه‌ی ورود، آیکون) بلافاصله به‌روز می‌شه.",
    "💡 روش محاسبه‌ی شارژ رو می‌تونید بین مبلغ ثابت، بر اساس متراژ یا بر اساس نفرات انتخاب کنید.",
    "💡 گزارش مالی هم به‌صورت ماهانه و هم سالانه قابل مشاهده و خروجی‌گیریه.",
    "💡 با کلیک روی «حذف» در تاریخچه‌ی پرداخت، اگه پرداختی اشتباه ثبت شده باشه می‌تونید برش گردونید.",
    "💡 توی بخش «واحدها» می‌تونید وضعیت هر واحد (ساکن/خالی) رو مشخص کنید تا تو تقسیم قبوض لحاظ بشه.",
    "💡 تاریخ‌ها تو کل برنامه به‌صورت شمسی (جلالی) نمایش داده می‌شن.",
    "💡 توی تنظیمات می‌تونید مشخص کنید برنامه هنگام روشن شدن ویندوز خودش اجرا بشه.",
    "💡 برای ثبت سریع قبض، می‌تونید متن قبض رو کپی کنید و برنامه خودش اطلاعاتش (مبلغ، تاریخ، مصرف) رو استخراج می‌کنه.",
    "💡 قبل از ارسال پیامک، می‌تونید موجودی حساب پیامکی‌تون رو از همون بخش پیامک چک کنید.",
    "💡 رمز عبور و اطلاعات ورودتون به‌صورت رمزنگاری‌شده ذخیره می‌شه، نه به‌صورت متن ساده.",
    "💡 هر تغییری رو در صفحه‌ی تنظیمات ذخیره کنید تا برای دفعات بعد هم اعمال بمونه.",
    "💡 می‌تونید نام و آدرس ساختمان رو از بخش تنظیمات هر وقت خواستید ویرایش کنید.",
    "💡 توی «هزینه‌ها»، هر هزینه یه دسته‌بندی داره؛ این کمک می‌کنه بفهمید بیشترین هزینه‌ها کجا میره.",
    "💡 برای هر شارژ می‌تونید یادداشت و توضیحات جداگانه ثبت کنید تا بعداً یادتون بیاد بابت چی بوده.",
    "💡 اعلان‌های داخل برنامه اولویت دارن (عادی، مهم، فوری) تا مهم‌ترین‌ها رو از دست ندید.",
    "💡 اگه یه یادآوری رو انجام دادید، می‌تونید یادداشت رو به‌عنوان «انجام‌شده» علامت بزنید.",
    "💡 خروجی PDF کاربرگ واحد شامل جزئیات کامل شارژها و پرداخت‌های همون واحده.",
    "💡 توی جدول شارژها، وضعیت هر ردیف با رنگ مشخص می‌شه: پرداخت‌شده، ناقص یا معوق.",
    "💡 می‌تونید بازه‌ی زمانی (دوره) گزارش‌ها رو از بالای صفحه تغییر بدید تا فقط همون ماه/سال رو ببینید.",
    "💡 آیکون برنامه (هم پنجره هم کنار ساعت ویندوز) از همون لوگویی که می‌سازید ساخته می‌شه.",
    "💡 برای بستن سریع بدون سؤال، می‌تونید تیک «دیگر پرسیده نشود» رو تو دیالوگ خروج بزنید.",
    "💡 با تغییر رنگ پس‌زمینه و متن لوگو در تنظیمات، پیش‌نمایش بلافاصله آپدیت می‌شه.",
    "💡 برای واحدهای خالی، سهم قبض به‌صورت منصفانه بین بقیه‌ی واحدهای ساکن تقسیم می‌شه.",
    "💡 می‌تونید مبلغ شارژ ثابت رو هر ماه، بدون تغییر نرخ سایر واحدها، برای یک واحد خاص تغییر بدید.",
    "💡 نوار جست‌وجو بالای جدول‌ها کمک می‌کنه سریع‌تر واحد یا رکورد موردنظرتون رو پیدا کنید.",
    "💡 بکاپ‌های خودکار با تاریخ و ساعت نام‌گذاری می‌شن تا راحت بشه نسخه‌ی موردنظر رو پیدا کرد.",
    "💡 اگه Tray غیرفعال باشه، بستن پنجره با ضربدر مستقیم برنامه رو کامل می‌بنده.",
    "💡 مبلغ‌ها بسته به تنظیم واحد پول، به تومان یا ریال نمایش داده می‌شن.",
]


def get_random_tip():
    return random.choice(APP_TIPS)


from bill_parser import parse_bill_text
from receipt_parser import parse_receipt as parse_receipt_ocr
from database import init_db
from notify import show_windows_notification, send_bulk_notifications
from tray import SystemTrayManager
from services import (
    # ─── اطلاعات پایه ───
    ensure_default_building,
    get_building_info,
    update_building_info,

    # ─── داشبورد ───
    get_dashboard_data,
    get_dashboard_advanced_data,

    # ─── واحدها ───
    list_units_with_debt,
    list_units_basic,
    get_unit_by_id,
    add_unit,
    update_unit,
    delete_unit,

    # ─── شارژ ───
    generate_monthly_charges,
    list_charges,
    delete_charge,
    mark_charge_paid,
    mark_charge_unpaid,
    get_charge_periods_list,
    check_and_auto_generate_charge,
    check_and_apply_late_fees,

    # ─── پرداخت ───
    add_payment,
    list_payments,
    delete_payment,

    # ─── هزینه ───
    add_expense,
    update_expense,
    get_expense_by_id,
    list_expenses,
    list_expenses_by_month,
    delete_expense,

    # ─── قبوض ───
    add_utility_bill,
    list_utility_bills,
    get_consumption_chart_data,
    delete_utility_bill,
    get_last_bill_reading,
    get_bill_stats,
    get_all_bills_summary,
    get_bills_by_period,
    get_bills_summary_by_period,
    check_duplicate_bill,
    calculate_bill_shares,

    # ─── پیامک ───
    send_sms,
    get_sms_credit,

    # ─── تنظیمات ───
    get_setting,
    set_setting,

    # ─── تاریخ و کمکی ───
    to_jalali,
    parse_date,
    MONTHS,
    get_jalali_year,
    get_jalali_month,
    # ─── بکاپ ───
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
    cleanup_old_backups,
    get_backup_stats,
    # ─── کاربر ───
    has_any_user,
    create_user,
    authenticate,
    get_security_question,
    verify_security_answer,
    reset_password,
    change_password,
    update_user_profile,
    get_user_by_id,
    save_remember_me,
    get_remembered_user,
    clear_remember_me,
    validate_password,
    # ─── کاربرگ ───
    get_unit_full_report,
    # ─── نوتیفیکیشن ───
    add_notification,
    list_notifications,
    count_unread_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    delete_notification,
    delete_all_notifications,
    check_and_create_auto_notifications,
    cleanup_old_notifications,
    # ─── داشبورد پیشرفته ───
    get_dashboard_alerts,
    get_financial_calendar,
    get_financial_forecast,
    get_activity_timeline,
    get_financial_trend,
    get_expenses_by_category,
    # ─── یادداشت‌ها ───
    add_note,
    update_note,
    delete_note,
    toggle_note_done,
    toggle_note_pin,
    list_notes,
    get_note_by_id,
    get_notes_stats,
    get_today_notes,
    check_and_create_note_notifications,

    add_utility_bill_new,

    is_startup_enabled,
    enable_startup,
    disable_startup,
)

# ═══════════ دسته‌بندی هزینه‌ها ═══════════

EXPENSE_CATEGORIES = [
    "آب",
    "برق",
    "گاز",
    "نظافت و سرایداری",
    "نگهبانی",
    "تعمیرات و نگهداری",
    "آسانسور",
    "فضای سبز",
    "بیمه و عوارض",
    "لوازم و تجهیزات",
    "هزینه اداری",
    "سایر",
]

# ═══════════ تبدیل اعداد به فارسی ═══════════

PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
}


# ═══════════ سیستم تم (روشن/تاریک) ═══════════

def get_theme_mode():
    """گرفتن حالت تم از تنظیمات"""
    try:
        return get_setting("theme_mode", "light")
    except Exception:
        return "light"


def is_dark_mode():
    """آیا حالت تاریک فعاله؟"""
    return get_theme_mode() == "dark"


def get_theme_colors():
    """رنگ‌های تم بر اساس حالت فعلی"""
    if is_dark_mode():
        return {
            # ─── پس‌زمینه ─────
            "bg_main": "#0F172A",
            "bg_card": "#1E293B",
            "bg_sidebar": "#1E293B",
            "bg_input": "#334155",
            "bg_hover": "#334155",
            "bg_table_header": "#1E40AF",
            "bg_table_row1": "#1E293B",
            "bg_table_row2": "#0F172A",

            # ─── متن ─────
            "text_main": "#F1F5F9",
            "text_secondary": "#CBD5E1",
            "text_muted": "#94A3B8",
            "text_on_primary": "#FFFFFF",

            # ─── حاشیه ─────
            "border": "#334155",
            "divider": "#475569",

            # ─── رنگ‌های اصلی ─────
            "primary": "#3B82F6",
            "success": "#10B981",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "purple": "#A855F7",
            "teal": "#14B8A6",

            # ─── پس‌زمینه‌های رنگی ─────
            "primary_bg": "#1E3A8A",
            "success_bg": "#064E3B",
            "warning_bg": "#78350F",
            "danger_bg": "#7F1D1D",
            "purple_bg": "#581C87",
            "info_bg": "#1E40AF",
            "yellow_bg": "#713F12",

            # ─── سایر ─────
            "shadow": "#000000",
        }
    else:
        return {
            # ─── پس‌زمینه ─────
            "bg_main": "#F5F7FA",
            "bg_card": "#FFFFFF",
            "bg_sidebar": "#EAF1FB",
            "bg_input": "#FFFFFF",
            "bg_hover": "#F5F5F5",
            "bg_table_header": "#1565C0",
            "bg_table_row1": "#FFFFFF",
            "bg_table_row2": "#F8F9FA",

            # ─── متن ─────
            "text_main": "#000000",
            "text_secondary": "#666666",
            "text_muted": "#999999",
            "text_on_primary": "#FFFFFF",

            # ─── حاشیه ─────
            "border": "#E0E0E0",
            "divider": "#CCCCCC",

            # ─── رنگ‌های اصلی ─────
            "primary": "#1565C0",
            "success": "#2E7D32",
            "warning": "#EF6C00",
            "danger": "#C62828",
            "purple": "#9C27B0",
            "teal": "#00838F",

            # ─── پس‌زمینه‌های رنگی ─────
            "primary_bg": "#E3F2FD",
            "success_bg": "#E8F5E9",
            "warning_bg": "#FFF3E0",
            "danger_bg": "#FFEBEE",
            "purple_bg": "#F3E5F5",
            "info_bg": "#E3F2FD",
            "yellow_bg": "#FFF9E6",

            # ─── سایر ─────
            "shadow": "#00000020",
        }


def to_persian(text):
    """تبدیل اعداد انگلیسی به فارسی"""
    if text is None:
        return ""
    text = str(text)
    for en, fa in PERSIAN_DIGITS.items():
        text = text.replace(en, fa)
    return text


def fmt_num(num, decimals=0):
    """فرمت عدد با جداکننده و فارسی‌سازی"""
    if num is None:
        return "۰"
    try:
        if decimals == 0:
            formatted = f"{int(num):,}"
        else:
            formatted = f"{num:,.{decimals}f}"
        return to_persian(formatted)
    except (ValueError, TypeError):
        return "۰"


# ═══════════ سیستم واحد پول ═══════════

def get_currency():
    """
    گرفتن واحد پول از تنظیمات
    خروجی: "toman" یا "rial"
    """
    try:
        return get_setting("currency", "toman")
    except Exception:
        return "toman"


def get_currency_label():
    """
    برچسب واحد پول برای نمایش
    خروجی: "تومان" یا "ریال"
    """
    if get_currency() == "rial":
        return "ریال"
    return "تومان"


def get_currency_short():
    """
    برچسب کوتاه واحد پول
    خروجی: "ت" یا "ر"
    """
    if get_currency() == "rial":
        return "ر"
    return "ت"


def convert_amount(amount):
    """
    تبدیل عدد از تومان (ذخیره‌شده) به واحد نمایش
    - اگه ریال باشه × 10 می‌کنه
    - اگه تومان باشه بدون تغییر
    """
    if amount is None:
        return 0
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return 0

    if get_currency() == "rial":
        return amount * 10
    return amount


def convert_amount_to_toman(amount):
    """
    تبدیل عدد از واحد نمایش به تومان (برای ذخیره)
    - اگه ریال باشه ÷ 10 می‌کنه
    - اگه تومان باشه بدون تغییر
    """
    if amount is None:
        return 0
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return 0

    if get_currency() == "rial":
        return amount / 10
    return amount


def fmt_money(amount, show_unit=True,
              short_unit=False):
    """
    فرمت کامل مبلغ با واحد پول

    Args:
        amount: مبلغ (به تومان ذخیره شده)
        show_unit: نمایش واحد پول
        short_unit: استفاده از فرم کوتاه (ت/ر)

    مثال‌ها:
        fmt_money(500000) → "500,000 تومان"
        fmt_money(500000, short_unit=True) → "500,000 ت"
        fmt_money(500000, show_unit=False) → "500,000"

    اگه واحد ریال باشه:
        fmt_money(500000) → "5,000,000 ریال"
    """
    if amount is None:
        return "۰"

    converted = convert_amount(amount)
    formatted = fmt_num(converted)

    if not show_unit:
        return formatted

    unit = (
        get_currency_short()
        if short_unit
        else get_currency_label()
    )

    return f"{formatted} {unit}"


def money_label(base_text=""):
    """
    برچسب داینامیک برای فیلدهای مبلغ

    مثال:
        money_label("مبلغ") → "مبلغ (تومان)"
        money_label("موجودی صندوق") → "موجودی صندوق (تومان)"
    """
    unit = get_currency_label()
    if base_text:
        return f"{base_text} ({unit})"
    return f"({unit})"


def money_hint():
    """
    راهنمای فیلد مبلغ (متن hint)
    داینامیک بر اساس واحد فعال
    """
    if get_currency() == "rial":
        return "مثال: 5,000,000"
    return "مثال: 500,000"


def read_amount(field_value):
    """
    خواندن مقدار از فیلد و تبدیل به تومان برای ذخیره

    ورودی: متن فیلد (مثلاً "5,000,000")
    خروجی: عدد به تومان

    اگه واحد ریال باشه، خودکار به تومان تبدیل می‌کنه
    """
    unformatted = unformat_amount(field_value)
    try:
        value = float(unformatted or 0)
    except ValueError:
        value = 0

    # تبدیل به تومان برای ذخیره
    return convert_amount_to_toman(value)


# ═══════════ فرمت خودکار مبلغ ═══════════

def format_amount_input(value):
    """
    فرمت کردن مبلغ با کاما
    مثال: 1500000 → 1,500,000
    """
    if not value:
        return ""

    # حذف کاما و کاراکترهای اضافه
    clean = str(value).replace(",", "").replace(" ", "")

    # فقط اعداد
    clean = "".join(
        c for c in clean if c.isdigit()
    )

    if not clean:
        return ""

    try:
        # فرمت با کاما
        return f"{int(clean):,}"
    except ValueError:
        return value


def unformat_amount(value):
    """حذف کاما از مبلغ برای ذخیره‌سازی"""
    if not value:
        return ""
    return str(value).replace(",", "").replace(" ", "")


def make_amount_field(label, width=200,
                      hint=None,
                      required=True,
                      initial_value=""):
    """ساخت TextField هوشمند برای مبلغ"""

    # اضافه کردن واحد به label
    unit = get_currency_label()
    if unit not in label:
        label = f"{label} ({unit})"

    label_text = f"{label} *" if required else label

    # هینت داینامیک
    if hint is None:
        hint = money_hint()

    # مقدار اولیه
    initial_formatted = ""
    if initial_value:
        # تبدیل از تومان به واحد نمایش
        converted = convert_amount(initial_value)
        initial_formatted = format_amount_input(
            str(int(converted))
        )

    field = ft.TextField(
        label=label_text,
        width=width,
        hint_text=hint,
        text_align=ft.TextAlign.RIGHT,
        value=initial_formatted,
    )

    def on_change_amount(e):
        old_value = field.value or ""
        new_value = format_amount_input(old_value)
        if new_value != old_value:
            field.value = new_value
            field.update()

    field.on_change = on_change_amount
    return field


# ═══════════ کلیپ‌بورد ═══════════

def copy_to_clipboard(page, text):
    """کپی متن به کلیپ‌بورد"""
    if not text:
        return False

    # روش ۱: pyperclip (پایدارترین)
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    except Exception as ex:
        print(f"❌ pyperclip: {ex}")

    # روش ۲: Flet
    try:
        if hasattr(page, 'clipboard'):
            page.clipboard = text
            return True
        elif hasattr(page, 'set_clipboard'):
            page.set_clipboard(text)
            return True
    except Exception as ex:
        print(f"❌ Flet clipboard: {ex}")

    return False


# ═══════════ ساخت لوگو مدرن با PIL ═══════════

def generate_circular_logo(
        text,
        bg_color="#1565C0",
        text_color="white",
        size=1000,
        filename="building_logo.png",
        app_name="ساختمان من",
        font_name="Vazirmatn-Bold.ttf"  # ← تغییر به Vazirmatn
):
    """
    ساخت لوگو با Pillow - پشتیبانی عالی از فارسی
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import arabic_reshaper
        from bidi.algorithm import get_display

        # ─── مسیر فونت‌ها ─────
        # نکته: قبلاً اینجا os.path.join(os.getcwd(), "fonts")
        # بود که روی نسخه‌ی پکیج‌شده (exe) درست کار نمی‌کرد — دقیقاً
        # همون مشکلی که برای فونت اصلیِ رابط کاربری هم داشتیم (فونت‌ها
        # با pyinstaller داخل _internal قرار می‌گیرن، نه کنار خودِ
        # exe). چون fallback این تابع «فونت پیش‌فرض PIL» بود که
        # اصلاً از فارسی پشتیبانی نمی‌کنه، متن روی لوگو یا خالی
        # می‌موند یا کاراکترهای ناخوانا نشون می‌داد. الان از همون
        # تابع مشترک _resolve_fonts_dir() استفاده می‌کنیم.
        fonts_dir = _resolve_fonts_dir()

        # فونت اصلی (برای اسم ساختمان)
        main_font_path = os.path.join(
            fonts_dir, font_name
        )

        # اگه Estedad نبود، fallback به Vazirmatn
        if not os.path.exists(main_font_path):
            main_font_path = os.path.join(
                fonts_dir, "Vazirmatn-Bold.ttf"
            )

        # فونت برای متن بالا (کوچک‌تر)
        top_font_path = os.path.join(
            fonts_dir, "Vazirmatn-Medium.ttf"
        )
        if not os.path.exists(top_font_path):
            top_font_path = main_font_path

        # ─── مسیر خروجی ─────
        logo_dir = os.path.join(
            os.getcwd(), "logos"
        )
        os.makedirs(logo_dir, exist_ok=True)
        logo_path = os.path.join(
            logo_dir, filename
        )

        # ─── تبدیل رنگ HEX به RGB ─────
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(
                int(hex_color[i:i + 2], 16)
                for i in (0, 2, 4)
            )

        bg_rgb = hex_to_rgb(bg_color)
        text_rgb = (
            (255, 255, 255)
            if text_color == "white"
            else (0, 0, 0)
        )

        # ─── آماده سازی متن فارسی ─────
        def prepare_text(txt):
            if not txt:
                return ""
            try:
                reshaped = arabic_reshaper.reshape(
                    txt
                )
                return get_display(reshaped)
            except Exception as ex:
                print(f"⚠️ خطای reshaper: {ex}")
                return txt

        text = str(text or "ساختمان").strip()
        app_name = str(app_name or "").strip()

        display_app_name = prepare_text(app_name)
        display_text = prepare_text(text)

        # ─── ساخت تصویر با گوشه‌های گرد ─────
        # تصویر با پس‌زمینه شفاف
        img = Image.new(
            'RGBA',
            (size, size),
            (0, 0, 0, 0)
        )
        draw = ImageDraw.Draw(img)

        # مربع با گوشه‌های گرد
        corner_radius = int(size * 0.08)
        draw.rounded_rectangle(
            [(0, 0), (size, size)],
            radius=corner_radius,
            fill=bg_rgb,
        )

        # ═══════════ خط آسمان ساختمان‌ها (Skyline) ═══════════
        try:
            import random

            # لایه جدا برای skyline
            skyline_layer = Image.new(
                'RGBA',
                (size, size),
                (0, 0, 0, 0)
            )
            skyline_draw = ImageDraw.Draw(
                skyline_layer
            )

            # ─── تنظیمات ─────
            # ساختمان‌ها از کف لوگو شروع می‌شن
            baseline_y = size  # کاملاً پایین

            # کل عرض لوگو رو پوشش می‌ده
            start_x = 0
            end_x = size
            total_width = end_x - start_x

            # تعداد ساختمان‌ها کمتر → عرض بیشتر
            num_buildings = 12

            # عرض هر ساختمان
            building_width = total_width // num_buildings

            # ─── ارتفاع‌های متنوع (کوتاه و بلند) ─────
            heights_pattern = [
                0.11, 0.19, 0.29, 0.15, 0.25,
                0.32, 0.17, 0.26, 0.13, 0.21, 0.16, 0.11,
            ]

            # ─── رسم ساختمان‌ها ─────
            building_color = text_rgb + (100,)  # نیمه شفاف

            # رنگ پنجره‌های زرد (چراغ روشن)
            yellow_light = (255, 220, 100, 240)
            # رنگ پنجره‌های خاموش (رنگ متن)
            off_light = text_rgb + (180,)

            random.seed(42)  # ثابت باشه

            for i in range(num_buildings):
                x = start_x + (i * building_width)
                height = int(size * heights_pattern[i])

                # فاصله ۲ پیکسل بین ساختمان‌ها
                gap = 3

                # ساختمان (مستطیل)
                building_rect = [
                    (x + gap, baseline_y - height),
                    (
                        x + building_width - gap,
                        baseline_y
                    )
                ]
                skyline_draw.rectangle(
                    building_rect,
                    fill=building_color,
                )

                # ─── پنجره‌ها ─────
                if height > int(size * 0.10):
                    window_size = max(
                        6, int(size * 0.015)
                    )

                    # فاصله بین پنجره‌ها
                    padding_top = int(size * 0.02)
                    padding_side = int(
                        building_width * 0.20
                    )

                    # فضای قابل استفاده برای پنجره‌ها
                    usable_height = (
                            height - padding_top - 10
                    )
                    usable_width = (
                            building_width -
                            (2 * padding_side)
                    )

                    # تعداد ردیف و ستون
                    row_spacing = window_size * 2
                    col_spacing = window_size * 2

                    num_rows = usable_height // row_spacing
                    num_cols = max(
                        2,
                        usable_width // col_spacing
                    )

                    # رسم پنجره‌ها
                    for row in range(num_rows):
                        for col in range(num_cols):
                            wx = (
                                    x + padding_side
                                    + (col * col_spacing)
                            )
                            wy = (
                                    baseline_y - height
                                    + padding_top
                                    + (row * row_spacing)
                            )

                            # تصادفی: زرد یا خاموش
                            # حدوداً 40% پنجره‌ها روشن
                            is_lit = (
                                    random.random() < 0.4
                            )

                            window_color = (
                                yellow_light
                                if is_lit
                                else off_light
                            )

                            skyline_draw.rectangle(
                                [
                                    (wx, wy),
                                    (
                                        wx + window_size,
                                        wy + window_size
                                    )
                                ],
                                fill=window_color,
                            )

            # ─── چسباندن روی لوگو ─────
            img = Image.alpha_composite(
                img, skyline_layer
            )
            draw = ImageDraw.Draw(img)

        except Exception as ex:
            print(f"⚠️ خطای skyline: {ex}")
            import traceback
            traceback.print_exc()
        # ─── فونت متن بالا (نام برنامه) ─────
        top_font_size = int(size * 0.12)
        try:
            top_font = ImageFont.truetype(
                top_font_path, top_font_size
            )
        except Exception:
            top_font = ImageFont.load_default()

        # ─── فونت متن اصلی (اسم ساختمان) ─────
        text_len = len(text)
        if text_len <= 4:
            main_font_size = int(size * 0.3)  # ← بزرگ‌تر
        elif text_len <= 8:
            main_font_size = int(size * 0.24)
        elif text_len <= 12:
            main_font_size = int(size * 0.18)
        elif text_len <= 18:
            main_font_size = int(size * 0.13)
        else:
            main_font_size = int(size * 0.1)

        # استفاده از فونت ضخیم‌تر برای متن اصلی
        bold_font_path = os.path.join(
            fonts_dir, "Vazirmatn-ExtraBold.ttf"
        )
        if not os.path.exists(bold_font_path):
            bold_font_path = main_font_path

        try:
            main_font = ImageFont.truetype(
                bold_font_path, main_font_size
            )
        except Exception:
            main_font = ImageFont.load_default()
        # ─── رسم متن بالا (نام برنامه) ─────
        if app_name:
            # محاسبه عرض متن برای وسط‌چین
            bbox = draw.textbbox(
                (0, 0),
                display_app_name,
                font=top_font
            )
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (size - text_width) // 2
            y = int(size * 0.24)

            draw.text(
                (x, y),
                display_app_name,
                font=top_font,
                fill=text_rgb + (230,),
            )

        # ─── رسم خط جدا کننده ─────
        line_y = int(size * 0.43)  # ← کمی پایین‌تر
        line_start = int(size * 0.08)  # ← بلندتر (چپ‌تر)
        line_end = int(size * 0.9)  # ← بلندتر (راست‌تر)
        line_color = text_rgb + (180,)  # ← کمی پررنگ‌تر

        draw.line(
            [
                (line_start, line_y),
                (line_end, line_y)
            ],
            fill=line_color,
            width=4,  # ← ضخیم‌تر
        )

        # نقطه‌های تزئینی
        dot_radius = int(size * 0.012)  # ← نسبی، بزرگ‌تر
        draw.ellipse(
            [
                (line_start - dot_radius,
                 line_y - dot_radius),
                (line_start + dot_radius,
                 line_y + dot_radius)
            ],
            fill=line_color,
        )
        draw.ellipse(
            [
                (line_end - dot_radius,
                 line_y - dot_radius),
                (line_end + dot_radius,
                 line_y + dot_radius)
            ],
            fill=line_color,
        )
        # ─── رسم متن اصلی (اسم ساختمان) ─────
        bbox = draw.textbbox(
            (0, 0),
            display_text,
            font=main_font
        )
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2
        y = int(size * 0.45)

        draw.text(
            (x, y),
            display_text,
            font=main_font,
            fill=text_rgb,
        )

        # ─── ذخیره ─────
        img.save(logo_path, 'PNG')

        return logo_path

    except ImportError as ex:
        print(f"❌ کتابخانه نصب نیست: {ex}")
        print(
            "دستور نصب:\n"
            "pip install Pillow arabic-reshaper "
            "python-bidi"
        )
        return None
    except Exception as ex:
        print(f"❌ خطای ساخت لوگو: {ex}")
        import traceback
        traceback.print_exc()
        return None


def get_logo_path():
    """گرفتن مسیر لوگو ذخیره شده"""
    logo_path = os.path.join(
        os.getcwd(), "logos", "building_logo.png"
    )
    if os.path.exists(logo_path):
        return logo_path
    return None


def _read_image_base64(path):
    """
    خواندن فایل تصویر و تبدیل به base64.

    نکته: قبلاً برای جلوگیری از کش شدن لوگو، یک query string
    مثل ?v=123 به انتهای مسیر فایل اضافه می‌شد (مثل
    "building_logo.png?v=123"). این ترفند فقط برای آدرس‌های وب
    معنی داره؛ برای مسیر فایل روی دیسک باعث می‌شد فایلی با همون
    اسم عجیب (که اصلاً وجود نداره) جستجو بشه و لود لوگو همیشه
    شکست بخوره. به‌جاش محتوای واقعی فایل رو می‌خونیم و به شکل
    base64 می‌دیم؛ هم مشکل مسیر رفع می‌شه، هم چون هر بار محتوای
    واقعی و به‌روز فایل خونده می‌شه، دیگه نیازی به cache-buster
    نیست.
    """
    try:
        with open(path, "rb") as f:
            import base64
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as ex:
        print(f"⚠️ خطا در خواندن فایل لوگو: {ex}")
        return None


def get_logo_or_default():
    """
    برگرداندن مسیر لوگو یا ساخت لوگو پیش‌فرض
    اگه لوگو وجود نداره، یه لوگو با تنظیمات فعلی می‌سازه
    """
    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        return logo_path

    # اگه لوگو نبود، بساز
    try:
        from services import (
            get_building_info,
            get_setting,
        )
        info = get_building_info()
        bg_color = get_setting(
            "logo_bg_color", "#1565C0"
        )
        text_color = get_setting(
            "logo_text_color", "white"
        )
        logo_path = generate_circular_logo(
            text=info["name"],
            bg_color=bg_color,
            text_color=text_color,
        )
        return logo_path
    except Exception as ex:
        print(f"⚠️ خطای ساخت لوگو پیش‌فرض: {ex}")
        return None


def build_logo_image(width=180, height=180, fallback_icon_size=None):
    """
    ساخت ویجت تصویر لوگو با استفاده مستقیم از فایل PNG
    """
    logo_path = get_logo_or_default()

    if logo_path and os.path.exists(logo_path):
        b64 = _read_image_base64(logo_path)
        if b64:
            return ft.Image(
                src=b64,
                width=width,
                height=height,
                fit=ft.BoxFit.CONTAIN,
                error_content=ft.Icon(
                    ft.Icons.APARTMENT,
                    size=fallback_icon_size or int(width * 0.7),
                    color=get_theme_colors()["primary"],
                ),
            )

    # حالت fallback
    theme = get_theme_colors()
    return ft.Icon(
        ft.Icons.APARTMENT,
        size=fallback_icon_size or int(width * 0.7),
        color=theme["primary"],
    )


# ═══════════ صفحه لودینگ ═══════════

def create_loading_screen(page):
    """
    صفحه لودینگ با انیمیشن Pulse روی لوگو
    """
    # گرفتن رنگ‌های تم
    theme = get_theme_colors()
    BG_MAIN = theme["bg_main"]
    BG_CARD = theme["bg_card"]
    P = theme["primary"]
    TEXT_SECONDARY = theme["text_secondary"]
    TEXT_MUTED = theme["text_muted"]

    logo_path = get_logo_or_default()

    # لوگو
    if logo_path and os.path.exists(logo_path):
        logo_widget = ft.Image(
            src=logo_path,
            width=200,
            height=200,
        )
    else:
        logo_widget = ft.Icon(
            ft.Icons.APARTMENT,
            size=150,
            color=P,
        )

    # کانتینر لوگو با انیمیشن
    logo_container = ft.Container(
        content=logo_widget,
        width=250,
        height=250,
        alignment=ft.Alignment.CENTER,
        animate_scale=ft.Animation(
            800,
            ft.AnimationCurve.EASE_IN_OUT,
        ),
        scale=1.0,
        border_radius=10,  # ← اضافه شد (نصف عرض لوگو)
        clip_behavior=ft.ClipBehavior.HARD_EDGE,  # ← اضافه شد
    )

    # متن لودینگ
    loading_text = ft.Text(
        "در حال بارگذاری...",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=P,
    )

    # نقاط چشمک‌زن
    dots_text = ft.Text(
        "●",
        size=20,
        color=P,
        animate_opacity=ft.Animation(
            500,
            ft.AnimationCurve.EASE_IN_OUT,
        ),
        opacity=1.0,
    )

    # ─── انیمیشن Pulse ─────
    def pulse_animation():
        import time
        import threading

        def animate():
            while True:
                try:
                    # بزرگ
                    logo_container.scale = 1.15
                    logo_container.update()
                    time.sleep(0.8)

                    # کوچیک
                    logo_container.scale = 1.0
                    logo_container.update()
                    time.sleep(0.8)

                    # نقاط چشمک‌زن
                    dots_text.opacity = 0.3
                    dots_text.update()
                    time.sleep(0.3)
                    dots_text.opacity = 1.0
                    dots_text.update()
                except Exception:
                    break

        thread = threading.Thread(
            target=animate, daemon=True
        )
        thread.start()

    # صفحه لودینگ
    loading_view = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,  # ← تغییر
        content=ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                logo_container,
                ft.Container(expand=True),
            ]),
            ft.Container(height=30),
            ft.Row([
                ft.Container(expand=True),
                loading_text,
                ft.Container(width=8),
                dots_text,
                ft.Container(expand=True),
            ]),
            ft.Container(height=20),
            ft.Row([
                ft.Container(expand=True),
                ft.ProgressBar(
                    width=300,
                    color=P,
                    bgcolor=theme["bg_input"],  # ← تغییر
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                ft.Text(
                    "© مدیریت ساختمان",
                    size=12,
                    color=TEXT_MUTED,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=20),
        ], spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return loading_view, pulse_animation


# ═══════════ صفحه لودینگ ═══════════

def show_loading_screen(page, duration=2.5, message="خوش آمدید"):
    """
    نمایش صفحه لودینگ - نسخه درست
    """
    import time

    # گرفتن رنگ‌های تم
    theme = get_theme_colors()
    BG_MAIN = theme["bg_main"]
    BG_CARD = theme["bg_card"]
    P = theme["primary"]
    TEXT_SECONDARY = theme["text_secondary"]
    TEXT_MUTED = theme["text_muted"]

    logo_path = get_logo_or_default()

    if logo_path and os.path.exists(logo_path):
        logo_widget = ft.Image(
            src=logo_path,
            width=280,
            height=280,
        )
    else:
        logo_widget = ft.Icon(
            ft.Icons.APARTMENT,
            size=180,
            color=P,
        )

    try:
        info = get_building_info()
        building_name = info["name"]
    except Exception:
        building_name = "ساختمان من"

    loading_view = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,  # ← تغییر
        content=ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                logo_widget,
                ft.Container(expand=True),
            ]),
            ft.Container(height=30),
            ft.Row([
                ft.Container(expand=True),
                ft.Text(
                    message,
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=P,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=10),
            ft.Row([
                ft.Container(expand=True),
                ft.Text(
                    building_name,
                    size=18,
                    color=TEXT_SECONDARY,  # ← تغییر
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=30),
            ft.Row([
                ft.Container(expand=True),
                ft.ProgressRing(
                    color=P,
                    width=45,
                    height=45,
                    stroke_width=4,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=15),
            ft.Row([
                ft.Container(expand=True),
                ft.Text(
                    "در حال بارگذاری...",
                    size=13,
                    color=TEXT_MUTED,  # ← تغییر
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                ft.Text(
                    "© سیستم مدیریت ساختمان",
                    size=11,
                    color=TEXT_MUTED,  # ← تغییر
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=20),
        ], spacing=0),
    )

    # ⭐ نمایش صفحه
    page.controls.clear()
    page.add(loading_view)
    page.update()

    # ⭐ صبر
    time.sleep(duration)

    # پاک کردن
    page.controls.clear()
    page.update()


def show_mini_loading(page, duration=1.5):
    """
    لودینگ کوتاه بین جابجایی صفحات
    """
    theme = get_theme_colors()
    BG_MAIN = theme["bg_main"]
    P = theme["primary"]

    logo_path = get_logo_or_default()

    if logo_path and os.path.exists(logo_path):
        b64 = _read_image_base64(logo_path)
    else:
        b64 = None

    if b64:
        logo_widget = ft.Image(
            src=b64,
            width=150,
            height=150,
            fit=ft.BoxFit.CONTAIN,
            error_content=ft.Icon(
                ft.Icons.APARTMENT, size=100, color=P
            ),
        )
    else:
        logo_widget = ft.Icon(ft.Icons.APARTMENT, size=100, color=P)

    # ─── کانتینر بدون گرد کردن ───
    logo_container = ft.Container(
        content=logo_widget,
        width=150,
        height=150,
        border_radius=10,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    mini_loading = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,
        content=ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                logo_container,
                ft.Container(expand=True),
            ]),
            ft.Container(height=20),
            ft.Row([
                ft.Container(expand=True),
                ft.ProgressRing(
                    color=P,
                    width=35,
                    height=35,
                    stroke_width=3,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=20),
            ft.Container(
                width=500,
                padding=ft.Padding(left=40, right=40, top=0, bottom=0),
                content=ft.Text(
                    get_random_tip(),
                    size=13,
                    color=theme["text_secondary"],
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
            ft.Container(expand=True),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    return mini_loading


def build_register_screen(
        page, on_success, P="#1565C0",
        S="#2E7D32", W="#EF6C00", D="#C62828"
):
    """
    صفحه ثبت‌نام اولیه (وقتی هنوز کاربری نداریم) - سازگار با حالت تاریک/روشن
    """
    # ═══════ گرفتن رنگ‌های تم ═══════
    theme = get_theme_colors()
    P = theme["primary"]
    S = theme["success"]
    W = theme["warning"]
    D = theme["danger"]
    BG_MAIN = theme["bg_main"]
    BG_CARD = theme["bg_card"]
    TEXT_MAIN = theme["text_main"]
    TEXT_SECONDARY = theme["text_secondary"]
    TEXT_MUTED = theme["text_muted"]

    logo_path = get_logo_or_default()

    if logo_path and os.path.exists(logo_path):
        b64 = _read_image_base64(logo_path)
    else:
        b64 = None

    if b64:
        logo_widget = ft.Image(
            src=b64,
            width=150,
            height=150,
            fit=ft.BoxFit.CONTAIN,
            border_radius=10,  # ← اضافه شد (نصف عرض لوگو)
            error_content=ft.Icon(
                ft.Icons.APARTMENT, size=120, color=P
            ),
        )
    else:
        logo_widget = ft.Icon(
            ft.Icons.APARTMENT,
            size=120,
            color=P,
        )

    # فیلدها
    username_field = ft.TextField(
        label="نام کاربری *",
        width=350,
        hint_text="فقط حروف انگلیسی، اعداد و _",
        prefix_icon=ft.Icons.PERSON,
    )

    full_name_field = ft.TextField(
        label="نام و نام خانوادگی",
        width=350,
        prefix_icon=ft.Icons.BADGE,
    )

    password_field = ft.TextField(
        label="رمز عبور *",
        width=350,
        password=True,
        can_reveal_password=True,
        hint_text="حداقل 8 کاراکتر شامل حرف و عدد",
        prefix_icon=ft.Icons.LOCK,
    )

    password_confirm_field = ft.TextField(
        label="تکرار رمز عبور *",
        width=350,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )

    # سوال امنیتی
    SECURITY_QUESTIONS = [
        "نام مادرتان چیست؟",
        "نام اولین معلمتان چیست؟",
        "نام حیوان خانگی محبوبتان چیست؟",
        "شهر محل تولدتان کجاست؟",
        "نام بهترین دوست دوران کودکی‌تان؟",
        "غذای مورد علاقه شما چیست؟",
        "نام کتاب مورد علاقه شما؟",
    ]

    security_question_dd = ft.Dropdown(
        label="سوال امنیتی *",
        width=350,
        value=SECURITY_QUESTIONS[0],
        options=[
            ft.dropdown.Option(text=q)
            for q in SECURITY_QUESTIONS
        ]
    )

    security_answer_field = ft.TextField(
        label="پاسخ سوال امنیتی *",
        width=350,
        hint_text="این پاسخ رو حتماً به یاد داشته باشید!",
        prefix_icon=ft.Icons.QUESTION_ANSWER,
    )

    # پیام خطا/موفقیت
    message_text = ft.Text(
        "", size=13, color=D,
    )

    def on_password_change(e):
        # وقتی کاربر شروع به تایپ می‌کند، چشم را فعال کن
        if password_field.value:
            password_field.can_reveal_password = True
            page.update()

    password_field.on_change = on_password_change

    def on_register(e):
        message_text.value = ""
        message_text.update()

        # بررسی تکرار رمز
        if password_field.value != password_confirm_field.value:
            message_text.value = "❌ رمز و تکرار آن یکسان نیستند."
            message_text.color = D
            message_text.update()
            return

        try:
            create_user(
                username=username_field.value,
                password=password_field.value,
                full_name=full_name_field.value,
                security_question=security_question_dd.value,
                security_answer=security_answer_field.value,
                role="admin",
            )

            message_text.value = "✅ حساب کاربری با موفقیت ساخته شد!"
            message_text.color = S
            message_text.update()

            # ─── بعد از ثبت‌نام، لاگین خودکار ───
            async def auto_login_after_register():
                await asyncio.sleep(1.0)
                result = authenticate(username_field.value, password_field.value)
                if result["success"]:
                    on_success(result["user"])
                else:
                    message_text.value = f"❌ خطا در ورود خودکار: {result['message']}"
                    message_text.color = D
                    message_text.update()

            asyncio.create_task(auto_login_after_register())

        except ValueError as ex:
            message_text.value = f"❌ {ex}"
            message_text.color = D
            message_text.update()
        except Exception as ex:
            message_text.value = f"❌ خطا: {ex}"
            message_text.color = D
            message_text.update()

    register_view = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,  # ← تغییر
        content=ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                ft.Container(
                    width=450,
                    bgcolor=BG_CARD,  # ← تغییر
                    border_radius=20,
                    padding=30,
                    content=ft.Column([
                        # لوگو
                        ft.Row([
                            ft.Container(expand=True),
                            logo_widget,
                            ft.Container(expand=True),
                        ]),
                        ft.Container(height=10),

                        # عنوان
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Text(
                                "🎉 خوش آمدید!",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=P,
                            ),
                            ft.Container(expand=True),
                        ]),
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Text(
                                "برای شروع، حساب مدیر بسازید",
                                size=13,
                                color=TEXT_SECONDARY,  # ← تغییر
                            ),
                            ft.Container(expand=True),
                        ]),
                        ft.Container(height=15),

                        # فیلدها
                        username_field,
                        full_name_field,
                        password_field,
                        password_confirm_field,
                        security_question_dd,
                        security_answer_field,

                        ft.Container(height=10),

                        # پیام
                        ft.Row([
                            ft.Container(expand=True),
                            message_text,
                            ft.Container(expand=True),
                        ]),

                        ft.Container(height=10),

                        # دکمه ثبت‌نام
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Button(
                                "✅ ثبت‌نام و ورود",
                                bgcolor=P,
                                color="white",
                                width=350,
                                height=50,
                                on_click=on_register,
                            ),
                            ft.Container(expand=True),
                        ]),

                    ], spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(expand=True),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )

    return register_view


# ═══════════ صفحه ورود ═══════════

def build_login_screen(
        page, on_success, P="#1565C0",
        S="#2E7D32", W="#EF6C00", D="#C62828"
):
    """صفحه ورود - سازگار با حالت تاریک/روشن"""
    # ═══════ گرفتن رنگ‌های تم ═══════
    theme = get_theme_colors()
    P = theme["primary"]
    S = theme["success"]
    W = theme["warning"]
    D = theme["danger"]
    BG_MAIN = theme["bg_main"]
    BG_CARD = theme["bg_card"]
    TEXT_MAIN = theme["text_main"]
    TEXT_SECONDARY = theme["text_secondary"]
    TEXT_MUTED = theme["text_muted"]

    logo_path = get_logo_or_default()

    if logo_path and os.path.exists(logo_path):
        b64 = _read_image_base64(logo_path)
    else:
        b64 = None

    if b64:
        logo_widget = ft.Image(
            src=b64,
            width=150,
            height=150,
            fit=ft.BoxFit.CONTAIN,
            border_radius=10,
            error_content=ft.Icon(
                ft.Icons.APARTMENT, size=120, color=P
            ),
        )
    else:
        logo_widget = ft.Icon(
            ft.Icons.APARTMENT,
            size=120,
            color=P,
        )

    # ─── فیلدها ─────
    username_field = ft.TextField(
        label="نام کاربری",
        width=350,
        prefix_icon=ft.Icons.PERSON,
        autofocus=True,
    )

    password_field = ft.TextField(
        label="رمز عبور",
        width=350,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
    )

    remember_checkbox = ft.Checkbox(
        label="مرا به خاطر بسپار",
        value=False,
    )

    message_text = ft.Text(
        "", size=13, color=D,
    )

    # ─── ورود ─────
    def do_login(e):
        message_text.value = ""
        message_text.update()

        try:
            result = authenticate(
                username_field.value,
                password_field.value,
            )

            if result["success"]:
                user = result["user"]

                if remember_checkbox.value:
                    save_remember_me(user["id"],
                                     password_field.value)  # ← رمز را ذخیره کن (رمزنگاری داخل تابع انجام می‌شود)

                else:
                    clear_remember_me()

                message_text.value = f"✅ خوش آمدید {user['full_name'] or user['username']}"
                message_text.color = S
                message_text.update()

                # ─── اجرای on_success با تاخیر ───
                async def do_login_success():
                    await asyncio.sleep(0.5)
                    on_success(user)

                asyncio.create_task(do_login_success())

            else:
                message_text.value = f"❌ {result['message']}"
                message_text.color = D
                message_text.update()

        except Exception as ex:
            message_text.value = f"❌ خطا: {ex}"
            message_text.color = D
            message_text.update()

    password_field.on_submit = do_login
    username_field.on_submit = lambda e: password_field.focus()

    # ─── فراموشی رمز ─────
    def show_forgot_password(e):
        show_forgot_dialog(
            page, P=P, S=S, W=W, D=D
        )

    # ─── چک remembered user ─────
    remembered_data = get_remembered_user()
    if remembered_data and remembered_data.get("user"):
        user = remembered_data["user"]
        username_field.value = user["username"]
        remember_checkbox.value = True
        if remembered_data.get("password"):
            password_field.value = remembered_data["password"]
            password_field.can_reveal_password = False  # ← غیرفعال کردن چشم
    login_view = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,  # ← تغییر
        content=ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                ft.Container(
                    width=450,
                    bgcolor=BG_CARD,  # ← تغییر
                    border_radius=20,
                    padding=30,
                    content=ft.Column([
                        # لوگو
                        ft.Row([
                            ft.Container(expand=True),
                            logo_widget,
                            ft.Container(expand=True),
                        ]),
                        ft.Container(height=10),

                        # عنوان
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Text(
                                "🔐 ورود به سیستم",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=P,
                            ),
                            ft.Container(expand=True),
                        ]),
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Text(
                                "لطفاً وارد حساب خود شوید",
                                size=13,
                                color=TEXT_SECONDARY,  # ← تغییر
                            ),
                            ft.Container(expand=True),
                        ]),
                        ft.Container(height=20),

                        # فیلدها
                        username_field,
                        password_field,

                        # مرا به خاطر بسپار
                        ft.Row([
                            remember_checkbox,
                            ft.Container(expand=True),
                            ft.TextButton(
                                "🔑 فراموشی رمز؟",
                                on_click=show_forgot_password,
                            ),
                        ], width=350),

                        # پیام
                        ft.Row([
                            ft.Container(expand=True),
                            message_text,
                            ft.Container(expand=True),
                        ]),

                        ft.Container(height=10),

                        # دکمه ورود
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Button(
                                "🚪 ورود",
                                bgcolor=P,
                                color="white",
                                width=350,
                                height=50,
                                on_click=do_login,
                            ),
                            ft.Container(expand=True),
                        ]),

                    ], spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(expand=True),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )

    return login_view


# ═══════════ دیالوگ فراموشی رمز ═══════════

def show_forgot_dialog(
        page, P="#1565C0", S="#2E7D32",
        W="#EF6C00", D="#C62828"
):
    """دیالوگ بازیابی رمز با سوال امنیتی"""

    # مرحله 1: نام کاربری
    username_input = ft.TextField(
        label="نام کاربری",
        width=350,
        autofocus=True,
    )

    # مرحله 2: سوال + پاسخ
    question_text = ft.Text(
        "", size=14, weight=ft.FontWeight.BOLD
    )
    answer_input = ft.TextField(
        label="پاسخ",
        width=350,
        password=True,
        can_reveal_password=True,
    )

    # مرحله 3: رمز جدید
    new_password_input = ft.TextField(
        label="رمز جدید",
        width=350,
        password=True,
        can_reveal_password=True,
        hint_text="حداقل 8 کاراکتر شامل حرف و عدد",
    )
    new_password_confirm = ft.TextField(
        label="تکرار رمز جدید",
        width=350,
        password=True,
        can_reveal_password=True,
    )

    msg_text = ft.Text("", size=13)

    # ─── محتواهای مراحل ─────
    step1_content = ft.Column([
        ft.Text(
            "🔑 بازیابی رمز عبور",
            size=18, weight=ft.FontWeight.BOLD
        ),
        ft.Text(
            "نام کاربری خود را وارد کنید:",
            size=13, color="#666"
        ),
        username_input,
        msg_text,
    ], tight=True, spacing=10)

    step2_content = ft.Column([
        ft.Text(
            "🤔 سوال امنیتی",
            size=18, weight=ft.FontWeight.BOLD
        ),
        question_text,
        answer_input,
        msg_text,
    ], tight=True, spacing=10)

    step3_content = ft.Column([
        ft.Text(
            "🔒 رمز جدید",
            size=18, weight=ft.FontWeight.BOLD
        ),
        ft.Text(
            "رمز جدید خود را انتخاب کنید:",
            size=13, color="#666"
        ),
        new_password_input,
        new_password_confirm,
        msg_text,
    ], tight=True, spacing=10)

    state = {"step": 1, "username": ""}

    # ─── ساخت دیالوگ ─────
    dlg = ft.AlertDialog(
        modal=True,
        content=ft.Container(
            width=400,
            content=step1_content,
        ),
        actions=[],
    )

    def close_dlg(e):
        dlg.open = False
        page.update()

    def next_step(e):
        msg_text.value = ""
        msg_text.update()

        if state["step"] == 1:
            # چک نام کاربری
            uname = username_input.value.strip()
            if not uname:
                msg_text.value = "❌ نام کاربری الزامی است."
                msg_text.color = D
                msg_text.update()
                return

            result = get_security_question(uname)
            if not result["success"]:
                msg_text.value = f"❌ {result['message']}"
                msg_text.color = D
                msg_text.update()
                return

            state["username"] = uname
            question_text.value = (
                f"❓ {result['question']}"
            )

            # رفتن به مرحله 2
            state["step"] = 2
            dlg.content = ft.Container(
                width=400, content=step2_content
            )
            page.update()

        elif state["step"] == 2:
            # چک پاسخ
            answer = answer_input.value.strip()
            if not answer:
                msg_text.value = "❌ پاسخ الزامی است."
                msg_text.color = D
                msg_text.update()
                return

            result = verify_security_answer(
                state["username"], answer
            )
            if not result["success"]:
                msg_text.value = f"❌ {result['message']}"
                msg_text.color = D
                msg_text.update()
                return

            # رفتن به مرحله 3
            state["step"] = 3
            dlg.content = ft.Container(
                width=400, content=step3_content
            )
            page.update()

        elif state["step"] == 3:
            # ریست رمز
            new_pwd = new_password_input.value
            new_pwd_confirm = (
                new_password_confirm.value
            )

            if new_pwd != new_pwd_confirm:
                msg_text.value = (
                    "❌ رمز و تکرار آن یکسان نیستند."
                )
                msg_text.color = D
                msg_text.update()
                return

            try:
                reset_password(
                    state["username"], new_pwd
                )
                msg_text.value = (
                    "✅ رمز با موفقیت تغییر کرد. حالا وارد شوید."
                )
                msg_text.color = S
                msg_text.update()

                import threading
                import time

                def auto_close():
                    time.sleep(2)

                    async def _do_close():
                        dlg.open = False
                        page.update()

                    # نکته: مثل باگ منوی Tray، این تابع روی یک ترد
                    # جداگانه اجرا می‌شه، پس آپدیت مستقیم کنترل‌ها از
                    # اینجا توی نسخه‌ی جدید flet کار نمی‌کنه؛ باید از
                    # طریق page.run_task به event loop اصلی فرستاده بشه.
                    try:
                        page.run_task(_do_close)
                    except Exception as ex:
                        print(f"⚠️ خطا در بستن خودکار دیالوگ: {ex}")

                threading.Thread(
                    target=auto_close, daemon=True
                ).start()

            except ValueError as ex:
                msg_text.value = f"❌ {ex}"
                msg_text.color = D
                msg_text.update()
            except Exception as ex:
                msg_text.value = f"❌ خطا: {ex}"
                msg_text.color = D
                msg_text.update()

    dlg.actions = [
        ft.Button(
            "بعدی ➡️",
            bgcolor=P, color="white",
            on_click=next_step,
        ),
        ft.TextButton(
            "انصراف", on_click=close_dlg,
        ),
    ]

    if dlg not in page.overlay:
        page.overlay.append(dlg)
    dlg.open = True
    page.update()


# ═══════════ Override اعداد فارسی ═══════════


_original_text_init = ft.Text.__init__


def _persian_text_init(self, *args, **kwargs):
    """اعمال خودکار اعداد فارسی روی همه Text ها"""
    # اگه value یا first argument یه string حاوی عدد هست
    if args and isinstance(args[0], str):
        args = (to_persian(args[0]),) + args[1:]

    if 'value' in kwargs and isinstance(
            kwargs['value'], str
    ):
        kwargs['value'] = to_persian(kwargs['value'])

    _original_text_init(self, *args, **kwargs)


# اعمال override
ft.Text.__init__ = _persian_text_init

# ═══════════ رفع مشکل Dropdown (نمایش text فارسی) ═══════════

_original_dropdown_option_init = ft.dropdown.Option.__init__

def _fixed_dropdown_option_init(self, key=None, text=None, **kwargs):
    """رفع مشکل Flet: اگه هم key و هم text بده، text رو نمایش بده"""
    _original_dropdown_option_init(self, key=key, text=text, **kwargs)

ft.dropdown.Option.__init__ = _fixed_dropdown_option_init

# ═══════════ تنظیمات فونت ═══════════

def _resolve_fonts_dir():
    """
    پیدا کردن مسیر واقعیِ پوشه‌ی fonts.

    نکته: توی حالت توسعه (python app.py)، فونت‌ها کنار خودِ
    app.py هستن، پس os.getcwd() درست جواب می‌ده. ولی توی نسخه‌ی
    پکیج‌شده با pyinstaller (build جدید، 6.x به بعد)، فایل‌هایی
    که با --add-data اضافه می‌شن دیگه مستقیم کنار exe نیستن؛
    داخل یه پوشه‌ی فرعی به اسم _internal قرار می‌گیرن. sys._MEIPASS
    دقیقاً همون مسیر واقعیِ فایل‌های bundle‌شده رو می‌ده (چه
    _internal باشه چه هر جای دیگه)، پس اول اونو چک می‌کنیم.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled = os.path.join(sys._MEIPASS, "fonts")
        if os.path.isdir(bundled):
            return bundled
    return os.path.join(os.getcwd(), "fonts")


_fonts_dir = _resolve_fonts_dir()

FONTS = {}

_font_files = {
    "Vazirmatn": "Vazirmatn-Regular.ttf",
    "Vazirmatn-Bold": "Vazirmatn-Bold.ttf",
    "Vazirmatn-Light": "Vazirmatn-Light.ttf",
    "Vazirmatn-Medium": "Vazirmatn-Medium.ttf",
    "Vazirmatn-SemiBold": "Vazirmatn-SemiBold.ttf",
    "Vazirmatn-ExtraBold": "Vazirmatn-ExtraBold.ttf",
}

# نکته: نسخه‌ی قبلی این کامنت اشتباه بود. رجیستر فونت با مسیر
# نسبی + assets_dir توی نسخه‌ی فعلی Flet یه باگ شناخته‌شده و حل‌
# نشده‌ست (issue #5425 در ریپوی رسمی Flet) — یعنی اصلاً کار
# نمی‌کنه، فارغ از این‌که کد ما چی باشه. برای همین برگشتیم به
# مسیر مطلق دیسک، که قبلاً هم توی حالت dev درست کار می‌کرد.
# اگه روی نسخه‌ی پکیج‌شده هنوز فونت درست نبود، مشکل جای دیگه‌ایه
# (احتمالاً پوشه‌ی کاری/working directory هنگام اجرا از میانبر)
# نه این خط.
for font_name, file_name in _font_files.items():
    font_path = os.path.join(_fonts_dir, file_name)
    if os.path.exists(font_path):
        FONTS[font_name] = font_path

DEFAULT_FONT = (
    "Vazirmatn" if "Vazirmatn" in FONTS
    else "Tahoma"
)

print(f"✅ فونت‌های بارگذاری شده: {list(FONTS.keys())}")
print(f"📁 مسیر فونت‌ها: {_fonts_dir}")
print(f"🎨 فونت پیش‌فرض: {DEFAULT_FONT}")


def get_icons_dir():
    """
    مسیر پوشه‌ی ذخیره‌ی آیکون‌های ساخته‌شده (ico).

    قبلاً فایل‌های آیکون (app_icon.ico و icon_<timestamp>.ico)
    مستقیم وسط پوشه‌ی اصلی پروژه ذخیره می‌شدن که شلوغ و نامرتب بود.
    الان همه‌شون داخل logos/icon ذخیره می‌شن.
    """
    d = os.path.join(os.getcwd(), "logos", "icon")
    os.makedirs(d, exist_ok=True)
    return d


def convert_logo_to_icon(logo_path=None, ico_path=None):
    """
    تبدیل لوگوی PNG به آیکون ICO برای ویندوز

    Args:
        logo_path: مسیر فایل PNG (اختیاری)
        ico_path: مسیر خروجی ICO (اختیاری)
    """
    try:
        from PIL import Image
        import os

        if logo_path is None:
            logo_path = os.path.join("logos", "building_logo.png")
        if ico_path is None:
            ico_path = os.path.join(get_icons_dir(), "app_icon.ico")

        if not os.path.exists(logo_path):
            print(f"ℹ️ لوگو وجود ندارد: {logo_path}")
            return False

        img = Image.open(logo_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # ذخیره با سایزهای استاندارد
        img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"✅ آیکون ساخته شد: {ico_path}")
        return True
    except Exception as ex:
        print(f"❌ خطا در ساخت آیکون: {ex}")
        return False


async def main(page: ft.Page):
    # ─── متغیر برای ذخیره کاربر فعلی ───
    current_user = {"id": None, "username": None, "full_name": None}
    # ═══════════ متغیر برای نگه داشتن task فعلی ═══════════
    current_nav_task = {"task": None}
    # ردیابی صفحه‌ی فعلی، تا بشه بعد از تغییر واحد پول/تم همون صفحه
    # رو با رنگ‌ها/مقادیر جدید دوباره ساخت (بدون ری‌استارت برنامه)
    current_page_builder = {"builder": None}
    # ═══════════ تنظیمات اولیه ═══════════
    page.title = "مدیریت ساختمان"
    page.rtl = True
    page.window.width = 1400
    page.window.height = 850
    page.window.min_width = 1200
    page.window.min_height = 700
    await page.window.center()  # ← در نسخه جدید flet این یک تابع async هست
    page.padding = 0

    # ═══════════ اعمال تم ═══════════
    THEME = get_theme_colors()

    if is_dark_mode():
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    page.bgcolor = THEME["bg_main"]

    # ═══════════ بکاپ خودکار هنگام بستن ═══════════
    def make_backup_on_exit():
        """ساخت بکاپ هنگام خروج"""
        try:
            print("🔄 در حال ساخت بکاپ خروج...")
            result = create_backup(auto=True)
            if result["success"]:
                print(
                    f"✅ بکاپ خودکار ساخته شد: "
                    f"{result.get('filename')}"
                )

            deleted = cleanup_old_backups(days=30)
            if deleted > 0:
                print(
                    f"🗑️ {deleted} بکاپ قدیمی حذف شد"
                )
        except Exception as ex:
            print(f"❌ خطای بکاپ خروج: {ex}")

    # ثبت تابع برای اجرا هنگام خروج
    import atexit
    atexit.register(make_backup_on_exit)
    # اعمال فونت
    if FONTS:
        page.fonts = FONTS
        page.theme = ft.Theme(
            font_family=DEFAULT_FONT,
        )
        page.dark_theme = ft.Theme(
            font_family=DEFAULT_FONT,
        )
    else:
        page.theme = ft.Theme(
            font_family="Tahoma",
        )

    # ═══════════ راه‌اندازی دیتابیس ═══════════
    init_db()
    ensure_default_building()

    # ─── بازیابی آیکون ذخیره‌شده ───
    try:
        saved_icon = get_setting("current_icon_path", "")
        if saved_icon and os.path.exists(saved_icon):
            page.window.icon = saved_icon
            print(f"✅ آیکون بازیابی شد: {saved_icon}")
        else:
            # اگر آیکون ذخیره‌شده وجود نداشت، از لوگوی پیش‌فرض استفاده کن
            ico_path = os.path.join(get_icons_dir(), "app_icon.ico")
            if os.path.exists(ico_path):
                page.window.icon = ico_path
                print(f"✅ آیکون پیش‌فرض بارگذاری شد: {ico_path}")
    except Exception as ex:
        print(f"⚠️ خطا در بازیابی آیکون: {ex}")

    # ⭐ اضافه کردن ستون related_expense_id به دیتابیس
    try:
        from sqlalchemy import text
        from database import engine
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE utility_bills "
                "ADD COLUMN related_expense_id INTEGER"
            ))
            conn.commit()
            print("✅ ستون related_expense_id اضافه شد")
    except Exception:
        pass  # اگه ستون قبلاً وجود داره، طبیعیه

    # ═══════════ چک صدور خودکار شارژ ═══════════
    auto_result = check_and_auto_generate_charge()
    if auto_result:
        print("=" * 50)
        print(
            f"✅ شارژ خودکار صادر شد: "
            f"{auto_result['period']}"
        )
        print(
            f"   تعداد: {auto_result['count']} واحد"
        )
        if auto_result.get('due_date'):
            print(
                f"   سررسید: {auto_result['due_date']}"
            )
        print("=" * 50)

    # ═══════════ اعمال جریمه دیرکرد ═══════════
    late_result = check_and_apply_late_fees()
    if late_result:
        print(
            f"⚠️ جریمه دیرکرد اعمال شد: "
            f"{late_result['count']} شارژ"
        )
    # ═══════════ چک نوتیفیکیشن‌های خودکار ═══════════
    try:
        notif_result = check_and_create_auto_notifications()
        if notif_result["count"] > 0:
            print(
                f"🔔 {notif_result['count']} نوتیفیکیشن جدید"
            )

        # پاکسازی قدیمی‌ها
        cleanup_old_notifications(days=30)
    except Exception as ex:
        print(f"❌ خطای نوتیفیکیشن: {ex}")

    # ═══════════ چک یادآوری‌های یادداشت ═══════════
    try:
        note_notifs = check_and_create_note_notifications()
        note_notifs_count = (
            note_notifs.get("count", 0)
            if isinstance(note_notifs, dict) else note_notifs
        )
        if note_notifs_count > 0:
            print(
                f"📝 {note_notifs_count} یادآوری یادداشت"
            )
    except Exception as ex:
        print(f"❌ خطای یادآوری یادداشت: {ex}")
    # ═══════════ رنگ‌های اصلی (از تم) ═══════════
    P = THEME["primary"]  # آبی
    S = THEME["success"]  # سبز
    W = THEME["warning"]  # نارنجی
    D = THEME["danger"]  # قرمز

    # رنگ‌های اضافی برای استفاده در صفحات
    BG_MAIN = THEME["bg_main"]
    BG_CARD = THEME["bg_card"]
    BG_SIDEBAR = THEME["bg_sidebar"]
    TEXT_MAIN = THEME["text_main"]
    TEXT_SECONDARY = THEME["text_secondary"]

    content_area = ft.Container(
        expand=True,
        padding=20,
    )

    # ───── پیام ─────
    def msg(text, color=S):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, color="white"),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    # ───── کارت آمار ─────
    def scard(title, value, color):
        return ft.Container(
            width=220, padding=16, border_radius=14,
            bgcolor="white",
            content=ft.Column([
                ft.Text(title, size=13, color="#666"),
                ft.Text(
                    str(value), size=22,
                    weight=ft.FontWeight.BOLD, color=color
                ),
            ], spacing=6),
        )

    def sc(status):
        if status == "تسویه": return S
        if status == "ناقص": return W
        return D

    # ───── validation ─────
    def validate(fields):
        """
        fields: list of (TextField_or_Dropdown, label, required)
        return True اگه همه ok بودن
        """
        ok = True
        first_invalid = None
        for ctrl, label, required in fields:
            val = ""
            if isinstance(ctrl, ft.TextField):
                val = ctrl.value or ""
            elif isinstance(ctrl, ft.Dropdown):
                val = ctrl.value or ""
            elif hasattr(ctrl, 'text_field'):
                val = ctrl.text_field.value or ""

            if required and not str(val).strip():
                if isinstance(ctrl, ft.TextField):
                    ctrl.error_text = f"«{label}» الزامی است"
                    ctrl.border_color = D
                elif isinstance(ctrl, ft.Dropdown):
                    # نکته: قبلاً برای دراپ‌داون خالی هیچ خطایی نشون
                    # داده نمی‌شد؛ کاربر دکمه‌ی ذخیره رو می‌زد، هیچ
                    # اتفاقی نمی‌افتاد و هیچ سرنخی هم نداشت چرا.
                    ctrl.error_text = f"«{label}» الزامی است"
                elif hasattr(ctrl, 'text_field'):
                    ctrl.text_field.error_text = (
                        f"«{label}» الزامی است"
                    )
                    ctrl.text_field.border_color = D
                if first_invalid is None:
                    first_invalid = ctrl
                ok = False
            else:
                if isinstance(ctrl, ft.TextField):
                    ctrl.error_text = None
                    ctrl.border_color = None
                elif isinstance(ctrl, ft.Dropdown):
                    ctrl.error_text = None
                elif hasattr(ctrl, 'text_field'):
                    ctrl.text_field.error_text = None
                    ctrl.text_field.border_color = None

        page.update()

        if first_invalid is not None:
            try:
                if isinstance(first_invalid, ft.TextField):
                    first_invalid.focus()
                elif hasattr(first_invalid, 'text_field'):
                    first_invalid.text_field.focus()
                page.update()
            except Exception:
                pass

        return ok

    def clear_errors(fields):
        for ctrl, _, _ in fields:
            try:
                if isinstance(ctrl, ft.TextField):
                    ctrl.error_text = None
                    ctrl.border_color = None
                elif hasattr(ctrl, 'text_field'):
                    ctrl.text_field.error_text = None
                    ctrl.text_field.border_color = None
            except Exception:
                pass

    # ───── تقویم شمسی ─────
    def get_today_jalali():
        j = jdatetime.date.today()
        return f"{j.year}/{j.month:02d}/{j.day:02d}"

    def jalali_date_picker(on_select, init_value=None):
        if init_value:
            try:
                parts = init_value.split("/")
                init_y = int(parts[0])
                init_m = int(parts[1])
                init_d = int(parts[2])
            except Exception:
                j = jdatetime.date.today()
                init_y, init_m, init_d = (
                    j.year, j.month, j.day
                )
        else:
            j = jdatetime.date.today()
            init_y, init_m, init_d = j.year, j.month, j.day

        # ─── سال ─────
        year_dd = ft.Dropdown(
            label="سال",
            width=110,
            value=str(init_y),
            options=[
                ft.dropdown.Option(text=str(y))
                for y in range(init_y - 10, init_y + 11)
            ]
        )

        # ─── ماه ─────
        month_dd = ft.Dropdown(
            label="ماه",
            width=140,
            value=MONTHS[init_m],
            options=[
                ft.dropdown.Option(text=MONTHS[i])
                for i in range(1, 13)
            ]
        )

        # ─── روز ─────
        day_dd = ft.Dropdown(
            label="روز",
            width=100,
            value=str(init_d),
            options=[
                ft.dropdown.Option(text=str(d))
                for d in range(1, 32)
            ]
        )

        def on_confirm(e):
            try:
                y = int(year_dd.value)
                m = MONTHS.index(month_dd.value)
                d = int(day_dd.value)
                jd = jdatetime.date(y, m, d)
                text = f"{y}/{m:02d}/{d:02d}"
                on_select(text, jd.togregorian())
                dlg.open = False
                page.update()
            except Exception as ex:
                msg(f"تاریخ نادرست: {ex}", D)

        def on_cancel(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "📅 انتخاب تاریخ شمسی",
                weight=ft.FontWeight.BOLD,
                size=16,
            ),
            content=ft.Container(
                width=420,
                height=200,
                padding=10,
                content=ft.Column([
                    ft.Container(height=10),
                    ft.Row(
                        [year_dd, month_dd, day_dd],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=15),
                    ft.Text(
                        "💡 راهنما: سال، ماه و روز را انتخاب کنید",
                        size=11,
                        color="#666",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ),
            actions=[
                ft.Button(
                    "✅ تایید",
                    bgcolor=S,
                    color="white",
                    on_click=on_confirm,
                ),
                ft.TextButton(
                    "❌ انصراف",
                    on_click=on_cancel,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return dlg

    def date_field_with_picker(label, width=200, default_today=True):
        today = get_today_jalali() if default_today else ""
        tf = ft.TextField(
            label=label,
            width=width - 50,
            hint_text="1404/04/15",
            value=today,
            read_only=False,  # ← اجازه تایپ دستی هم بده
        )

        def on_pick(e):
            def on_select(text, greg):
                tf.value = text
                tf.data = greg
                tf.error_text = None
                tf.border_color = None
                page.update()

            dlg = jalali_date_picker(on_select, tf.value)
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()

        btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=on_pick,
            tooltip="انتخاب تاریخ"
        )
        row = ft.Row([tf, btn], spacing=0, width=width)
        row.text_field = tf
        return row

    def period_picker():
        j_year = get_jalali_year()

        # نکته: بازه‌ی سال قبلاً ثابت (۵± سال) بود. حالا سال‌هایی که
        # واقعاً توشون شارژ صادر شده رو هم اضافه می‌کنیم تا اگه چند
        # سال متوالی از برنامه استفاده بشه (حتی خارج از این بازه‌ی
        # پیش‌فرض)، انتخابشون از دراپ‌داون هم امکان‌پذیر بمونه.
        existing_years = set()
        try:
            for p in get_charge_periods_list():
                parts = str(p).rsplit(" ", 1)
                if len(parts) == 2 and parts[1].strip().isdigit():
                    existing_years.add(int(parts[1].strip()))
        except Exception:
            pass
        year_range = set(range(j_year - 5, j_year + 6)) | existing_years
        year_options_list = sorted(year_range, reverse=True)

        year_dd = ft.Dropdown(
            label="سال", width=100, value=str(j_year),
            options=[
                ft.dropdown.Option(text=str(y))
                for y in year_options_list
            ]
        )
        month_dd = ft.Dropdown(
            label="ماه", width=140,
            value=MONTHS[get_jalali_month()],
            options=[
                ft.dropdown.Option(text=MONTHS[i])
                for i in range(1, 13)
            ]
        )

        def get_period():
            # ماه به صورت متن فارسی هست، مستقیم استفاده کن
            return f"{month_dd.value} {year_dd.value}"

        def set_period(month_name, year_str):
            month_dd.value = month_name
            year_dd.value = year_str

        row = ft.Row([year_dd, month_dd], spacing=6)
        row.get_period = get_period
        row.set_period = set_period
        row.year_dd = year_dd
        row.month_dd = month_dd
        return row

    # ═══════════ توابع مدیریت کاربر ═══════════

    def on_login_success(user):
        """پس از ورود موفق، لودینگ کوچک و سپس داشبورد"""
        current_user["id"] = user["id"]
        current_user["username"] = user["username"]
        current_user["full_name"] = user["full_name"]

        # ─── ⭐ بازسازی لوگوی سایدبار با لوگوی جدید ───
        try:
            new_logo_widget = build_logo_image(width=180, height=180)
            sidebar_logo.content = new_logo_widget
        except Exception as ex:
            print(f"⚠️ خطا در بازسازی لوگوی سایدبار: {ex}")

        # ─── نمایش لودینگ کوچک ───
        mini_loading = show_mini_loading(page)
        page.controls.clear()
        page.add(mini_loading)
        page.update()

        # ─── بعد از 1.5 ثانیه، صفحه اصلی ───
        # ⭐ ۲ ثانیه‌ی اضافه (طبق درخواست) به مدت این لودینگ هم اضافه شد
        async def show_main_after_delay():
            await asyncio.sleep(1.5 + 2)
            page.controls.clear()
            page.add(main_layout)
            update_user_display()
            page.update()

        asyncio.create_task(show_main_after_delay())

    def show_login_or_register():
        """نمایش صفحه ورود یا ثبت‌نام بر اساس وجود کاربر"""
        if has_any_user():
            login_view = build_login_screen(page, on_login_success)
            page.controls.clear()
            page.add(login_view)
        else:
            register_view = build_register_screen(page, on_login_success)
            page.controls.clear()
            page.add(register_view)
        page.update()  # ← فقط page.update()

    def update_user_display():
        """بروزرسانی نام کاربر در سایدبار"""
        try:
            # پیدا کردن المان نمایش نام کاربر در سایدبار
            for control in side.content.controls:
                if isinstance(control, ft.Container) and control.content and isinstance(control.content, ft.Text):
                    if control.content.value.startswith("👤"):
                        control.content.value = f"👤 {current_user['full_name'] or current_user['username'] or 'کاربر'}"
                        page.update()
                        break
        except Exception as ex:
            print(f"خطا در بروزرسانی نام کاربر: {ex}")

    def logout_click(e):
        """خروج از حساب و بازگشت به صفحه ورود"""
        clear_remember_me()
        current_user["id"] = None
        current_user["username"] = None
        current_user["full_name"] = None
        show_login_or_register()  # این تابع sync است و خودش page.update() را انجام می‌دهد
        # نیازی به await نیست

    # ═══════════ ذخیره و نمایش تصاویر ═══════════

    def _sanitize_filename(name):
        """حذف کاراکترهای غیرمجاز از نام فایل"""
        if not name:
            return "file"
        import re as _re
        name = _re.sub(r'[<>:"/\\|?*]', '', name)
        name = _re.sub(r'\s+', ' ', name).strip()
        if len(name) > 80:
            name = name[:80]
        return name or "file"

    def save_uploaded_image(src_path, category, date_obj=None,
                            custom_name=None):
        """
        ذخیره تصویر در پوشه‌ی ماهانه با نام دلخواه.

        Args:
            src_path: مسیر فایل مبدأ
            category: "invoices" یا "receipts"
            date_obj: date میلادی (اختیاری)
            custom_name: نام دلخواه فایل (بدون پسوند)
        """
        if not src_path or not os.path.exists(src_path):
            return ""
        try:
            base_dir = os.path.join(
                os.getcwd(), "uploads", category
            )

            if date_obj is not None:
                try:
                    j = jdatetime.date.fromgregorian(date=date_obj)
                    month_label = f"{MONTHS[j.month]} {j.year}"
                    base_dir = os.path.join(base_dir, month_label)
                except Exception as ex:
                    print(f"⚠️ خطای محاسبه ماه: {ex}")

            os.makedirs(base_dir, exist_ok=True)

            ext = os.path.splitext(src_path)[1].lower()
            allowed = ['.png', '.jpg', '.jpeg', '.gif',
                       '.bmp', '.webp']
            if ext not in allowed:
                ext = '.png'

            # ⭐ اگه نام دلخواه داده شده، ازش استفاده کن
            if custom_name:
                safe_name = _sanitize_filename(custom_name)
            else:
                from datetime import datetime as _dt
                timestamp = _dt.now().strftime("%Y%m%d_%H%M%S_%f")
                safe_name = f"img_{timestamp}"

            dest = os.path.join(base_dir, safe_name + ext)

            # اگه فایل با همین نام وجود داشت، شماره اضافه کن
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(
                    base_dir, f"{safe_name}_{counter}{ext}"
                )
                counter += 1

            shutil.copy2(src_path, dest)
            return dest
        except Exception as ex:
            print(f"❌ خطای ذخیره تصویر: {ex}")
            import traceback
            traceback.print_exc()
            return ""

    def image_to_base64_src(path):
        """تبدیل فایل تصویر به data URI برای Flet"""
        if not path or not os.path.exists(path):
            return ""
        try:
            import base64 as _b64
            ext = os.path.splitext(path)[1].lower().lstrip('.')
            if ext == 'jpg':
                ext = 'jpeg'
            if ext not in ['png', 'jpeg', 'gif', 'bmp', 'webp']:
                ext = 'png'
            with open(path, "rb") as f:
                b64 = _b64.b64encode(f.read()).decode('utf-8')
            return f"data:image/{ext};base64,{b64}"
        except Exception as ex:
            print(f"❌ خطای base64: {ex}")
            return ""

    def build_image_uploader(page, label="📎 انتخاب تصویر",
                             theme=None, initial_path="",
                             on_upload=None):
        """آپلودر تصویر برای Flet 0.86+ (با callback اختیاری بعد از آپلود)"""
        selected_path = [initial_path or ""]
        preview = ft.Image(
            width=100, height=100,
            fit=ft.BoxFit.COVER,
            visible=bool(initial_path),
            src=image_to_base64_src(initial_path)
            if initial_path else "",
        )
        status_text = ft.Text(
            os.path.basename(initial_path)
            if initial_path else "تصویری انتخاب نشده",
            size=10,
            color=(theme.get("success") if initial_path
                   else theme.get("text_muted", "#888"))
            if theme else "#888",
        )

        file_picker = ft.FilePicker()

        added_to = "none"
        try:
            if hasattr(page, "services") and page.services is not None:
                if file_picker not in page.services:
                    page.services.append(file_picker)
                added_to = "services"
        except Exception as ex:
            print(f"⚠️ خطای services: {ex}")

        if added_to == "none":
            try:
                page.overlay.append(file_picker)
                added_to = "overlay"
            except Exception as ex:
                print(f"❌ خطای overlay: {ex}")

        async def _do_pick_async():
            try:
                result = await file_picker.pick_files(
                    allow_multiple=False,
                    file_type=ft.FilePickerFileType.IMAGE,
                )

                if result and len(result) > 0:
                    f = result[0]
                    selected_path[0] = f.path
                    preview.src = image_to_base64_src(f.path)
                    preview.visible = True
                    status_text.value = f.name
                    if theme:
                        status_text.color = theme.get("success", "green")
                    page.update()

                    # ⭐ فراخوانی callback بعد از انتخاب موفق
                    if on_upload:
                        try:
                            on_upload(f.path)
                        except Exception as ex:
                            print(f"⚠️ خطای callback upload: {ex}")
                            import traceback
                            traceback.print_exc()
            except Exception as ex:
                print(f"❌ خطا در pick_files: {ex}")
                import traceback
                traceback.print_exc()

        def open_picker(e):
            try:
                page.run_task(_do_pick_async)
            except Exception as ex:
                print(f"❌ خطا در run_task: {ex}")
                import traceback
                traceback.print_exc()

        def clear():
            selected_path[0] = ""
            preview.src = ""
            preview.visible = False
            status_text.value = "تصویری انتخاب نشده"
            if theme:
                status_text.color = theme.get("text_muted", "#888")

        def do_clear(e):
            clear()
            try:
                page.update()
            except Exception:
                pass

        def set_path(p):
            selected_path[0] = p or ""
            if p and os.path.exists(p):
                preview.src = image_to_base64_src(p)
                preview.visible = True
                status_text.value = os.path.basename(p)
                if theme:
                    status_text.color = theme.get("success", "green")
            else:
                clear()

        pick_btn = ft.Button(
            label,
            icon=ft.Icons.UPLOAD_FILE,
            bgcolor=theme.get("primary") if theme else None,
            color="white" if theme else None,
            on_click=open_picker,
            height=36,
        )

        clear_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=(theme.get("danger", "#c00")
                        if theme else "#c00"),
            tooltip="حذف تصویر",
            icon_size=18,
            on_click=do_clear,
        )

        component = ft.Container(
            padding=10,
            border_radius=8,
            bgcolor=theme.get("bg_card") if theme else None,
            content=ft.Column([
                ft.Row([pick_btn, clear_btn]),
                preview,
                status_text,
            ], spacing=6),
        )

        return {
            "component": component,
            "get_path": lambda: selected_path[0] or "",
            "clear": clear,
            "set_path": set_path,
        }

    def show_full_image(page, path):
        """نمایش تصویر در حالت بزرگ"""
        if not path or not os.path.exists(path):
            return
        try:
            b64 = image_to_base64_src(path)
            if not b64:
                return

            dlg = ft.AlertDialog(
                content=ft.Container(
                    width=600, height=600,
                    content=ft.Image(
                        src=b64,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                ),
                actions=[
                    ft.TextButton(
                        "بستن",
                        on_click=lambda e: (
                            setattr(dlg, "open", False),
                            page.update(),
                        ),
                    ),
                ],
            )
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()
        except Exception as ex:
            print(f"❌ خطای نمایش تصویر: {ex}")

    def _info_pair(label, value, color):
        """ردیف label/value برای تاریخچه"""
        return ft.Row([
            ft.Text(label, size=11, color=color,
                    weight=ft.FontWeight.BOLD, width=150),
            ft.Text(str(value), size=11,
                    color=color, selectable=True,
                    expand=True),
        ], spacing=6)
    # ═══════════ داشبورد ═══════════
    def build_dashboard():
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_MAIN = theme["bg_main"]
        BG_CARD = theme["bg_card"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        TEXT_ON_PRIMARY = theme["text_on_primary"]

        d = get_dashboard_data()
        adv = get_dashboard_advanced_data()
        units = list_units_with_debt()
        dbtrs = [u for u in units if u["debt"] > 0]

        alerts = get_dashboard_alerts()
        calendar_events = get_financial_calendar(days=30)
        forecast = get_financial_forecast()
        activities = get_activity_timeline(limit=8)
        trend_data = get_financial_trend(months=9)

        # ─── نمودار دایره‌ای ───
        def build_pie_chart():
            payments = d["payments_total"]
            expenses = d["expenses_total"]
            total = payments + expenses

            if total == 0:
                return ft.Container(
                    width=240, height=240,
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.PIE_CHART_OUTLINE,
                            size=70, color=TEXT_MUTED
                        ),
                        ft.Text(
                            "هنوز داده‌ای نیست",
                            size=13, color=TEXT_MUTED,
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10)
                )

            try:
                import matplotlib.pyplot as plt
                import matplotlib
                from matplotlib import font_manager
                matplotlib.use('Agg')

                # نکته: قبلاً فقط Vazirmatn-Bold ثبت می‌شد و به matplotlib
                # معرفی می‌شد به اسم خانواده‌ی 'Vazirmatn'. چون این فایل
                # فقط وزن Bold (700) رو داره، هر جا matplotlib می‌خواست
                # متن با وزن normal (پیش‌فرض) رسم کنه، فونت normal پیدا
                # نمی‌شد و هشدار "Failed to find font weight normal"
                # می‌داد. الان فونت Regular رو هم اضافه می‌کنیم تا هر دو
                # وزن موجود باشن.
                regular_font_path = os.path.join(
                    _resolve_fonts_dir(), "Vazirmatn-Regular.ttf"
                )
                bold_font_path = os.path.join(
                    _resolve_fonts_dir(), "Vazirmatn-Bold.ttf"
                )

                if os.path.exists(regular_font_path):
                    font_manager.fontManager.addfont(regular_font_path)
                if os.path.exists(bold_font_path):
                    font_manager.fontManager.addfont(bold_font_path)
                if os.path.exists(regular_font_path) or os.path.exists(bold_font_path):
                    plt.rcParams['font.family'] = 'Vazirmatn'

                chart_dir = os.path.join(
                    os.getcwd(), "temp_charts"
                )
                os.makedirs(chart_dir, exist_ok=True)
                chart_path = os.path.join(
                    chart_dir, "pie_chart.png"
                )

                fig, ax = plt.subplots(
                    figsize=(5, 5),
                    subplot_kw=dict(aspect="equal"),
                    facecolor='none'
                )

                sizes = [payments, expenses]
                colors_list = ['#00C853', '#FF6D00']

                def fa_pct(pct):
                    val = f"{pct:.0f}"
                    persian_map = str.maketrans(
                        "0123456789", "۰۱۲۳۴۵۶۷۸۹"
                    )
                    val_fa = val.translate(persian_map)
                    return f"{val_fa}٪"

                wedges, texts, autotexts = ax.pie(
                    sizes,
                    colors=colors_list,
                    autopct=fa_pct,
                    startangle=90,
                    pctdistance=0.72,
                    textprops={
                        'color': 'white',
                        'fontsize': 24,
                        'fontweight': 'bold',
                    },
                    wedgeprops={
                        'linewidth': 0,
                        'antialiased': True,
                    },
                )

                for autotext in autotexts:
                    autotext.set_fontsize(24)
                    autotext.set_fontweight('bold')
                    autotext.set_color('white')

                fig.patch.set_alpha(0)
                ax.set_facecolor('none')

                plt.savefig(
                    chart_path,
                    format='png',
                    bbox_inches='tight',
                    transparent=True,
                    dpi=200,
                    pad_inches=0.1
                )
                plt.close(fig)

                # همون رفع باگ کشِ تصویر که برای نمودار هزینه‌ها هم
                # انجام شد: اسم فایل نمودار ثابته، پس با base64
                # همیشه محتوای تازه نشون داده بشه.
                b64 = _read_image_base64(chart_path)
                if b64:
                    return ft.Image(
                        src=b64,
                        height=350,
                        fit=ft.BoxFit.CONTAIN,
                        expand=True,
                    )
                return ft.Image(
                    src=chart_path,
                    height=350,
                    expand=True,  # ⭐ به جای fit
                )

            except Exception as ex:
                print(f"❌ خطای نمودار: {ex}")
                return ft.Container(
                    width=240, height=240,
                    content=ft.Text(
                        f"خطا: {ex}",
                        color=D, size=11
                    )
                )

        # ─── نمودار خطی روند مالی ───
        def build_trend_chart():
            if not trend_data or all(
                    t["income"] == 0 and t["expense"] == 0
                    for t in trend_data
            ):
                return ft.Container(
                    height=300,
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.SHOW_CHART,
                            size=60, color=TEXT_MUTED
                        ),
                        ft.Text(
                            "داده‌ای برای نمایش نیست",
                            color=TEXT_MUTED, size=13
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10)
                )

            try:
                import matplotlib.pyplot as plt
                import matplotlib
                from matplotlib import font_manager
                matplotlib.use('Agg')

                # نکته: قبلاً فقط Vazirmatn-Bold ثبت می‌شد و به matplotlib
                # معرفی می‌شد به اسم خانواده‌ی 'Vazirmatn'. چون این فایل
                # فقط وزن Bold (700) رو داره، هر جا matplotlib می‌خواست
                # متن با وزن normal (پیش‌فرض) رسم کنه، فونت normal پیدا
                # نمی‌شد و هشدار "Failed to find font weight normal"
                # می‌داد. الان فونت Regular رو هم اضافه می‌کنیم تا هر دو
                # وزن موجود باشن.
                regular_font_path = os.path.join(
                    _resolve_fonts_dir(), "Vazirmatn-Regular.ttf"
                )
                bold_font_path = os.path.join(
                    _resolve_fonts_dir(), "Vazirmatn-Bold.ttf"
                )

                if os.path.exists(regular_font_path):
                    font_manager.fontManager.addfont(regular_font_path)
                if os.path.exists(bold_font_path):
                    font_manager.fontManager.addfont(bold_font_path)
                if os.path.exists(regular_font_path) or os.path.exists(bold_font_path):
                    plt.rcParams['font.family'] = 'Vazirmatn'

                chart_dir = os.path.join(
                    os.getcwd(), "temp_charts"
                )
                os.makedirs(chart_dir, exist_ok=True)
                chart_path = os.path.join(
                    chart_dir, "trend_chart.png"
                )

                months = [t["month"] for t in trend_data]
                incomes = [
                    t["income"] / 1000000
                    for t in trend_data
                ]
                expenses = [
                    t["expense"] / 1000000
                    for t in trend_data
                ]

                fig, ax = plt.subplots(
                    figsize=(18, 4.5),  # ⭐ خیلی عریض‌تر
                    facecolor='none'
                )

                ax.plot(
                    months, incomes,
                    marker='o', linewidth=3.5,
                    markersize=11,
                    color='#00C853',
                    label='درآمد',
                    zorder=3,
                )
                ax.plot(
                    months, expenses,
                    marker='s', linewidth=3.5,
                    markersize=11,
                    color='#FF6D00',
                    label='هزینه',
                    zorder=3,
                )

                ax.fill_between(
                    months, incomes,
                    alpha=0.15, color='#00C853'
                )
                ax.fill_between(
                    months, expenses,
                    alpha=0.15, color='#FF6D00'
                )

                ax.set_facecolor('none')
                fig.patch.set_alpha(0)
                ax.grid(
                    True, alpha=0.2, linestyle='--'
                )
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#999')
                ax.spines['bottom'].set_color('#999')
                ax.tick_params(colors='#666')

                legend = ax.legend(
                    loc='upper left',
                    frameon=False,
                    fontsize=12,
                )
                for text in legend.get_texts():
                    text.set_color('#333')

                plt.tight_layout()
                plt.savefig(
                    chart_path,
                    format='png',
                    bbox_inches='tight',
                    transparent=True,
                    dpi=150,
                )
                plt.close(fig)

                b64 = _read_image_base64(chart_path)
                if b64:
                    return ft.Image(
                        src=b64,
                        height=300,
                        fit=ft.BoxFit.CONTAIN,
                    )
                return ft.Image(
                    src=chart_path,
                    height=300,
                )

            except Exception as ex:
                print(f"❌ خطای نمودار trend: {ex}")
                return ft.Text(
                    f"خطا: {ex}", color=D, size=11
                )

        # ═══════════ سربرگ ═══════════
        today_j = jdatetime.date.today()
        today_str = to_persian(
            today_j.strftime('%d %B %Y')
        )

        header = ft.Container(
            padding=15,
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        "داشبورد",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=P,
                    ),
                    ft.Row([
                        ft.Icon(
                            ft.Icons.CALENDAR_TODAY,
                            size=14, color=TEXT_MUTED
                        ),
                        ft.Text(
                            today_str,
                            size=14, color=TEXT_MUTED,
                        ),
                    ], spacing=5),
                ], spacing=4, expand=True),

                ft.Container(
                    padding=14,
                    bgcolor=BG_CARD,
                    border_radius=30,
                    content=ft.Row([
                        ft.Container(
                            width=40, height=40,
                            border_radius=20,
                            bgcolor=theme["primary_bg"],
                            content=ft.Icon(
                                ft.Icons.APARTMENT,
                                color=P, size=22
                            )
                        ),
                        ft.Column([
                            ft.Text(
                                "ساختمان",
                                size=10, color=TEXT_MUTED
                            ),
                            ft.Text(
                                d["building_name"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=P
                            ),
                        ], spacing=0),
                    ], spacing=10)
                ),
            ])
        )

        # ═══════════ نوار اعلان‌های مهم ═══════════
        alerts_row = ft.Row(spacing=10)

        for alert in alerts:
            if alert["type"] == "danger":
                a_color = D
                a_bg = theme["danger_bg"]
            elif alert["type"] == "warning":
                a_color = W
                a_bg = theme["warning_bg"]
            elif alert["type"] == "success":
                a_color = S
                a_bg = theme["success_bg"]
            else:
                a_color = P
                a_bg = theme["primary_bg"]

            def make_click(action):
                def on_click(e):
                    if action == "units":
                        nav(build_units_page)
                    elif action == "charges":
                        nav(build_charges_page)
                    elif action == "bills":
                        nav(build_bills_page)

                return on_click

            # ⭐ محتوای وسط‌چین با آیکون + متن در یک ردیف
            alert_card = ft.Container(
                expand=True,
                padding=14,
                border_radius=12,
                bgcolor=a_bg,
                ink=True if alert["action"] else False,
                on_click=(
                    make_click(alert["action"])
                    if alert["action"]
                    else None
                ),
                content=ft.Row([
                    ft.Text(alert["icon"], size=22),
                    ft.Column([
                        ft.Text(
                            alert["title"],
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=a_color,
                        ),
                        ft.Text(
                            (
                                fmt_money(alert["value"])
                                if alert["value"]
                                else "کلیک برای مشاهده"
                                if alert["action"]
                                else ""
                            ),
                            size=10,
                            color=TEXT_MUTED,
                        ),
                    ], spacing=2, expand=True),
                ], spacing=10),
            )

            alerts_row.controls.append(alert_card)

        alerts_section = alerts_row

        # ═══════════ کارت آماری ═══════════
        def stat_card(icon, title, value,
                      color, bg_color, subtitle=""):
            return ft.Container(
                padding=20,
                border_radius=18,
                bgcolor=bg_color,
                expand=True,
                content=ft.Column([
                    ft.Container(
                        width=55, height=55,
                        border_radius=16,
                        bgcolor=color,
                        content=ft.Text(
                            icon,
                            size=26,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.Container(height=12),
                    ft.Text(
                        title,
                        size=13,
                        color=TEXT_SECONDARY,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Container(height=6),
                    ft.Text(
                        str(value),
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                    ),
                    ft.Text(
                        subtitle,
                        size=11,
                        color=TEXT_MUTED,
                    ) if subtitle else ft.Container(),
                ], spacing=0)
            )

        # ═══════════ کارت یادداشت‌های امروز ═══════════
        CARD_HEIGHT_1 = 380
        try:
            today_notes = get_today_notes(limit=3)
        except Exception:
            today_notes = []

        CATEGORY_ICONS_NOTES = {
            "کار": "💼", "جلسه": "📅",
            "خرید": "🛒", "تعمیرات": "🔧",
            "شخصی": "👤", "یادآوری": "⏰",
        }

        notes_header = ft.Row([
            ft.Container(
                width=45, height=45,
                border_radius=13,
                bgcolor=W,
                content=ft.Text(
                    "📝", size=22,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
            ft.Column([
                ft.Text(
                    "یادداشت‌ها",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_MAIN,
                ),
                ft.Text(
                    f"{to_persian(str(len(today_notes)))} فعال",
                    size=10, color=TEXT_MUTED,
                ),
            ], spacing=0, expand=True),
        ], spacing=8)

        if not today_notes:
            notes_body = ft.Column([
                ft.Container(expand=True),
                ft.Icon(
                    ft.Icons.NOTE_ALT_OUTLINED,
                    size=35,
                    color=TEXT_MUTED,
                ),
                ft.Text(
                    "یادداشتی موجود نیست",
                    color=TEXT_MUTED,
                    size=11,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(expand=True),
                ft.Button(
                    "➕ افزودن",
                    bgcolor=W,
                    color="white",
                    on_click=lambda e: nav(
                        build_notes_page
                    ),
                    width=180,
                ),
            ], spacing=6, expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER)
        else:
            from datetime import datetime as _dt
            notes_items = ft.Column(
                spacing=5,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

            for note in today_notes:
                icon_n = CATEGORY_ICONS_NOTES.get(
                    note["category"], "📝"
                )

                time_text = ""
                time_color = TEXT_MUTED
                if note["reminder_at"]:
                    try:
                        r = note["reminder_at"]
                        now = _dt.now()
                        if r.date() == now.date():
                            time_text = to_persian(
                                f"امروز {r.hour:02d}:{r.minute:02d}"
                            )
                            time_color = D
                        elif (
                                (r.date() - now.date()).days
                                == 1
                        ):
                            time_text = to_persian(
                                f"فردا {r.hour:02d}:{r.minute:02d}"
                            )
                            time_color = W
                    except Exception:
                        pass

                notes_items.controls.append(
                    ft.Container(
                        bgcolor=BG_CARD,
                        border_radius=8,
                        padding=8,
                        content=ft.Row([
                            ft.Text(icon_n, size=14),
                            ft.Column([
                                ft.Text(
                                    note["title"],
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_MAIN,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    time_text,
                                    size=9,
                                    color=time_color,
                                    weight=ft.FontWeight.BOLD,
                                ) if time_text
                                else ft.Container(),
                            ], spacing=1, expand=True),
                        ], spacing=6),
                    )
                )

            notes_body = ft.Column([
                notes_items,
                ft.Container(
                    padding=ft.Padding(0, 5, 0, 0),
                    content=ft.Row([
                        ft.Container(expand=True),
                        ft.TextButton(
                            "مشاهده همه ⬅",
                            on_click=lambda e: nav(
                                build_notes_page
                            ),
                        ),
                    ]),
                ),
            ], spacing=4, expand=True)

        notes_card = ft.Container(
            expand=3,
            height=CARD_HEIGHT_1,  # ⭐ ارتفاع یکسان با موجودی
            padding=20,
            border_radius=20,
            bgcolor=theme["warning_bg"],
            content=ft.Column([
                notes_header,
                ft.Divider(
                    height=1,
                    color=theme["divider"],
                ),
                notes_body,
            ], spacing=10, expand=True),
        )

        # ═══════════ ردیف بالا (4 کارت آماری) ═══════════
        top_cards = ft.Row([
            stat_card(
                "🏢", "کل واحدها",
                fmt_num(d["total_units"]),
                P, theme["primary_bg"], "واحد"
            ),
            stat_card(
                "⚠️", "بدهکارها",
                fmt_num(d["debtors"]),
                D, theme["danger_bg"], "واحد"
            ),
            stat_card(
                "💸", "کل بدهی",
                fmt_money(
                    d["total_debt"],
                    show_unit=False
                ),
                D, theme["danger_bg"],
                get_currency_label()
            ),
            stat_card(
                "📋", "شارژ صادره",
                fmt_money(
                    d["charges_total"],
                    show_unit=False
                ),
                W, theme["warning_bg"],
                get_currency_label()
            ),
        ], spacing=15)
        # ═══════════ کارت موجودی + نمودار ═══════════
        CARD_HEIGHT_1 = 380

        balance_card = ft.Container(
            expand=6,
            height=CARD_HEIGHT_1,
            bgcolor=BG_CARD,
            border_radius=20,
            padding=25,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=55, height=55,
                        border_radius=16,
                        bgcolor=theme["primary_bg"],
                        content=ft.Icon(
                            ft.Icons.ACCOUNT_BALANCE_WALLET,
                            color=P, size=28
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "موجودی صندوق",
                            size=14, color=TEXT_SECONDARY,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Row([
                            ft.Container(
                                width=8, height=8,
                                border_radius=4,
                                bgcolor=S,
                            ),
                            ft.Text(
                                "لحظه به لحظه",
                                size=11, color=TEXT_MUTED
                            ),
                        ], spacing=5),
                    ], spacing=2),
                ], spacing=12),

                ft.Container(expand=True),

                ft.Row([
                    ft.Text(
                        fmt_money(
                            d["cash_balance"],
                            show_unit=False
                        ),
                        size=42,
                        weight=ft.FontWeight.BOLD,
                        color=P,
                    ),
                    ft.Column([
                        ft.Container(expand=True),
                        ft.Text(
                            get_currency_label(),
                            size=15,
                            color=TEXT_MUTED,
                            weight=ft.FontWeight.W_500,
                        ),
                    ], spacing=0),
                ], spacing=8),

                ft.Container(expand=True),

                ft.Divider(height=1, color=theme["divider"]),
                ft.Container(height=12),

                ft.Row([
                    ft.Container(
                        expand=True,
                        padding=12,
                        border_radius=12,
                        bgcolor=theme["success_bg"],
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    width=10, height=10,
                                    border_radius=5,
                                    bgcolor=S
                                ),
                                ft.Text(
                                    "دریافتی",
                                    size=11, color=TEXT_SECONDARY
                                ),
                            ], spacing=6),
                            ft.Text(
                                fmt_money(
                                    d["payments_total"],
                                    show_unit=False
                                ),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=S
                            ),
                        ], spacing=4)
                    ),
                    ft.Container(
                        expand=True,
                        padding=12,
                        border_radius=12,
                        bgcolor=theme["warning_bg"],
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    width=10, height=10,
                                    border_radius=5,
                                    bgcolor=W
                                ),
                                ft.Text(
                                    "هزینه",
                                    size=11, color=TEXT_SECONDARY
                                ),
                            ], spacing=6),
                            ft.Text(
                                fmt_money(
                                    d["expenses_total"],
                                    show_unit=False
                                ),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=W
                            ),
                        ], spacing=4)
                    ),
                    ft.Container(
                        expand=True,
                        padding=12,
                        border_radius=12,
                        bgcolor=theme["bg_input"],
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    width=10, height=10,
                                    border_radius=5,
                                    bgcolor=TEXT_MUTED
                                ),
                                ft.Text(
                                    "اولیه",
                                    size=11, color=TEXT_SECONDARY
                                ),
                            ], spacing=6),
                            ft.Text(
                                fmt_money(
                                    d["initial_balance"],
                                    show_unit=False
                                ),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_MUTED
                            ),
                        ], spacing=4)
                    ),
                ], spacing=10),
            ], spacing=0)
        )

        chart_card = ft.Container(
            expand=4,
            height=CARD_HEIGHT_1,
            bgcolor=BG_CARD,
            border_radius=20,
            padding=20,
            content=ft.Column([
                # هدر
                ft.Row([
                    ft.Container(
                        width=40, height=40,
                        border_radius=12,
                        bgcolor=theme["purple_bg"],
                        content=ft.Icon(
                            ft.Icons.PIE_CHART,
                            color=theme["purple"], size=22
                        ),
                    ),
                    ft.Text(
                        "نسبت مالی",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN,
                    ),
                ], spacing=10),

                # ⭐ نمودار دقیقاً وسط با استفاده از Container با alignment
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=build_pie_chart(),
                ),

                # لجند پایین
                ft.Row([
                    ft.Row([
                        ft.Container(
                            width=14, height=14,
                            border_radius=4,
                            bgcolor="#00C853"
                        ),
                        ft.Text(
                            "دریافتی",
                            size=12,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_MAIN,
                        ),
                    ], spacing=6),
                    ft.Container(width=20),
                    ft.Row([
                        ft.Container(
                            width=14, height=14,
                            border_radius=4,
                            bgcolor="#FF6D00"
                        ),
                        ft.Text(
                            "هزینه",
                            size=12,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_MAIN,
                        ),
                    ], spacing=6),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=10)
        )

        # ═══════════ پیش‌بینی مالی ═══════════
        forecast_card = ft.Container(
            bgcolor=BG_CARD,
            border_radius=20,
            padding=25,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=50, height=50,
                        border_radius=15,
                        bgcolor=theme["purple_bg"],
                        content=ft.Icon(
                            ft.Icons.TRENDING_UP,
                            color=theme["purple"], size=24
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "پیش‌بینی مالی ماه آینده",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Text(
                            "بر اساس روند ۳۰ روز اخیر",
                            size=11, color=TEXT_MUTED
                        ),
                    ], spacing=2, expand=True),
                ], spacing=12),

                ft.Container(height=15),

                ft.Row([
                    ft.Container(
                        expand=True,
                        padding=15,
                        border_radius=12,
                        bgcolor=theme["success_bg"],
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.TRENDING_UP,
                                    size=16, color=S
                                ),
                                ft.Text(
                                    "درآمد پیش‌بینی",
                                    size=11, color=TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ], spacing=5),
                            ft.Text(
                                fmt_money(
                                    forecast["predicted_income"],
                                    show_unit=False
                                ),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=S
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=2)
                    ),
                    ft.Container(
                        expand=True,
                        padding=15,
                        border_radius=12,
                        bgcolor=theme["warning_bg"],
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.TRENDING_DOWN,
                                    size=16, color=W
                                ),
                                ft.Text(
                                    "هزینه پیش‌بینی",
                                    size=11, color=TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ], spacing=5),
                            ft.Text(
                                fmt_money(
                                    forecast["predicted_expenses"],
                                    show_unit=False
                                ),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=W
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=2)
                    ),
                    ft.Container(
                        expand=True,
                        padding=15,
                        border_radius=12,
                        bgcolor=(
                            theme["success_bg"]
                            if forecast["predicted_balance"] > forecast["current_balance"]
                            else theme["danger_bg"]
                        ),
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.ACCOUNT_BALANCE_WALLET,
                                    size=16,
                                    color=(
                                        S if forecast["predicted_balance"] > forecast["current_balance"]
                                        else D
                                    )
                                ),
                                ft.Text(
                                    "موجودی نهایی",
                                    size=11, color=TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ], spacing=5),
                            ft.Text(
                                fmt_money(
                                    forecast["predicted_balance"],
                                    show_unit=False
                                ),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=(
                                    S if forecast["predicted_balance"] > forecast["current_balance"]
                                    else D
                                )
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=2)
                    ),
                ], spacing=12),
            ], spacing=0)
        )

        # ═══════════ شارژ ماه جاری ═══════════
        pct = adv["current_percent"]
        pct_color = (
            S if pct > 75
            else W if pct > 25
            else D
        )
        pct_bg = (
            theme["success_bg"] if pct > 75
            else theme["warning_bg"] if pct > 25
            else theme["danger_bg"]
        )

        current_charge = ft.Container(
            bgcolor=BG_CARD,
            border_radius=20,
            padding=25,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=50, height=50,
                        border_radius=15,
                        bgcolor=theme["success_bg"],
                        content=ft.Icon(
                            ft.Icons.CALENDAR_MONTH,
                            color=S, size=24
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "وضعیت شارژ ماه جاری",
                            size=13, color=TEXT_SECONDARY
                        ),
                        ft.Text(
                            adv['current_period'],
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                    ], spacing=2, expand=True),
                    ft.Container(
                        padding=10,
                        border_radius=20,
                        bgcolor=pct_bg,
                        content=ft.Row([
                            ft.Icon(
                                (
                                    ft.Icons.CHECK_CIRCLE
                                    if pct == 100
                                    else ft.Icons.TIMER
                                ),
                                color=pct_color,
                                size=16
                            ),
                            ft.Text(
                                f'{to_persian(f"{pct:.0f}")}٪ وصول شده',
                                size=13,
                                color=pct_color,
                                weight=ft.FontWeight.BOLD
                            ),
                        ], spacing=5)
                    ),
                ], spacing=12),

                ft.Container(height=20),

                ft.Row([
                    ft.Container(
                        expand=True,
                        padding=15,
                        border_radius=12,
                        bgcolor=theme["primary_bg"],
                        content=ft.Column([
                            ft.Text(
                                "کل شارژ",
                                size=11, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                fmt_money(
                                    adv["current_total"],
                                    show_unit=False
                                ),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=P
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=2)
                    ),
                    ft.Container(
                        expand=True,
                        padding=15,
                        border_radius=12,
                        bgcolor=theme["success_bg"],
                        content=ft.Column([
                            ft.Text(
                                "پرداخت‌شده",
                                size=11, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                fmt_money(
                                    adv["current_paid"],
                                    show_unit=False
                                ),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=S
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=2)
                    ),
                    ft.Container(
                        expand=True,
                        padding=15,
                        border_radius=12,
                        bgcolor=theme["danger_bg"],
                        content=ft.Column([
                            ft.Text(
                                "معوق",
                                size=11, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                fmt_money(
                                    adv["current_unpaid"],
                                    show_unit=False
                                ),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=D
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=2)
                    ),
                ], spacing=12),

                ft.Container(height=15),

                ft.Column([
                    ft.Row([
                        ft.Text(
                            "پیشرفت وصول:",
                            size=12, color=TEXT_SECONDARY
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            f'{to_persian(f"{pct:.0f}")}٪',
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=pct_color
                        ),
                    ]),
                    ft.Container(height=5),
                    ft.ProgressBar(
                        value=pct / 100,
                        color=pct_color,
                        bgcolor=theme["bg_input"],
                        height=12,
                    ),
                ], spacing=0),
            ], spacing=0)
        )

        # ═══════════ تقویم مالی + تایم لاین ═══════════
        CARD_HEIGHT_3 = 400

        # ─── تقویم ─────
        calendar_col = ft.Column(spacing=6)

        if not calendar_events:
            calendar_body = ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Icon(
                            ft.Icons.EVENT_AVAILABLE,
                            size=60, color=S
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "رویدادی در ۳۰ روز آینده نیست",
                            color=S, size=13,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4),
                    ft.Container(expand=True),
                ]),
                ft.Container(expand=True),
            ], expand=True, spacing=0)
        else:
            for event in calendar_events[:6]:
                d_left = event["days_left"]
                if d_left == 0:
                    day_text = "امروز"
                    day_color = D
                elif d_left <= 3:
                    day_text = f"{to_persian(str(d_left))} روز"
                    day_color = D
                elif d_left <= 7:
                    day_text = f"{to_persian(str(d_left))} روز"
                    day_color = W
                else:
                    day_text = f"{to_persian(str(d_left))} روز"
                    day_color = P

                calendar_col.controls.append(
                    ft.Container(
                        bgcolor=theme["bg_input"],
                        border_radius=10,
                        padding=10,
                        content=ft.Row([
                            ft.Container(
                                width=50, height=50,
                                border_radius=10,
                                bgcolor=BG_CARD,
                                content=ft.Column([
                                    ft.Text(
                                        event["icon"],
                                        size=18,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Text(
                                        day_text,
                                        size=9,
                                        color=day_color,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ], spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.CENTER)
                            ),
                            ft.Column([
                                ft.Text(
                                    event["title"],
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_MAIN,
                                ),
                                ft.Text(
                                    to_jalali(event["date"]),
                                    size=10, color=TEXT_MUTED,
                                ),
                            ], spacing=2, expand=True),
                            ft.Column([
                                ft.Text(
                                    fmt_money(
                                        event["amount"],
                                        show_unit=False
                                    ),
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=day_color,
                                ),
                                ft.Text(
                                    get_currency_label(),
                                    size=9, color=TEXT_MUTED,
                                ),
                            ], spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END),
                        ], spacing=10)
                    )
                )
            calendar_body = ft.Column(
                [calendar_col],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

        calendar_card = ft.Container(
            expand=True,
            height=CARD_HEIGHT_3,
            bgcolor=BG_CARD,
            border_radius=20,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=40, height=40,
                        border_radius=12,
                        bgcolor=theme["primary_bg"],
                        content=ft.Icon(
                            ft.Icons.CALENDAR_MONTH,
                            color=P, size=22
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "تقویم مالی",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Text(
                            "رویدادهای ۳۰ روز آینده",
                            size=11, color=TEXT_MUTED
                        ),
                    ], spacing=2, expand=True),
                    ft.Container(
                        padding=8,
                        border_radius=15,
                        bgcolor=theme["primary_bg"],
                        content=ft.Text(
                            f'{to_persian(str(len(calendar_events)))} رویداد',
                            size=11,
                            color=P,
                            weight=ft.FontWeight.BOLD
                        )
                    ),
                ], spacing=10),
                ft.Divider(height=1, color=theme["divider"]),
                ft.Container(
                    expand=True,
                    content=calendar_body,
                ),
            ], spacing=12)
        )

        # ─── تایم لاین ─────
        timeline_col = ft.Column(spacing=6)

        if not activities:
            timeline_body = ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Icon(
                            ft.Icons.TIMELINE,
                            size=60, color=TEXT_MUTED
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "فعالیتی ثبت نشده",
                            color=TEXT_MUTED, size=13,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4),
                    ft.Container(expand=True),
                ]),
                ft.Container(expand=True),
            ], expand=True, spacing=0)
        else:
            for act in activities:
                color_map = {
                    "success": S,
                    "warning": W,
                    "primary": P,
                    "info": theme["purple"],
                }
                bg_map = {
                    "success": theme["success_bg"],
                    "warning": theme["warning_bg"],
                    "primary": theme["primary_bg"],
                    "info": theme["purple_bg"],
                }
                act_color = color_map.get(
                    act["color"], P
                )
                act_bg = bg_map.get(
                    act["color"], theme["primary_bg"]
                )

                from datetime import datetime
                if act["timestamp"]:
                    delta = (
                            datetime.now() - act["timestamp"]
                    )
                    if delta.days > 0:
                        time_ago = f"{delta.days} روز پیش"
                    elif delta.seconds > 3600:
                        time_ago = (
                            f"{delta.seconds // 3600} ساعت پیش"
                        )
                    elif delta.seconds > 60:
                        time_ago = (
                            f"{delta.seconds // 60} دقیقه پیش"
                        )
                    else:
                        time_ago = "لحظاتی پیش"
                    time_ago = to_persian(time_ago)
                else:
                    time_ago = ""

                timeline_col.controls.append(
                    ft.Container(
                        padding=10,
                        border_radius=10,
                        bgcolor=act_bg,
                        content=ft.Row([
                            ft.Container(
                                width=35, height=35,
                                border_radius=17,
                                bgcolor=BG_CARD,
                                content=ft.Text(
                                    act["icon"],
                                    size=18,
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ),
                            ft.Column([
                                ft.Text(
                                    act["title"],
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=act_color,
                                ),
                                ft.Row([
                                    ft.Text(
                                        act["description"],
                                        size=10,
                                        color=TEXT_MUTED,
                                    ),
                                    ft.Container(expand=True),
                                    ft.Text(
                                        time_ago,
                                        size=9,
                                        color=TEXT_MUTED,
                                    ),
                                ]),
                            ], spacing=2, expand=True),
                            ft.Text(
                                fmt_money(
                                    act["amount"],
                                    show_unit=False
                                ),
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=act_color,
                            ),
                        ], spacing=8)
                    )
                )
            timeline_body = ft.Column(
                [timeline_col],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

        timeline_card = ft.Container(
            expand=True,
            height=CARD_HEIGHT_3,
            bgcolor=BG_CARD,
            border_radius=20,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=40, height=40,
                        border_radius=12,
                        bgcolor=theme["success_bg"],
                        content=ft.Icon(
                            ft.Icons.HISTORY,
                            color=S, size=22
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "فعالیت‌های اخیر",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Text(
                            "تایم لاین آخرین تراکنش‌ها",
                            size=11, color=TEXT_MUTED
                        ),
                    ], spacing=2, expand=True),
                    ft.Container(
                        padding=8,
                        border_radius=15,
                        bgcolor=theme["success_bg"],
                        content=ft.Text(
                            f'{to_persian(str(len(activities)))} فعالیت',
                            size=11,
                            color=S,
                            weight=ft.FontWeight.BOLD
                        )
                    ),
                ], spacing=10),
                ft.Divider(height=1, color=theme["divider"]),
                ft.Container(
                    expand=True,
                    content=timeline_body,
                ),
            ], spacing=12)
        )

        # ═══════════ بدهکارها + هزینه‌ها ═══════════
        CARD_HEIGHT_2 = 420

        dl = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        empty_debtors = False

        if not dbtrs:
            empty_debtors = True
        else:
            for u in dbtrs[:5]:
                dl.controls.append(ft.Container(
                    bgcolor=theme["danger_bg"],
                    border_radius=12,
                    padding=12,
                    content=ft.Row([
                        ft.Container(
                            width=45, height=45,
                            border_radius=22,
                            bgcolor=BG_CARD,
                            content=ft.Text(
                                to_persian(str(u["number"])),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=D,
                                text_align=ft.TextAlign.CENTER,
                            )
                        ),
                        ft.Column([
                            ft.Text(
                                u["resident_name"] or "-",
                                weight=ft.FontWeight.BOLD,
                                size=13,
                                color=TEXT_MAIN,
                            ),
                            ft.Text(
                                f'واحد {to_persian(str(u["number"]))}',
                                size=11, color=TEXT_MUTED
                            ),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(
                                fmt_money(
                                    u["debt"],
                                    show_unit=False
                                ),
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=D
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.END),
                    ], spacing=10)
                ))

            if len(dbtrs) > 5:
                remaining = len(dbtrs) - 5
                dl.controls.append(
                    ft.Container(
                        padding=10,
                        content=ft.Text(
                            f"+ {to_persian(str(remaining))} بدهکار دیگر",
                            size=12, color=TEXT_MUTED,
                            italic=True,
                            text_align=ft.TextAlign.CENTER
                        )
                    )
                )

        if empty_debtors:
            debtors_content_body = ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=64, color=S
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "همه واحدها تسویه هستند",
                            size=15, color=S,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "🎉", size=28,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4),
                    ft.Container(expand=True),
                ]),
                ft.Container(expand=True),
            ], expand=True, spacing=0)
        else:
            debtors_content_body = dl

        debtors_card = ft.Container(
            expand=True,
            height=CARD_HEIGHT_2,
            bgcolor=BG_CARD,
            border_radius=20,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=40, height=40,
                        border_radius=12,
                        bgcolor=theme["danger_bg"],
                        content=ft.Icon(
                            ft.Icons.WARNING_AMBER,
                            color=D, size=22
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "بدهکاران", size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Text(
                            "لیست واحدهای دارای بدهی",
                            size=11, color=TEXT_MUTED
                        ),
                    ], spacing=2, expand=True),
                    ft.Container(
                        padding=8,
                        border_radius=15,
                        bgcolor=theme["danger_bg"],
                        content=ft.Text(
                            f'{to_persian(str(len(dbtrs)))} واحد',
                            size=11,
                            color=D,
                            weight=ft.FontWeight.BOLD
                        )
                    ),
                ], spacing=10),
                ft.Divider(height=1, color=theme["divider"]),
                ft.Container(
                    expand=True,
                    content=debtors_content_body,
                ),
            ], spacing=12)
        )

        exp_col = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        empty_expenses = False

        if not adv["recent_expenses"]:
            empty_expenses = True
        else:
            cat_icons = {
                "آب": "💧", "برق": "⚡", "گاز": "🔥",
                "نظافت و سرایداری": "🧹",
                "نگهبانی": "🛡️",
                "تعمیرات و نگهداری": "🔧",
                "آسانسور": "🛗",
                "فضای سبز": "🌿",
                "بیمه و عوارض": "📋",
                "لوازم و تجهیزات": "🛠️",
                "هزینه اداری": "📎",
                "سایر": "📌",
            }

            for exp in adv["recent_expenses"][:5]:
                icon = cat_icons.get(
                    exp["category"], "📌"
                )
                exp_col.controls.append(ft.Container(
                    bgcolor=theme["warning_bg"],
                    border_radius=12,
                    padding=12,
                    content=ft.Row([
                        ft.Container(
                            width=45, height=45,
                            border_radius=12,
                            bgcolor=BG_CARD,
                            content=ft.Text(
                                icon, size=22,
                                text_align=ft.TextAlign.CENTER
                            )
                        ),
                        ft.Column([
                            ft.Text(
                                exp["title"],
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_MAIN,
                            ),
                            ft.Text(
                                exp["category"],
                                size=11, color=TEXT_MUTED
                            ),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(
                                fmt_money(
                                    exp["amount"],
                                    show_unit=False
                                ),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=W
                            ),
                            ft.Text(
                                get_currency_label(),
                                size=10, color=TEXT_MUTED
                            ),
                        ], spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.END),
                    ], spacing=10)
                ))

        if empty_expenses:
            expenses_content_body = ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            size=64, color=TEXT_MUTED
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "هزینه‌ای ثبت نشده",
                            color=TEXT_MUTED, size=14,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4),
                    ft.Container(expand=True),
                ]),
                ft.Container(expand=True),
            ], expand=True, spacing=0)
        else:
            expenses_content_body = exp_col

        expenses_card = ft.Container(
            expand=True,
            height=CARD_HEIGHT_2,
            bgcolor=BG_CARD,
            border_radius=20,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=40, height=40,
                        border_radius=12,
                        bgcolor=theme["warning_bg"],
                        content=ft.Icon(
                            ft.Icons.RECEIPT,
                            color=W, size=22
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "هزینه‌های اخیر", size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Text(
                            "آخرین هزینه‌های ثبت شده",
                            size=11, color=TEXT_MUTED
                        ),
                    ], spacing=2, expand=True),
                    ft.Container(
                        padding=8,
                        border_radius=15,
                        bgcolor=theme["warning_bg"],
                        content=ft.Text(
                            f'{to_persian(str(len(adv["recent_expenses"])))} مورد',
                            size=11,
                            color=W,
                            weight=ft.FontWeight.BOLD
                        )
                    ),
                ], spacing=10),
                ft.Divider(height=1, color=theme["divider"]),
                ft.Container(
                    expand=True,
                    content=expenses_content_body,
                ),
            ], spacing=12)
        )

        # ═══════════ نمودار خطی روند مالی ═══════════
        trend_chart_card = ft.Container(
            bgcolor=BG_CARD,
            border_radius=20,
            padding=25,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=45, height=45,
                        border_radius=13,
                        bgcolor=theme["primary_bg"],
                        content=ft.Icon(
                            ft.Icons.SHOW_CHART,
                            color=P, size=24
                        ),
                    ),
                    ft.Column([
                        ft.Text(
                            "روند مالی ۶ ماه اخیر",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Text(
                            f"مقایسه درآمد و هزینه (میلیون {get_currency_label()})",
                            size=11, color=TEXT_MUTED
                        ),
                    ], spacing=2),
                ], spacing=10),
                ft.Divider(height=1, color=theme["divider"]),
                ft.Container(height=10),
                # ⭐ Container با alignment برای وسط چین کردن
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=build_trend_chart(),
                ),
            ], spacing=12)
        )

        # ═══════════ چیدمان نهایی ═══════════
        return ft.Column([
            header,
            ft.Container(height=5),
            alerts_section,
            ft.Container(height=15),
            top_cards,
            ft.Container(height=18),
            ft.Row([
                balance_card,
                chart_card,
                notes_card,
            ], spacing=18),
            ft.Container(height=18),
            forecast_card,
            ft.Container(height=18),
            current_charge,
            ft.Container(height=18),
            ft.Row([
                calendar_card,
                timeline_card,
            ], spacing=18),
            ft.Container(height=18),
            ft.Row([
                debtors_card,
                expenses_card,
            ], spacing=18),
            ft.Container(height=18),
            trend_chart_card,
            ft.Container(height=20),
        ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0)

    def build_units_page():
        # ═══════ گرفتن رنگ‌های تم ═══════
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_MAIN = theme["bg_main"]
        BG_CARD = theme["bg_card"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        list_col = ft.Column(spacing=10)
        editing_id = [None]

        # ─── فیلدها ─────
        n = ft.TextField(
            label="شماره واحد *", width=140
        )
        fl = ft.TextField(
            label="طبقه *", width=110
        )
        ar = ft.TextField(
            label="متراژ *", width=110
        )
        pc = ft.TextField(
            label="نفرات *", width=110
        )
        rn = ft.TextField(
            label="نام ساکن *", width=200
        )
        ph = ft.TextField(
            label="موبایل *", width=170,
            hint_text="09123456789"
        )
        rt = ft.Dropdown(
            label="نوع", width=140, value="مالک",
            options=[
                ft.dropdown.Option("مالک"),
                ft.dropdown.Option("مستاجر"),
            ]
        )
        st = ft.Dropdown(
            label="وضعیت", width=140, value="ساکن",
            options=[
                ft.dropdown.Option("ساکن"),
                ft.dropdown.Option("خالی"),
            ]
        )
        nt = ft.TextField(
            label="توضیحات",
            width=350,
            multiline=True,
            min_lines=1,
            max_lines=2,
        )
        save_btn = ft.Button(
            "💾 ذخیره واحد",
            bgcolor=P, color="white"
        )

        required_fields = [
            (n, "شماره واحد", True),
            (fl, "طبقه", True),
            (ar, "متراژ", True),
            (pc, "نفرات", True),
            (rn, "نام ساکن", True),
            (ph, "موبایل", True),
        ]

        def clear():
            editing_id[0] = None
            n.value = ""
            fl.value = ""
            ar.value = ""
            pc.value = ""
            rn.value = ""
            ph.value = ""
            rt.value = "مالک"
            st.value = "ساکن"
            nt.value = ""
            save_btn.text = "💾 ذخیره واحد"
            clear_errors(required_fields)
            page.update()

        def confirm_delete_unit(unit_id, unit_number):
            """دیالوگ تایید حذف واحد."""

            def do_delete(e):
                try:
                    delete_unit(unit_id)
                    dlg.open = False
                    page.update()
                    msg("واحد حذف شد.", W)
                    load()
                except Exception as ex:
                    msg(str(ex), D)

            def close_dlg(e):
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=D, size=26),
                    ft.Text("تایید حذف",
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=380,
                    content=ft.Column([
                        ft.Text(
                            f"آیا از حذف واحد "
                            f"{to_persian(str(unit_number))} "
                            f"مطمئن هستید؟",
                            size=13, color=TEXT_SECONDARY,
                        ),
                        ft.Container(height=4),
                        ft.Text(
                            "⚠️ تمام شارژها و پرداخت‌های این واحد "
                            "نیز حذف خواهند شد.",
                            size=11, color=D,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ], spacing=6),
                ),
                actions=[
                    ft.Button("حذف", bgcolor=D, color="white",
                              on_click=do_delete),
                    ft.TextButton("انصراف", on_click=close_dlg),
                ],
            )
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def load():
            list_col.controls.clear()
            units = list_units_with_debt()

            if not units:
                list_col.controls.append(
                    ft.Container(
                        padding=40,
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.APARTMENT,
                                size=60, color=TEXT_MUTED
                            ),
                            ft.Text(
                                "واحدی ثبت نشده",
                                color=TEXT_MUTED,
                                size=14
                            ),
                        ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8)
                    )
                )
                page.update()
                return

            for u in units:
                # وضعیت رنگ
                if u["status"] == "ساکن":
                    status_color = S
                    status_bg = theme["success_bg"]
                else:
                    status_color = TEXT_MUTED
                    status_bg = theme["bg_input"]

                # بدهی
                has_debt = u["debt"] > 0
                debt_color = D if has_debt else S

                list_col.controls.append(
                    ft.Container(
                        bgcolor=BG_CARD,
                        border_radius=14,
                        padding=15,
                        content=ft.Row([
                            # شماره واحد
                            ft.Container(
                                width=60, height=60,
                                border_radius=15,
                                bgcolor=theme["danger_bg"] if has_debt else theme["primary_bg"],
                                content=ft.Text(
                                    to_persian(
                                        str(u["number"])
                                    ),
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=D if has_debt else P,
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ),
                            # اطلاعات
                            ft.Column([
                                ft.Row([
                                    ft.Text(
                                        u["resident_name"]
                                        or "بدون ساکن",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_MAIN,
                                    ),
                                    ft.Container(
                                        padding=6,
                                        border_radius=10,
                                        bgcolor=status_bg,
                                        content=ft.Text(
                                            u["status"],
                                            size=10,
                                            color=status_color,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    ),
                                    ft.Container(
                                        padding=6,
                                        border_radius=10,
                                        bgcolor=theme["bg_hover"],
                                        content=ft.Text(
                                            u["resident_type"],
                                            size=10,
                                            color=TEXT_SECONDARY,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    ),
                                ], spacing=8),
                                ft.Row([
                                    ft.Icon(
                                        ft.Icons.PHONE,
                                        size=12,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Text(
                                        to_persian(
                                            u["phone"]
                                        ) if u["phone"]
                                        else "-",
                                        size=11,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Container(width=10),
                                    ft.Icon(
                                        ft.Icons.LAYERS,
                                        size=12,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Text(
                                        f'طبقه {to_persian(str(u["floor"]))}',
                                        size=11,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Container(width=10),
                                    ft.Icon(
                                        ft.Icons.SQUARE_FOOT,
                                        size=12,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Text(
                                        f'{to_persian(str(u["area"]))} متر',
                                        size=11,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Container(width=10),
                                    ft.Icon(
                                        ft.Icons.PEOPLE,
                                        size=12,
                                        color=TEXT_SECONDARY
                                    ),
                                    ft.Text(
                                        f'{to_persian(str(u["people_count"]))} نفر',
                                        size=11,
                                        color=TEXT_SECONDARY
                                    ),
                                ], spacing=5),
                            ], spacing=6, expand=True),
                            # بدهی
                            ft.Column([
                                ft.Text(
                                    "بدهی",
                                    size=10, color=TEXT_MUTED
                                ),
                                ft.Text(
                                    fmt_money(
                                        u["debt"],
                                        show_unit=False
                                    ),
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=debt_color
                                ),
                                ft.Text(
                                    get_currency_label(),
                                    size=10, color=TEXT_MUTED
                                ),
                            ], spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END),
                            # دکمه‌ها
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.DESCRIPTION,
                                    icon_color=theme["purple"],
                                    tooltip="کاربرگ",
                                    on_click=lambda e, uid=u["id"]:
                                    show_unit_report(uid),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=P,
                                    tooltip="ویرایش",
                                    on_click=lambda e, uid=u["id"]:
                                    on_edit(uid),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=D,
                                    tooltip="حذف",
                                    on_click=lambda e, uid=u["id"],
                                                    num=u["number"]:
                                    confirm_delete_unit(uid, num),
                                ),
                            ], spacing=0),
                        ], spacing=15)
                    )
                )

            page.update()

        # ─── دیالوگ کاربرگ واحد ─────
        def show_unit_report(unit_id):
            """نمایش کاربرگ کامل واحد"""
            report = get_unit_full_report(unit_id)

            if not report:
                msg("اطلاعات واحد پیدا نشد.", D)
                return

            u = report["unit"]
            summary = report["summary"]

            # ─── محاسبه رنگ درصد ─────
            pct = summary["collection_percent"]
            if pct >= 90:
                pct_color = S
                pct_bg = theme["success_bg"]
            elif pct >= 50:
                pct_color = W
                pct_bg = theme["warning_bg"]
            else:
                pct_color = D
                pct_bg = theme["danger_bg"]

            # ─── هدر اطلاعات واحد ─────
            header_section = ft.Container(
                bgcolor=theme["primary_bg"],
                border_radius=12,
                padding=15,
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=60, height=60,
                            border_radius=15,
                            bgcolor=BG_CARD,
                            content=ft.Text(
                                to_persian(
                                    str(u["number"])
                                ),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=P,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),
                        ft.Column([
                            ft.Text(
                                u["resident_name"]
                                or "بدون ساکن",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_MAIN,
                            ),
                            ft.Text(
                                f'واحد {to_persian(str(u["number"]))}'
                                f' - طبقه {to_persian(str(u["floor"]))}',
                                size=12,
                                color=TEXT_SECONDARY,
                            ),
                        ], spacing=2, expand=True),
                    ], spacing=12),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Row([
                            ft.Icon(
                                ft.Icons.PHONE,
                                size=14, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                to_persian(u["phone"])
                                if u["phone"] else "-",
                                size=12,
                                color=TEXT_MAIN,
                            ),
                        ], spacing=4),
                        ft.Container(width=15),
                        ft.Row([
                            ft.Icon(
                                ft.Icons.SQUARE_FOOT,
                                size=14, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                f'{to_persian(str(u["area"]))} متر',
                                size=12,
                                color=TEXT_MAIN,
                            ),
                        ], spacing=4),
                        ft.Container(width=15),
                        ft.Row([
                            ft.Icon(
                                ft.Icons.PEOPLE,
                                size=14, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                f'{to_persian(str(u["people_count"]))} نفر',
                                size=12,
                                color=TEXT_MAIN,
                            ),
                        ], spacing=4),
                        ft.Container(width=15),
                        ft.Row([
                            ft.Icon(
                                ft.Icons.HOME,
                                size=14, color=TEXT_SECONDARY
                            ),
                            ft.Text(
                                u["resident_type"],
                                size=12,
                                color=TEXT_MAIN,
                            ),
                        ], spacing=4),
                    ], wrap=True),
                ], spacing=8)
            )

            # ─── خلاصه مالی ─────
            summary_section = ft.Row([
                ft.Container(
                    expand=True,
                    padding=12,
                    border_radius=10,
                    bgcolor=theme["primary_bg"],
                    content=ft.Column([
                        ft.Text(
                            "کل شارژ صادره",
                            size=11, color=TEXT_SECONDARY
                        ),
                        ft.Text(
                            fmt_money(
                                summary["total_charges"],
                                show_unit=False
                            ),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=P,
                        ),
                        ft.Text(
                            get_currency_label(),
                            size=10, color=TEXT_MUTED
                        ),
                    ], spacing=2)
                ),
                ft.Container(
                    expand=True,
                    padding=12,
                    border_radius=10,
                    bgcolor=theme["success_bg"],
                    content=ft.Column([
                        ft.Text(
                            "کل پرداختی",
                            size=11, color=TEXT_SECONDARY
                        ),
                        ft.Text(
                            fmt_money(
                                summary["total_paid"],
                                show_unit=False
                            ),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=S,
                        ),
                        ft.Text(
                            get_currency_label(),
                            size=10, color=TEXT_MUTED
                        ),
                    ], spacing=2)
                ),
                ft.Container(
                    expand=True,
                    padding=12,
                    border_radius=10,
                    bgcolor=theme["danger_bg"],
                    content=ft.Column([
                        ft.Text(
                            "بدهی فعلی",
                            size=11, color=TEXT_SECONDARY
                        ),
                        ft.Text(
                            fmt_money(
                                summary["total_debt"],
                                show_unit=False
                            ),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=D,
                        ),
                        ft.Text(
                            get_currency_label(),
                            size=10, color=TEXT_MUTED
                        ),
                    ], spacing=2)
                ),
                ft.Container(
                    expand=True,
                    padding=12,
                    border_radius=10,
                    bgcolor=pct_bg,
                    content=ft.Column([
                        ft.Text(
                            "درصد وصول",
                            size=11, color=TEXT_SECONDARY
                        ),
                        ft.Text(
                            f'{to_persian(f"{pct:.1f}")}٪',
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=pct_color,
                        ),
                        ft.Text(
                            "از کل شارژ",
                            size=10, color=TEXT_MUTED
                        ),
                    ], spacing=2)
                ),
            ], spacing=8)

            # ─── لیست شارژها ─────
            charges_col = ft.Column(spacing=6)

            if not report["charges"]:
                charges_col.controls.append(
                    ft.Container(
                        padding=20,
                        content=ft.Text(
                            "شارژی ثبت نشده",
                            color=TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER,
                        )
                    )
                )
            else:
                # هدر جدول
                charges_col.controls.append(
                    ft.Container(
                        bgcolor=P,
                        border_radius=8,
                        padding=8,
                        content=ft.Row([
                            ft.Text(
                                "دوره", width=100,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "مبلغ", width=110,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "پرداختی", width=110,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "باقیمانده", width=110,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "وضعیت", width=90,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                        ], spacing=4)
                    )
                )

                for i, c in enumerate(report["charges"]):
                    bg = theme["bg_table_row1"] if i % 2 == 0 else theme["bg_table_row2"]
                    status_color = {
                        "تسویه": S,
                        "ناقص": W,
                        "پرداخت نشده": D,
                    }.get(c["status"], TEXT_SECONDARY)

                    charges_col.controls.append(
                        ft.Container(
                            bgcolor=bg,
                            padding=8,
                            border_radius=6,
                            content=ft.Row([
                                ft.Text(
                                    c["period"],
                                    width=100, size=11,
                                    color=TEXT_MAIN,
                                ),
                                ft.Text(
                                    fmt_money(
                                        c["amount"],
                                        show_unit=False
                                    ),
                                    width=110, size=11,
                                    color=P,
                                ),
                                ft.Text(
                                    fmt_money(
                                        c["paid_amount"],
                                        show_unit=False
                                    ),
                                    width=110, size=11,
                                    color=S,
                                ),
                                ft.Text(
                                    fmt_money(
                                        c["remaining"],
                                        show_unit=False
                                    ),
                                    width=110, size=11,
                                    color=D if c["remaining"] > 0 else S,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    c["status"],
                                    width=90, size=10,
                                    color=status_color,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ], spacing=4)
                        )
                    )

            # ─── لیست پرداخت‌ها ─────
            payments_col = ft.Column(spacing=6)

            if not report["payments"]:
                payments_col.controls.append(
                    ft.Container(
                        padding=20,
                        content=ft.Text(
                            "پرداختی ثبت نشده",
                            color=TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER,
                        )
                    )
                )
            else:
                # هدر جدول
                payments_col.controls.append(
                    ft.Container(
                        bgcolor=S,
                        border_radius=8,
                        padding=8,
                        content=ft.Row([
                            ft.Text(
                                "تاریخ", width=130,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "مبلغ", width=130,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "روش", width=90,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "پیگیری", width=120,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                            ft.Text(
                                "توضیحات",
                                expand=True,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                                size=11
                            ),
                        ], spacing=4)
                    )
                )

                for i, p in enumerate(report["payments"]):
                    bg = theme["bg_table_row1"] if i % 2 == 0 else theme["bg_table_row2"]

                    payments_col.controls.append(
                        ft.Container(
                            bgcolor=bg,
                            padding=8,
                            border_radius=6,
                            content=ft.Row([
                                ft.Text(
                                    to_jalali(
                                        p["payment_date"]
                                    ),
                                    width=130, size=11,
                                    color=TEXT_MAIN,
                                ),
                                ft.Text(
                                    fmt_money(
                                        p["amount"],
                                        show_unit=False
                                    ),
                                    width=130, size=11,
                                    color=S,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    p["payment_method"]
                                    or "-",
                                    width=90, size=11,
                                    color=TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    to_persian(
                                        p["tracking_code"]
                                        or "-"
                                    ),
                                    width=120, size=10,
                                    color=TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    p["description"]
                                    or "-",
                                    expand=True,
                                    size=10,
                                    color=TEXT_SECONDARY,
                                ),
                            ], spacing=4)
                        )
                    )

            # ─── دکمه‌های عملیات ─────
            def close_dlg(e):
                report_dlg.open = False
                page.update()

            def print_report(e):
                msg(
                    "قابلیت چاپ در نسخه بعدی اضافه می‌شود",
                    W
                )

            def export_pdf(e):
                try:
                    from pdf_generator import (
                        generate_unit_report_pdf
                    )

                    # اطلاعات ساختمان
                    b_info = get_building_info()

                    # اطلاعات بانکی
                    bank_info = {
                        "card": get_setting(
                            "bank_card", ""
                        ),
                        "owner": get_setting(
                            "bank_owner", ""
                        ),
                        "sheba": get_setting(
                            "bank_sheba", ""
                        ),
                    }

                    # رنگ لوگو
                    theme_color = get_setting(
                        "logo_bg_color", "#1565C0"
                    )

                    # مسیر لوگو
                    logo_path = get_logo_path()

                    result = generate_unit_report_pdf(
                        report_data=report,
                        building_name=b_info["name"],
                        building_info={
                            "address": b_info["address"],
                            "floors": b_info["floors"],
                            "total_units": b_info[
                                "total_units"
                            ],
                        },
                        bank_info=bank_info,
                        currency_label=(
                            get_currency_label()
                        ),
                        logo_path=logo_path,
                        theme_color=theme_color,
                    )

                    if result["success"]:
                        msg(f"✅ PDF ساخته شد", S)
                        try:
                            os.startfile(result["path"])
                        except Exception:
                            try:
                                import subprocess
                                subprocess.Popen(
                                    ["xdg-open", result["path"]]
                                )
                            except Exception:
                                pass
                    else:
                        msg(
                            f"❌ {result['message']}",
                            D
                        )
                except ImportError:
                    msg(
                        "reportlab نصب نیست.",
                        D
                    )
                except Exception as ex:
                    msg(f"خطا: {ex}", D)

            # ─── محتوای دیالوگ ─────
            content = ft.Container(
                width=900,
                height=650,
                content=ft.Column([
                    header_section,
                    ft.Container(height=10),

                    ft.Text(
                        "📊 خلاصه مالی",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN,
                    ),
                    summary_section,
                    ft.Container(height=15),

                    ft.Row([
                        ft.Text(
                            "📋 لیست شارژها",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            padding=6,
                            border_radius=8,
                            bgcolor=theme["primary_bg"],
                            content=ft.Text(
                                f'{to_persian(str(summary["charges_count"]))} مورد',
                                size=11,
                                color=P,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]),
                    charges_col,
                    ft.Container(height=15),

                    ft.Row([
                        ft.Text(
                            "💳 لیست پرداخت‌ها",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            padding=6,
                            border_radius=8,
                            bgcolor=theme["success_bg"],
                            content=ft.Text(
                                f'{to_persian(str(summary["payments_count"]))} مورد',
                                size=11,
                                color=S,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]),
                    payments_col,

                ], scroll=ft.ScrollMode.AUTO,
                    spacing=8)
            )

            report_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(
                        ft.Icons.DESCRIPTION,
                        color=P, size=28
                    ),
                    ft.Text(
                        f"کاربرگ واحد {to_persian(str(u['number']))}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN,
                    ),
                ]),
                content=content,
                actions=[
                    ft.Button(
                        "📄 خروجی PDF",
                        bgcolor=theme["purple"],
                        color="white",
                        on_click=export_pdf,
                    ),
                    ft.Button(
                        "🖨️ چاپ",
                        bgcolor=W,
                        color="white",
                        on_click=print_report,
                    ),
                    ft.TextButton(
                        "بستن",
                        on_click=close_dlg,
                    ),
                ],
            )

            if report_dlg not in page.overlay:
                page.overlay.append(report_dlg)
            report_dlg.open = True
            page.update()

        def on_edit(uid):
            try:
                u = get_unit_by_id(uid)
                if not u:
                    msg("واحد پیدا نشد.", D)
                    return

                editing_id[0] = uid
                n.value = str(u["number"])
                fl.value = str(u["floor"])
                ar.value = str(u["area"])
                pc.value = str(u["people_count"])
                rn.value = u["resident_name"]
                ph.value = u["phone"]
                rt.value = u["resident_type"]
                st.value = u["status"]
                nt.value = u["notes"]

                save_btn.text = "✏️ بروزرسانی"
                clear_errors(required_fields)

                # اسکرول به فرم
                try:
                    page.scroll_to(offset=0, duration=300)
                except Exception:
                    pass

                page.update()
                msg(
                    f"✏️ ویرایش واحد {to_persian(str(u['number']))}",
                    P
                )
            except Exception as ex:
                msg(f"خطا در ویرایش: {ex}", D)
                import traceback
                traceback.print_exc()

        def on_save(e):
            if not validate(required_fields):
                return

            try:
                if editing_id[0]:
                    update_unit(
                        editing_id[0],
                        n.value, fl.value,
                        ar.value, pc.value,
                        rn.value, ph.value,
                        rt.value, st.value,
                        nt.value
                    )
                    msg("واحد بروزرسانی شد.")
                else:
                    add_unit(
                        n.value, fl.value,
                        ar.value, pc.value,
                        rn.value, ph.value,
                        rt.value, st.value,
                        nt.value
                    )
                    msg("واحد ثبت شد.")

                clear()
                load()

            except Exception as ex:
                msg(str(ex), D)

        save_btn.on_click = on_save

        # آمار
        all_units = list_units_with_debt()
        total_units = len(all_units)
        occupied = len(
            [u for u in all_units if u["status"] == "ساکن"]
        )
        vacant = len(
            [u for u in all_units if u["status"] == "خالی"]
        )
        debtors = len(
            [u for u in all_units if u["debt"] > 0]
        )

        stats_row = ft.Row([
            ft.Container(
                expand=True,
                padding=15,
                border_radius=12,
                bgcolor=theme["primary_bg"],
                content=ft.Column([
                    ft.Row([
                        ft.Icon(
                            ft.Icons.APARTMENT,
                            color=P, size=20
                        ),
                        ft.Text(
                            "کل واحدها",
                            size=12, color=TEXT_SECONDARY
                        ),
                    ], spacing=6),
                    ft.Text(
                        fmt_num(total_units),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=P
                    ),
                ], spacing=4)
            ),
            ft.Container(
                expand=True,
                padding=15,
                border_radius=12,
                bgcolor=theme["success_bg"],
                content=ft.Column([
                    ft.Row([
                        ft.Icon(
                            ft.Icons.HOME,
                            color=S, size=20
                        ),
                        ft.Text(
                            "ساکن",
                            size=12, color=TEXT_SECONDARY
                        ),
                    ], spacing=6),
                    ft.Text(
                        fmt_num(occupied),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=S
                    ),
                ], spacing=4)
            ),
            ft.Container(
                expand=True,
                padding=15,
                border_radius=12,
                bgcolor=theme["bg_input"],
                content=ft.Column([
                    ft.Row([
                        ft.Icon(
                            ft.Icons.HOUSE,
                            color=TEXT_MUTED, size=20
                        ),
                        ft.Text(
                            "خالی",
                            size=12, color=TEXT_SECONDARY
                        ),
                    ], spacing=6),
                    ft.Text(
                        fmt_num(vacant),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MUTED
                    ),
                ], spacing=4)
            ),
            ft.Container(
                expand=True,
                padding=15,
                border_radius=12,
                bgcolor=theme["danger_bg"],
                content=ft.Column([
                    ft.Row([
                        ft.Icon(
                            ft.Icons.WARNING_AMBER,
                            color=D, size=20
                        ),
                        ft.Text(
                            "بدهکار",
                            size=12, color=TEXT_SECONDARY
                        ),
                    ], spacing=6),
                    ft.Text(
                        fmt_num(debtors),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=D
                    ),
                ], spacing=4)
            ),
        ], spacing=15)

        load()

        return ft.Column([
            ft.Text(
                "مدیریت واحدها",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=TEXT_MAIN,
            ),

            stats_row,

            ft.Container(height=15),

            # فرم
            ft.Container(
                bgcolor=BG_CARD,
                border_radius=14,
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(
                            ft.Icons.ADD_HOME,
                            color=P, size=22
                        ),
                        ft.Text(
                            "ثبت / ویرایش واحد",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN,
                        ),
                    ], spacing=8),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Row(
                        [n, fl, ar, pc, rn, ph],
                        wrap=True
                    ),
                    ft.Row([rt, st], wrap=True),
                    ft.Row([nt]),
                    ft.Row([
                        save_btn,
                        ft.TextButton(
                            "انصراف",
                            on_click=lambda e: clear()
                        ),
                    ], spacing=8),
                ], spacing=10)
            ),

            ft.Container(height=15),

            # لیست
            ft.Text(
                "📋 لیست واحدها",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=TEXT_MAIN,
            ),

            ft.Container(height=8),

            list_col,

        ], scroll=ft.ScrollMode.AUTO, expand=True)

    # ═══════════ شارژ و پرداخت ═════════
    def build_charges_page():
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_CARD = theme["bg_card"]
        BG_MAIN = theme["bg_main"]
        BG_HOVER = theme["bg_hover"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        state = {
            "selected_period": None,
            "filter_year": str(get_jalali_year()),
            "search_period": "",
            "filter_status": "all",
            "search_resident": "",
            "show_archive": False,
        }

        STATUS_MAP = {
            "🔎 همه": "all",
            "✅ تسویه": "paid",
            "⏳ ناقص": "partial",
            "⚠️ پرداخت‌نشده": "unpaid",
        }
        STATUS_MAP_REV = {v: k for k, v in STATUS_MAP.items()}

        METHOD_MAP = {
            "مبلغ ثابت": "manual",
            "بر اساس متراژ": "area",
            "بر اساس نفرات": "person",
        }

        PAY_METHODS = ["کارت", "نقد", "واریز", "چک"]

        def get_available_years():
            all_rows = list_charges(None)
            years = set()
            for r in all_rows:
                period = r.get("period") or ""
                parts = period.strip().split()
                if parts:
                    try:
                        years.add(int(parts[-1]))
                    except (ValueError, IndexError):
                        pass
            if not years:
                years.add(get_jalali_year())
            return sorted(years, reverse=True)

        def period_sort_key(p):
            if not p:
                return (0, 0)
            parts = p.strip().split()
            try:
                year = int(parts[-1])
                month_name = parts[0]
                month_order = MONTHS.index(month_name) if month_name in MONTHS else 0
                return (year, month_order)
            except (ValueError, IndexError):
                return (0, 0)

        def extract_year(period):
            if not period:
                return None
            parts = period.strip().split()
            if parts:
                try:
                    return int(parts[-1])
                except (ValueError, IndexError):
                    return None
            return None

        def get_last_payment_for_unit(unit_number):
            try:
                payments = list_payments()
                for p in payments:
                    if p["unit_number"] == unit_number:
                        return p
            except Exception:
                pass
            return None

        periods_sidebar = ft.Column(spacing=8)
        details_panel = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        stats_row_container = ft.Container()

        def build_stats_cards():
            try:
                all_rows = list_charges(None)
            except Exception:
                all_rows = []

            total_amount = sum(r["amount"] or 0 for r in all_rows)
            total_paid = sum(r["paid_amount"] or 0 for r in all_rows)
            total_remaining = sum(r["remaining"] or 0 for r in all_rows)
            paid_count = len([r for r in all_rows if r["status"] == "تسویه"])
            unpaid_count = len([r for r in all_rows if r["status"] == "پرداخت نشده"])
            partial_count = len([r for r in all_rows if r["status"] == "ناقص"])

            def mini_card(icon, title, value, color, subtitle=""):
                return ft.Container(
                    expand=True, padding=14, border_radius=12, bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Container(
                            width=42, height=42, border_radius=12,
                            bgcolor=color + "20",
                            content=ft.Text(icon, size=20,
                                            text_align=ft.TextAlign.CENTER),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column([
                            ft.Text(title, size=11, color=TEXT_SECONDARY),
                            ft.Text(value, size=15,
                                    weight=ft.FontWeight.BOLD, color=color),
                        ], spacing=1, expand=True),
                    ], spacing=10),
                )

            return ft.Row([
                mini_card("📋", "کل شارژ صادره",
                          fmt_money(total_amount, show_unit=False),
                          P, f"{to_persian(str(len(all_rows)))} ردیف"),
                mini_card("✅", "کل دریافتی",
                          fmt_money(total_paid, show_unit=False),
                          S, f"{to_persian(str(paid_count))} تسویه"),
                mini_card("⏳", "ناقص",
                          fmt_money(
                              sum(r["paid_amount"] or 0 for r in all_rows
                                  if r["status"] == "ناقص"),
                              show_unit=False),
                          W, f"{to_persian(str(partial_count))} ناقص"),
                mini_card("⚠️", "معوق",
                          fmt_money(total_remaining, show_unit=False),
                          D, f"{to_persian(str(unpaid_count))} پرداخت‌نشده"),
            ], spacing=10)

        def build_period_item(period, rows_in_period):
            total = sum(r["amount"] or 0 for r in rows_in_period)
            paid = sum(r["paid_amount"] or 0 for r in rows_in_period)
            pct = (paid / total * 100) if total > 0 else 0

            if pct >= 90:
                bar_color = S
            elif pct >= 50:
                bar_color = W
            else:
                bar_color = D

            is_selected = state["selected_period"] == period
            paid_count = len([r for r in rows_in_period if r["status"] == "تسویه"])

            def on_click_period(e):
                state["selected_period"] = period
                state["filter_status"] = "all"
                state["search_resident"] = ""
                refresh_sidebar()
                refresh_details()

            return ft.Container(
                padding=12, border_radius=12,
                bgcolor=theme["primary_bg"] if is_selected else BG_CARD,
                on_click=on_click_period, ink=True,
                content=ft.Row([
                    ft.Container(width=4, height=60, border_radius=2, bgcolor=bar_color),
                    ft.Container(width=10),
                    ft.Column([
                        ft.Row([
                            ft.Text(period, size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=P if is_selected else TEXT_MAIN),
                            ft.Container(expand=True),
                            ft.Container(
                                padding=6, border_radius=8,
                                bgcolor=bar_color + "20",
                                content=ft.Text(
                                    f'{to_persian(f"{pct:.0f}")}٪',
                                    size=10, color=bar_color,
                                    weight=ft.FontWeight.BOLD),
                            ),
                        ]),
                        ft.Container(height=6),
                        ft.ProgressBar(value=pct / 100, color=bar_color,
                                       bgcolor=BG_HOVER, height=4, border_radius=2),
                        ft.Container(height=4),
                        ft.Text(
                            f'{to_persian(str(len(rows_in_period)))} ردیف • '
                            f'{to_persian(str(paid_count))} تسویه',
                            size=10, color=TEXT_MUTED),
                    ], spacing=0, expand=True),
                ], spacing=0),
            )

        def refresh_sidebar():
            periods_sidebar.controls.clear()
            try:
                all_rows = list_charges(None)
            except Exception:
                all_rows = []

            year = state["filter_year"]
            if year != "all":
                try:
                    year_int = int(year)
                    all_rows = [r for r in all_rows
                                if extract_year(r["period"]) == year_int]
                except ValueError:
                    pass

            grouped = {}
            for r in all_rows:
                grouped.setdefault(r["period"], []).append(r)

            search = state["search_period"].strip()
            if search:
                grouped = {k: v for k, v in grouped.items() if search in k}

            sorted_periods = sorted(grouped.keys(),
                                    key=period_sort_key, reverse=True)

            if not sorted_periods:
                periods_sidebar.controls.append(
                    ft.Container(
                        padding=30, alignment=ft.Alignment.CENTER,
                        content=ft.Column([
                            ft.Icon(ft.Icons.INBOX, size=50, color=TEXT_MUTED),
                            ft.Text("هیچ دوره‌ای یافت نشد", size=12,
                                    color=TEXT_MUTED,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("سال دیگری را امتحان کنید",
                                    size=10, color=TEXT_MUTED),
                        ], spacing=6,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )
                try:
                    periods_sidebar.update()
                except Exception:
                    pass
                return

            if state["selected_period"] not in sorted_periods:
                state["selected_period"] = sorted_periods[0]

            recent = sorted_periods[:6]
            archived = sorted_periods[6:]

            for period in recent:
                periods_sidebar.controls.append(
                    build_period_item(period, grouped[period])
                )

            if archived:
                if state["show_archive"]:
                    for period in archived:
                        periods_sidebar.controls.append(
                            build_period_item(period, grouped[period])
                        )
                else:
                    periods_sidebar.controls.append(
                        ft.Container(
                            padding=12, border_radius=12, bgcolor=BG_HOVER,
                            on_click=lambda e: toggle_archive(),
                            ink=True,
                            content=ft.Row([
                                ft.Icon(ft.Icons.ARCHIVE, size=22, color=TEXT_MUTED),
                                ft.Column([
                                    ft.Text(
                                        f"آرشیو ({to_persian(str(len(archived)))} دوره)",
                                        size=12, weight=ft.FontWeight.BOLD,
                                        color=TEXT_MAIN),
                                    ft.Text("برای مشاهده کلیک کنید",
                                            size=10, color=TEXT_MUTED),
                                ], spacing=1, expand=True),
                                ft.Icon(ft.Icons.CHEVRON_LEFT, size=22,
                                        color=TEXT_MUTED),
                            ], spacing=8),
                        )
                    )

            try:
                periods_sidebar.update()
            except Exception:
                pass

        def toggle_archive():
            state["show_archive"] = not state["show_archive"]
            refresh_sidebar()

        def build_charge_row(c):
            is_paid = c["status"] == "تسویه"

            status_color = {
                "پرداخت نشده": D,
                "ناقص": W,
                "تسویه": S,
            }.get(c["status"], TEXT_MUTED)

            status_bg = {
                "پرداخت نشده": theme["danger_bg"],
                "ناقص": theme["warning_bg"],
                "تسویه": theme["success_bg"],
            }.get(c["status"], BG_HOVER)

            pct = 0
            if c["amount"] > 0:
                pct = min(100, (c["paid_amount"] / c["amount"]) * 100)

            previous_debt = c.get("previous_debt", 0)
            if previous_debt > 0:
                prev_badge = ft.Container(
                    padding=ft.Padding(6, 2, 6, 2),
                    border_radius=6,
                    bgcolor="#FFF3E0",
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING_AMBER, size=11, color=W),
                        ft.Text(
                            "بدهی قبلی: " +
                            fmt_money(previous_debt, show_unit=False) +
                            " " + get_currency_short(),
                            size=9, color=W, weight=ft.FontWeight.BOLD),
                    ], spacing=3),
                )
            else:
                prev_badge = ft.Container()

            last_payment = get_last_payment_for_unit(c["unit_number"])
            payment_info_children = []
            if last_payment:
                if last_payment.get("payment_date"):
                    payment_info_children.extend([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=10, color=S),
                        ft.Text(to_jalali(last_payment["payment_date"]),
                                size=9, color=TEXT_MUTED),
                        ft.Container(width=8),
                    ])
                if last_payment.get("tracking_code"):
                    payment_info_children.extend([
                        ft.Icon(ft.Icons.CONFIRMATION_NUMBER, size=10, color=P),
                        ft.Text(to_persian(last_payment["tracking_code"]),
                                size=9, color=TEXT_MUTED),
                    ])

            payment_info_row = ft.Row(
                payment_info_children, spacing=3,
            ) if payment_info_children else ft.Container()

            return ft.Container(
                padding=10, border_radius=8, bgcolor=BG_CARD,
                content=ft.Row([
                    ft.Container(
                        width=42, height=42, border_radius=21,
                        bgcolor=theme["primary_bg"],
                        content=ft.Text(
                            to_persian(str(c["unit_number"])),
                            size=13, weight=ft.FontWeight.BOLD,
                            color=P, text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(width=10),
                    ft.Column([
                        ft.Text(c["resident_name"] or "بدون ساکن",
                                size=12, weight=ft.FontWeight.BOLD,
                                color=TEXT_MAIN),
                        ft.Container(height=4),
                        ft.Row([
                            ft.ProgressBar(value=pct / 100, color=status_color,
                                           bgcolor=BG_HOVER, height=3,
                                           border_radius=2, expand=True),
                            ft.Container(width=6),
                            ft.Text(f"{to_persian(f'{pct:.0f}')}٪",
                                    size=9, color=status_color,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                        payment_info_row,
                        prev_badge,
                    ], spacing=2, expand=3),
                    ft.Column([
                        ft.Text("مبلغ", size=9, color=TEXT_MUTED),
                        ft.Text(fmt_money(c["amount"], show_unit=False),
                                size=11, color=TEXT_MAIN,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=1, expand=2),
                    ft.Column([
                        ft.Text("پرداختی", size=9, color=TEXT_MUTED),
                        ft.Text(fmt_money(c["paid_amount"], show_unit=False),
                                size=11, color=S, weight=ft.FontWeight.BOLD),
                    ], spacing=1, expand=2),
                    ft.Column([
                        ft.Text("باقیمانده", size=9, color=TEXT_MUTED),
                        ft.Text(fmt_money(c["remaining"], show_unit=False),
                                size=11,
                                color=D if c["remaining"] > 0 else S,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=1, expand=2),
                    ft.Container(
                        width=85, padding=6, border_radius=10,
                        bgcolor=status_bg,
                        content=ft.Text(c["status"], size=10,
                                        color=status_color,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER),
                    ),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.PAYMENT,
                            icon_color="#ccc" if is_paid else S,
                            disabled=is_paid, tooltip="ثبت پرداخت",
                            icon_size=18,
                            on_click=lambda e, ch=c: open_pay_dialog(ch),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.HISTORY, icon_color=P,
                            tooltip="تاریخچه پرداخت", icon_size=18,
                            on_click=lambda e, ch=c: open_history_dialog(
                                ch["unit_id"], ch["unit_number"]),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE, icon_color=D,
                            tooltip="حذف", icon_size=18,
                            on_click=lambda e, cid=c["id"]: (
                                delete_charge(cid), refresh_all(),
                                msg("حذف شد.", W)),
                        ),
                    ], spacing=0, width=110),
                ], spacing=8),
            )

        def build_period_details(period):
            try:
                all_rows = list_charges(period)
            except Exception:
                all_rows = []

            if not all_rows:
                return ft.Container(
                    padding=60, alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=70, color=TEXT_MUTED),
                        ft.Text("هیچ شارژی یافت نشد", color=TEXT_MUTED,
                                size=14, weight=ft.FontWeight.BOLD),
                    ], spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )

            filtered = all_rows
            if state["filter_status"] == "paid":
                filtered = [r for r in filtered if r["status"] == "تسویه"]
            elif state["filter_status"] == "partial":
                filtered = [r for r in filtered if r["status"] == "ناقص"]
            elif state["filter_status"] == "unpaid":
                filtered = [r for r in filtered if r["status"] == "پرداخت نشده"]

            if state["search_resident"].strip():
                s = state["search_resident"].strip().lower()
                filtered = [
                    r for r in filtered
                    if (s in (r["resident_name"] or "").lower())
                       or (s in str(r["unit_number"]).lower())
                ]

            total = sum(r["amount"] or 0 for r in all_rows)
            paid = sum(r["paid_amount"] or 0 for r in all_rows)
            remaining = total - paid
            pct = (paid / total * 100) if total > 0 else 0
            paid_count = len([r for r in all_rows if r["status"] == "تسویه"])

            pct_color = S if pct >= 90 else W if pct >= 50 else D
            pct_bg = (theme["success_bg"] if pct >= 90
                      else theme["warning_bg"] if pct >= 50
            else theme["danger_bg"])

            header = ft.Container(
                padding=18, border_radius=14, bgcolor=theme["primary_bg"],
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=50, height=50, border_radius=14,
                            bgcolor=BG_CARD,
                            content=ft.Icon(ft.Icons.CALENDAR_MONTH,
                                            color=P, size=26),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column([
                            ft.Text(period, size=18,
                                    weight=ft.FontWeight.BOLD, color=P),
                            ft.Text(
                                f'{to_persian(str(len(all_rows)))} ردیف • '
                                f'{to_persian(f"{pct:.0f}")}٪ وصول',
                                size=11, color=TEXT_SECONDARY),
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.PICTURE_AS_PDF,
                            icon_color=theme["purple"],
                            tooltip="خروجی PDF این دوره",
                            on_click=lambda e, p=period: export_period_pdf(p),
                        ),
                    ], spacing=12),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Container(expand=True, padding=10,
                                     border_radius=10, bgcolor=BG_CARD,
                                     content=ft.Column([
                                         ft.Text("کل", size=10, color=TEXT_MUTED),
                                         ft.Text(fmt_money(total, show_unit=False),
                                                 size=13, color=P,
                                                 weight=ft.FontWeight.BOLD),
                                     ], spacing=2)),
                        ft.Container(expand=True, padding=10,
                                     border_radius=10, bgcolor=BG_CARD,
                                     content=ft.Column([
                                         ft.Text("دریافتی", size=10,
                                                 color=TEXT_MUTED),
                                         ft.Text(fmt_money(paid, show_unit=False),
                                                 size=13, color=S,
                                                 weight=ft.FontWeight.BOLD),
                                     ], spacing=2)),
                        ft.Container(expand=True, padding=10,
                                     border_radius=10, bgcolor=BG_CARD,
                                     content=ft.Column([
                                         ft.Text("معوق", size=10,
                                                 color=TEXT_MUTED),
                                         ft.Text(fmt_money(remaining,
                                                           show_unit=False),
                                                 size=13,
                                                 color=D if remaining > 0 else S,
                                                 weight=ft.FontWeight.BOLD),
                                     ], spacing=2)),
                        ft.Container(expand=True, padding=10,
                                     border_radius=10, bgcolor=BG_CARD,
                                     content=ft.Column([
                                         ft.Text("تسویه", size=10,
                                                 color=TEXT_MUTED),
                                         ft.Text(
                                             f"{to_persian(str(paid_count))} از "
                                             f"{to_persian(str(len(all_rows)))}",
                                             size=13, color=S,
                                             weight=ft.FontWeight.BOLD),
                                     ], spacing=2)),
                        ft.Container(expand=True, padding=10,
                                     border_radius=10, bgcolor=pct_bg,
                                     content=ft.Column([
                                         ft.Text("درصد وصول", size=10,
                                                 color=TEXT_MUTED),
                                         ft.Text(f'{to_persian(f"{pct:.0f}")}٪',
                                                 size=13, color=pct_color,
                                                 weight=ft.FontWeight.BOLD),
                                     ], spacing=2)),
                    ], spacing=8),
                ], spacing=0),
            )

            def on_status_filter(e):
                state["filter_status"] = STATUS_MAP.get(e.control.value, "all")
                refresh_details()

            def on_search_resident(e):
                state["search_resident"] = e.control.value
                refresh_details()

            status_filter_dd = ft.Dropdown(
                label="وضعیت", width=150,
                value=STATUS_MAP_REV.get(state["filter_status"], "🔎 همه"),
                on_change=on_status_filter,
                options=[ft.dropdown.Option(text=t) for t in STATUS_MAP.keys()],
            )

            search_resident_field = ft.TextField(
                label="🔍 جستجوی ساکن یا شماره واحد",
                expand=True,
                value=state["search_resident"],
                on_change=on_search_resident,
            )

            filter_row = ft.Container(
                padding=12, border_radius=12, bgcolor=BG_CARD,
                content=ft.Row([
                    status_filter_dd,
                    search_resident_field,
                    ft.IconButton(
                        icon=ft.Icons.REFRESH, icon_color=P,
                        tooltip="بروزرسانی",
                        on_click=lambda e: refresh_all(),
                    ),
                ], spacing=10),
            )

            if not filtered:
                rows_col = ft.Container(
                    padding=40, alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.FILTER_ALT_OFF, size=50,
                                color=TEXT_MUTED),
                        ft.Text("هیچ ردیفی با این فیلتر یافت نشد",
                                size=12, color=TEXT_MUTED,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )
            else:
                rows_col = ft.Column(
                    spacing=8,
                    controls=[build_charge_row(c) for c in filtered],
                )

            filtered_total = sum(r["amount"] or 0 for r in filtered)
            filtered_paid = sum(r["paid_amount"] or 0 for r in filtered)
            filtered_remaining = sum(r["remaining"] or 0 for r in filtered)

            summary_row = ft.Container(
                padding=14, border_radius=12, bgcolor=theme["primary_bg"],
                content=ft.Row([
                    ft.Icon(ft.Icons.SUMMARIZE, color=P, size=18),
                    ft.Text("جمع کل:", size=12, color=P,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    ft.Text(fmt_money(filtered_total, show_unit=False),
                            size=12, color=P, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text("دریافتی:", size=11, color=TEXT_SECONDARY),
                    ft.Text(fmt_money(filtered_paid, show_unit=False),
                            size=12, color=S, weight=ft.FontWeight.BOLD),
                    ft.Container(width=15),
                    ft.Text("معوق:", size=11, color=TEXT_SECONDARY),
                    ft.Text(fmt_money(filtered_remaining, show_unit=False),
                            size=12,
                            color=D if filtered_remaining > 0 else S,
                            weight=ft.FontWeight.BOLD),
                ], spacing=6),
            )

            return ft.Column([
                header, ft.Container(height=12),
                filter_row, ft.Container(height=12),
                rows_col, ft.Container(height=12),
                summary_row,
            ], spacing=0)

        def refresh_details():
            details_panel.controls.clear()
            if not state["selected_period"]:
                details_panel.controls.append(
                    ft.Container(
                        padding=60, alignment=ft.Alignment.CENTER,
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHEVRON_LEFT, size=70,
                                    color=TEXT_MUTED),
                            ft.Text("یک دوره را از لیست انتخاب کنید",
                                    size=13, color=TEXT_MUTED,
                                    weight=ft.FontWeight.BOLD),
                        ], spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )
            else:
                details_panel.controls.append(
                    build_period_details(state["selected_period"])
                )
            try:
                details_panel.update()
            except Exception:
                pass

        # ═══════════════════════════════════
        # ═══  دیالوگ صدور شارژ  ═══
        # ═══════════════════════════════════
        pp = period_picker()

        method = ft.Dropdown(
            label="روش محاسبه *", width=200, value="مبلغ ثابت",
            options=[ft.dropdown.Option(text=t) for t in METHOD_MAP.keys()],
        )

        rate = make_amount_field(label="مبلغ / نرخ", width=200,
                                 hint=money_hint())
        due_picker = date_field_with_picker("سررسید", 200)
        gen_fields = [(method, "روش محاسبه", True),
                      (rate, "مبلغ / نرخ", True)]

        def close_gen(e):
            gen_dlg.open = False
            page.update()

        def do_gen(e):
            if not validate(gen_fields):
                return
            try:
                period_text = pp.get_period()
                due_val = due_picker.text_field.value
                method_key = METHOD_MAP.get(method.value, "manual")
                cnt = generate_monthly_charges(
                    period_text, method_key,
                    read_amount(rate.value), due_val,
                )
                gen_dlg.open = False
                new_years = get_available_years()
                year_filter.options = [
                    ft.dropdown.Option(text=str(y)) for y in new_years
                ]
                year_filter.update()
                state["selected_period"] = period_text
                refresh_all()
                msg(f"✅ {cnt} شارژ برای «{period_text}» صادر شد.")
            except Exception as ex:
                msg(str(ex), D)

        gen_dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE, color=P, size=26),
                ft.Text("صدور شارژ جدید", weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN),
            ]),
            content=ft.Container(
                width=500,
                content=ft.Column([
                    ft.Text("دوره و روش محاسبه را انتخاب کنید:",
                            size=12, color=TEXT_SECONDARY),
                    ft.Container(height=10),
                    ft.Row([pp], wrap=True),
                    ft.Container(height=5),
                    ft.Row([method, rate], wrap=True),
                    ft.Container(height=5),
                    ft.Row([due_picker], wrap=True),
                ], tight=True, spacing=8),
            ),
            actions=[
                ft.Button("✅ صدور", bgcolor=P, color="white", on_click=do_gen),
                ft.TextButton("انصراف", on_click=close_gen),
            ],
        )

        def open_gen_dialog(e):
            if gen_dlg not in page.overlay:
                page.overlay.append(gen_dlg)
            gen_dlg.open = True
            page.update()

        # ═══════════════════════════════════
        # ═══  دیالوگ پرداخت (با OCR خودکار)  ═══
        # ═══════════════════════════════════
        pay_amount = make_amount_field(label="مبلغ پرداخت", width=200)
        pay_date = date_field_with_picker("تاریخ پرداخت", 200,
                                          default_today=True)

        pay_method = ft.Dropdown(
            label="روش پرداخت", width=150, value="کارت",
            options=[ft.dropdown.Option(text=m) for m in PAY_METHODS],
        )
        pay_tracking = ft.TextField(label="شماره پیگیری", width=200)
        pay_desc = ft.TextField(label="توضیحات", width=420)
        pay_fields = [
            (pay_amount, "مبلغ پرداخت", True),
            (pay_date, "تاریخ پرداخت", True),
        ]
        active_charge = {"unit_id": None}
        pay_unit_label = ft.Text("", size=13,
                                 weight=ft.FontWeight.BOLD, color=S)

        # ─── وضعیت OCR ───
        ocr_status_text = ft.Text(
            "", size=11, color=TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
        )
        ocr_progress = ft.ProgressBar(
            width=300, height=4,
            color=theme["purple"],
            bgcolor=theme["bg_input"],
            visible=False,
        )
        ocr_status_container = ft.Container(
            padding=8, border_radius=8,
            bgcolor=theme["purple_bg"],
            visible=False,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_FIX_HIGH,
                            color=theme["purple"], size=16),
                    ft.Text("استخراج خودکار اطلاعات از فیش",
                            size=11, color=theme["purple"],
                            weight=ft.FontWeight.BOLD),
                ], spacing=6),
                ocr_status_text,
                ft.Container(height=4),
                ocr_progress,
            ], spacing=4, tight=True),
        )

        # ⭐ OCR خودکار (بعد از آپلود)
        def _run_ocr_auto(uploaded_path):
            if not uploaded_path or not os.path.exists(uploaded_path):
                return

            ocr_status_container.visible = True
            ocr_progress.visible = True
            ocr_progress.value = None
            ocr_status_text.value = "⏳ در حال خواندن فیش..."
            ocr_status_text.color = theme["purple"]
            try:
                page.update()
            except Exception:
                pass

            import threading

            def _worker():
                try:
                    from receipt_parser import parse_receipt as parse_receipt_ocr
                    result = parse_receipt_ocr(uploaded_path, debug=False)
                except Exception as e:
                    print(f"❌ OCR error: {e}")
                    import traceback
                    traceback.print_exc()
                    result = {"success": False, "error": str(e)}

                async def _apply():
                    try:
                        ocr_progress.value = 1.0
                        ocr_progress.visible = False
                    except Exception:
                        pass

                    if not result.get("success"):
                        ocr_status_text.value = (
                            "⚠️ اطلاعاتی استخراج نشد. دستی پر کنید."
                        )
                        ocr_status_text.color = W
                        try:
                            page.update()
                        except Exception:
                            pass
                        return

                    filled = []

                    if result.get("amount_rial"):
                        try:
                            toman = int(result["amount_rial"]) // 10
                            pay_amount.value = format_amount_input(str(toman))
                            filled.append("مبلغ")
                        except Exception as ex:
                            print(f"⚠️ خطای مبلغ: {ex}")

                    if result.get("tracking_code"):
                        try:
                            pay_tracking.value = str(result["tracking_code"])
                            filled.append("پیگیری")
                        except Exception as ex:
                            print(f"⚠️ خطای پیگیری: {ex}")

                    if result.get("date"):
                        try:
                            pay_date.text_field.value = str(result["date"])
                            filled.append("تاریخ")
                        except Exception as ex:
                            print(f"⚠️ خطای تاریخ: {ex}")

                    try:
                        page.update()
                    except Exception:
                        pass

                    if filled:
                        ocr_status_text.value = (
                            f"✅ {', '.join(filled)} استخراج شد"
                        )
                        ocr_status_text.color = S
                    else:
                        ocr_status_text.value = "⚠️ فیلدی استخراج نشد"
                        ocr_status_text.color = W

                    try:
                        page.update()
                    except Exception:
                        pass

                try:
                    page.run_task(_apply)
                except Exception as ex:
                    print(f"❌ خطای run_task: {ex}")

            threading.Thread(target=_worker, daemon=True).start()

        # ⭐ اپلودر با callback
        pay_receipt_uploader = build_image_uploader(
            page,
            label="📎 انتخاب فیش واریزی",
            theme=theme,
            on_upload=_run_ocr_auto,
        )

        def close_pay(e):
            pay_dlg.open = False
            ocr_status_container.visible = False
            ocr_progress.visible = False
            ocr_status_text.value = ""
            page.update()

        def do_save_pay(e):
            if not validate(pay_fields):
                return
            try:
                try:
                    payment_date_obj = parse_date(
                        pay_date.text_field.value
                    )
                except Exception:
                    payment_date_obj = None

                raw_path = pay_receipt_uploader["get_path"]()
                saved_receipt = ""
                if raw_path:
                    period_txt = active_charge.get("period", "") or ""
                    month_part = period_txt.replace(" ", "_")
                    name_part = (active_charge.get("resident_name", "")
                                 or "").strip() or "بدون_نام"
                    unit_part = str(active_charge.get("unit_number", "") or "")
                    custom_name = (
                        f"فیش_واریز_شارژ_{month_part}_{name_part}"
                        f"_واحد_{unit_part}"
                    )

                    saved_receipt = save_uploaded_image(
                        raw_path, "receipts",
                        date_obj=payment_date_obj,
                        custom_name=custom_name,
                    )

                add_payment(
                    unit_id=active_charge["unit_id"],
                    amount=read_amount(pay_amount.value),
                    payment_date=pay_date.text_field.value,
                    payment_method=pay_method.value,
                    tracking_code=pay_tracking.value,
                    description=pay_desc.value,
                    target_charge_id=active_charge.get("charge_id"),
                    receipt_image=saved_receipt,
                )
                pay_dlg.open = False
                pay_receipt_uploader["clear"]()
                ocr_status_container.visible = False
                ocr_progress.visible = False
                ocr_status_text.value = ""
                refresh_all()
                msg("✅ پرداخت ثبت شد.")
            except Exception as ex:
                msg(str(ex), D)

        pay_dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.PAYMENT, color=S, size=26),
                ft.Text("ثبت پرداخت", weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN),
            ]),
            content=ft.Container(
                width=500,
                content=ft.Column([
                    ft.Container(
                        bgcolor=theme["success_bg"],
                        border_radius=8, padding=12,
                        content=ft.Column([
                            ft.Text("واحد مورد نظر:", size=11,
                                    color=TEXT_SECONDARY),
                            pay_unit_label,
                        ], spacing=2),
                    ),
                    ft.Row([pay_amount, pay_date], wrap=True),
                    ft.Row([pay_method, pay_tracking], wrap=True),
                    ft.Row([pay_desc]),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Text("فیش واریزی (اختیاری):", size=11,
                            color=TEXT_SECONDARY),
                    pay_receipt_uploader["component"],
                    ocr_status_container,
                ], tight=True, spacing=12,
                    scroll=ft.ScrollMode.AUTO),
            ),
            actions=[
                ft.Button("ثبت پرداخت", bgcolor=S, color="white",
                          on_click=do_save_pay),
                ft.TextButton("بستن", on_click=close_pay),
            ],
        )

        def open_pay_dialog(charge):
            active_charge["unit_id"] = charge["unit_id"]
            active_charge["charge_id"] = charge["id"]
            active_charge["unit_number"] = charge.get("unit_number", "")
            active_charge["resident_name"] = charge.get("resident_name", "")
            active_charge["period"] = charge.get("period", "")

            pay_amount.value = format_amount_input(
                str(int(convert_amount(charge["remaining"])))
            )
            pay_date.text_field.value = get_today_jalali()
            pay_method.value = "کارت"
            pay_tracking.value = ""
            pay_desc.value = ""
            pay_receipt_uploader["clear"]()

            ocr_status_container.visible = False
            ocr_progress.visible = False
            ocr_status_text.value = ""

            info_text = (
                f'واحد {to_persian(str(charge["unit_number"]))} • '
                f'{charge["resident_name"] or "بدون ساکن"} • '
                f'دوره {charge["period"]}'
            )
            prev_debt = charge.get("previous_debt", 0)
            if prev_debt > 0:
                info_text += (
                        "\n⚠️ این واحد بدهی قبلی دارد: " +
                        fmt_money(prev_debt)
                )
            pay_unit_label.value = info_text

            clear_errors(pay_fields)
            if pay_dlg not in page.overlay:
                page.overlay.append(pay_dlg)
            pay_dlg.open = True
            page.update()

        # ═══════════════════════════════════
        # ═══  دیالوگ تاریخچه  ═══
        # ═══════════════════════════════════
        history_col = ft.Column(spacing=8)

        def close_history(e):
            history_dlg.open = False
            page.update()

        history_dlg = ft.AlertDialog(
            title=ft.Text("تاریخچه پرداخت",
                          weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
            content=ft.Container(
                width=600, height=550,
                content=ft.Column([history_col],
                                  scroll=ft.ScrollMode.AUTO, tight=True),
            ),
            actions=[ft.TextButton("بستن", on_click=close_history)],
        )

        def open_history_dialog(unit_id, unit_number):
            history_col.controls.clear()
            try:
                payments = list_payments()
            except Exception:
                payments = []
            unit_payments = [p for p in payments
                             if p["unit_number"] == unit_number]

            unit_payments.sort(
                key=lambda p: (
                    p.get("payment_date") is None,
                    -(p.get("payment_date").toordinal()
                      if p.get("payment_date") else 0),
                )
            )

            if not unit_payments:
                history_col.controls.append(
                    ft.Container(
                        padding=30, alignment=ft.Alignment.CENTER,
                        content=ft.Column([
                            ft.Icon(ft.Icons.RECEIPT_LONG, size=50,
                                    color=TEXT_MUTED),
                            ft.Text("پرداختی ثبت نشده.", size=13,
                                    color=TEXT_MUTED),
                        ], spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )
            else:
                total_paid_unit = 0
                for p in unit_payments:
                    total_paid_unit += p["amount"] or 0

                    def make_del(pid):
                        def do_del(e):
                            try:
                                delete_payment(pid)
                                open_history_dialog(unit_id, unit_number)
                                refresh_all()
                            except Exception as ex:
                                msg(str(ex), D)

                        return do_del

                    receipt_path = p.get("receipt_image") or ""
                    if receipt_path and os.path.exists(receipt_path):
                        img_widget = ft.Container(
                            padding=4, border_radius=8,
                            bgcolor=theme["primary_bg"],
                            content=ft.Column([
                                ft.Image(
                                    src=image_to_base64_src(receipt_path),
                                    width=200, height=200,
                                    fit=ft.BoxFit.CONTAIN,
                                ),
                                ft.TextButton(
                                    "🔍 بزرگنمایی",
                                    on_click=lambda e, pp=receipt_path:
                                    show_full_image(page, pp),
                                ),
                            ], spacing=4,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        )
                    else:
                        img_widget = ft.Container()

                    details_rows = [
                        _info_pair("💰 مبلغ",
                                   fmt_money(p["amount"]), S),
                        _info_pair("📅 تاریخ پرداخت",
                                   to_jalali(p["payment_date"])
                                   if p["payment_date"] else "-",
                                   TEXT_MAIN),
                        _info_pair("💳 روش پرداخت",
                                   p.get("payment_method") or "-",
                                   TEXT_MAIN),
                    ]
                    if p.get("tracking_code"):
                        details_rows.append(
                            _info_pair("🔢 کد پیگیری",
                                       to_persian(p["tracking_code"]), P)
                        )
                    if p.get("description"):
                        details_rows.append(
                            _info_pair("📝 توضیحات",
                                       p["description"], TEXT_SECONDARY)
                        )
                    if p.get("created_at"):
                        try:
                            j_ct = jdatetime.datetime.fromgregorian(
                                datetime=p["created_at"]
                            )
                            ct_str = (
                                f"{j_ct.year}/{j_ct.month:02d}/{j_ct.day:02d} "
                                f"- {j_ct.hour:02d}:{j_ct.minute:02d}"
                            )
                        except Exception:
                            ct_str = "-"
                        details_rows.append(
                            _info_pair("🕒 زمان ثبت در سیستم",
                                       to_persian(ct_str), TEXT_MUTED)
                        )

                    history_col.controls.append(
                        ft.Container(
                            padding=14, border_radius=12,
                            bgcolor=theme["success_bg"],
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(
                                        width=42, height=42,
                                        border_radius=21, bgcolor=BG_CARD,
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(
                                            ft.Icons.PAYMENT,
                                            color=S, size=22,
                                        ),
                                    ),
                                    ft.Column([
                                        ft.Text(fmt_money(p["amount"]),
                                                weight=ft.FontWeight.BOLD,
                                                color=S, size=15),
                                        ft.Text(
                                            to_jalali(p["payment_date"])
                                            if p["payment_date"] else "-",
                                            size=11, color=TEXT_SECONDARY),
                                    ], spacing=2, expand=True),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE, icon_color=D,
                                        tooltip="حذف",
                                        on_click=make_del(p["id"]),
                                    ),
                                ]),
                                ft.Divider(height=1, color=DIVIDER),
                                ft.Column(details_rows, spacing=4),
                                img_widget,
                            ], spacing=8),
                        )
                    )

                history_col.controls.append(
                    ft.Container(
                        padding=12, border_radius=10,
                        bgcolor=theme["primary_bg"],
                        content=ft.Row([
                            ft.Text("جمع کل پرداختی:", size=12, color=P,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(fmt_money(total_paid_unit),
                                    size=14, color=P,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    )
                )

            history_dlg.title = ft.Text(
                f"تاریخچه پرداخت واحد {to_persian(str(unit_number))}",
                weight=ft.FontWeight.BOLD, color=TEXT_MAIN,
            )
            if history_dlg not in page.overlay:
                page.overlay.append(history_dlg)
            history_dlg.open = True
            page.update()

        # ═══════════════════════════════════
        # ═══  PDF دوره  ═══
        # ═══════════════════════════════════
        def export_period_pdf(period):
            try:
                from pdf_generator import generate_period_report_pdf
                from database import SessionLocal
                from models import Charge, Payment, Unit
                from collections import defaultdict

                b_info = get_building_info()
                bank_info = {
                    "card": get_setting("bank_card", ""),
                    "owner": get_setting("bank_owner", ""),
                    "sheba": get_setting("bank_sheba", ""),
                }
                logo_path = get_logo_path()
                theme_color = get_setting("logo_bg_color", "#1565C0")

                period_rows = list_charges(period)
                total_amount = sum(r["amount"] or 0 for r in period_rows)
                total_paid = sum(r["paid_amount"] or 0 for r in period_rows)
                total_remaining = total_amount - total_paid
                pct = (total_paid / total_amount * 100) if total_amount > 0 else 0

                period_charge_ids = set(r["id"] for r in period_rows)
                unit_ids = list(set(r["unit_id"] for r in period_rows))

                period_payments = []

                if unit_ids:
                    with SessionLocal() as db:
                        all_charges = db.query(Charge).filter(
                            Charge.unit_id.in_(unit_ids)
                        ).order_by(
                            Charge.created_at.asc(),
                            Charge.id.asc()
                        ).all()

                        all_payments = db.query(Payment).filter(
                            Payment.unit_id.in_(unit_ids)
                        ).order_by(
                            Payment.payment_date.asc(),
                            Payment.id.asc()
                        ).all()

                        charges_by_unit = defaultdict(list)
                        for c in all_charges:
                            charges_by_unit[c.unit_id].append(c)

                        payments_by_unit = defaultdict(list)
                        for p in all_payments:
                            payments_by_unit[p.unit_id].append(p)

                        period_payment_ids = set()

                        for uid in unit_ids:
                            unit_charges = charges_by_unit[uid]
                            unit_payments = payments_by_unit[uid]

                            remaining = {
                                c.id: float(c.amount or 0)
                                for c in unit_charges
                            }

                            for p in unit_payments:
                                amt = float(p.amount or 0)
                                first_hit_charge_id = None

                                for c in unit_charges:
                                    if remaining[c.id] <= 0:
                                        continue
                                    if first_hit_charge_id is None:
                                        first_hit_charge_id = c.id

                                    use = min(amt, remaining[c.id])
                                    remaining[c.id] -= use
                                    amt -= use
                                    if amt <= 0:
                                        break

                                if first_hit_charge_id in period_charge_ids:
                                    period_payment_ids.add(p.id)

                        if period_payment_ids:
                            matched_rows = db.query(Payment, Unit).join(
                                Unit, Payment.unit_id == Unit.id
                            ).filter(
                                Payment.id.in_(period_payment_ids)
                            ).order_by(
                                Payment.payment_date.asc()
                            ).all()

                            period_payments = [
                                {
                                    "id": pay.id,
                                    "unit_id": pay.unit_id,
                                    "unit_number": u.number,
                                    "resident_name": u.resident_name,
                                    "amount": pay.amount,
                                    "payment_date": pay.payment_date,
                                    "payment_method": pay.payment_method,
                                    "tracking_code": pay.tracking_code,
                                    "description": pay.description,
                                    "receipt_image": pay.receipt_image or "",
                                    "created_at": pay.created_at,
                                }
                                for pay, u in matched_rows
                            ]

                report_data = {
                    "period": period,
                    "charges": period_rows,
                    "payments": period_payments,
                    "summary": {
                        "total_amount": total_amount,
                        "total_paid": total_paid,
                        "total_remaining": total_remaining,
                        "collection_percent": pct,
                        "units_count": len(period_rows),
                        "paid_count": len([r for r in period_rows if r["status"] == "تسویه"]),
                        "unpaid_count": len([r for r in period_rows if r["status"] == "پرداخت نشده"]),
                        "partial_count": len([r for r in period_rows if r["status"] == "ناقص"]),
                    },
                }

                result = generate_period_report_pdf(
                    report_data=report_data,
                    building_name=b_info["name"],
                    building_info={
                        "address": b_info["address"],
                        "floors": b_info["floors"],
                        "total_units": b_info["total_units"],
                    },
                    bank_info=bank_info,
                    currency_label=get_currency_label(),
                    logo_path=logo_path,
                    theme_color=theme_color,
                )

                if result["success"]:
                    msg("✅ PDF ساخته شد.", S)
                    try:
                        os.startfile(result["path"])
                    except Exception:
                        try:
                            import subprocess
                            subprocess.Popen(["xdg-open", result["path"]])
                        except Exception:
                            pass
                else:
                    msg(f"❌ {result['message']}", D)
            except ImportError as ex:
                msg(f"❌ pdf_generator مشکل داره: {ex}", D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)
                import traceback
                traceback.print_exc()

        # ═══════════════════════════════════
        # ═══  فیلتر سال  ═══
        # ═══════════════════════════════════
        available_years = get_available_years()
        current_year_str = str(get_jalali_year())

        year_filter = ft.Dropdown(
            label="سال", width=150,
            value=current_year_str if current_year_str in [str(y) for y in available_years]
            else str(available_years[0]),
            options=[ft.dropdown.Option(text=str(y)) for y in available_years],
        )

        def on_year_change(e):
            state["filter_year"] = e.control.value
            refresh_sidebar()

        year_filter.on_change = on_year_change

        search_period_field = ft.TextField(
            label="🔍 جستجوی دوره", width=250,
            on_change=lambda e: (
                state.update({"search_period": e.control.value}),
                refresh_sidebar(),
            ),
        )

        def refresh_all():
            stats_row_container.content = build_stats_cards()
            try:
                stats_row_container.update()
            except Exception:
                pass
            refresh_sidebar()
            refresh_details()

        refresh_all()

        sidebar = ft.Container(
            width=200, padding=15, border_radius=14, bgcolor=BG_MAIN,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=P, size=20),
                    ft.Text("دوره‌ها", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(expand=True),
                ]),
                ft.Container(height=5),
                search_period_field,
                year_filter,
                ft.Container(height=5),
                periods_sidebar,
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
        )

        main_panel = ft.Container(
            expand=True, padding=15, border_radius=14, bgcolor=BG_MAIN,
            content=ft.Container(content=details_panel, expand=True),
        )

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("شارژ و پرداخت", size=28,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("مدیریت کامل شارژها، پرداخت‌ها و تاریخچه",
                            size=12, color=TEXT_MUTED),
                ], spacing=2, expand=True),
                ft.Button(
                    "➕ صدور شارژ جدید",
                    bgcolor=P, color="white", height=42,
                    on_click=open_gen_dialog,
                ),
            ]),
            ft.Container(height=15),
            stats_row_container,
            ft.Container(height=15),
            ft.Row([
                sidebar, ft.Container(width=15), main_panel,
            ], expand=True, spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.START),
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    # ═══════════ هزینه‌ها ═══════════
    def build_expenses_page():
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_CARD = theme["bg_card"]
        BG_MAIN = theme["bg_main"]
        BG_HOVER = theme["bg_hover"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        cat_icons_map = {
            "آب": "💧", "برق": "⚡", "گاز": "🔥",
            "نظافت و سرایداری": "🧹",
            "نگهبانی": "🛡️",
            "تعمیرات و نگهداری": "🔧",
            "آسانسور": "🛗",
            "فضای سبز": "🌿",
            "بیمه و عوارض": "📋",
            "لوازم و تجهیزات": "🛠️",
            "هزینه اداری": "📎",
            "سایر": "📌",
        }

        state = {
            "selected_month": None,
            "filter_year": str(get_jalali_year()),
            "search_month": "",
            "show_archive": False,
        }

        def extract_year_from_month(month_label):
            if not month_label:
                return None
            parts = month_label.strip().split()
            if parts:
                try:
                    return int(parts[-1])
                except (ValueError, IndexError):
                    return None
            return None

        def month_sort_key(month_label):
            if not month_label:
                return (0, 0)
            parts = month_label.strip().split()
            try:
                year = int(parts[-1])
                month_name = parts[0]
                month_order = MONTHS.index(month_name) if month_name in MONTHS else 0
                return (year, month_order)
            except (ValueError, IndexError):
                return (0, 0)

        def get_available_years():
            try:
                all_expenses = list_expenses()
            except Exception:
                all_expenses = []
            years = set()
            for ex in all_expenses:
                if ex.get("expense_date"):
                    try:
                        j = jdatetime.date.fromgregorian(date=ex["expense_date"])
                        years.add(j.year)
                    except Exception:
                        pass
            if not years:
                years.add(get_jalali_year())
            return sorted(years, reverse=True)

        def get_grouped_expenses():
            try:
                all_expenses = list_expenses()
            except Exception:
                all_expenses = []

            year = state["filter_year"]
            if year != "all":
                try:
                    year_int = int(year)
                    filtered = []
                    for ex in all_expenses:
                        if ex.get("expense_date"):
                            try:
                                j = jdatetime.date.fromgregorian(date=ex["expense_date"])
                                if j.year == year_int:
                                    filtered.append(ex)
                            except Exception:
                                pass
                    all_expenses = filtered
                except ValueError:
                    pass

            grouped = {}
            for ex in all_expenses:
                if ex.get("expense_date"):
                    try:
                        j = jdatetime.date.fromgregorian(date=ex["expense_date"])
                        key = f"{MONTHS[j.month]} {j.year}"
                    except Exception:
                        key = "بدون تاریخ"
                else:
                    key = "بدون تاریخ"
                grouped.setdefault(key, []).append(ex)

            return grouped

        def compute_categories(expenses_list):
            cat_totals = {}
            for ex in expenses_list:
                cat = ex.get("category", "سایر")
                cat_totals[cat] = cat_totals.get(cat, 0) + (ex.get("amount") or 0)

            total_all = sum(cat_totals.values()) or 1
            result = []
            for cat, total in sorted(cat_totals.items(), key=lambda x: -x[1]):
                result.append({
                    "category": cat,
                    "total": total,
                    "percent": (total / total_all) * 100,
                    "count": len([e for e in expenses_list
                                  if e.get("category") == cat]),
                })
            return result

        months_sidebar = ft.Column(spacing=8)
        details_panel = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        stats_row_container = ft.Container()

        def build_stats_cards():
            try:
                all_expenses = list_expenses()
            except Exception:
                all_expenses = []

            total = sum(e["amount"] or 0 for e in all_expenses)
            count = len(all_expenses)

            grouped = {}
            for e in all_expenses:
                if e.get("expense_date"):
                    try:
                        j = jdatetime.date.fromgregorian(date=e["expense_date"])
                        key = f"{MONTHS[j.month]} {j.year}"
                        grouped.setdefault(key, 0)
                        grouped[key] += e["amount"] or 0
                    except Exception:
                        pass
            avg_monthly = (sum(grouped.values()) / len(grouped)) if grouped else 0
            max_expense = max((e["amount"] or 0 for e in all_expenses), default=0)

            def mini_card(icon, title, value, color, subtitle=""):
                return ft.Container(
                    expand=True, padding=14, border_radius=12, bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Container(
                            width=42, height=42, border_radius=12,
                            bgcolor=color + "20",
                            content=ft.Text(icon, size=20,
                                            text_align=ft.TextAlign.CENTER),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column([
                            ft.Text(title, size=11, color=TEXT_SECONDARY),
                            ft.Text(value, size=15,
                                    weight=ft.FontWeight.BOLD, color=color),
                        ], spacing=1, expand=True),
                    ], spacing=10),
                )

            return ft.Row([
                mini_card("💰", "کل هزینه‌ها",
                          fmt_money(total, show_unit=False),
                          W, f"{to_persian(str(count))} مورد"),
                mini_card("📅", "میانگین ماهانه",
                          fmt_money(avg_monthly, show_unit=False),
                          P, f"{to_persian(str(len(grouped)))} ماه"),
                mini_card("📈", "بزرگترین هزینه",
                          fmt_money(max_expense, show_unit=False),
                          D, "تکی"),
                mini_card("📊", "تعداد دسته‌ها",
                          to_persian(str(len(compute_categories(all_expenses)))),
                          S, "دسته‌بندی"),
            ], spacing=10)

        def build_month_item(month_label, items):
            total = sum(e["amount"] or 0 for e in items)
            is_selected = state["selected_month"] == month_label

            def on_click_month(e):
                state["selected_month"] = month_label
                refresh_sidebar()
                refresh_details()

            return ft.Container(
                padding=12, border_radius=12,
                bgcolor=theme["primary_bg"] if is_selected else BG_CARD,
                on_click=on_click_month, ink=True,
                content=ft.Row([
                    ft.Container(width=4, height=55, border_radius=2, bgcolor=W),
                    ft.Container(width=10),
                    ft.Column([
                        ft.Row([
                            ft.Text(month_label, size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=P if is_selected else TEXT_MAIN),
                            ft.Container(expand=True),
                            ft.Container(
                                padding=6, border_radius=8, bgcolor=W + "20",
                                content=ft.Text(to_persian(str(len(items))),
                                                size=10, color=W,
                                                weight=ft.FontWeight.BOLD),
                            ),
                        ]),
                        ft.Container(height=6),
                        ft.Text(
                            fmt_money(total, show_unit=False) + " " + get_currency_short(),
                            size=12, color=W, weight=ft.FontWeight.BOLD),
                    ], spacing=0, expand=True),
                ], spacing=0),
            )

        def refresh_sidebar():
            try:
                months_sidebar.controls.clear()
                grouped = get_grouped_expenses()

                search = state["search_month"].strip()
                if search:
                    grouped = {k: v for k, v in grouped.items() if search in k}

                sorted_months = sorted(grouped.keys(), key=month_sort_key, reverse=True)

                if not sorted_months:
                    months_sidebar.controls.append(
                        ft.Container(
                            padding=30, alignment=ft.Alignment.CENTER,
                            content=ft.Column([
                                ft.Icon(ft.Icons.INBOX, size=50, color=TEXT_MUTED),
                                ft.Text("هیچ ماهی یافت نشد", size=12,
                                        color=TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                ft.Text("سال دیگری را امتحان کنید",
                                        size=10, color=TEXT_MUTED),
                            ], spacing=6,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        )
                    )
                    try:
                        months_sidebar.update()
                    except Exception:
                        pass
                    return

                if state["selected_month"] not in sorted_months:
                    state["selected_month"] = sorted_months[0]

                recent = sorted_months[:6]
                archived = sorted_months[6:]

                for month in recent:
                    months_sidebar.controls.append(
                        build_month_item(month, grouped[month])
                    )

                if archived:
                    if state["show_archive"]:
                        for month in archived:
                            months_sidebar.controls.append(
                                build_month_item(month, grouped[month])
                            )
                    else:
                        months_sidebar.controls.append(
                            ft.Container(
                                padding=12, border_radius=12, bgcolor=BG_HOVER,
                                on_click=lambda e: toggle_archive(),
                                ink=True,
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ARCHIVE, size=22, color=TEXT_MUTED),
                                    ft.Column([
                                        ft.Text(
                                            f"آرشیو ({to_persian(str(len(archived)))} ماه)",
                                            size=12, weight=ft.FontWeight.BOLD,
                                            color=TEXT_MAIN),
                                        ft.Text("برای مشاهده کلیک کنید",
                                                size=10, color=TEXT_MUTED),
                                    ], spacing=1, expand=True),
                                    ft.Icon(ft.Icons.CHEVRON_LEFT, size=22,
                                            color=TEXT_MUTED),
                                ], spacing=8),
                            )
                        )

                try:
                    months_sidebar.update()
                except Exception:
                    pass
            except Exception as ex:
                print(f"❌ خطای refresh_sidebar: {ex}")
                import traceback
                traceback.print_exc()

        def toggle_archive():
            state["show_archive"] = not state["show_archive"]
            refresh_sidebar()

        def build_expense_row(ex):
            try:
                icon = cat_icons_map.get(ex["category"], "📌")

                invoice_path = ex.get("invoice_image") or ""
                if invoice_path and os.path.exists(invoice_path):
                    invoice_thumb = ft.Container(
                        width=50, height=50, border_radius=8,
                        bgcolor=theme["primary_bg"],
                        alignment=ft.Alignment.CENTER,
                        on_click=lambda e, pp=invoice_path: show_full_image(page, pp),
                        ink=True, tooltip="مشاهده فاکتور",
                        content=ft.Image(
                            src=image_to_base64_src(invoice_path),
                            width=50, height=50, fit=ft.BoxFit.COVER,
                        ),
                    )
                else:
                    invoice_thumb = ft.Container(width=0)

                return ft.Container(
                    padding=12, border_radius=10, bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Container(
                            width=45, height=45, border_radius=12,
                            bgcolor=theme["warning_bg"],
                            content=ft.Text(icon, size=22,
                                            text_align=ft.TextAlign.CENTER),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text(ex["title"], size=13,
                                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                            ft.Container(height=2),
                            ft.Row([
                                ft.Text(ex["category"] or "-", size=10,
                                        color=TEXT_MUTED),
                                ft.Text("•", size=10, color=TEXT_MUTED),
                                ft.Text(to_jalali(ex["expense_date"]),
                                        size=10, color=TEXT_MUTED),
                            ], spacing=4),
                            ft.Text(ex["description"] or "",
                                    size=10, color=TEXT_SECONDARY, italic=True)
                            if ex.get("description") else ft.Container(),
                        ], spacing=2, expand=True),
                        invoice_thumb,
                        ft.Container(width=6),
                        ft.Column([
                            ft.Text(fmt_money(ex["amount"], show_unit=False),
                                    size=14, weight=ft.FontWeight.BOLD, color=W),
                            ft.Text(get_currency_label(), size=9, color=TEXT_MUTED),
                        ], spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.END),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT, icon_color=P,
                                tooltip="ویرایش", icon_size=18,
                                on_click=lambda e, eid=ex["id"]: open_expense_dialog(eid),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE, icon_color=D,
                                tooltip="حذف", icon_size=18,
                                on_click=lambda e, eid=ex["id"]: confirm_delete_expense(eid),
                            ),
                        ], spacing=0),
                    ], spacing=8),
                )
            except Exception as ex_row:
                print(f"❌ خطای build_expense_row: {ex_row}")
                import traceback
                traceback.print_exc()
                return ft.Container()

        def confirm_delete_expense(expense_id):
            def do_delete(e):
                try:
                    delete_expense(expense_id)
                    dlg.open = False
                    page.update()
                    refresh_all()
                    msg("🗑️ هزینه حذف شد.", W)
                except Exception as ex:
                    msg(f"خطا: {ex}", D)

            def close_dlg(e):
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=D, size=26),
                    ft.Text("تایید حذف", weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=350,
                    content=ft.Text("آیا از حذف این هزینه مطمئن هستید؟",
                                    size=13, color=TEXT_SECONDARY),
                ),
                actions=[
                    ft.Button("حذف", bgcolor=D, color="white", on_click=do_delete),
                    ft.TextButton("انصراف", on_click=close_dlg),
                ],
            )
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def build_month_chart(month_label, items):
            categories = compute_categories(items)

            if not categories:
                return ft.Container(
                    width=300, height=300, alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.PIE_CHART_OUTLINE, size=60,
                                color=TEXT_MUTED),
                        ft.Text("داده‌ای برای نمایش نیست",
                                color=TEXT_MUTED, size=12),
                    ], spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )

            try:
                import matplotlib.pyplot as plt
                import matplotlib
                from matplotlib import font_manager
                import hashlib
                import base64
                matplotlib.use('Agg')

                fonts_dir = os.path.join(os.getcwd(), "fonts")
                regular_path = os.path.join(fonts_dir, "Vazirmatn-Regular.ttf")
                bold_path = os.path.join(fonts_dir, "Vazirmatn-Bold.ttf")

                if os.path.exists(regular_path):
                    font_manager.fontManager.addfont(regular_path)
                if os.path.exists(bold_path):
                    font_manager.fontManager.addfont(bold_path)
                plt.rcParams['font.family'] = 'Vazirmatn'

                chart_dir = os.path.join(os.getcwd(), "temp_charts")
                os.makedirs(chart_dir, exist_ok=True)

                safe_hash = hashlib.md5(month_label.encode('utf-8')).hexdigest()[:10]
                chart_path = os.path.join(chart_dir, f"expenses_{safe_hash}.png")

                sizes = [c["total"] for c in categories]
                colors_list = [
                    '#EF6C00', '#1565C0', '#2E7D32',
                    '#C62828', '#6A1B9A', '#00838F',
                    '#F9A825', '#5D4037', '#455A64',
                    '#AD1457', '#00695C', '#4527A0',
                ]

                fig, ax = plt.subplots(
                    figsize=(6, 6),
                    subplot_kw=dict(aspect="equal"),
                    facecolor='none'
                )

                def fa_pct(pct):
                    val = f"{pct:.0f}"
                    p_map = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
                    return f"{val.translate(p_map)}٪"

                try:
                    dark = is_dark_mode()
                except Exception:
                    dark = False

                wedges, texts, autotexts = ax.pie(
                    sizes, colors=colors_list[:len(sizes)],
                    autopct=fa_pct, startangle=90, pctdistance=0.75,
                    textprops={'fontsize': 14, 'fontweight': 'bold'},
                    wedgeprops={
                        'linewidth': 3,
                        'edgecolor': '#0F172A' if dark else 'white',
                        'antialiased': True,
                    },
                )

                for at in autotexts:
                    at.set_color('white')
                    at.set_fontweight('bold')
                    at.set_fontsize(14)

                fig.patch.set_alpha(0)
                ax.set_facecolor('none')

                plt.savefig(chart_path, format='png',
                            bbox_inches='tight', transparent=True,
                            dpi=150, pad_inches=0.1)
                plt.close(fig)

                with open(chart_path, "rb") as f:
                    img_data = f.read()
                b64 = base64.b64encode(img_data).decode('utf-8')
                return ft.Image(
                    src=f"data:image/png;base64,{b64}",
                    width=300, height=300, fit=ft.BoxFit.CONTAIN,
                )

            except Exception as ex:
                print(f"❌ خطای نمودار ماه: {ex}")
                import traceback
                traceback.print_exc()
                return ft.Container(
                    width=300, height=300, alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=D),
                        ft.Text("خطا در ساخت نمودار", color=D, size=12,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )

        def build_month_categories_list(month_label, items):
            categories = compute_categories(items)

            colors_palette = [
                "#EF6C00", "#1565C0", "#2E7D32",
                "#C62828", "#6A1B9A", "#00838F",
                "#F9A825", "#5D4037", "#455A64",
                "#AD1457", "#00695C", "#4527A0",
            ]

            col = ft.Column(spacing=8)

            if not categories:
                col.controls.append(
                    ft.Container(
                        padding=20,
                        content=ft.Text("دسته‌بندی موجود نیست",
                                        color=TEXT_MUTED, size=11,
                                        text_align=ft.TextAlign.CENTER),
                    )
                )
                return col

            for i, cat in enumerate(categories):
                cat_color = colors_palette[i % len(colors_palette)]
                icon = cat_icons_map.get(cat["category"], "📌")

                col.controls.append(
                    ft.Container(
                        bgcolor=theme["bg_input"],
                        border_radius=10, padding=10,
                        content=ft.Row([
                            ft.Container(width=12, height=12,
                                         border_radius=6, bgcolor=cat_color),
                            ft.Text(icon, size=18),
                            ft.Column([
                                ft.Text(cat["category"], size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_MAIN),
                                ft.Text(f'{to_persian(str(cat["count"]))} مورد',
                                        size=9, color=TEXT_MUTED),
                            ], spacing=1, expand=True),
                            ft.Column([
                                ft.Text(fmt_money(cat["total"], show_unit=False),
                                        size=12, weight=ft.FontWeight.BOLD,
                                        color=cat_color),
                                ft.Text(to_persian(f"{cat['percent']:.0f}") + "٪",
                                        size=9, color=TEXT_SECONDARY,
                                        weight=ft.FontWeight.BOLD),
                            ], spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END),
                        ], spacing=8),
                    )
                )

            return col

        def export_month_expenses_pdf(month_label):
            """خروجی PDF گزارش هزینه‌های ماه با جزئیات کامل"""
            try:
                from pdf_generator import generate_month_expenses_pdf
            except Exception as ex:
                msg("PDF در دسترس نیست: " + str(ex), D)
                return

            try:
                grouped = get_grouped_expenses()
                month_expenses = grouped.get(month_label, [])

                if not month_expenses:
                    msg("هزینه‌ای برای این ماه وجود ندارد.", W)
                    return

                b_info = get_building_info()
                logo_path = get_logo_path()
                theme_color = get_setting("logo_bg_color", "#1565C0")

                result = generate_month_expenses_pdf(
                    month_label=month_label,
                    expenses=month_expenses,
                    building_name=b_info["name"],
                    building_info={
                        "address": b_info["address"],
                        "floors": b_info["floors"],
                        "total_units": b_info["total_units"],
                    },
                    currency_label=get_currency_label(),
                    logo_path=logo_path,
                    theme_color=theme_color,
                )

                if result.get("success"):
                    msg("✅ PDF گزارش هزینه‌ها ساخته شد.", S)
                    try:
                        os.startfile(result["path"])
                    except Exception:
                        try:
                            import subprocess
                            subprocess.Popen(["xdg-open", result["path"]])
                        except Exception:
                            pass
                else:
                    msg(result.get("message", "خطا"), D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)
                import traceback
                traceback.print_exc()

        def export_month_invoices_pdf(month_label, include_receipts=False):
            """خروجی PDF فاکتورها (گرید ۲×۲)"""
            try:
                from pdf_generator import generate_month_invoices_pdf
            except Exception as ex:
                msg("PDF در دسترس نیست: " + str(ex), D)
                return

            try:
                grouped = get_grouped_expenses()
                month_expenses = grouped.get(month_label, [])

                month_payments = []
                if include_receipts:
                    parts = month_label.strip().split()
                    if len(parts) >= 2:
                        try:
                            m_name = parts[0]
                            m_year = int(parts[-1])
                            m_idx = (MONTHS.index(m_name) + 1
                                     if m_name in MONTHS else None)
                            if m_idx:
                                for p in list_payments():
                                    pd = p.get("payment_date")
                                    if pd:
                                        try:
                                            j = jdatetime.date.fromgregorian(date=pd)
                                            if (j.year == m_year
                                                    and j.month == m_idx):
                                                month_payments.append(p)
                                        except Exception:
                                            pass
                        except Exception:
                            pass

                b_info = get_building_info()
                logo_path = get_logo_path()
                theme_color = get_setting("logo_bg_color", "#1565C0")

                result = generate_month_invoices_pdf(
                    month_label=month_label,
                    expenses=month_expenses,
                    payments=month_payments,
                    building_name=b_info["name"],
                    building_info={
                        "address": b_info["address"],
                        "floors": b_info["floors"],
                        "total_units": b_info["total_units"],
                    },
                    currency_label=get_currency_label(),
                    logo_path=logo_path,
                    theme_color=theme_color,
                    include_receipts=include_receipts,
                )

                if result.get("success"):
                    msg("✅ PDF اسناد ساخته شد.", S)
                    try:
                        os.startfile(result["path"])
                    except Exception:
                        try:
                            import subprocess
                            subprocess.Popen(["xdg-open", result["path"]])
                        except Exception:
                            pass
                else:
                    msg(result.get("message", "خطا"), D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)
                import traceback
                traceback.print_exc()

        def build_month_details(month_label):
            grouped = get_grouped_expenses()
            items = grouped.get(month_label, [])

            if not items:
                return ft.Container(
                    padding=60, alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=70, color=TEXT_MUTED),
                        ft.Text("هیچ هزینه‌ای یافت نشد",
                                color=TEXT_MUTED, size=14,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )

            total = sum(e["amount"] or 0 for e in items)
            count = len(items)

            # ⭐ فقط ۲ دکمه خروجی
            def _print_expenses(e):
                export_month_expenses_pdf(month_label)

            def _print_invoices(e):
                export_month_invoices_pdf(month_label, include_receipts=False)

            print_btn = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.DESCRIPTION,
                    icon_color=P,
                    tooltip="📊 گزارش هزینه‌های ماه (PDF با جزئیات)",
                    on_click=_print_expenses,
                ),
                ft.IconButton(
                    icon=ft.Icons.RECEIPT_LONG,
                    icon_color=W,
                    tooltip="🧾 چاپ فاکتورها (۴ در هر صفحه)",
                    on_click=_print_invoices,
                ),
            ], spacing=0)

            header = ft.Container(
                padding=18, border_radius=14, bgcolor=theme["primary_bg"],
                content=ft.Row([
                    ft.Container(
                        width=50, height=50, border_radius=14,
                        bgcolor=BG_CARD,
                        content=ft.Icon(ft.Icons.CALENDAR_MONTH, color=P, size=26),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Text(month_label, size=18,
                                weight=ft.FontWeight.BOLD, color=P),
                        ft.Text(f'{to_persian(str(count))} هزینه ثبت شده',
                                size=11, color=TEXT_SECONDARY),
                    ], spacing=2, expand=True),
                    print_btn,
                    ft.Column([
                        ft.Text("کل ماه", size=10, color=TEXT_MUTED),
                        ft.Text(
                            fmt_money(total, show_unit=False) + " " + get_currency_short(),
                            size=15, weight=ft.FontWeight.BOLD, color=W),
                    ], spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.END),
                ], spacing=12),
            )

            chart_section = ft.Container(
                padding=15, border_radius=14, bgcolor=BG_CARD,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PIE_CHART, color=theme["purple"], size=20),
                        ft.Text("تقسیم هزینه‌ها بر دسته", size=14,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Container(expand=True),
                        ft.Container(
                            padding=6, border_radius=10,
                            bgcolor=theme["purple_bg"],
                            content=ft.Text(
                                f'{to_persian(str(len(compute_categories(items))))} دسته',
                                size=10, color=theme["purple"],
                                weight=ft.FontWeight.BOLD),
                        ),
                    ], spacing=8),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            width=320, alignment=ft.Alignment.CENTER,
                            content=build_month_chart(month_label, items),
                        ),
                        ft.Container(width=15),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                [build_month_categories_list(month_label, items)],
                                scroll=ft.ScrollMode.AUTO,
                            ),
                        ),
                    ], spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.START),
                ], spacing=10),
            )

            rows_col = ft.Column(
                spacing=8,
                controls=[build_expense_row(e) for e in items],
            )

            expenses_section = ft.Container(
                padding=15, border_radius=14, bgcolor=BG_CARD,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.RECEIPT_LONG, color=W, size=20),
                        ft.Text("لیست هزینه‌ها", size=14,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Container(expand=True),
                        ft.Container(
                            padding=6, border_radius=10, bgcolor=W + "20",
                            content=ft.Text(f'{to_persian(str(count))} مورد',
                                            size=10, color=W,
                                            weight=ft.FontWeight.BOLD),
                        ),
                    ], spacing=8),
                    ft.Divider(height=1, color=DIVIDER),
                    rows_col,
                ], spacing=10),
            )

            return ft.Column([
                header,
                ft.Container(height=12),
                chart_section,
                ft.Container(height=12),
                expenses_section,
            ], spacing=0)

        def refresh_details():
            try:
                details_panel.controls.clear()
                if not state["selected_month"]:
                    details_panel.controls.append(
                        ft.Container(
                            padding=60, alignment=ft.Alignment.CENTER,
                            content=ft.Column([
                                ft.Icon(ft.Icons.CHEVRON_LEFT, size=70,
                                        color=TEXT_MUTED),
                                ft.Text("یک ماه را از لیست انتخاب کنید",
                                        size=13, color=TEXT_MUTED,
                                        weight=ft.FontWeight.BOLD),
                            ], spacing=8,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        )
                    )
                else:
                    details_panel.controls.append(
                        build_month_details(state["selected_month"])
                    )
                try:
                    details_panel.update()
                except Exception:
                    pass
            except Exception as ex:
                print(f"❌ خطای refresh_details: {ex}")
                import traceback
                traceback.print_exc()

        def open_expense_dialog(expense_id=None):
            editing = expense_id is not None

            if editing:
                ex = get_expense_by_id(expense_id)
                if not ex:
                    msg("هزینه پیدا نشد.", D)
                    return
            else:
                ex = None

            dlg_title = ft.TextField(
                label="عنوان *", width=300,
                value=ex["title"] if ex else "",
                autofocus=True,
            )

            dlg_category = ft.Dropdown(
                label="دسته‌بندی *", width=220,
                value=(ex["category"] if ex and ex["category"] in EXPENSE_CATEGORIES
                       else None),
                options=[ft.dropdown.Option(text=c) for c in EXPENSE_CATEGORIES],
            )

            dlg_amount = make_amount_field(
                label="مبلغ", width=200,
                initial_value=ex["amount"] if ex else "",
            )

            dlg_date = date_field_with_picker("تاریخ", 200, default_today=True)
            if ex and ex["expense_date"]:
                j = jdatetime.date.fromgregorian(date=ex["expense_date"])
                dlg_date.text_field.value = f"{j.year}/{j.month:02d}/{j.day:02d}"

            dlg_desc = ft.TextField(
                label="توضیحات", width=420,
                multiline=True, min_lines=1, max_lines=3,
                value=ex["description"] if ex else "",
            )

            dlg_fields = [
                (dlg_title, "عنوان", True),
                (dlg_category, "دسته‌بندی", True),
                (dlg_amount, "مبلغ", True),
            ]

            initial_invoice = ""
            if ex and ex.get("invoice_image"):
                initial_invoice = ex["invoice_image"]

            dlg_invoice_uploader = build_image_uploader(
                page,
                label="📎 انتخاب فاکتور خرید",
                theme=theme,
                initial_path=initial_invoice,
            )

            def close_dlg(e):
                dlg.open = False
                page.update()

            def save_dlg(e):
                if not validate(dlg_fields):
                    return
                try:
                    try:
                        expense_date_obj = parse_date(dlg_date.text_field.value)
                    except Exception:
                        expense_date_obj = None

                    raw_path = dlg_invoice_uploader["get_path"]()
                    saved_invoice = ""
                    if raw_path:
                        if editing and raw_path == initial_invoice:
                            saved_invoice = initial_invoice
                        else:
                            # ⭐ ساخت نام دلخواه
                            title_txt = (dlg_title.value or "").strip()
                            cat_txt = (dlg_category.value or "").strip()
                            month_part = ""
                            if expense_date_obj:
                                try:
                                    j = jdatetime.date.fromgregorian(
                                        date=expense_date_obj
                                    )
                                    month_part = f"{MONTHS[j.month]}_{j.year}"
                                except Exception:
                                    pass
                            custom_name = (
                                f"فاکتور_{cat_txt}_{title_txt}_{month_part}"
                            )

                            saved_invoice = save_uploaded_image(
                                raw_path, "invoices",
                                date_obj=expense_date_obj,
                                custom_name=custom_name,
                            )
                    elif editing:
                        saved_invoice = ""

                    if editing:
                        update_expense(
                            expense_id,
                            dlg_title.value,
                            dlg_category.value,
                            read_amount(dlg_amount.value),
                            dlg_date.text_field.value,
                            dlg_desc.value,
                            invoice_image=saved_invoice,
                        )
                        msg("✅ هزینه بروزرسانی شد.", S)
                    else:
                        add_expense(
                            dlg_title.value,
                            dlg_category.value,
                            read_amount(dlg_amount.value),
                            dlg_date.text_field.value,
                            dlg_desc.value,
                            invoice_image=saved_invoice,
                        )
                        msg("✅ هزینه ثبت شد.", S)

                    dlg.open = False
                    page.update()
                    refresh_all()
                except Exception as exc:
                    msg(str(exc), D)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.EDIT if editing else ft.Icons.ADD_CIRCLE,
                            color=W, size=24),
                    ft.Text("ویرایش هزینه" if editing else "ثبت هزینه جدید",
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=500,
                    content=ft.Column([
                        dlg_title,
                        ft.Row([dlg_category, dlg_amount], wrap=True),
                        dlg_date,
                        dlg_desc,
                        ft.Divider(height=1, color=DIVIDER),
                        ft.Text("فاکتور خرید (اختیاری):", size=11,
                                color=TEXT_SECONDARY),
                        dlg_invoice_uploader["component"],
                    ], tight=True, spacing=12,
                        scroll=ft.ScrollMode.AUTO),
                ),
                actions=[
                    ft.Button(
                        "✏️ بروزرسانی" if editing else "💾 ثبت",
                        bgcolor=W if editing else P, color="white",
                        on_click=save_dlg,
                    ),
                    ft.TextButton("انصراف", on_click=close_dlg),
                ],
            )
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()

        available_years = get_available_years()
        current_year_str = str(get_jalali_year())

        year_filter = ft.Dropdown(
            label="سال", width=140,
            value=(current_year_str
                   if current_year_str in [str(y) for y in available_years]
                   else str(available_years[0])),
            options=[ft.dropdown.Option(text=str(y)) for y in available_years],
        )

        def on_year_change(e):
            state["filter_year"] = e.control.value
            refresh_sidebar()

        year_filter.on_change = on_year_change

        search_month_field = ft.TextField(
            label="🔍 جستجوی ماه", width=200,
            on_change=lambda e: (
                state.update({"search_month": e.control.value}),
                refresh_sidebar(),
            ),
        )

        def refresh_all():
            try:
                stats_row_container.content = build_stats_cards()
                try:
                    stats_row_container.update()
                except Exception:
                    pass
            except Exception as ex:
                print(f"❌ خطای stats: {ex}")
                import traceback
                traceback.print_exc()

            try:
                refresh_sidebar()
            except Exception as ex:
                print(f"❌ خطای sidebar: {ex}")
                import traceback
                traceback.print_exc()

            try:
                refresh_details()
            except Exception as ex:
                print(f"❌ خطای details: {ex}")
                import traceback
                traceback.print_exc()

        print("🔵 در حال ساخت صفحه هزینه‌ها...")
        refresh_all()
        print("✅ صفحه هزینه‌ها ساخته شد")

        sidebar = ft.Container(
            width=210, padding=15, border_radius=14, bgcolor=BG_MAIN,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=W, size=20),
                    ft.Text("ماه‌ها", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(expand=True),
                ]),
                ft.Container(height=5),
                search_month_field,
                year_filter,
                ft.Container(height=5),
                months_sidebar,
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
        )

        main_panel = ft.Container(
            expand=True, padding=15, border_radius=14, bgcolor=BG_MAIN,
            content=ft.Container(content=details_panel, expand=True),
        )

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("هزینه‌ها", size=28,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("مدیریت کامل هزینه‌ها بر اساس ماه",
                            size=12, color=TEXT_MUTED),
                ], spacing=2, expand=True),
                ft.Button(
                    "➕ ثبت هزینه جدید",
                    bgcolor=W, color="white", height=42,
                    on_click=lambda e: open_expense_dialog(None),
                ),
            ]),
            ft.Container(height=15),
            stats_row_container,
            ft.Container(height=15),
            ft.Row([
                sidebar, ft.Container(width=15), main_panel,
            ], expand=True, spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.START),
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    # ═══════════ قبوض ═══════════
    def build_bills_page():
        # ═══════ گرفتن رنگ‌های تم ═══════
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_MAIN = theme["bg_main"]
        BG_CARD = theme["bg_card"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        table_col = ft.Column(spacing=0)
        chart_col = ft.Column(spacing=8)
        stats_col = ft.Row(wrap=True, spacing=10)

        current_type = ["آب"]

        # ─── state نمودار (بین رفرش‌ها حفظ می‌شه) ───
        chart_state = {
            "chart_type": "bar_3d",
            "chart_mode": "consumption",
        }

        bill_id = ft.TextField(
            label="💧 شناسه قبض آب *",
            width=280,
        )

        # ═══════════ ثبت دستی قبض ═══════════
        manual_visible = [False]

        manual_amount = ft.TextField(
            label="مبلغ (ریال) *", width=250,
            hint_text="مثال: 79,903,000",
        )

        _current_jmonth = get_jalali_month()
        _current_jyear = get_jalali_year()

        manual_month_dd = ft.Dropdown(
            label="ماه دوره *",
            width=180,
            options=[
                ft.dropdown.Option(text=m)
                for m in MONTHS[1:]
            ],
            value=MONTHS[_current_jmonth],
        )

        manual_year_dd = ft.Dropdown(
            label="سال دوره *",
            width=120,
            options=[
                ft.dropdown.Option(text=str(y))
                for y in range(_current_jyear - 2, _current_jyear + 2)
            ],
            value=str(_current_jyear),
        )

        manual_expense_date = date_field_with_picker(
            "تاریخ هزینه *", 220, default_today=True
        )

        manual_meter = ft.TextField(
            label="شماره کنتور", width=250, hint_text="اختیاری",
        )
        manual_prev_reading = ft.TextField(
            label="قرائت قبلی", width=200, hint_text="اختیاری",
        )
        manual_curr_reading = ft.TextField(
            label="قرائت فعلی", width=200, hint_text="اختیاری",
        )
        manual_desc = ft.TextField(
            label="توضیحات", width=460, hint_text="اختیاری",
        )

        manual_consumption_label = ft.Text(
            "🔢 مصرف محاسبه‌شده: -",
            size=13, weight=ft.FontWeight.BOLD, color=P,
        )

        manual_type_label = ft.Text(
            "نوع فعلی: آب", size=12,
            weight=ft.FontWeight.BOLD, color=P,
        )

        def _to_float_or_zero(val):
            if val is None:
                return 0
            s = str(val).strip()
            if not s:
                return 0
            try:
                return float(unformat_amount(s) or 0)
            except Exception:
                return 0

        def update_consumption_preview(e=None):
            prev_r = _to_float_or_zero(
                manual_prev_reading.value
                if manual_prev_reading.value else ""
            )
            curr_r = _to_float_or_zero(
                manual_curr_reading.value
                if manual_curr_reading.value else ""
            )
            if prev_r > 0 and curr_r > 0:
                cons = max(curr_r - prev_r, 0)
                unit = "m³" if current_type[0] in ["آب", "گاز"] else "kWh"
                manual_consumption_label.value = (
                    f"🔢 مصرف محاسبه‌شده: {cons:,.0f} {unit}"
                )
            else:
                manual_consumption_label.value = "🔢 مصرف محاسبه‌شده: -"
            try:
                page.update()
            except Exception:
                pass

        manual_prev_reading.on_change = update_consumption_preview
        manual_curr_reading.on_change = update_consumption_preview

        def toggle_manual(e):
            manual_visible[0] = not manual_visible[0]
            manual_container.visible = manual_visible[0]
            page.update()

        def save_manual_bill(e):
            if not manual_amount.value or not manual_amount.value.strip():
                msg("مبلغ قبض رو وارد کنید.", D)
                return
            amt = _to_float_or_zero(manual_amount.value)
            if amt <= 0:
                msg("مبلغ نامعتبر.", D)
                return

            if not manual_month_dd.value or not manual_year_dd.value:
                msg("ماه و سال دوره رو انتخاب کنید.", D)
                return

            period_text = f"{manual_month_dd.value} {manual_year_dd.value}"

            expense_date_str = (
                    manual_expense_date.text_field.value or ""
            ).strip()
            try:
                expense_date_obj = parse_date(expense_date_str)
            except Exception:
                expense_date_obj = None

            if expense_date_obj is None:
                msg("تاریخ هزینه نامعتبر است.", D)
                return

            prev_r = _to_float_or_zero(
                manual_prev_reading.value
                if manual_prev_reading.value else ""
            )
            curr_r = _to_float_or_zero(
                manual_curr_reading.value
                if manual_curr_reading.value else ""
            )

            try:
                add_utility_bill_new(
                    bill_type=current_type[0],
                    bill_identifier="",
                    pay_identifier="",
                    period=period_text,
                    from_date=None,
                    to_date=None,
                    previous_reading=prev_r,
                    current_reading=curr_r,
                    amount=amt,
                    consumption_unit=(
                        "m³" if current_type[0] in ["آب", "گاز"]
                        else "kWh"
                    ),
                    issue_date=None,
                    due_date=None,
                    description=(
                        manual_desc.value.strip()
                        if manual_desc.value else "ثبت دستی"
                    ),
                    owner_name="",
                    address="",
                    postal_code="",
                    usage_type="",
                    meter_number=(
                        manual_meter.value.strip()
                        if manual_meter.value else ""
                    ),
                    city="",
                    bill_date="",
                    expense_date_override=expense_date_obj,
                    check_duplicate=False,
                )

                for f in [
                    manual_amount, manual_meter,
                    manual_prev_reading, manual_curr_reading,
                    manual_desc,
                ]:
                    f.value = ""

                manual_consumption_label.value = "🔢 مصرف محاسبه‌شده: -"

                try:
                    manual_month_dd.value = MONTHS[get_jalali_month()]
                    manual_year_dd.value = str(get_jalali_year())
                except Exception:
                    pass

                try:
                    manual_expense_date.text_field.value = get_today_jalali()
                except Exception:
                    pass

                manual_visible[0] = False
                manual_container.visible = False
                load()
                page.update()
                msg("✅ قبض به صورت دستی ثبت شد.", S)
            except Exception as ex:
                msg(f"خطا: {ex}", D)
                import traceback
                traceback.print_exc()

        manual_container = ft.Container(
            visible=False,
            bgcolor=BG_CARD,
            border_radius=14,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.EDIT, color=W, size=22),
                    ft.Text("ثبت دستی قبض", size=16,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(expand=True),
                    ft.Container(
                        bgcolor=theme["primary_bg"],
                        border_radius=8, padding=10,
                        content=manual_type_label,
                    ),
                ]),
                ft.Divider(height=1, color=DIVIDER),
                ft.Container(
                    bgcolor=theme["warning_bg"],
                    border_radius=8, padding=10,
                    content=ft.Column([
                        ft.Text("💡 راهنما:", size=12,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text(
                            "«مبلغ»، «دوره» و «تاریخ هزینه» ضروری هستند.",
                            size=11, color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            "هزینه در ماهِ «تاریخ هزینه» ثبت می‌شود.",
                            size=11, color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            "با وارد کردن قرائت قبلی و فعلی، مصرف خودکار محاسبه می‌شود.",
                            size=11, color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            "نوع قبض از دکمه‌های «آب / برق / گاز» بالای صفحه انتخاب می‌شود.",
                            size=11, color=TEXT_SECONDARY,
                        ),
                    ], spacing=3)
                ),
                ft.Row([
                    ft.Text("🔴 ضروری:", size=12,
                            weight=ft.FontWeight.BOLD, color=D),
                ]),
                ft.Row([manual_amount], wrap=True, spacing=10),
                ft.Row([manual_month_dd, manual_year_dd],
                       wrap=True, spacing=10),
                ft.Row([manual_expense_date],
                       wrap=True, spacing=10),
                ft.Divider(height=1, color=DIVIDER),
                ft.Row([
                    ft.Text("⚪ اختیاری:", size=12,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_SECONDARY),
                ]),
                ft.Row([manual_meter], wrap=True, spacing=10),
                ft.Row([manual_prev_reading, manual_curr_reading],
                       wrap=True, spacing=10),
                ft.Container(
                    bgcolor=theme["primary_bg"],
                    border_radius=8, padding=10,
                    content=manual_consumption_label,
                ),
                ft.Row([manual_desc], wrap=True, spacing=10),
                ft.Row([
                    ft.Button(
                        "💾 ثبت قبض دستی",
                        bgcolor=S, color="white",
                        on_click=save_manual_bill,
                        width=180,
                    ),
                ]),
            ], spacing=10)
        )

        # ═══════════ تغییر نوع قبض ═══════════
        def change_type(new_type):
            current_type[0] = new_type

            saved = ""
            icons = {"آب": "💧", "برق": "⚡", "گاز": "🔥"}
            icon = icons.get(new_type, "")

            if new_type == "آب":
                saved = get_setting("water_bill_id", "")
            elif new_type == "برق":
                saved = get_setting("electricity_bill_id", "")
            elif new_type == "گاز":
                saved = get_setting("gas_bill_id", "")

            bill_id.value = saved
            bill_id.label = f"{icon} شناسه قبض {new_type} *"

            btn_water.bgcolor = P if new_type == "آب" else theme["bg_hover"]
            btn_water.color = "white" if new_type == "آب" else TEXT_SECONDARY

            btn_elec.bgcolor = W if new_type == "برق" else theme["bg_hover"]
            btn_elec.color = "white" if new_type == "برق" else TEXT_SECONDARY

            btn_gas.bgcolor = D if new_type == "گاز" else theme["bg_hover"]
            btn_gas.color = "white" if new_type == "گاز" else TEXT_SECONDARY

            try:
                manual_type_label.value = f"نوع فعلی: {new_type}"
                update_consumption_preview()
            except Exception:
                pass

            page.update()
            load()

        btn_water = ft.Button(
            "💧 آب",
            bgcolor=P, color="white",
            width=110, height=45,
            on_click=lambda e: change_type("آب")
        )
        btn_elec = ft.Button(
            "⚡ برق",
            bgcolor=theme["bg_hover"], color=TEXT_SECONDARY,
            width=110, height=45,
            on_click=lambda e: change_type("برق")
        )
        btn_gas = ft.Button(
            "🔥 گاز",
            bgcolor=theme["bg_hover"], color=TEXT_SECONDARY,
            width=110, height=45,
            on_click=lambda e: change_type("گاز")
        )
        bt_container = ft.Row([btn_water, btn_elec, btn_gas], spacing=8)

        # ═══════════ محاسبه‌گر سهم ═══════════
        calc_visible = [False]
        calc_amount = make_amount_field(
            label="مبلغ کل قبض (ریال)",
            width=250,
            hint="مثال: 79,903,000"
        )
        calc_result_col = ft.Column(spacing=0)

        def toggle_calculator(e):
            calc_visible[0] = not calc_visible[0]
            calc_container.visible = calc_visible[0]
            page.update()

        def do_calculate(e):
            if not calc_amount.value:
                msg("مبلغ قبض رو وارد کنید.", D)
                return
            try:
                amt = float(unformat_amount(calc_amount.value) or 0)
            except ValueError:
                msg("مبلغ نامعتبر.", D)
                return
            shares = calculate_bill_shares(current_type[0], amt)
            if not shares:
                msg("واحد ساکن‌داری ثبت نشده.", D)
                return
            calc_result_col.controls.clear()
            methods = {"آب": "نفرات", "گاز": "متراژ", "برق": "مساوی"}
            method_label = methods.get(current_type[0], "")
            calc_result_col.controls.append(
                ft.Container(
                    bgcolor=P, border_radius=10, padding=10,
                    content=ft.Row([
                        ft.Text("واحد", width=60, color="white",
                                weight=ft.FontWeight.BOLD, size=12),
                        ft.Text("ساکن", width=120, color="white",
                                weight=ft.FontWeight.BOLD, size=12),
                        ft.Text(method_label, width=80, color="white",
                                weight=ft.FontWeight.BOLD, size=12),
                        ft.Text("سهم (ریال)", width=120, color="white",
                                weight=ft.FontWeight.BOLD, size=12),
                        ft.Text("سهم (تومان)", width=120, color="white",
                                weight=ft.FontWeight.BOLD, size=12),
                    ], spacing=4)
                )
            )
            for i, s in enumerate(shares):
                bg = theme["bg_table_row1"] if i % 2 == 0 else theme["bg_table_row2"]
                calc_result_col.controls.append(
                    ft.Container(
                        bgcolor=bg, padding=8,
                        content=ft.Row([
                            ft.Text(s["unit_number"], width=60, size=12, color=TEXT_MAIN),
                            ft.Text(s["resident_name"] or "-", width=120, size=12, color=TEXT_SECONDARY),
                            ft.Text(f'{s["factor"]} {s["factor_label"]}', width=80, size=12, color=TEXT_SECONDARY),
                            ft.Text(f'{s["share"]:,.0f}', width=120, size=12,
                                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                            ft.Text(f'{s["share"] / 10:,.0f}', width=120, size=12, color=S),
                        ], spacing=4)
                    )
                )
            total = sum(s["share"] for s in shares)
            calc_result_col.controls.append(
                ft.Container(
                    bgcolor=theme["primary_bg"],
                    border_radius=10, padding=10,
                    content=ft.Row([
                        ft.Text("جمع کل:", width=260, weight=ft.FontWeight.BOLD,
                                size=13, color=TEXT_MAIN),
                        ft.Text(f'{total:,.0f}', width=120, size=13,
                                weight=ft.FontWeight.BOLD, color=D),
                        ft.Text(f'{total / 10:,.0f} تومان', width=120, size=13,
                                weight=ft.FontWeight.BOLD, color=S),
                    ], spacing=4)
                )
            )
            page.update()

        calc_container = ft.Container(
            visible=False,
            bgcolor=BG_CARD,
            border_radius=14,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CALCULATE, color=theme["purple"], size=22),
                    ft.Text("محاسبه سهم هر واحد از قبض", size=16,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                ft.Divider(height=1, color=DIVIDER),
                ft.Container(
                    bgcolor=theme["warning_bg"],
                    border_radius=8, padding=10,
                    content=ft.Column([
                        ft.Text("💡 روش محاسبه:", size=12,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text("💧 آب: بر اساس تعداد نفرات", size=11, color=TEXT_SECONDARY),
                        ft.Text("🔥 گاز: بر اساس متراژ", size=11, color=TEXT_SECONDARY),
                        ft.Text("⚡ برق: تقسیم مساوی", size=11, color=TEXT_SECONDARY),
                    ], spacing=3)
                ),
                ft.Row([
                    calc_amount,
                    ft.Button("🧮 محاسبه", bgcolor=theme["purple"],
                              color="white", on_click=do_calculate),
                ], wrap=True),
                calc_result_col,
            ], spacing=10)
        )

        # ═══════════ باز کردن قبضینو ═══════════
        def open_ghabzino(e):
            urls = {
                "آب": "https://ghabzino.com/water",
                "برق": "https://ghabzino.com/electricity",
                "گاز": "https://ghabzino.com/gas",
            }
            url = urls.get(current_type[0], "https://ghabzino.com")

            if bill_id.value and bill_id.value.strip():
                copied = copy_to_clipboard(page, bill_id.value.strip())
                if copied:
                    clipboard_msg = "✅ شناسه به کلیپ‌بورد کپی شد!"
                else:
                    clipboard_msg = ("⚠️ شناسه را دستی کپی کنید: "
                                     + bill_id.value.strip())
            else:
                clipboard_msg = ""

            try:
                webbrowser.open(url)
                show_ghabzino_guide(clipboard_msg)
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        def show_ghabzino_guide(clipboard_msg=""):
            def close_dlg(e):
                guide_dlg.open = False
                page.update()

            def do_paste(e):
                guide_dlg.open = False
                page.update()
                paste_from_clipboard()

            items = []
            if clipboard_msg:
                items.append(ft.Container(
                    bgcolor=theme["success_bg"],
                    border_radius=8, padding=12,
                    content=ft.Text(clipboard_msg, size=13, color=S,
                                    weight=ft.FontWeight.BOLD)
                ))
                items.append(ft.Divider(color=DIVIDER))

            items.extend([
                ft.Text("📋 مراحل:", size=15,
                        weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("1️⃣ در قبضینو، شناسه رو Paste کنید (Ctrl+V)",
                                size=13, color=TEXT_SECONDARY),
                        ft.Text("2️⃣ «استعلام» را بزنید", size=13, color=TEXT_SECONDARY),
                        ft.Text("3️⃣ «جزئیات» را باز کنید", size=13, color=TEXT_SECONDARY),
                        ft.Text("4️⃣ Ctrl+A و بعد Ctrl+C کنید", size=13, color=TEXT_SECONDARY),
                        ft.Text("5️⃣ برگردید و «دریافت از کلیپ‌بورد» بزنید",
                                size=13, color=P, weight=ft.FontWeight.BOLD),
                    ], spacing=6)
                ),
            ])

            guide_dlg = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.HELP_OUTLINE, color=P, size=28),
                    ft.Text("راهنمای قبضینو", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=500, bgcolor=BG_CARD,
                    content=ft.Column(items, spacing=10, tight=True)
                ),
                actions=[
                    ft.Button("📥 دریافت از کلیپ‌بورد", bgcolor=S,
                              color="white", on_click=do_paste),
                    ft.TextButton("بستن", on_click=close_dlg),
                ],
            )
            if guide_dlg not in page.overlay:
                page.overlay.append(guide_dlg)
            guide_dlg.open = True
            page.update()

        # ═══════════ دریافت از کلیپ‌بورد ═══════════
        def paste_from_clipboard(e=None):
            text = ""
            try:
                import pyperclip
                text = pyperclip.paste()
            except ImportError:
                msg("لطفاً pyperclip رو نصب کنید:\n"
                    "pip install pyperclip", D)
                return
            except Exception:
                pass

            if not text:
                try:
                    if hasattr(page, 'clipboard'):
                        text = page.clipboard or ""
                    elif hasattr(page, 'get_clipboard'):
                        text = page.get_clipboard() or ""
                except Exception:
                    pass

            if not text or len(text.strip()) < 20:
                msg("❌ کلیپ‌بورد خالیه یا کوتاهه.\n"
                    "از سایت قبضینو یا آپ Ctrl+A و Ctrl+C کنید.", D)
                return

            loading_dlg = ft.AlertDialog(
                modal=True,
                content=ft.Container(
                    width=300, height=120, bgcolor=BG_CARD,
                    content=ft.Column([
                        ft.ProgressRing(color=P),
                        ft.Text("در حال پردازش...", size=14, color=TEXT_MAIN),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15)
                ),
            )
            if loading_dlg not in page.overlay:
                page.overlay.append(loading_dlg)
            loading_dlg.open = True
            page.update()

            try:
                result = parse_bill_text(text, forced_type=current_type[0])
                loading_dlg.open = False
                page.update()

                if not result:
                    msg("❌ نتونستم اطلاعات رو استخراج کنم.\n"
                        "متن رو چک کنید یا از سایت رسمی امتحان کنید.", D)
                    return

                if (result.get("bill_type") and
                        result["bill_type"] != current_type[0]):
                    detected = result["bill_type"]
                    change_type(detected)

                if result.get("bill_id"):
                    dup = check_duplicate_bill(
                        bill_type=current_type[0],
                        from_date=result.get("from_date"),
                        to_date=result.get("to_date"),
                        bill_identifier=result.get("bill_id"),
                        period=result.get("period"),
                    )
                    if dup["exists"]:
                        show_duplicate_dialog(dup["message"], result)
                        return

                show_result_dialog(result)

            except Exception as ex:
                loading_dlg.open = False
                page.update()
                import traceback
                traceback.print_exc()
                msg(f"خطا: {ex}", D)

        # ═══════════ دیالوگ تکراری ═══════════
        def show_duplicate_dialog(message, data):
            def close_dlg(e):
                dup_dlg.open = False
                page.update()

            def force_save(e):
                dup_dlg.open = False
                page.update()
                show_result_dialog(data, allow_duplicate=True)

            dup_dlg = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=W, size=28),
                    ft.Text("قبض تکراری!", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=450, bgcolor=BG_CARD,
                    content=ft.Column([
                        ft.Container(
                            bgcolor=theme["warning_bg"],
                            border_radius=8, padding=12,
                            content=ft.Text(message, size=13, color=W)
                        ),
                        ft.Text("می‌خواهید ثبت کنید؟", size=13, color=TEXT_SECONDARY),
                    ], spacing=8, tight=True)
                ),
                actions=[
                    ft.Button("بله، ثبت شود", bgcolor=W, color="white",
                              on_click=force_save),
                    ft.TextButton("خیر", on_click=close_dlg),
                ],
            )
            if dup_dlg not in page.overlay:
                page.overlay.append(dup_dlg)
            dup_dlg.open = True
            page.update()

        # ═══════════ نمایش نتیجه ═══════════
        def show_result_dialog(data, allow_duplicate=False):
            def save_directly(e):
                try:
                    add_utility_bill(
                        bill_type=current_type[0],
                        bill_identifier=(data.get("bill_id", "") or bill_id.value),
                        pay_identifier=data.get("pay_id", ""),
                        period=data.get("period", ""),
                        from_date=data.get("from_date"),
                        to_date=data.get("to_date"),
                        previous_reading=data.get("previous_reading", 0),
                        current_reading=data.get("current_reading", 0),
                        amount=data.get("amount", 0),
                        consumption_unit=("m³" if current_type[0] in ["آب", "گاز"] else "kWh"),
                        issue_date=data.get("issue_date"),
                        due_date=data.get("due_date"),
                        description="ثبت خودکار",
                        owner_name=data.get("owner_name", ""),
                        address=data.get("address", ""),
                        postal_code=data.get("postal_code", ""),
                        usage_type=data.get("usage_type", ""),
                        meter_number=data.get("meter_number", ""),
                        city=data.get("city", ""),
                        bill_date=data.get("bill_date", ""),
                        check_duplicate=(not allow_duplicate),
                    )
                    result_dlg.open = False
                    load()
                    page.update()
                    msg("✅ قبض ثبت شد و به‌طور خودکار در هزینه‌ها ثبت گردید.", S)
                except Exception as ex:
                    msg(f"خطا: {ex}", D)

            def close_dlg(e):
                result_dlg.open = False
                page.update()

            def info_row(label, value, color=None):
                if value is None or str(value).strip() == "":
                    return None
                if str(value).strip() in ("0", "0.0"):
                    return None
                return ft.Row([
                    ft.Text(label, width=140, weight=ft.FontWeight.BOLD,
                            size=13, color=TEXT_SECONDARY),
                    ft.Text(str(value), expand=True, size=13,
                            color=color or TEXT_MAIN, selectable=True),
                ], spacing=8)

            def build_section(title, bg, tc, rows):
                filtered = [r for r in rows if r is not None]
                if not filtered:
                    return None
                return ft.Container(
                    bgcolor=bg, border_radius=8, padding=15,
                    content=ft.Column([
                        ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=tc),
                        ft.Divider(height=1, color=DIVIDER),
                        *filtered,
                    ], spacing=6)
                )

            content_items = []

            sec = build_section(
                "👤 اطلاعات مشترک", theme["purple_bg"], theme["purple"],
                [
                    info_row("نام مالک:", data.get("owner_name")),
                    info_row("شهر:", data.get("city")),
                    info_row("آدرس:", data.get("address")),
                    info_row("کد پستی:", data.get("postal_code")),
                    info_row("نوع مصرف:", data.get("usage_type")),
                    info_row("شماره کنتور:", data.get("meter_number")),
                ]
            )
            if sec:
                content_items.append(sec)
                content_items.append(ft.Container(height=8))

            sec = build_section(
                "🔑 اطلاعات قبض", theme["success_bg"], S,
                [
                    info_row("شناسه قبض:", data.get("bill_id")),
                    info_row("دوره:", data.get("period")),
                    info_row("تاریخ صدور:", data.get("issue_date")),
                ]
            )
            if sec:
                content_items.append(sec)
                content_items.append(ft.Container(height=8))

            sec = build_section(
                "📅 تاریخ‌ها", theme["warning_bg"], W,
                [
                    info_row("قرائت قبلی:", data.get("from_date")),
                    info_row("قرائت فعلی:", data.get("to_date")),
                    info_row("تعداد روز:",
                             str(data.get("days_count", 0)) if data.get("days_count") else None),
                    info_row("مهلت پرداخت:", data.get("due_date"), D),
                ]
            )
            if sec:
                content_items.append(sec)
                content_items.append(ft.Container(height=8))

            sec = build_section(
                "📊 مصرف", theme["primary_bg"], P,
                [
                    info_row("کنتور قبلی:",
                             f'{data.get("previous_reading", 0):,.0f}' if data.get("previous_reading") else None),
                    info_row("کنتور فعلی:",
                             f'{data.get("current_reading", 0):,.0f}' if data.get("current_reading") else None),
                    info_row("مصرف:",
                             f'{data.get("consumption", 0):,.0f}' if data.get("consumption") else None, P),
                ]
            )
            if sec:
                content_items.append(sec)
                content_items.append(ft.Container(height=8))

            content_items.append(ft.Container(
                bgcolor=theme["danger_bg"], border_radius=8, padding=15,
                content=ft.Row([
                    ft.Text("💰 مبلغ:", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(expand=True),
                    ft.Text(f'{data.get("amount", 0):,.0f} ریال', size=20,
                            weight=ft.FontWeight.BOLD, color=D),
                ])
            ))

            result_dlg = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=S, size=28),
                    ft.Text(f"استعلام قبض {current_type[0]}", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=580, height=550, bgcolor=BG_CARD,
                    content=ft.Column(content_items, spacing=0,
                                      scroll=ft.ScrollMode.AUTO, tight=True)
                ),
                actions=[
                    ft.Button("💾 ثبت قبض", bgcolor=S, color="white",
                              on_click=save_directly),
                    ft.TextButton("بستن", on_click=close_dlg),
                ],
            )
            if result_dlg not in page.overlay:
                page.overlay.append(result_dlg)
            result_dlg.open = True
            page.update()

        # ═══════════ جزئیات ═══════════
        def show_bill_details(b):
            def close_dlg(e):
                details_dlg.open = False
                page.update()

            def info_row(label, value):
                if not value or str(value).strip() == "":
                    return None
                if str(value).strip() in ("0", "0.0"):
                    return None
                return ft.Row([
                    ft.Text(label, width=150, weight=ft.FontWeight.BOLD,
                            size=13, color=TEXT_SECONDARY),
                    ft.Text(str(value), expand=True, size=13,
                            color=TEXT_MAIN, selectable=True),
                ], spacing=8)

            rows = [
                info_row("نوع قبض:", b.get("bill_type")),
                info_row("شناسه قبض:", b.get("bill_identifier")),
                info_row("دوره:", b.get("period")),
                info_row("نام مالک:", b.get("owner_name")),
                info_row("شهر:", b.get("city")),
                info_row("آدرس:", b.get("address")),
                info_row("کد پستی:", b.get("postal_code")),
                info_row("نوع مصرف:", b.get("usage_type")),
                info_row("شماره کنتور:", b.get("meter_number")),
                info_row("قرائت قبلی:", to_jalali(b.get("from_date"))),
                info_row("قرائت فعلی:", to_jalali(b.get("to_date"))),
                info_row("تعداد روز:",
                         str(b.get("days_count", 0)) if b.get("days_count") else None),
                info_row("کنتور قبلی:",
                         f'{b.get("previous_reading", 0):,.0f}' if b.get("previous_reading") else None),
                info_row("کنتور فعلی:",
                         f'{b.get("current_reading", 0):,.0f}' if b.get("current_reading") else None),
                info_row("مصرف کل:",
                         (f'{b.get("consumption", 0):,.0f} {b.get("consumption_unit", "")}')
                         if b.get("consumption") else None),
                info_row("مصرف روزانه:",
                         f'{b.get("daily_avg_consumption", 0):.2f}' if b.get("daily_avg_consumption") else None),
                info_row("مبلغ:",
                         f'{b.get("amount", 0):,.0f} ریال' if b.get("amount") else None),
                info_row("مبلغ روزانه:",
                         f'{b.get("daily_avg_amount", 0):,.0f} ریال' if b.get("daily_avg_amount") else None),
                info_row("مهلت پرداخت:", to_jalali(b.get("due_date"))),
            ]
            filtered = [r for r in rows if r is not None]

            details_dlg = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.INFO, color=P, size=26),
                    ft.Text(f"جزئیات قبض {b.get('bill_type')}", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=580, height=550, bgcolor=BG_CARD,
                    content=ft.Column(filtered, spacing=6,
                                      scroll=ft.ScrollMode.AUTO, tight=True)
                ),
                actions=[ft.TextButton("بستن", on_click=close_dlg)],
            )
            if details_dlg not in page.overlay:
                page.overlay.append(details_dlg)
            details_dlg.open = True
            page.update()

        # ═══════════ آمار ═══════════
        def load_stats():
            stats_col.controls.clear()
            stats = get_bill_stats(current_type[0])
            if not stats:
                stats_col.controls.append(
                    ft.Text("هنوز قبضی ثبت نشده.", color=TEXT_MUTED)
                )
                return
            unit = "m³" if current_type[0] in ["آب", "گاز"] else "kWh"

            def stat_card(icon, title, value, color):
                return ft.Container(
                    width=180, padding=12, border_radius=10, bgcolor=BG_CARD,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(icon, size=18),
                            ft.Text(title, size=11, color=TEXT_SECONDARY),
                        ], spacing=4),
                        ft.Text(value, size=15, weight=ft.FontWeight.BOLD, color=color),
                    ], spacing=4)
                )

            stats_col.controls.extend([
                stat_card("📊", f"جمع کل مصرف ({unit})", f'{stats["total_consumption"]:,.0f}', P),
                stat_card("💰", f"جمع کل مبلغ ({get_currency_label()})",
                          fmt_money(stats["total_amount"] / 10, show_unit=False), D),
                stat_card("📈", f"میانگین مصرف ({unit})", f'{stats["avg_monthly_consumption"]:,.2f}', W),
                stat_card("💵", f"میانگین مبلغ ({get_currency_label()})",
                          fmt_money(stats["avg_monthly_amount"] / 10, show_unit=False), W),
                stat_card("⬆️", f"بیشترین مصرف ({unit})", f'{stats["max_consumption"]:,.0f}', D),
                stat_card("⬇️", f"کمترین مصرف ({unit})", f'{stats["min_consumption"]:,.0f}', S),
                stat_card("🔺", f"بیشترین مبلغ ({get_currency_label()})",
                          fmt_money(stats["max_amount"] / 10, show_unit=False), D),
                stat_card("🔻", f"کمترین مبلغ ({get_currency_label()})",
                          fmt_money(stats["min_amount"] / 10, show_unit=False), S),
                stat_card("📅", "تعداد قبوض", f'{stats["count"]}', P),
            ])

        # ═══════════ لود جدول ═══════════
        def load():
            table_col.controls.clear()
            rows = list_utility_bills(current_type[0])
            if not rows:
                table_col.controls.append(ft.Container(
                    bgcolor=BG_CARD, padding=20, border_radius=12,
                    content=ft.Text(f"قبض {current_type[0]} ثبت نشده.", color=TEXT_MUTED)
                ))
                load_chart()
                load_stats()
                page.update()
                return

            header = ft.Container(
                bgcolor=P, border_radius=12, padding=10,
                content=ft.Row([
                    ft.Text("#", width=30, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("دوره", width=100, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("از", width=100, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("تا", width=100, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("روز", width=40, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("قبلی", width=80, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("فعلی", width=80, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("مصرف", width=80, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("روزانه", width=80, color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text(f"مبلغ ({get_currency_label()})", width=110,
                            color="white", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("عملیات", width=140, color="white", weight=ft.FontWeight.BOLD, size=12),
                ], spacing=4)
            )
            table_col.controls.append(header)

            for i, b in enumerate(rows):
                bg = theme["bg_table_row1"] if i % 2 == 0 else theme["bg_table_row2"]
                extra_info = []
                if b.get("owner_name"):
                    extra_info.append(f'👤 {b["owner_name"]}')
                if b.get("meter_number"):
                    extra_info.append(f'کنتور: {b["meter_number"]}')

                row_content = ft.Row([
                    ft.Text(str(i + 1), width=30, size=12, color=TEXT_MAIN),
                    ft.Text(b["period"] or "-", width=100, size=11, color=TEXT_SECONDARY),
                    ft.Text(to_jalali(b["from_date"]) or "-", width=100, size=11, color=TEXT_SECONDARY),
                    ft.Text(to_jalali(b["to_date"]) or "-", width=100, size=11, color=TEXT_SECONDARY),
                    ft.Text(str(b["days_count"]), width=40, size=12, color=TEXT_MAIN),
                    ft.Text(f'{b["previous_reading"]:.0f}', width=80, size=12, color=TEXT_SECONDARY),
                    ft.Text(f'{b["current_reading"]:.0f}', width=80, size=12, color=TEXT_SECONDARY),
                    ft.Text(f'{b["consumption"]:.0f}', width=80, size=12,
                            weight=ft.FontWeight.BOLD, color=P),
                    ft.Text(f'{b["daily_avg_consumption"]:.2f}', width=80, size=12,
                            color=TEXT_SECONDARY),
                    ft.Text(
                        fmt_money((b.get("amount", 0) or 0) / 10, show_unit=False),
                        width=110, size=12,
                        weight=ft.FontWeight.BOLD, color=TEXT_MAIN
                    ),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.INFO_OUTLINE, icon_color=P,
                                      icon_size=18, tooltip="جزئیات",
                                      on_click=lambda e, bb=b: show_bill_details(bb)),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=D,
                                      icon_size=18, tooltip="حذف",
                                      on_click=lambda e, bid=b["id"]: do_del(bid)),
                    ], spacing=0, width=140),
                ], spacing=4)

                if extra_info:
                    cell = ft.Container(
                        bgcolor=bg, padding=8,
                        content=ft.Column([
                            row_content,
                            ft.Text(" | ".join(extra_info), size=11,
                                    color=TEXT_MUTED, italic=True)
                        ], spacing=4)
                    )
                else:
                    cell = ft.Container(bgcolor=bg, padding=8, content=row_content)
                table_col.controls.append(cell)

            load_chart()
            load_stats()
            page.update()

        def do_del(bid):
            try:
                delete_utility_bill(bid)
                load()
                msg("قبض حذف شد.", W)
            except Exception as ex:
                msg(str(ex), D)

        # ═══════════ نمودار ═══════════
        def load_chart():
            chart_col.controls.clear()

            data = get_consumption_chart_data(current_type[0])
            if not data:
                chart_col.controls.append(
                    ft.Container(
                        padding=40, alignment=ft.Alignment.CENTER,
                        content=ft.Column([
                            ft.Icon(ft.Icons.INSERT_CHART_OUTLINED,
                                    size=50, color=TEXT_MUTED),
                            ft.Text("داده‌ای برای نمایش نیست",
                                    size=12, color=TEXT_MUTED,
                                    weight=ft.FontWeight.BOLD),
                        ], spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )
                try:
                    chart_col.update()
                except Exception:
                    pass
                return

            try:
                from chart_generator import generate_chart, CHART_TYPES
            except ImportError as ex:
                chart_col.controls.append(
                    ft.Text(f"❌ chart_generator: {ex}", color=D, size=11))
                try:
                    chart_col.update()
                except Exception:
                    pass
                return

            KEY_TO_TITLE = {k: t for k, t, _ in CHART_TYPES}
            TITLE_TO_KEY = {t: k for k, t, _ in CHART_TYPES}

            MODE_TITLE_TO_KEY = {
                "📊 مصرف": "consumption",
                "💰 مبلغ": "amount",
            }
            MODE_KEY_TO_TITLE = {v: k for k, v in MODE_TITLE_TO_KEY.items()}

            is_dark = is_dark_mode()
            unit = "m³" if current_type[0] in ["آب", "گاز"] else "kWh"

            def _render_b64(ct, md):
                ul = unit if md == "consumption" else get_currency_label()
                res = generate_chart(
                    chart_type=ct,
                    data=data,
                    bill_type=current_type[0],
                    unit_label=ul,
                    is_dark=is_dark,
                    mode=md,
                )
                if not res.get("success"):
                    print(f"⚠️ render error: {res.get('message')}")
                    return None
                return _read_image_base64(res["path"])

            dd_type = ft.Dropdown(
                label="نوع نمودار",
                width=220,
                value=KEY_TO_TITLE.get(chart_state["chart_type"], "میله سه‌بعدی"),
                options=[ft.dropdown.Option(text=t) for _, t, _ in CHART_TYPES],
            )

            def on_type_change(e):
                chart_state["chart_type"] = TITLE_TO_KEY.get(
                    e.control.value, "bar_3d"
                )
                load_chart()

            dd_type.on_change = on_type_change

            dd_mode = ft.Dropdown(
                label="نمایش",
                width=170,
                value=MODE_KEY_TO_TITLE.get(chart_state["chart_mode"], "📊 مصرف"),
                options=[ft.dropdown.Option(text=t) for t in MODE_TITLE_TO_KEY.keys()],
            )

            def on_mode_change(e):
                chart_state["chart_mode"] = MODE_TITLE_TO_KEY.get(
                    e.control.value, "consumption"
                )
                load_chart()

            dd_mode.on_change = on_mode_change

            chart_col.controls.append(
                ft.Container(
                    padding=14, border_radius=12, bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Container(
                            width=38, height=38, border_radius=10,
                            bgcolor=theme["primary_bg"],
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.INSIGHTS, color=P, size=20),
                        ),
                        ft.Column([
                            ft.Text("نمودار", size=13,
                                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                            ft.Text("نوع نمودار و نمایش را انتخاب کنید",
                                    size=10, color=TEXT_MUTED),
                        ], spacing=1, expand=True),
                        dd_type,
                        dd_mode,
                    ], spacing=12),
                )
            )

            chart_col.controls.append(ft.Container(height=12))

            b64 = _render_b64(chart_state["chart_type"], chart_state["chart_mode"])

            if b64:
                chart_col.controls.append(
                    ft.Container(
                        padding=20,
                        border_radius=14,
                        bgcolor=BG_CARD,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Image(
                            src=b64,
                            height=420,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                    )
                )
            else:
                chart_col.controls.append(
                    ft.Container(
                        padding=50,
                        border_radius=14,
                        bgcolor=BG_CARD,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Column([
                            ft.Icon(ft.Icons.ERROR_OUTLINE, size=44, color=D),
                            ft.Text("خطا در ساخت نمودار",
                                    color=D, size=13,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("لطفاً نوع نمودار دیگری را انتخاب کنید",
                                    color=TEXT_MUTED, size=11),
                        ], spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )

            try:
                chart_col.update()
            except Exception:
                pass

        # ═══════════ خروجی PDF قبوض ═══════════
        def export_bills_pdf(e):
            try:
                from pdf_generator import generate_bills_report_pdf
                from chart_generator import generate_chart
            except Exception as ex:
                msg(f"❌ import: {ex}", D)
                return
            try:
                b_info = get_building_info()
                logo_path = get_logo_path()
                theme_color = get_setting("logo_bg_color", "#1565C0")

                bills = list_utility_bills(current_type[0])
                stats = get_bill_stats(current_type[0])

                if not bills:
                    msg("قبضی برای این نوع ثبت نشده.", W)
                    return

                # ─── ساخت نمودارها برای PDF ───
                chart_data = get_consumption_chart_data(current_type[0])
                unit = "m³" if current_type[0] in ["آب", "گاز"] else "kWh"
                chart_paths = {}

                print("=" * 60)
                print(f"📊 ساخت نمودارها برای PDF - نوع: {current_type[0]}")

                # مصرف
                for ct in ["bar_3d", "area", "bubble"]:
                    try:
                        res = generate_chart(
                            chart_type=ct,
                            data=chart_data,
                            bill_type=current_type[0],
                            unit_label=unit,
                            is_dark=False,
                            mode="consumption",
                        )
                        if res.get("success") and res.get("path"):
                            chart_paths[ct] = res["path"]
                            print(f"  ✅ {ct}: {res['path']}")
                    except Exception as ex_inner:
                        print(f"  ❌ {ct}: {ex_inner}")

                # مبلغ (فقط bar_3d)
                try:
                    res = generate_chart(
                        chart_type="bar_3d",
                        data=chart_data,
                        bill_type=current_type[0],
                        unit_label=get_currency_label(),
                        is_dark=False,
                        mode="amount",
                    )
                    if res.get("success") and res.get("path"):
                        chart_paths["bar_3d_amount"] = res["path"]
                        print(f"  ✅ bar_3d_amount: {res['path']}")
                except Exception as ex_inner:
                    print(f"  ❌ bar_3d_amount: {ex_inner}")

                print(f"📊 کل نمودارهای ساخته‌شده: {len(chart_paths)}")
                print("=" * 60)

                result = generate_bills_report_pdf(
                    bill_type=current_type[0],
                    bills=bills,
                    building_name=b_info["name"],
                    building_info={
                        "address": b_info["address"],
                        "floors": b_info["floors"],
                        "total_units": b_info["total_units"],
                    },
                    currency_label=get_currency_label(),
                    logo_path=logo_path,
                    theme_color=theme_color,
                    stats=stats,
                    chart_paths=chart_paths,
                )

                if result.get("success"):
                    msg("✅ PDF ساخته شد.", S)
                    try:
                        os.startfile(result["path"])
                    except Exception:
                        pass
                else:
                    msg(result.get("message", "خطا"), D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)
                import traceback
                traceback.print_exc()

        # لود اولیه
        initial_saved = get_setting("water_bill_id", "")
        bill_id.value = initial_saved
        bill_id.label = "💧 شناسه قبض آب *"
        load()

        # ═══════════ UI ═══════════
        return ft.Column([
            ft.Text("قبوض ساختمان", size=28,
                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),

            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Text("🔍 استعلام قبض از قبضینو (رایگان)", size=16,
                            weight=ft.FontWeight.BOLD, color="#00A86B"),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Container(
                        bgcolor=theme["success_bg"], border_radius=8, padding=10,
                        content=ft.Column([
                            ft.Text("💡 روش استفاده:", size=12,
                                    weight=ft.FontWeight.BOLD, color=S),
                            ft.Text("1. شناسه قبض رو وارد کنید", size=11, color=TEXT_SECONDARY),
                            ft.Text("2. «باز کردن قبضینو» رو بزنید", size=11, color=TEXT_SECONDARY),
                            ft.Text("3. در قبضینو استعلام بگیرید", size=11, color=TEXT_SECONDARY),
                            ft.Text("4. Ctrl+A بعد Ctrl+C کنید", size=11, color=TEXT_SECONDARY),
                            ft.Text("5. «دریافت از کلیپ‌بورد» بزنید", size=11,
                                    color=S, weight=ft.FontWeight.BOLD),
                        ], spacing=3)
                    ),
                    ft.Row([
                        ft.Text("نوع قبض:", size=13,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        bt_container,
                    ], spacing=10),
                    ft.Container(height=4),
                    ft.Row([bill_id]),
                    ft.Row([
                        ft.Button("🌐 باز کردن قبضینو", bgcolor="#00A86B",
                                  color="white", on_click=open_ghabzino, width=200),
                        ft.Button("📥 دریافت از کلیپ‌بورد", bgcolor=S,
                                  color="white", on_click=paste_from_clipboard,
                                  width=210),
                    ], wrap=True),
                ], spacing=10)
            ),

            ft.Container(height=4),

            ft.Row([
                ft.Button("🧮 محاسبه‌گر سهم قبض هر واحد",
                          bgcolor=theme["purple"], color="white",
                          on_click=toggle_calculator),
                ft.Button("✏️ ثبت دستی قبض", bgcolor=W, color="white",
                          on_click=toggle_manual),
                ft.Button("📄 خروجی PDF", bgcolor=S, color="white",
                          on_click=export_bills_pdf),
            ], wrap=True, spacing=10),

            calc_container,
            manual_container,

            ft.Container(height=8),

            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Text("📈 خلاصه گزارش", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Divider(height=1, color=DIVIDER),
                    stats_col,
                ], spacing=10)
            ),

            ft.Container(height=8),

            ft.Text("📋 لیست قبوض", size=18,
                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
            table_col,

            ft.Container(height=8),

            chart_col,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    # ═══════════ گزارش مالی ═══════════
    def build_reports_page():
        # ─── رنگ‌های تم ───
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_CARD = theme["bg_card"]
        BG_MAIN = theme["bg_main"]
        BG_HOVER = theme["bg_hover"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]
        PURPLE = theme["purple"]

        # ─── State ───
        state = {
            "period_type": "all",
            "selected_month": None,
            "selected_year": None,
            "expense_chart_path": None,
            "method_chart_path": None,
            "trend_chart_path": None,
        }

        # ══════════════════════════════════════════
        # ═══  توابع کمکی  ═══
        # ══════════════════════════════════════════

        def extract_year(period_str):
            if not period_str:
                return None
            parts = period_str.strip().split()
            if not parts:
                return None
            try:
                return int(parts[-1])
            except (ValueError, IndexError):
                return None

        def get_available_periods():
            try:
                all_charges = list_charges(None)
            except Exception:
                all_charges = []

            months_set = set()
            years_set = set()

            for c in all_charges:
                period = c.get("period") or ""
                parts = period.strip().split()
                if parts:
                    try:
                        y = int(parts[-1])
                        years_set.add(y)
                        months_set.add(period)
                    except (ValueError, IndexError):
                        pass

            def month_sort_key(p):
                parts = p.strip().split()
                try:
                    y = int(parts[-1])
                    idx = MONTHS.index(parts[0]) if parts[0] in MONTHS else 0
                    return (y, idx)
                except Exception:
                    return (0, 0)

            months_sorted = sorted(months_set, key=month_sort_key, reverse=True)
            years_sorted = sorted(years_set, reverse=True)
            if not years_sorted:
                years_sorted = [get_jalali_year()]

            return months_sorted, years_sorted

        def collect_data():
            try:
                all_charges = list_charges(None)
            except Exception:
                all_charges = []
            try:
                all_payments = list_payments()
            except Exception:
                all_payments = []
            try:
                all_expenses = list_expenses()
            except Exception:
                all_expenses = []
            try:
                all_bills = list_utility_bills(None)
            except Exception:
                all_bills = []

            ptype = state["period_type"]

            if ptype == "monthly":
                month = state["selected_month"]
                if not month:
                    return {
                        "charges": [], "payments": [],
                        "expenses": [], "bills": [],
                        "label": "بدون دوره",
                    }

                charges = [c for c in all_charges
                           if c.get("period") == month]

                target = None
                parts = month.strip().split()
                try:
                    target = (int(parts[-1]), MONTHS.index(parts[0]))
                except Exception:
                    pass

                payments = []
                expenses = []
                bills = []

                if target:
                    for p in all_payments:
                        pd = p.get("payment_date")
                        if pd:
                            try:
                                j = jdatetime.date.fromgregorian(date=pd)
                                if (j.year, j.month) == target:
                                    payments.append(p)
                            except Exception:
                                pass
                    for e in all_expenses:
                        ed = e.get("expense_date")
                        if ed:
                            try:
                                j = jdatetime.date.fromgregorian(date=ed)
                                if (j.year, j.month) == target:
                                    expenses.append(e)
                            except Exception:
                                pass
                    for b in all_bills:
                        bd = b.get("due_date") or b.get("issue_date")
                        if bd is None:
                            bd_str = b.get("bill_date")
                            if bd_str:
                                try:
                                    bd = parse_date(bd_str)
                                except Exception:
                                    bd = None
                        if bd is None:
                            continue
                        try:
                            j = jdatetime.date.fromgregorian(date=bd)
                            if (j.year, j.month) == target:
                                bills.append(b)
                        except Exception:
                            pass

                return {
                    "charges": charges,
                    "payments": payments,
                    "expenses": expenses,
                    "bills": bills,
                    "label": month,
                }

            if ptype == "yearly":
                year = state["selected_year"]
                if not year:
                    return {
                        "charges": [], "payments": [],
                        "expenses": [], "bills": [],
                        "label": "بدون دوره",
                    }

                ty = int(year)
                charges = [c for c in all_charges
                           if extract_year(c.get("period")) == ty]

                payments = []
                expenses = []
                bills = []

                for p in all_payments:
                    pd = p.get("payment_date")
                    if pd:
                        try:
                            j = jdatetime.date.fromgregorian(date=pd)
                            if j.year == ty:
                                payments.append(p)
                        except Exception:
                            pass

                for e in all_expenses:
                    ed = e.get("expense_date")
                    if ed:
                        try:
                            j = jdatetime.date.fromgregorian(date=ed)
                            if j.year == ty:
                                expenses.append(e)
                        except Exception:
                            pass

                for b in all_bills:
                    bd = b.get("due_date") or b.get("issue_date")
                    if bd is None:
                        bd_str = b.get("bill_date")
                        if bd_str:
                            try:
                                bd = parse_date(bd_str)
                            except Exception:
                                bd = None
                    if bd is None:
                        continue
                    try:
                        j = jdatetime.date.fromgregorian(date=bd)
                        if j.year == ty:
                            bills.append(b)
                    except Exception:
                        pass

                label = "سال " + to_persian(str(ty))
                return {
                    "charges": charges,
                    "payments": payments,
                    "expenses": expenses,
                    "bills": bills,
                    "label": label,
                }

            return {
                "charges": all_charges,
                "payments": all_payments,
                "expenses": all_expenses,
                "bills": all_bills,
                "label": "از ابتدا تا کنون",
            }

        def calc_summary(data):
            charges = data.get("charges", [])
            payments = data.get("payments", [])
            expenses = data.get("expenses", [])

            total_charges = 0
            total_paid_on_charges = 0
            total_remaining = 0
            for c in charges:
                total_charges += c.get("amount", 0) or 0
                total_paid_on_charges += c.get("paid_amount", 0) or 0
                total_remaining += c.get("remaining", 0) or 0

            total_payments = 0
            for p in payments:
                total_payments += p.get("amount", 0) or 0

            total_expenses = 0
            for e in expenses:
                total_expenses += e.get("amount", 0) or 0

            paid_count = 0
            unpaid_count = 0
            partial_count = 0
            for c in charges:
                st = c.get("status")
                if st == "تسویه":
                    paid_count += 1
                elif st == "پرداخت نشده":
                    unpaid_count += 1
                elif st == "ناقص":
                    partial_count += 1

            pct = 0
            if total_charges > 0:
                pct = (total_paid_on_charges / total_charges) * 100

            return {
                "total_charges": total_charges,
                "total_paid_on_charges": total_paid_on_charges,
                "total_remaining": total_remaining,
                "total_payments": total_payments,
                "total_expenses": total_expenses,
                "net": total_payments - total_expenses,
                "charges_count": len(charges),
                "payments_count": len(payments),
                "expenses_count": len(expenses),
                "paid_count": paid_count,
                "unpaid_count": unpaid_count,
                "partial_count": partial_count,
                "collection_pct": pct,
            }

        def calc_categories(expenses):
            buckets = {}
            for e in expenses:
                cat = e.get("category", "سایر")
                buckets[cat] = buckets.get(cat, 0) + (e.get("amount", 0) or 0)

            total = 0
            for v in buckets.values():
                total += v
            if total == 0:
                total = 1

            items = sorted(buckets.items(), key=lambda x: -x[1])
            result = []
            for cat, amt in items:
                cnt = 0
                for x in expenses:
                    if x.get("category") == cat:
                        cnt += 1
                result.append({
                    "category": cat,
                    "total": amt,
                    "percent": (amt / total) * 100,
                    "count": cnt,
                })
            return result

        def calc_payment_methods(payments):
            buckets = {}
            for p in payments:
                m = p.get("payment_method", "نامشخص")
                buckets[m] = buckets.get(m, 0) + (p.get("amount", 0) or 0)

            total = 0
            for v in buckets.values():
                total += v
            if total == 0:
                total = 1

            items = sorted(buckets.items(), key=lambda x: -x[1])
            result = []
            for m, amt in items:
                cnt = 0
                for x in payments:
                    if x.get("payment_method") == m:
                        cnt += 1
                result.append({
                    "method": m,
                    "total": amt,
                    "percent": (amt / total) * 100,
                    "count": cnt,
                })
            return result

        def calc_debtors(charges):
            buckets = {}
            for c in charges:
                rem = c.get("remaining", 0) or 0
                if rem <= 0:
                    continue
                key = c.get("unit_number", "-")
                if key not in buckets:
                    buckets[key] = {
                        "unit_number": key,
                        "resident_name": c.get("resident_name", "-"),
                        "phone": c.get("phone", ""),
                        "debt": 0,
                        "periods": [],
                        "periods_detail": [],
                    }
                period = c.get("period") or "-"
                buckets[key]["debt"] += rem
                buckets[key]["periods"].append(period)

                sort_key = (0, 0)
                parts = period.strip().split()
                if len(parts) >= 2:
                    try:
                        y = int(parts[-1])
                        idx = MONTHS.index(parts[0]) if parts[0] in MONTHS else 0
                        sort_key = (y, idx)
                    except Exception:
                        pass

                buckets[key]["periods_detail"].append({
                    "period": period,
                    "amount": rem,
                    "sort_key": sort_key,
                })

            result = []
            for b in buckets.values():
                details = sorted(
                    b["periods_detail"],
                    key=lambda x: x["sort_key"]
                )
                b["periods_detail"] = details
                b["first_period"] = details[0]["period"] if details else "-"
                b["last_period"] = details[-1]["period"] if details else "-"
                b["periods_count"] = len(details)
                b["period_range"] = (
                    b["first_period"]
                    if b["first_period"] == b["last_period"]
                    else f'{b["first_period"]} تا {b["last_period"]}'
                )
                result.append(b)

            return sorted(result, key=lambda x: -x["debt"])

        # ═══════════════════════════════════════════
        # محاسبه آمار پرداخت‌کنندگان + امتیاز
        # قوانین:
        #   - پرداخت روز 1-28 ماه M  → شارژ ماه M
        #   - پرداخت روز 29+ ماه M   → شارژ ماه M+1
        #   - سررسید شارژ هر ماه = روز 10 ام
        #   - امتیاز هر پرداخت از 20
        # ═══════════════════════════════════════════
        def calc_all_payers_stats(charges, payments):
            """محاسبه آمار پرداخت + امتیاز نظم پرداخت هر واحد."""

            def _payment_target_period(j_pd):
                d = j_pd.day
                m = j_pd.month
                y = j_pd.year
                if d >= 29:
                    if m == 12:
                        return (y + 1, 1)
                    return (y, m + 1)
                return (y, m)

            def _payment_score(diff):
                """امتیاز یک پرداخت از 20."""
                if diff > 0:
                    return 10 + min(diff, 10)
                elif diff == 0:
                    return 10
                else:
                    return max(10 - min(abs(diff), 10), 0)

            def _pay_sort_key(p):
                pd = p.get("payment_date")
                if pd is None:
                    return (1, 0)
                return (0, pd.toordinal())

            payments_by_unit = {}
            for p in payments:
                unit = p.get("unit_number")
                if unit is None:
                    continue
                payments_by_unit.setdefault(unit, []).append(p)

            payer_stats = []

            for unit, unit_payments in payments_by_unit.items():
                sorted_payments = sorted(unit_payments, key=_pay_sort_key)

                early_count = 0
                late_count = 0
                total_early_days = 0
                total_late_days = 0
                total_score = 0.0
                scored_payments = 0

                for p in sorted_payments:
                    pd = p.get("payment_date")
                    if pd is None:
                        continue

                    try:
                        j_pd = jdatetime.date.fromgregorian(date=pd)
                    except Exception:
                        continue

                    target_year, target_month = _payment_target_period(j_pd)

                    try:
                        due = jdatetime.date(
                            target_year, target_month, 10
                        )
                    except Exception:
                        continue

                    diff = (due - j_pd).days

                    if diff > 0:
                        early_count += 1
                        total_early_days += diff
                    elif diff < 0:
                        late_count += 1
                        total_late_days += (-diff)

                    total_score += _payment_score(diff)
                    scored_payments += 1

                avg_score = (total_score / scored_payments
                             if scored_payments > 0 else 0)

                valid_dates = [
                    p.get("payment_date") for p in unit_payments
                    if p.get("payment_date") is not None
                ]
                valid_dates.sort()

                total_paid = sum(
                    (p.get("amount", 0) or 0) for p in unit_payments
                )
                resident = (
                    sorted_payments[0].get("resident_name", "-")
                    if sorted_payments else "-"
                )

                payer_stats.append({
                    "unit_number": unit,
                    "resident_name": resident,
                    "paid": total_paid,
                    "early_count": early_count,
                    "late_count": late_count,
                    "total_early_days": total_early_days,
                    "total_late_days": total_late_days,
                    "first_payment_date": valid_dates[0] if valid_dates else None,
                    "last_payment_date": valid_dates[-1] if valid_dates else None,
                    "payments_count": len(unit_payments),
                    "avg_score": round(avg_score, 1),
                })

            # مرتب‌سازی: بالاترین امتیاز اول
            payer_stats.sort(
                key=lambda x: (-x["avg_score"], -x["early_count"])
            )
            return payer_stats

        def calc_top_payers(charges, payments, top_n=3):
            all_stats = calc_all_payers_stats(charges, payments)
            all_stats = [s for s in all_stats if s["payments_count"] > 0]
            return all_stats[:top_n]

        def calc_late_payers(charges, payments, top_n=3):
            all_stats = calc_all_payers_stats(charges, payments)
            all_stats = [s for s in all_stats if s["payments_count"] > 0]

            if len(all_stats) <= top_n:
                if len(all_stats) < 2:
                    return []
                return list(reversed(all_stats[1:]))

            last_n = all_stats[-top_n:]
            last_n.reverse()
            return last_n

        # ══════════════════════════════════════════
        # ═══  نمودار دایره‌ای  ═══
        # ══════════════════════════════════════════

        def build_pie_chart(labels, values, chart_key, title="",
                            width=280, height=280):
            if not labels or not values:
                return ft.Container(
                    width=width, height=height,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.PIE_CHART_OUTLINE,
                                size=50, color=TEXT_MUTED),
                        ft.Text("داده‌ای موجود نیست",
                                size=11, color=TEXT_MUTED),
                    ], spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )

            all_zero = True
            for v in values:
                if v and v > 0:
                    all_zero = False
                    break
            if all_zero:
                return ft.Container(
                    width=width, height=height,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("داده‌ای موجود نیست",
                                    size=11, color=TEXT_MUTED),
                )

            try:
                import matplotlib.pyplot as plt
                import matplotlib
                from matplotlib import font_manager
                import base64

                matplotlib.use('Agg')

                fonts_dir = os.path.join(os.getcwd(), "fonts")
                regular = os.path.join(fonts_dir, "Vazirmatn-Regular.ttf")
                bold = os.path.join(fonts_dir, "Vazirmatn-Bold.ttf")
                if os.path.exists(regular):
                    font_manager.fontManager.addfont(regular)
                if os.path.exists(bold):
                    font_manager.fontManager.addfont(bold)
                plt.rcParams['font.family'] = 'Vazirmatn'

                chart_dir = os.path.join(os.getcwd(), "temp_charts")
                os.makedirs(chart_dir, exist_ok=True)

                chart_path = os.path.join(
                    chart_dir, "chart_" + chart_key + ".png"
                )

                colors_list = [
                    '#00C853', '#FF6D00', '#1565C0',
                    '#9C27B0', '#C62828', '#00838F',
                    '#F9A825', '#5D4037', '#455A64',
                    '#AD1457', '#00695C', '#4527A0',
                ]

                fig, ax = plt.subplots(
                    figsize=(5, 5),
                    subplot_kw=dict(aspect="equal"),
                    facecolor='none',
                )

                def fa_pct(pct):
                    p_map = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
                    val = f"{pct:.0f}"
                    return val.translate(p_map) + "٪"

                wedge_props = {
                    'linewidth': 2,
                    'antialiased': True,
                }
                if is_dark_mode():
                    wedge_props['edgecolor'] = '#0F172A'
                else:
                    wedge_props['edgecolor'] = 'white'

                wedges, texts, autotexts = ax.pie(
                    values,
                    colors=colors_list[:len(values)],
                    autopct=fa_pct,
                    startangle=90,
                    pctdistance=0.75,
                    textprops={'fontsize': 12, 'fontweight': 'bold'},
                    wedgeprops=wedge_props,
                )

                for at in autotexts:
                    at.set_color('white')
                    at.set_fontweight('bold')

                fig.patch.set_alpha(0)
                ax.set_facecolor('none')

                plt.savefig(
                    chart_path,
                    format='png',
                    bbox_inches='tight',
                    transparent=True,
                    dpi=140,
                    pad_inches=0.1,
                )
                plt.close(fig)

                if chart_key == "expenses":
                    state["expense_chart_path"] = chart_path
                elif chart_key == "methods":
                    state["method_chart_path"] = chart_path

                with open(chart_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')

                src = "data:image/png;base64," + b64
                return ft.Image(
                    src=src,
                    width=width,
                    height=height,
                    fit=ft.BoxFit.CONTAIN,
                )

            except Exception as ex:
                print("❌ خطای نمودار: " + str(ex))
                return ft.Container(
                    width=width, height=height,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("خطا در نمودار",
                                    size=11, color=D),
                )

        # ══════════════════════════════════════════
        # ═══  نمودار خطی روند ۶ ماه  ═══
        # ══════════════════════════════════════════

        def build_trend_6months():
            try:
                import matplotlib.pyplot as plt
                import matplotlib
                from matplotlib import font_manager
                import base64

                matplotlib.use('Agg')

                fonts_dir = os.path.join(os.getcwd(), "fonts")
                for f in ["Vazirmatn-Regular.ttf", "Vazirmatn-Bold.ttf"]:
                    fp = os.path.join(fonts_dir, f)
                    if os.path.exists(fp):
                        font_manager.fontManager.addfont(fp)
                plt.rcParams['font.family'] = 'Vazirmatn'

                try:
                    all_payments = list_payments()
                    all_expenses = list_expenses()
                except Exception:
                    all_payments = []
                    all_expenses = []

                today = jdatetime.date.today()
                months_data = []

                for i in range(5, -1, -1):
                    target_month = today.month - i
                    target_year = today.year
                    while target_month <= 0:
                        target_month += 12
                        target_year -= 1

                    income = 0
                    for p in all_payments:
                        pd = p.get("payment_date")
                        if pd:
                            try:
                                j = jdatetime.date.fromgregorian(date=pd)
                                if j.year == target_year and j.month == target_month:
                                    income += p.get("amount", 0) or 0
                            except Exception:
                                pass

                    expense = 0
                    for e in all_expenses:
                        ed = e.get("expense_date")
                        if ed:
                            try:
                                j = jdatetime.date.fromgregorian(date=ed)
                                if j.year == target_year and j.month == target_month:
                                    expense += e.get("amount", 0) or 0
                            except Exception:
                                pass

                    months_data.append({
                        "month_label": MONTHS[target_month],
                        "year": target_year,
                        "income": income,
                        "expense": expense,
                    })

                has_data = False
                for m in months_data:
                    if m["income"] > 0 or m["expense"] > 0:
                        has_data = True
                        break

                if not has_data:
                    return None

                chart_dir = os.path.join(os.getcwd(), "temp_charts")
                os.makedirs(chart_dir, exist_ok=True)
                chart_path = os.path.join(chart_dir, "chart_trend_6m.png")

                fig, ax = plt.subplots(figsize=(12, 3), facecolor='none')

                labels = [m["month_label"] for m in months_data]
                incomes = [m["income"] / 1000000 for m in months_data]
                expenses_arr = [m["expense"] / 1000000 for m in months_data]

                ax.plot(labels, incomes, marker='o', linewidth=2.5,
                        markersize=8, color='#00C853', label='درآمد')
                ax.plot(labels, expenses_arr, marker='s', linewidth=2.5,
                        markersize=8, color='#FF6D00', label='هزینه')

                ax.fill_between(labels, incomes, alpha=0.15, color='#00C853')
                ax.fill_between(labels, expenses_arr, alpha=0.15, color='#FF6D00')

                ax.set_facecolor('none')
                fig.patch.set_alpha(0)
                ax.grid(True, alpha=0.2, linestyle='--')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#999')
                ax.spines['bottom'].set_color('#999')
                ax.tick_params(colors='#666', labelsize=9)

                legend = ax.legend(loc='upper left',
                                   frameon=False, fontsize=10)
                for text in legend.get_texts():
                    text.set_color('#666')

                plt.tight_layout()
                plt.savefig(chart_path, format='png',
                            bbox_inches='tight', transparent=True,
                            dpi=130)
                plt.close(fig)

                state["trend_chart_path"] = chart_path

                with open(chart_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')

                src = "data:image/png;base64," + b64
                return ft.Image(
                    src=src,
                    height=250,
                    fit=ft.BoxFit.FILL,
                    expand=True,
                )

            except Exception as ex:
                print("❌ خطای نمودار روند: " + str(ex))
                return None

        # ══════════════════════════════════════════
        # ═══  ویجت‌های کمکی  ═══
        # ══════════════════════════════════════════

        def section_title(icon, title, subtitle=""):
            col_children = [
                ft.Text(title, size=16,
                        weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
            ]
            if subtitle:
                col_children.append(
                    ft.Text(subtitle, size=11, color=TEXT_MUTED)
                )
            return ft.Row([
                ft.Container(
                    width=42, height=42, border_radius=12,
                    bgcolor=P + "20",
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(icon, size=20,
                                    text_align=ft.TextAlign.CENTER),
                ),
                ft.Column(col_children, spacing=1, expand=True),
            ], spacing=10)

        def stat_card(icon, title, value, color, subtitle=""):
            col_children = [
                ft.Text(title, size=11, color=TEXT_SECONDARY),
                ft.Text(value, size=16,
                        weight=ft.FontWeight.BOLD, color=color),
            ]
            if subtitle:
                col_children.append(
                    ft.Text(subtitle, size=9, color=TEXT_MUTED)
                )
            return ft.Container(
                expand=True, padding=14, border_radius=12,
                bgcolor=BG_CARD,
                content=ft.Row([
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=color + "20",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(icon, size=19,
                                        text_align=ft.TextAlign.CENTER),
                    ),
                    ft.Column(col_children, spacing=1, expand=True),
                ], spacing=10),
            )

        def empty_box(text):
            return ft.Container(
                padding=40,
                alignment=ft.Alignment.CENTER,
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=50, color=TEXT_MUTED),
                    ft.Text(text, size=12, color=TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                ], spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            )

        # ══════════════════════════════════════════
        # ═══  بخش‌های گزارش  ═══
        # ══════════════════════════════════════════

        def build_summary_section(data, summary):
            cards = ft.Row([
                stat_card(
                    "📋", "کل شارژ صادره",
                    fmt_money(summary["total_charges"], show_unit=False),
                    P,
                    to_persian(str(summary["charges_count"])) + " ردیف",
                ),
                stat_card(
                    "✅", "کل دریافتی",
                    fmt_money(summary["total_payments"], show_unit=False),
                    S,
                    to_persian(str(summary["payments_count"])) + " پرداخت",
                ),
                stat_card(
                    "💸", "کل هزینه",
                    fmt_money(summary["total_expenses"], show_unit=False),
                    W,
                    to_persian(str(summary["expenses_count"])) + " مورد",
                ),
                stat_card(
                    "💰", "خالص",
                    fmt_money(summary["net"], show_unit=False),
                    S if summary["net"] >= 0 else D,
                    "درآمد - هزینه",
                ),
            ], spacing=10)

            pct = summary["collection_pct"]
            if pct >= 90:
                pct_color = S
            elif pct >= 50:
                pct_color = W
            else:
                pct_color = D

            pct_text = to_persian(str(round(pct, 1))) + "٪"
            paid_text = "✅ " + to_persian(str(summary["paid_count"])) + " تسویه"
            partial_text = "⏳ " + to_persian(str(summary["partial_count"])) + " ناقص"
            unpaid_text = "⚠️ " + to_persian(str(summary["unpaid_count"])) + " پرداخت‌نشده"

            return ft.Column([
                section_title("💰", "خلاصه مالی", "آمار کلیدی دوره"),
                ft.Container(height=8),
                cards,
                ft.Container(height=12),
                ft.Container(
                    padding=18, border_radius=12, bgcolor=BG_CARD,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PERCENT, color=pct_color, size=20),
                            ft.Text("درصد وصول شارژها",
                                    size=14, weight=ft.FontWeight.BOLD,
                                    color=TEXT_MAIN),
                            ft.Container(expand=True),
                            ft.Text(pct_text, size=18,
                                    color=pct_color,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Container(height=8),
                        ft.ProgressBar(value=pct / 100,
                                       color=pct_color, bgcolor=BG_HOVER,
                                       height=10, border_radius=5),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text(paid_text, size=11, color=S,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(width=15),
                            ft.Text(partial_text, size=11, color=W,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(width=15),
                            ft.Text(unpaid_text, size=11, color=D,
                                    weight=ft.FontWeight.BOLD),
                        ], spacing=5),
                    ], spacing=0),
                ),
            ], spacing=0)

        def build_charges_section(data):
            charges = data.get("charges", [])

            result = [
                section_title("📋", "خلاصه شارژها",
                              to_persian(str(len(charges))) + " شارژ ثبت شده"),
            ]

            if not charges:
                result.append(ft.Container(height=10))
                result.append(empty_box("هیچ شارژی در این دوره ثبت نشده"))
                return ft.Column(result, spacing=10)

            # ─── جمع‌ها (همه به تومان در دیتابیس) ───
            total_amount = sum(c.get("amount", 0) or 0 for c in charges)
            total_paid = sum(c.get("paid_amount", 0) or 0 for c in charges)
            total_remaining = sum(c.get("remaining", 0) or 0 for c in charges)
            paid_count = len([c for c in charges if c.get("status") == "تسویه"])
            pct = (total_paid / total_amount * 100) if total_amount > 0 else 0

            pct_color = S if pct >= 90 else W if pct >= 50 else D

            # ─── نمایش با واحد پول سیستم ───
            # نکته: fmt_money خودش تبدیل تومان → واحد سیستم رو انجام می‌ده.
            # پس مقادیر تومان رو بدون /10 بدیم.
            summary_row = ft.Container(
                padding=14, border_radius=12, bgcolor=theme["primary_bg"],
                content=ft.Row([
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("کل شارژ", size=10, color=TEXT_MUTED),
                            ft.Text(
                                fmt_money(total_amount, show_unit=False) +
                                " " + get_currency_short(),
                                size=13, color=P,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=2),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("دریافتی", size=10, color=TEXT_MUTED),
                            ft.Text(
                                fmt_money(total_paid, show_unit=False) +
                                " " + get_currency_short(),
                                size=13, color=S,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=2),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("معوق", size=10, color=TEXT_MUTED),
                            ft.Text(
                                fmt_money(total_remaining, show_unit=False) +
                                " " + get_currency_short(),
                                size=13,
                                color=D if total_remaining > 0 else S,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=2),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("تسویه", size=10, color=TEXT_MUTED),
                            ft.Text(
                                f"{to_persian(str(paid_count))} از "
                                f"{to_persian(str(len(charges)))}",
                                size=13, color=S,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=2),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("درصد وصول", size=10, color=TEXT_MUTED),
                            ft.Text(
                                f"{to_persian(f'{pct:.0f}')}٪",
                                size=13, color=pct_color,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=2),
                    ),
                ], spacing=8),
            )

            result.append(ft.Container(height=8))
            result.append(summary_row)

            return ft.Column(result, spacing=0)
        # ═══════════════════════════════════════════
        # ⭐ کمک‌تابع: یادداشت و رنگ بر اساس امتیاز
        # ═══════════════════════════════════════════
        def _score_note(score):
            """یادداشت متنی بر اساس امتیاز."""
            if score >= 18:
                return "⭐⭐⭐ عالی"
            elif score >= 15:
                return "⭐⭐ خیلی خوب"
            elif score >= 12:
                return "👍 خوب"
            elif score >= 8:
                return "⚡ متوسط"
            else:
                return "⚠️ نیازمند پیگیری"

        def _score_color(score):
            """رنگ امتیاز."""
            if score >= 15:
                return S
            elif score >= 12:
                return P
            elif score >= 8:
                return W
            else:
                return D

        # ═══════════════════════════════════════════
        # ⭐ جدول رتبه‌بندی نظم پرداخت با امتیاز
        # ═══════════════════════════════════════════
        def build_payers_ranking_section(data):
            """جدول رتبه‌بندی نظم پرداخت تمام واحدها با سیستم امتیازدهی."""
            charges = data.get("charges", [])
            payments = data.get("payments", [])

            all_stats = calc_all_payers_stats(charges, payments)
            all_stats = [s for s in all_stats if s["payments_count"] > 0]

            if not all_stats:
                return ft.Column([
                    section_title("🏆", "رتبه‌بندی نظم پرداخت",
                                  "پرداختی ثبت نشده"),
                    ft.Container(height=10),
                    empty_box("پرداختی ثبت نشده"),
                ], spacing=0)

            result = [
                section_title("🏆", "رتبه‌بندی نظم پرداخت",
                              to_persian(str(len(all_stats))) + " واحد"),
            ]

            # ─── راهنمای امتیازدهی ───
            guide_box = ft.Container(
                padding=12, border_radius=10,
                bgcolor=theme["primary_bg"],
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=P),
                        ft.Text("نحوه محاسبه امتیاز (از ۲۰)",
                                size=12, weight=ft.FontWeight.BOLD,
                                color=P),
                    ], spacing=6),
                    ft.Container(height=4),
                    ft.Text("• امتیاز پایه هر پرداخت: ۱۰",
                            size=10, color=TEXT_SECONDARY),
                    ft.Text("• زودتر از سررسید (روز ۱۰ ماه): +۱ به ازای هر روز (حداکثر +۱۰)",
                            size=10, color=S,
                            weight=ft.FontWeight.BOLD),
                    ft.Text("• با تأخیر: −۱ به ازای هر روز (حداکثر −۱۰)",
                            size=10, color=D,
                            weight=ft.FontWeight.BOLD),
                    ft.Text("• امتیاز نهایی هر واحد = میانگین امتیاز پرداخت‌هایش",
                            size=10, color=TEXT_SECONDARY),
                ], spacing=2),
            )

            result.append(ft.Container(height=8))
            result.append(guide_box)
            result.append(ft.Container(height=10))

            # ─── هدر جدول (بدون ستون یادداشت) ───
            header = ft.Container(
                padding=10, border_radius=8, bgcolor=P,
                content=ft.Row([
                    ft.Text("رتبه", width=50, size=11,
                            color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("واحد", width=50, size=11,
                            color="white", weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("ساکن", expand=True, size=11,
                            color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("پرداخت", width=80, size=11,
                            color="white", weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("امتیاز", width=100, size=11,
                            color="white", weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                ], spacing=4),
            )

            rows_col = ft.Column(spacing=3)

            for rank, u in enumerate(all_stats, 1):
                if rank == 1:
                    rank_display = "🥇"
                    row_bg = "#FFF8E1"
                elif rank == 2:
                    rank_display = "🥈"
                    row_bg = "#F5F5F5"
                elif rank == 3:
                    rank_display = "🥉"
                    row_bg = "#FBEEE6"
                else:
                    rank_display = to_persian(str(rank))
                    row_bg = (theme["bg_table_row1"] if rank % 2 == 0
                              else theme["bg_table_row2"])

                score = u.get("avg_score", 0)
                score_color = _score_color(score)

                rows_col.controls.append(
                    ft.Container(
                        padding=10, border_radius=6,
                        bgcolor=row_bg,
                        content=ft.Row([
                            ft.Container(
                                width=50,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    rank_display,
                                    size=16 if rank <= 3 else 13,
                                    weight=ft.FontWeight.BOLD,
                                    color=P if rank > 3 else TEXT_MAIN,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ),
                            ft.Container(
                                width=50,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    to_persian(str(u["unit_number"])),
                                    size=13, color=P,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ),
                            ft.Text(u["resident_name"] or "-",
                                    expand=True, size=13,
                                    color=TEXT_MAIN,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(
                                to_persian(str(u.get("payments_count", 0))),
                                width=80, size=12,
                                color=TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(
                                width=100,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    to_persian(f"{score:.1f}"),
                                    size=16,
                                    color=score_color,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ),
                        ], spacing=4),
                    )
                )

            result.append(header)
            result.append(ft.Container(height=4))
            result.append(rows_col)

            return ft.Column(result, spacing=0)

        def build_payments_section(data):
            payments = data.get("payments", [])

            result = [
                section_title("💳", "روش‌های پرداخت",
                              to_persian(str(len(payments))) + " پرداخت"),
            ]

            if not payments:
                result.append(ft.Container(height=10))
                result.append(empty_box("پرداختی ثبت نشده"))
                return ft.Column(result, spacing=10)

            methods = calc_payment_methods(payments)

            pie_labels = []
            pie_values = []
            for m in methods:
                pie_labels.append(m["method"])
                pie_values.append(m["total"])

            chart = build_pie_chart(
                pie_labels, pie_values, "methods", "روش‌ها", 200, 200
            )

            methods_col = ft.Column(spacing=6)
            for m in methods:
                pct_text = to_persian(str(round(m["percent"]))) + "٪"
                methods_col.controls.append(
                    ft.Container(
                        padding=10, border_radius=8,
                        bgcolor=BG_CARD,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(m["method"], size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_MAIN, expand=True),
                                ft.Text(pct_text, size=11,
                                        color=S, weight=ft.FontWeight.BOLD),
                            ]),
                            ft.Container(height=2),
                            ft.Row([
                                ft.Text(to_persian(str(m["count"])) + " مورد",
                                        size=10, color=TEXT_MUTED),
                                ft.Container(expand=True),
                                ft.Text(fmt_money(m["total"], show_unit=False),
                                        size=11, color=S,
                                        weight=ft.FontWeight.BOLD),
                            ]),
                        ], spacing=0),
                    )
                )

            result.append(ft.Container(height=10))
            result.append(ft.Container(
                padding=12, border_radius=12, bgcolor=BG_CARD,
                content=ft.Row([
                    ft.Container(
                        width=200,
                        alignment=ft.Alignment.CENTER,
                        content=chart,
                    ),
                    ft.Container(width=12),
                    ft.Container(expand=True, content=methods_col),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ))

            return ft.Column(result, spacing=0)

        def build_debtors_section(data):
            debtors = calc_debtors(data.get("charges", []))

            result = [
                section_title("⚠️", "گزارش بدهکاران",
                              to_persian(str(len(debtors))) + " واحد"),
            ]

            if not debtors:
                result.append(ft.Container(height=10))
                result.append(ft.Container(
                    padding=40, alignment=ft.Alignment.CENTER,
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=50, color=S),
                        ft.Text("همه واحدها تسویه هستند",
                                size=13, color=S,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ))
                return ft.Column(result, spacing=10)

            total_debt = sum(d["debt"] for d in debtors)

            result.append(ft.Container(height=8))
            result.append(ft.Container(
                padding=12, border_radius=10,
                bgcolor=theme["danger_bg"],
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=D, size=20),
                    ft.Text("کل بدهی:", size=12,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN),
                    ft.Container(width=8),
                    ft.Text(fmt_money(total_debt),
                            size=14, color=D,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text("💡 پیامک با آیکون",
                            size=9, color=TEXT_MUTED),
                ], spacing=6),
            ))

            debtors_col = ft.Column(spacing=6)
            for d in debtors[:3]:
                cnt = d.get("periods_count", len(d.get("periods", [])))
                phone_display = to_persian(d["phone"]) \
                    if d["phone"] else "بدون شماره"

                sms_btn = ft.IconButton(
                    icon=ft.Icons.SMS,
                    icon_color=S if d["phone"] else "#ccc",
                    disabled=not bool(d["phone"]),
                    icon_size=18,
                    tooltip="پیامک",
                    on_click=lambda e: nav(build_sms_page),
                )

                debtors_col.controls.append(
                    ft.Container(
                        padding=10, border_radius=10,
                        bgcolor=theme["danger_bg"],
                        content=ft.Row([
                            ft.Container(
                                width=38, height=38,
                                border_radius=19, bgcolor=BG_CARD,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    to_persian(str(d["unit_number"])),
                                    size=13, color=D,
                                    weight=ft.FontWeight.BOLD),
                            ),
                            ft.Container(width=8),
                            ft.Column([
                                ft.Text(d["resident_name"] or "-",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_MAIN),
                                ft.Text(
                                    f"{to_persian(str(cnt))} دوره • {phone_display}",
                                    size=9, color=TEXT_MUTED),
                            ], spacing=1, expand=True),
                            ft.Text(
                                fmt_money(d["debt"], show_unit=False),
                                size=12, color=D,
                                weight=ft.FontWeight.BOLD),
                            ft.Container(width=2),
                            sms_btn,
                        ], spacing=4),
                    )
                )

            if len(debtors) > 3:
                debtors_col.controls.append(
                    ft.Container(
                        padding=6,
                        content=ft.Text(
                            f"+ {to_persian(str(len(debtors) - 3))} بدهکار دیگر",
                            size=10, color=TEXT_MUTED,
                            italic=True,
                            text_align=ft.TextAlign.CENTER),
                    )
                )

            result.append(ft.Container(height=8))
            result.append(debtors_col)
            return ft.Column(result, spacing=0)

        def build_recent_payments_section(data):
            payments = data.get("payments", [])

            if not payments:
                return ft.Column()

            def recent_sort_key(p):
                pd = p.get("payment_date")
                if pd is None:
                    return (0, 0)
                return (1, pd.toordinal())

            sorted_recent = sorted(
                payments,
                key=recent_sort_key,
                reverse=True,
            )[:10]

            header_row = ft.Container(
                padding=8, border_radius=8,
                bgcolor=P,
                content=ft.Row([
                    ft.Text("واحد", width=50, size=10,
                            color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("تاریخ", width=110, size=10,
                            color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("روش", width=80, size=10,
                            color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("پیگیری", expand=True, size=10,
                            color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("مبلغ", width=130, size=10,
                            color="white", weight=ft.FontWeight.BOLD),
                ], spacing=4),
            )

            rows_col = ft.Column(spacing=3)
            for i, p in enumerate(sorted_recent):
                bg = theme["bg_table_row1"] if i % 2 == 0 else theme["bg_table_row2"]
                pd_text = to_jalali(p.get("payment_date")) \
                    if p.get("payment_date") else "-"
                tc_text = to_persian(p.get("tracking_code") or "-")

                rows_col.controls.append(
                    ft.Container(
                        padding=6, border_radius=6,
                        bgcolor=bg,
                        content=ft.Row([
                            ft.Text(to_persian(str(p.get("unit_number", "-"))),
                                    width=50, size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_MAIN),
                            ft.Text(pd_text, width=110, size=11,
                                    color=TEXT_SECONDARY),
                            ft.Text(p.get("payment_method", "-"),
                                    width=80, size=11,
                                    color=TEXT_SECONDARY),
                            ft.Text(tc_text, expand=True, size=10,
                                    color=TEXT_MUTED),
                            ft.Text(fmt_money(p.get("amount", 0),
                                              show_unit=False),
                                    width=130, size=11, color=S,
                                    weight=ft.FontWeight.BOLD),
                        ], spacing=4),
                    )
                )

            return ft.Column([
                section_title("📋", "آخرین پرداخت‌ها",
                              to_persian(str(len(sorted_recent))) + " مورد اخیر"),
                ft.Container(height=8),
                ft.Container(
                    padding=10, border_radius=10,
                    bgcolor=BG_CARD,
                    content=ft.Column([
                        header_row,
                        ft.Container(height=4),
                        rows_col,
                    ], spacing=0),
                ),
            ], spacing=0)

        def build_expenses_section(data):
            expenses = data.get("expenses", [])

            result = [
                section_title("💸", "گزارش هزینه‌ها",
                              to_persian(str(len(expenses))) + " هزینه ثبت شده"),
            ]

            if not expenses:
                result.append(ft.Container(height=10))
                result.append(empty_box("هیچ هزینه‌ای در این دوره ثبت نشده"))
                return ft.Column(result, spacing=10)

            categories = calc_categories(expenses)

            pie_labels = []
            pie_values = []
            for c in categories[:8]:
                pie_labels.append(c["category"])
                pie_values.append(c["total"])

            chart = build_pie_chart(
                pie_labels, pie_values, "expenses", "هزینه‌ها", 280, 280
            )

            cats_col = ft.Column(spacing=6)
            for c in categories:
                pct_text = to_persian(str(round(c["percent"]))) + "٪"
                cats_col.controls.append(
                    ft.Container(
                        padding=10, border_radius=8,
                        bgcolor=BG_CARD,
                        content=ft.Row([
                            ft.Text(c["category"], size=11,
                                    color=TEXT_MAIN, expand=True,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(
                                to_persian(str(c["count"])) + " مورد",
                                size=10, color=TEXT_MUTED),
                            ft.Container(width=10),
                            ft.Text(
                                fmt_money(c["total"], show_unit=False),
                                size=11, color=W,
                                weight=ft.FontWeight.BOLD),
                            ft.Container(width=10),
                            ft.Text(pct_text, size=10,
                                    color=TEXT_SECONDARY),
                        ], spacing=4),
                    )
                )

            result.append(ft.Container(height=10))
            result.append(ft.Container(
                padding=15, border_radius=14, bgcolor=BG_CARD,
                content=ft.Row([
                    ft.Container(
                        width=300,
                        alignment=ft.Alignment.CENTER,
                        content=chart,
                    ),
                    ft.Container(width=15),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("تفکیک بر اساس دسته",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_MAIN),
                            ft.Container(height=6),
                            cats_col,
                        ], spacing=0),
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
            ))

            return ft.Column(result, spacing=0)

        def build_bills_section(data):
            bills = data.get("bills", [])

            result = [
                section_title("📄", "گزارش قبوض",
                              to_persian(str(len(bills))) + " قبض ثبت شده"),
            ]

            if not bills:
                result.append(ft.Container(height=10))
                result.append(empty_box("هیچ قبیضی در این دوره ثبت نشده"))
                return ft.Column(result, spacing=10)

            types_data = {}
            for b in bills:
                bt = b.get("bill_type", "سایر")
                if bt not in types_data:
                    types_data[bt] = {"amount": 0, "count": 0}
                types_data[bt]["amount"] += b.get("amount", 0) or 0
                types_data[bt]["count"] += 1

            icons_map = {"آب": "💧", "برق": "⚡", "گاز": "🔥"}
            colors_map = {
                "آب": "#00BCD4",
                "برق": "#FFC107",
                "گاز": "#FF5722",
            }

            bill_cards = ft.Row(spacing=10)
            for bt in types_data:
                td = types_data[bt]
                icon = icons_map.get(bt, "📋")
                color = colors_map.get(bt, P)
                bill_cards.controls.append(
                    ft.Container(
                        expand=True, padding=14,
                        border_radius=12, bgcolor=BG_CARD,
                        content=ft.Row([
                            ft.Container(
                                width=42, height=42,
                                border_radius=12,
                                bgcolor=color + "20",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(icon, size=20,
                                                text_align=ft.TextAlign.CENTER),
                            ),
                            ft.Column([
                                ft.Text("قبض " + bt, size=11,
                                        color=TEXT_SECONDARY),
                                ft.Text(
                                    fmt_money(
                                        td["amount"] / 10,
                                        show_unit=False,
                                    ),
                                    size=14, color=color,
                                    weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    to_persian(str(td["count"])) + " قبض",
                                    size=9, color=TEXT_MUTED),
                            ], spacing=1, expand=True),
                        ], spacing=10),
                    )
                )

            result.append(ft.Container(height=10))
            result.append(bill_cards)

            return ft.Column(result, spacing=0)

        # ══════════════════════════════════════════
        # ═══  محتوای اصلی گزارش  ═══
        # ══════════════════════════════════════════

        content_col = ft.Column(spacing=0)

        def rebuild_content():
            content_col.controls.clear()

            data = collect_data()
            summary = calc_summary(data)

            state["expense_chart_path"] = None
            state["method_chart_path"] = None
            state["trend_chart_path"] = None

            # ═══ هدر دوره ═══
            content_col.controls.append(
                ft.Container(
                    padding=14, border_radius=12,
                    bgcolor=theme["primary_bg"],
                    content=ft.Row([
                        ft.Container(
                            width=42, height=42,
                            border_radius=12, bgcolor=BG_CARD,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.ASSESSMENT,
                                            color=P, size=22),
                        ),
                        ft.Column([
                            ft.Text("گزارش دوره", size=15,
                                    weight=ft.FontWeight.BOLD, color=P),
                            ft.Text(data["label"], size=11,
                                    color=TEXT_SECONDARY),
                        ], spacing=2, expand=True),
                    ], spacing=10),
                )
            )

            # ═══ خلاصه مالی ═══
            content_col.controls.append(ft.Container(height=12))
            content_col.controls.append(
                build_summary_section(data, summary)
            )

            # ═══ رتبه‌بندی نظم پرداخت ═══
            content_col.controls.append(ft.Container(height=12))
            content_col.controls.append(
                build_payers_ranking_section(data)
            )

            # ═══ خلاصه شارژها ═══
            content_col.controls.append(ft.Container(height=12))
            content_col.controls.append(build_charges_section(data))

            # ═══ ردیف: روش‌های پرداخت + بدهکاران ═══
            content_col.controls.append(ft.Container(height=12))
            content_col.controls.append(
                ft.Row([
                    ft.Container(expand=True,
                                 content=build_payments_section(data)),
                    ft.Container(width=12),
                    ft.Container(expand=True,
                                 content=build_debtors_section(data)),
                ], vertical_alignment=ft.CrossAxisAlignment.START)
            )

            # ═══ آخرین پرداخت‌ها ═══
            recent = build_recent_payments_section(data)
            if recent.controls:
                content_col.controls.append(ft.Container(height=12))
                content_col.controls.append(recent)

            # ═══ هزینه‌ها ═══
            content_col.controls.append(ft.Container(height=12))
            content_col.controls.append(build_expenses_section(data))

            # ═══ قبوض ═══
            content_col.controls.append(ft.Container(height=12))
            content_col.controls.append(build_bills_section(data))

            # ═══ نمودار روند ═══
            trend_img = build_trend_6months()
            if trend_img is not None:
                content_col.controls.append(ft.Container(height=12))
                content_col.controls.append(
                    section_title("📈", "روند ۶ ماه اخیر",
                                  "مقایسه درآمد و هزینه ماهانه")
                )
                content_col.controls.append(ft.Container(height=6))
                content_col.controls.append(
                    ft.Container(
                        padding=12, border_radius=12,
                        bgcolor=BG_CARD,
                        content=ft.Row([trend_img]),
                    )
                )

            try:
                content_col.update()
            except Exception:
                pass

        # ══════════════════════════════════════════
        # ═══  فیلترها  ═══
        # ══════════════════════════════════════════

        months_list, years_list = get_available_periods()

        default_month = months_list[0] if months_list else None
        default_year = years_list[0] if years_list else get_jalali_year()

        state["selected_month"] = default_month
        state["selected_year"] = default_year

        period_type_dd = ft.Dropdown(
            label="نوع گزارش",
            width=180,
            value="از ابتدا تا کنون",
            options=[
                ft.dropdown.Option(text="ماهانه"),
                ft.dropdown.Option(text="سالانه"),
                ft.dropdown.Option(text="از ابتدا تا کنون"),
            ],
        )

        month_dd = ft.Dropdown(
            label="ماه",
            width=180,
            value=default_month,
            options=[ft.dropdown.Option(text=m) for m in months_list],
        )

        year_dd = ft.Dropdown(
            label="سال",
            width=140,
            value=str(default_year),
            options=[ft.dropdown.Option(text=str(y)) for y in years_list],
        )

        month_wrapper = ft.Container(content=month_dd, visible=False)
        year_wrapper = ft.Container(content=year_dd, visible=False)

        def on_period_type_change(e):
            value = e.control.value
            if value == "ماهانه":
                state["period_type"] = "monthly"
                month_wrapper.visible = True
                year_wrapper.visible = False
            elif value == "سالانه":
                state["period_type"] = "yearly"
                month_wrapper.visible = False
                year_wrapper.visible = True
            else:
                state["period_type"] = "all"
                month_wrapper.visible = False
                year_wrapper.visible = False

            try:
                month_wrapper.update()
                year_wrapper.update()
            except Exception:
                pass

            rebuild_content()

        def on_month_change(e):
            state["selected_month"] = e.control.value
            rebuild_content()

        def on_year_change(e):
            try:
                state["selected_year"] = int(e.control.value)
            except Exception:
                pass
            rebuild_content()

        period_type_dd.on_change = on_period_type_change
        month_dd.on_change = on_month_change
        year_dd.on_change = on_year_change

        # ══════════════════════════════════════════
        # ═══  خروجی PDF  ═══
        # ══════════════════════════════════════════

        def export_pdf(e):
            try:
                from pdf_generator import generate_financial_report_pdf
            except Exception as ex:
                msg("PDF در دسترس نیست: " + str(ex), D)
                return

            try:
                b_info = get_building_info()
                bank_info = {
                    "card": get_setting("bank_card", ""),
                    "owner": get_setting("bank_owner", ""),
                    "sheba": get_setting("bank_sheba", ""),
                }
                logo_path = get_logo_path()
                theme_color = get_setting("logo_bg_color", "#1565C0")

                data = collect_data()
                summary = calc_summary(data)

                categories = calc_categories(data.get("expenses", []))
                methods = calc_payment_methods(data.get("payments", []))
                debtors = calc_debtors(data.get("charges", []))

                # ⭐ رتبه‌بندی کامل همه پرداخت‌کنندگان
                all_payers = calc_all_payers_stats(
                    data.get("charges", []),
                    data.get("payments", []),
                )
                all_payers = [
                    s for s in all_payers if s["payments_count"] > 0
                ]

                # سازگاری با نسخه‌های قدیمی PDF
                top_payers = all_payers[:3] if all_payers else []
                late_payers = []

                def pay_sort_key(p):
                    pd = p.get("payment_date")
                    if pd is None:
                        return (1, 0)
                    return (0, pd.toordinal())

                sorted_payments = sorted(
                    data.get("payments", []),
                    key=pay_sort_key,
                )

                report_data = {
                    "label": data.get("label", "گزارش مالی"),
                    "summary": {
                        "total_charges": summary["total_charges"],
                        "total_payments": summary["total_payments"],
                        "total_expenses": summary["total_expenses"],
                        "net": summary["net"],
                        "total_remaining": summary["total_remaining"],
                        "collection_percent": summary["collection_pct"],
                        "paid_count": summary["paid_count"],
                        "partial_count": summary["partial_count"],
                        "unpaid_count": summary["unpaid_count"],
                    },
                    "charges": data.get("charges", []),
                    "payments": sorted_payments,
                    "expenses": data.get("expenses", []),
                    "bills": data.get("bills", []),
                    "categories": categories,
                    "methods": methods,
                    "debtors": debtors,
                    "all_payers": all_payers,  # ⭐ جدید
                    "top_payers": top_payers,
                    "late_payers": late_payers,
                    "expense_chart_path": state.get("expense_chart_path"),
                    "method_chart_path": state.get("method_chart_path"),
                    "trend_chart_path": state.get("trend_chart_path"),
                }

                result = generate_financial_report_pdf(
                    report_data=report_data,
                    building_name=b_info["name"],
                    building_info={
                        "address": b_info["address"],
                        "floors": b_info["floors"],
                        "total_units": b_info["total_units"],
                    },
                    bank_info=bank_info,
                    currency_label=get_currency_label(),
                    logo_path=logo_path,
                    theme_color=theme_color,
                )

                if result.get("success"):
                    msg("✅ PDF ساخته شد", S)
                    try:
                        os.startfile(result["path"])
                    except Exception:
                        try:
                            import subprocess
                            subprocess.Popen(["xdg-open", result["path"]])
                        except Exception:
                            pass
                else:
                    msg(result.get("message", "خطا در ساخت PDF"), D)

            except Exception as ex:
                msg("خطا: " + str(ex), D)
                import traceback
                traceback.print_exc()

        # ══════════════════════════════════════════
        # ═══  چیدمان نهایی  ═══
        # ══════════════════════════════════════════

        rebuild_content()

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("گزارش مالی", size=28,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN),
                    ft.Text("گزارش کامل مالی با تمام جزئیات",
                            size=12, color=TEXT_MUTED),
                ], spacing=2, expand=True),
                ft.Button(
                    "📄 خروجی PDF",
                    bgcolor=PURPLE,
                    color="white",
                    height=42,
                    on_click=export_pdf,
                ),
            ]),

            ft.Container(height=15),

            ft.Container(
                padding=15, border_radius=14,
                bgcolor=BG_CARD,
                content=ft.Row([
                    ft.Icon(ft.Icons.FILTER_ALT, color=P, size=22),
                    ft.Text("فیلتر:", size=13,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN),
                    ft.Container(width=10),
                    period_type_dd,
                    month_wrapper,
                    year_wrapper,
                ], spacing=10, wrap=True),
            ),

            ft.Container(height=15),

            content_col,

        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def build_sms_page():
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_MAIN = theme["bg_main"]
        BG_CARD = theme["bg_card"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        from services import get_sms_template

        TARGET_MAP = {
            "🏢 همه ساکنین": "all",
            "⚠️ فقط بدهکاران": "debtors",
            "✅ پرداخت‌کنندگان": "paid",
            "👤 انتخاب دستی": "custom",
        }

        TEMPLATE_MAP = {
            "🔔 یادآوری شارژ": "reminder",
            "🙏 تشکر از پرداخت": "thanks",
            "⚠️ اخطار عدم پرداخت": "overdue",
            "📅 اعلان جلسه": "meeting",
            "✏️ متن دلخواه": "custom",
        }

        def _get_dummy_unit():
            return {
                "id": 0,
                "number": "1",
                "resident_name": "علی احمدی",
                "phone": "09121234567",
                "debt": 500000,
            }

        def get_template_text(template_key, unit_info=None):
            if not unit_info:
                unit_info = _get_dummy_unit()
            return get_sms_template(template_key, unit_info=unit_info)

        state = {
            "current_template": "reminder",
            "current_target": "all",
            "selected_unit_id": None,
            "selected_unit_number": None,
        }

        units = list_units_with_debt()
        UNIT_MAP = {}
        unit_options_text = []
        for u in units:
            text = (
                f'واحد {to_persian(str(u["number"]))} - '
                f'{u["resident_name"] or "خالی"}'
            )
            UNIT_MAP[text] = u["id"]
            unit_options_text.append(text)

        def _get_sample_unit():
            fresh_units = list_units_with_debt()
            if not fresh_units:
                return None

            target = state["current_target"]

            if target == "debtors":
                debtors = [u for u in fresh_units if u.get("debt", 0) > 0]
                return debtors[0] if debtors else fresh_units[0]
            elif target == "paid":
                paid = [u for u in fresh_units if u.get("debt", 0) == 0]
                return paid[0] if paid else fresh_units[0]
            elif target == "custom":
                if state["selected_unit_id"]:
                    selected = [u for u in fresh_units if u["id"] == state["selected_unit_id"]]
                    if selected:
                        return selected[0]
                return fresh_units[0]
            return fresh_units[0]

        message_text = ft.TextField(
            label="متن پیام",
            multiline=True,
            min_lines=8,
            max_lines=12,
            expand=True,
        )

        char_counter = ft.Text("۰ کاراکتر", size=11, color=TEXT_MUTED)

        def update_counter():
            length = len(message_text.value or "")
            char_counter.value = f"{to_persian(str(length))} کاراکتر"
            char_counter.color = W if length > 70 else TEXT_MUTED

        def refresh_message_text():
            key = state["current_template"]
            if key == "custom":
                message_text.value = ""
                message_text.hint_text = (
                    "متن دلخواه خود را اینجا بنویسید...\n"
                    "می‌توانید از متغیرها استفاده کنید:\n"
                    "{نام} - {واحد} - {بدهی} - {ساختمان} - {کارت}"
                )
            else:
                sample = _get_sample_unit()
                message_text.value = get_template_text(key, sample)
                message_text.hint_text = None
            update_counter()
            page.update()

        def on_template_change(e):
            state["current_template"] = TEMPLATE_MAP.get(e.control.value, "reminder")
            refresh_message_text()

        def on_target_change(e):
            state["current_target"] = TARGET_MAP.get(e.control.value, "all")
            unit_selector.visible = (state["current_target"] == "custom")
            refresh_message_text()

        def on_unit_selected(e):
            state["selected_unit_id"] = UNIT_MAP.get(e.control.value)
            if state["current_template"] != "custom":
                refresh_message_text()

        def on_text_change(e):
            update_counter()
            page.update()

        message_text.on_change = on_text_change

        target_type = ft.Dropdown(
            label="ارسال به",
            width=250,
            value="🏢 همه ساکنین",
            on_change=on_target_change,
            options=[ft.dropdown.Option(text=t) for t in TARGET_MAP.keys()],
        )

        unit_selector = ft.Dropdown(
            label="انتخاب واحد",
            width=280,
            visible=False,
            on_change=on_unit_selected,
            options=[ft.dropdown.Option(text=t) for t in unit_options_text],
        )

        template_type = ft.Dropdown(
            label="نوع پیام",
            width=300,
            value="🔔 یادآوری شارژ",
            on_change=on_template_change,
            options=[ft.dropdown.Option(text=t) for t in TEMPLATE_MAP.keys()],
        )

        initial_sample = _get_sample_unit() or _get_dummy_unit()
        message_text.value = get_template_text("reminder", initial_sample)
        char_counter.value = f"{to_persian(str(len(message_text.value)))} کاراکتر"

        result_col = ft.Column(spacing=6)

        def get_target_units():
            all_units = list_units_with_debt()
            if state["current_target"] == "all":
                return all_units
            elif state["current_target"] == "debtors":
                return [u for u in all_units if u.get("debt", 0) > 0]
            elif state["current_target"] == "paid":
                return [u for u in all_units if u.get("debt", 0) == 0]
            elif state["current_target"] == "custom":
                if state["selected_unit_id"]:
                    return [u for u in all_units if u["id"] == state["selected_unit_id"]]
            return []

        def build_message_for_unit(u):
            key = state["current_template"]
            if key == "custom":
                try:
                    building_name = get_building_info().get("name") or "ساختمان"
                except Exception:
                    building_name = "ساختمان"
                bank_card = get_setting("bank_card", "") or "----"

                text = message_text.value or ""
                text = text.replace("{نام}", u.get("resident_name") or "")
                text = text.replace("{واحد}", to_persian(str(u.get("number") or "")))
                text = text.replace("{بدهی}", fmt_money(u.get("debt") or 0))
                text = text.replace("{ساختمان}", building_name)
                text = text.replace("{کارت}", bank_card)
                return text
            return get_template_text(key, u)

        def preview_messages(e):
            targets = get_target_units()
            if not targets:
                msg("گیرنده‌ای پیدا نشد.", W)
                return

            if (state["current_template"] == "custom"
                    and not (message_text.value or "").strip()):
                msg("متن پیام خالی است. لطفاً متن وارد کنید.", D)
                return

            result_col.controls.clear()
            result_col.controls.append(
                ft.Container(
                    bgcolor=theme["primary_bg"],
                    padding=12, border_radius=10,
                    content=ft.Text(
                        f'📋 پیش‌نمایش {to_persian(str(len(targets)))} پیام',
                        size=14, weight=ft.FontWeight.BOLD, color=P,
                    )
                )
            )

            for u in targets[:5]:
                text = build_message_for_unit(u)
                phone = u.get("phone") or "بدون شماره"
                result_col.controls.append(
                    ft.Container(
                        bgcolor=BG_CARD,
                        padding=12, border_radius=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(
                                    f'👤 {u.get("resident_name") or "-"}',
                                    weight=ft.FontWeight.BOLD,
                                    size=12, color=TEXT_MAIN,
                                ),
                                ft.Container(expand=True),
                                ft.Text(f'📱 {phone}', size=11, color=TEXT_SECONDARY),
                            ]),
                            ft.Container(
                                bgcolor=theme["bg_hover"],
                                padding=10, border_radius=6,
                                content=ft.Text(
                                    text, size=11, color=TEXT_MAIN,
                                    selectable=True,
                                )
                            ),
                        ], spacing=6)
                    )
                )

            if len(targets) > 5:
                result_col.controls.append(
                    ft.Text(
                        f'... و {to_persian(str(len(targets) - 5))} پیام دیگر',
                        size=12, color=TEXT_MUTED, italic=True,
                    )
                )
            page.update()

        def do_send_sms(e):
            targets = get_target_units()
            if not targets:
                msg("گیرنده‌ای انتخاب نشده", W)
                return

            if (state["current_template"] == "custom"
                    and not (message_text.value or "").strip()):
                msg("متن پیام خالی است. لطفاً متن وارد کنید.", D)
                return

            valid_targets = [u for u in targets if u.get("phone")]
            if not valid_targets:
                msg("هیچ واحدی شماره تلفن ندارد", D)
                return

            gate_user = get_setting("smsgate_username", "").strip()
            gate_pass = get_setting("smsgate_password", "").strip()
            if not gate_user or not gate_pass:
                msg("اطلاعات SMSGate تنظیم نشده. به تنظیمات → پیامک برو.", D)
                return

            result_col.controls.clear()
            result_col.controls.append(
                ft.Container(
                    bgcolor=theme["warning_bg"],
                    padding=12, border_radius=10,
                    content=ft.Text(
                        f'⏳ در حال ارسال به {to_persian(str(len(valid_targets)))} نفر...',
                        size=14, weight=ft.FontWeight.BOLD, color=W,
                    )
                )
            )
            page.update()

            success = 0
            failed = 0
            for u in valid_targets:
                text = build_message_for_unit(u)
                try:
                    result = send_sms(u["phone"], text)
                    if result.get("success"):
                        success += 1
                    else:
                        failed += 1
                        print(f"❌ خطا برای {u['phone']}: {result.get('message')}")
                except Exception as ex:
                    failed += 1
                    print(f"❌ Exception برای {u['phone']}: {ex}")

            result_col.controls.clear()
            result_col.controls.append(
                ft.Container(
                    bgcolor=theme["success_bg"],
                    padding=15, border_radius=10,
                    content=ft.Column([
                        ft.Text("✅ نتیجه ارسال", size=15,
                                weight=ft.FontWeight.BOLD, color=S),
                        ft.Text(f'✅ موفق: {to_persian(str(success))}', size=13, color=S),
                        ft.Text(f'❌ ناموفق: {to_persian(str(failed))}', size=13, color=D),
                    ], spacing=4)
                )
            )
            msg(
                f"ارسال کامل شد. موفق: {success}, ناموفق: {failed}",
                S if failed == 0 else W,
            )
            page.update()

        help_text = ft.Container(
            bgcolor=theme["warning_bg"],
            padding=12, border_radius=10,
            content=ft.Column([
                ft.Text("💡 متغیرهای قابل استفاده در متن دلخواه:",
                        size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Text("{نام} - نام ساکن  |  {واحد} - شماره واحد  |  {بدهی} - مبلغ بدهی",
                        size=11, color=TEXT_SECONDARY),
                ft.Text("{ساختمان} - نام ساختمان  |  {کارت} - شماره کارت",
                        size=11, color=TEXT_SECONDARY),
                ft.Text("⚡ این متغیرها هنگام ارسال، برای هر واحد جداگانه جایگزین می‌شوند",
                        size=11, color=P, weight=ft.FontWeight.BOLD),
            ], spacing=3)
        )

        gate_user = get_setting("smsgate_username", "").strip()
        is_gate_ready = bool(gate_user and get_setting("smsgate_password", "").strip())

        if is_gate_ready:
            status_bar = ft.Container(
                bgcolor=theme["success_bg"],
                border_radius=10, padding=12,
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=S, size=20),
                    ft.Text("SMSGate آماده است — ارسال از خط شخصی شما",
                            size=12, color=S, weight=ft.FontWeight.BOLD),
                ], spacing=8),
            )
        else:
            status_bar = ft.Container(
                bgcolor=theme["danger_bg"],
                border_radius=10, padding=12,
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR, color=D, size=20),
                    ft.Text("SMSGate تنظیم نشده! به تنظیمات → پیامک برو",
                            size=12, color=D, weight=ft.FontWeight.BOLD),
                ], spacing=8),
            )

        fresh_units = list_units_with_debt()
        total_count = len(fresh_units)
        debtor_count = len([u for u in fresh_units if u.get("debt", 0) > 0])
        paid_count = len([u for u in fresh_units if u.get("debt", 0) == 0])
        has_phone = len([u for u in fresh_units if u.get("phone")])

        stats_row = ft.Container(
            bgcolor=theme["bg_hover"],
            border_radius=10, padding=12,
            content=ft.Row([
                ft.Container(
                    padding=8, border_radius=8, bgcolor=theme["primary_bg"],
                    content=ft.Text(f'🏢 کل: {to_persian(str(total_count))}',
                                    size=12, color=P, weight=ft.FontWeight.BOLD)),
                ft.Container(
                    padding=8, border_radius=8, bgcolor=theme["danger_bg"],
                    content=ft.Text(f'⚠️ بدهکار: {to_persian(str(debtor_count))}',
                                    size=12, color=D, weight=ft.FontWeight.BOLD)),
                ft.Container(
                    padding=8, border_radius=8, bgcolor=theme["success_bg"],
                    content=ft.Text(f'✅ تسویه: {to_persian(str(paid_count))}',
                                    size=12, color=S, weight=ft.FontWeight.BOLD)),
                ft.Container(
                    padding=8, border_radius=8, bgcolor=theme["warning_bg"],
                    content=ft.Text(f'📱 دارای شماره: {to_persian(str(has_phone))}',
                                    size=12, color=W, weight=ft.FontWeight.BOLD)),
            ], spacing=8, wrap=True)
        )

        return ft.Column([
            ft.Text("پیامک و اطلاع‌رسانی", size=28,
                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
            stats_row,
            ft.Container(height=8),
            status_bar,
            ft.Container(height=8),
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SMS, color=P, size=24),
                        ft.Text("ارسال پیامک", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ], spacing=8),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Row([target_type, unit_selector], wrap=True),
                    ft.Row([template_type]),
                    ft.Row([message_text]),
                    ft.Row([char_counter, ft.Container(expand=True)]),
                    help_text,
                    ft.Row([
                        ft.Button("👁️ پیش‌نمایش", bgcolor=P, color="white",
                                  on_click=preview_messages, width=150),
                        ft.Button("📤 ارسال پیامک", bgcolor=S, color="white",
                                  on_click=do_send_sms, width=180),
                    ], spacing=8),
                ], spacing=12)
            ),
            ft.Container(height=15),
            result_col,
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    # ═══════════ صفحه یادداشت‌ها ═══════════
    def build_notes_page():
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_CARD = theme["bg_card"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        CATEGORIES = [
            "کار", "جلسه", "خرید",
            "تعمیرات", "شخصی", "یادآوری"
        ]

        CATEGORY_ICONS = {
            "کار": "💼", "جلسه": "📅", "خرید": "🛒",
            "تعمیرات": "🔧", "شخصی": "👤", "یادآوری": "⏰",
        }

        NOTE_COLORS = {
            "yellow": {"bg": "#FFF9C4", "border": "#F9A825", "dark_bg": "#5D4E00"},
            "green": {"bg": "#C8E6C9", "border": "#2E7D32", "dark_bg": "#1B5E20"},
            "orange": {"bg": "#FFCCBC", "border": "#E64A19", "dark_bg": "#5D2A00"},
            "purple": {"bg": "#E1BEE7", "border": "#6A1B9A", "dark_bg": "#4A148C"},
            "blue": {"bg": "#BBDEFB", "border": "#1565C0", "dark_bg": "#0D47A1"},
            "pink": {"bg": "#F8BBD0", "border": "#AD1457", "dark_bg": "#880E4F"},
        }

        PRIORITY_LABELS = {
            "normal": "عادی", "important": "مهم", "urgent": "فوری",
        }

        PRIORITY_COLORS = {
            "normal": TEXT_MUTED, "important": W, "urgent": D,
        }

        state = {
            "filter_category": None,
            "only_pinned": False,
            "only_reminder": False,
            "show_done": False,
            "search": "",
        }

        notes_grid_container = ft.Column(spacing=15)

        # ═══════════ ساخت Border استاندارد و ایمن ═══════════
        def make_safe_border(width, color):
            return ft.Border(
                top=ft.BorderSide(width, color),
                bottom=ft.BorderSide(width, color),
                left=ft.BorderSide(width, color),
                right=ft.BorderSide(width, color),
            )

        # ═══════════ کارت یادداشت ═══════════
        def build_note_card(note):
            color_info = NOTE_COLORS.get(
                note["color"] or "yellow",
                NOTE_COLORS["yellow"]
            )

            if is_dark_mode():
                bg_color = color_info["dark_bg"]
                border_color = color_info["border"]
            else:
                bg_color = color_info["bg"]
                border_color = color_info["border"]

            icon = CATEGORY_ICONS.get(
                note["category"], "📝"
            )
            priority_color = PRIORITY_COLORS.get(
                note["priority"], TEXT_MUTED
            )
            priority_label = PRIORITY_LABELS.get(
                note["priority"], "عادی"
            )

            reminder_text = None
            if note["reminder_at"]:
                try:
                    r = note["reminder_at"]
                    j = jdatetime.datetime.fromgregorian(date=r)
                    reminder_text = to_persian(
                        f"{j.year}/{j.month:02d}/{j.day:02d} "
                        f"{j.hour:02d}:{j.minute:02d}"
                    )
                except Exception:
                    pass

            def make_toggle_done(nid):
                def do(e):
                    toggle_note_done(nid)
                    load_notes()

                return do

            def make_toggle_pin(nid):
                def do(e):
                    toggle_note_pin(nid)
                    load_notes()

                return do

            def make_edit(nid):
                def do(e):
                    show_note_dialog(nid)

                return do

            def make_delete(nid):
                def do(e):
                    delete_note(nid)
                    msg("یادداشت حذف شد.", W)
                    load_notes()

                return do

            footer_items = [
                ft.Container(
                    padding=ft.Padding(6, 3, 6, 3),
                    border_radius=8,
                    bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Text(icon, size=11),
                        ft.Text(
                            note["category"], size=10,
                            color=TEXT_MAIN,
                        ),
                    ], spacing=3),
                ),
            ]

            if note["priority"] != "normal":
                footer_items.append(ft.Container(
                    padding=ft.Padding(6, 3, 6, 3),
                    border_radius=8,
                    bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Container(
                            width=8, height=8,
                            border_radius=4,
                            bgcolor=priority_color,
                        ),
                        ft.Text(
                            priority_label, size=10,
                            color=priority_color,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ], spacing=3),
                ))

            if reminder_text:
                footer_items.append(ft.Container(
                    padding=ft.Padding(6, 3, 6, 3),
                    border_radius=8,
                    bgcolor=BG_CARD,
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.ALARM, size=12, color=P
                        ),
                        ft.Text(
                            reminder_text, size=9,
                            color=P,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ], spacing=3),
                ))

            return ft.Container(
                expand=1,
                bgcolor=bg_color,
                border=make_safe_border(2, border_color),
                border_radius=14,
                padding=15,
                opacity=0.6 if note["is_done"] else 1.0,
                content=ft.Column([
                    ft.Row([
                        ft.Checkbox(
                            value=bool(note["is_done"]),
                            on_change=make_toggle_done(note["id"]),
                            scale=0.9,
                        ),
                        ft.Text(
                            note["title"], size=14,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN, expand=True,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.IconButton(
                            icon=(
                                ft.Icons.PUSH_PIN
                                if note["is_pinned"]
                                else ft.Icons.PUSH_PIN_OUTLINED
                            ),
                            icon_color=(
                                W if note["is_pinned"]
                                else TEXT_MUTED
                            ),
                            icon_size=18,
                            on_click=make_toggle_pin(note["id"]),
                        ),
                    ], spacing=4),
                    ft.Divider(height=1, color=border_color),
                    ft.Text(
                        note["content"] or "", size=12,
                        color=TEXT_SECONDARY,
                        max_lines=4,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ) if note["content"]
                    else ft.Container(height=1),
                    ft.Container(height=5),
                    ft.Row(
                        footer_items, spacing=5, wrap=True
                    ),
                    ft.Container(height=5),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=P, icon_size=18,
                            on_click=make_edit(note["id"]),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=D, icon_size=18,
                            on_click=make_delete(note["id"]),
                        ),
                    ], spacing=0,
                        alignment=ft.MainAxisAlignment.END),
                ], spacing=6),
            )

        # ═══════════ لود ═══════════
        def load_notes():
            notes = list_notes(
                category=state["filter_category"],
                only_pinned=state["only_pinned"],
                only_with_reminder=state["only_reminder"],
                only_undone=not state["show_done"],
                search=state["search"] or None,
            )

            notes_grid_container.controls.clear()

            if not notes:
                notes_grid_container.controls.append(
                    ft.Container(
                        padding=30,
                        bgcolor=BG_CARD,
                        border_radius=14,
                        height=200,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.NOTE_ADD,
                                size=50, color=TEXT_MUTED
                            ),
                            ft.Text(
                                "یادداشتی پیدا نشد",
                                color=TEXT_MUTED, size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "برای شروع، یادداشت جدیدی بسازید",
                                color=TEXT_MUTED, size=11,
                            ),
                        ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6),
                    )
                )
            else:
                current_row = []
                for note in notes:
                    current_row.append(
                        build_note_card(note)
                    )
                    if len(current_row) == 3:
                        notes_grid_container.controls.append(
                            ft.Row(current_row, spacing=15)
                        )
                        current_row = []

                if current_row:
                    while len(current_row) < 3:
                        current_row.append(
                            ft.Container(expand=1)
                        )
                    notes_grid_container.controls.append(
                        ft.Row(current_row, spacing=15)
                    )

            try:
                notes_grid_container.update()
            except Exception:
                pass

        # ═══════════ دیالوگ ═══════════
        def show_note_dialog(note_id=None):
            editing = note_id is not None

            title_field = ft.TextField(
                label="عنوان *", width=460, autofocus=True,
            )
            content_field = ft.TextField(
                label="متن یادداشت", width=460,
                multiline=True, min_lines=4, max_lines=8,
            )

            category_dd = ft.Dropdown(
                label="دسته‌بندی", width=220,
                value="یادآوری",
                options=[
                    ft.dropdown.Option(text=c)
                    for c in CATEGORIES
                ]
            )

            PRIORITY_MAP = {
                "عادی": "normal", "مهم": "important",
                "فوری": "urgent",
            }
            PRIORITY_REVERSE = {
                v: k for k, v in PRIORITY_MAP.items()
            }
            priority_dd = ft.Dropdown(
                label="اولویت", width=220, value="عادی",
                options=[
                    ft.dropdown.Option(text=t)
                    for t in PRIORITY_MAP.keys()
                ]
            )

            COLOR_MAP = {
                "🟡 زرد": "yellow", "🟢 سبز": "green",
                "🟠 نارنجی": "orange", "🟣 بنفش": "purple",
                "🔵 آبی": "blue", "🩷 صورتی": "pink",
            }
            COLOR_REVERSE = {
                v: k for k, v in COLOR_MAP.items()
            }
            color_dd = ft.Dropdown(
                label="رنگ", width=220, value="🟡 زرد",
                options=[
                    ft.dropdown.Option(text=t)
                    for t in COLOR_MAP.keys()
                ]
            )

            has_reminder = ft.Checkbox(
                label="فعال‌سازی یادآوری", value=False,
            )
            reminder_date = date_field_with_picker(
                "تاریخ یادآوری", 200, default_today=False,
            )
            reminder_time = ft.TextField(
                label="ساعت (HH:MM)", width=150,
                hint_text="14:30", value="12:00",
            )

            reminder_row = ft.Row(
                [reminder_date, reminder_time],
                wrap=True, visible=False,
            )

            def on_reminder_toggle(e):
                reminder_row.visible = has_reminder.value
                try:
                    reminder_row.update()
                except Exception:
                    pass

            has_reminder.on_change = on_reminder_toggle

            if editing:
                note = get_note_by_id(note_id)
                if note:
                    title_field.value = note["title"]
                    content_field.value = (
                            note["content"] or ""
                    )
                    category_dd.value = (
                            note["category"] or "یادآوری"
                    )
                    priority_dd.value = PRIORITY_REVERSE.get(
                        note["priority"], "عادی"
                    )
                    color_dd.value = COLOR_REVERSE.get(
                        note["color"], "🟡 زرد"
                    )

                    if note["reminder_at"]:
                        has_reminder.value = True
                        reminder_row.visible = True
                        r = note["reminder_at"]
                        try:
                            j = jdatetime.date.fromgregorian(
                                date=r.date()
                            )
                            reminder_date.text_field.value = (
                                f"{j.year}/"
                                f"{j.month:02d}/"
                                f"{j.day:02d}"
                            )
                            reminder_time.value = (
                                f"{r.hour:02d}:"
                                f"{r.minute:02d}"
                            )
                        except Exception:
                            pass

            def close_dlg(e):
                note_dlg.open = False
                page.update()
                try:
                    page.overlay.remove(note_dlg)
                except Exception:
                    pass

            def save_note(e):
                if not title_field.value or \
                        not title_field.value.strip():
                    msg("عنوان الزامی است.", D)
                    return

                try:
                    reminder_str = None
                    if has_reminder.value:
                        r_date = reminder_date.text_field.value
                        r_time = (
                                reminder_time.value or "12:00"
                        )
                        if r_date:
                            reminder_str = (
                                f"{r_date} {r_time}"
                            )

                    priority_key = PRIORITY_MAP.get(
                        priority_dd.value, "normal"
                    )
                    color_key = COLOR_MAP.get(
                        color_dd.value, "yellow"
                    )

                    if editing:
                        update_note(
                            note_id=note_id,
                            title=title_field.value,
                            content=content_field.value,
                            category=category_dd.value,
                            priority=priority_key,
                            color=color_key,
                            reminder_at=(
                                reminder_str
                                if has_reminder.value
                                else ""
                            ),
                        )
                        msg("یادداشت بروزرسانی شد.", S)
                    else:
                        add_note(
                            title=title_field.value,
                            content=content_field.value,
                            category=category_dd.value,
                            priority=priority_key,
                            color=color_key,
                            reminder_at=reminder_str,
                        )
                        msg("یادداشت ثبت شد.", S)

                    note_dlg.open = False
                    page.update()
                    try:
                        page.overlay.remove(note_dlg)
                    except Exception:
                        pass

                    load_notes()

                except Exception as ex:
                    msg(f"خطا: {ex}", D)

            note_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    (
                        "✏️ ویرایش یادداشت"
                        if editing
                        else "📝 یادداشت جدید"
                    ),
                    size=18, weight=ft.FontWeight.BOLD,
                ),
                content=ft.Container(
                    width=520,
                    content=ft.Column([
                        title_field,
                        content_field,
                        ft.Row(
                            [category_dd, priority_dd],
                            wrap=True,
                        ),
                        ft.Row([color_dd]),
                        ft.Divider(height=1),
                        has_reminder,
                        reminder_row,
                    ],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=12, tight=True),
                ),
                actions=[
                    ft.Button(
                        "💾 ذخیره", bgcolor=P,
                        color="white", on_click=save_note,
                    ),
                    ft.TextButton(
                        "انصراف", on_click=close_dlg,
                    ),
                ],
            )
            if note_dlg not in page.overlay:
                page.overlay.append(note_dlg)
            note_dlg.open = True
            page.update()

        # ═══════════ آمار ═══════════
        try:
            stats = get_notes_stats()
        except Exception:
            stats = {
                "total": 0, "done": 0, "undone": 0,
                "with_reminder": 0, "today_reminders": 0,
            }

        stats_row = ft.Row([
            ft.Container(
                padding=12, border_radius=12,
                bgcolor=theme["primary_bg"],
                content=ft.Row([
                    ft.Text("📝", size=18),
                    ft.Column([
                        ft.Text(
                            "کل", size=10,
                            color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            to_persian(str(stats["total"])),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=P,
                        ),
                    ], spacing=0),
                ], spacing=8),
            ),
            ft.Container(
                padding=12, border_radius=12,
                bgcolor=theme["success_bg"],
                content=ft.Row([
                    ft.Text("✅", size=18),
                    ft.Column([
                        ft.Text(
                            "انجام شده", size=10,
                            color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            to_persian(str(stats["done"])),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=S,
                        ),
                    ], spacing=0),
                ], spacing=8),
            ),
            ft.Container(
                padding=12, border_radius=12,
                bgcolor=theme["warning_bg"],
                content=ft.Row([
                    ft.Text("⏰", size=18),
                    ft.Column([
                        ft.Text(
                            "امروز/فردا", size=10,
                            color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            to_persian(
                                str(stats["today_reminders"])
                            ),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=W,
                        ),
                    ], spacing=0),
                ], spacing=8),
            ),
            ft.Container(
                padding=12, border_radius=12,
                bgcolor=theme["purple_bg"],
                content=ft.Row([
                    ft.Text("🔔", size=18),
                    ft.Column([
                        ft.Text(
                            "یادآوری", size=10,
                            color=TEXT_SECONDARY,
                        ),
                        ft.Text(
                            to_persian(
                                str(stats["with_reminder"])
                            ),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=theme["purple"],
                        ),
                    ], spacing=0),
                ], spacing=8),
            ),
        ], spacing=10, wrap=True)

        # ═══════════ جستجو ═══════════
        search_field = ft.TextField(
            label="🔍 جستجو در یادداشت‌ها",
            expand=True,
            on_change=lambda e: (
                state.update({"search": e.control.value}),
                load_notes()
            ),
        )

        new_btn = ft.Button(
            "➕ یادداشت جدید",
            bgcolor=W, color="white",
            on_click=lambda e: show_note_dialog(),
            height=45,
        )

        # ═══════════ دسته‌بندی ═══════════
        def make_filter_click(cat):
            def on_click(e):
                if state["filter_category"] == cat:
                    state["filter_category"] = None
                else:
                    state["filter_category"] = cat
                load_notes()
                for btn in category_buttons:
                    is_active = (
                            btn.data == state["filter_category"]
                    )
                    btn.bgcolor = (
                        P if is_active else theme["bg_hover"]
                    )
                    btn.color = (
                        "white" if is_active
                        else TEXT_SECONDARY
                    )
                try:
                    for btn in category_buttons:
                        btn.update()
                except Exception:
                    pass

            return on_click

        all_btn = ft.Button(
            "همه", bgcolor=P, color="white",
            on_click=make_filter_click(None), data=None,
        )

        category_buttons = [all_btn]
        for cat in CATEGORIES:
            btn = ft.Button(
                f"{CATEGORY_ICONS[cat]} {cat}",
                bgcolor=theme["bg_hover"],
                color=TEXT_SECONDARY,
                on_click=make_filter_click(cat), data=cat,
            )
            category_buttons.append(btn)

        def on_pinned_toggle(e):
            state["only_pinned"] = e.control.value
            load_notes()

        def on_reminder_check(e):
            state["only_reminder"] = e.control.value
            load_notes()

        def on_show_done_toggle(e):
            state["show_done"] = e.control.value
            load_notes()

        pinned_check = ft.Checkbox(
            label="📌 پین‌شده‌ها", value=False,
            on_change=on_pinned_toggle,
        )
        reminder_check = ft.Checkbox(
            label="⏰ دارای یادآوری", value=False,
            on_change=on_reminder_check,
        )
        done_check = ft.Checkbox(
            label="✅ شامل انجام شده‌ها", value=False,
            on_change=on_show_done_toggle,
        )

        load_notes()

        return ft.Column([
            ft.Text(
                "یادداشت‌ها", size=28,
                weight=ft.FontWeight.BOLD,
                color=TEXT_MAIN,
            ),
            ft.Container(height=10),
            stats_row,
            ft.Container(height=10),
            ft.Row(
                [search_field, new_btn],
                spacing=10,
            ),
            ft.Container(height=8),
            ft.Row(
                category_buttons,
                spacing=6, wrap=True,
            ),
            ft.Container(height=8),
            ft.Row([
                pinned_check,
                reminder_check,
                done_check,
            ], spacing=10, wrap=True),
            ft.Container(height=15),
            notes_grid_container,
            ft.Container(height=20),
        ], scroll=ft.ScrollMode.AUTO, expand=True,
            spacing=0)

    # ═══════════ اعمال آنیِ تغییر واحد پول/تم ═══════════
    def apply_appearance_change():
        """
        بعد از تغییر واحد پول یا حالت روشن/تاریک، به‌جای ری‌استارت
        کامل برنامه (که قبلاً هم برای تم subprocess جدید باز می‌کرد و
        هم برای واحد پول فقط یه پیام «برنامه رو دوباره باز کنید» نشون
        می‌داد)، همین‌جا صفحه‌ی فعلی و رنگ‌های اصلی رو با مقادیر جدید
        دوباره می‌سازیم. توجه: چون سایدبار (منو/آیکون‌ها) فقط یک‌بار
        موقع باز شدن برنامه ساخته می‌شه، رنگ پس‌زمینه‌اش آپدیت می‌شه
        ولی رنگ آیکون‌های منو تا دفعه‌ی بعد که برنامه باز بشه همون
        رنگ قبلی می‌مونه (یه محدودیت جزئی و صرفاً ظاهری).
        """
        try:
            page.theme_mode = (
                ft.ThemeMode.DARK
                if is_dark_mode() else ft.ThemeMode.LIGHT
            )
            new_theme = get_theme_colors()
            page.bgcolor = new_theme["bg_main"]
            try:
                side.bgcolor = new_theme["bg_sidebar"]
            except Exception:
                pass

            builder = current_page_builder.get("builder")
            if builder:
                content_area.content = builder()

            page.update()
        except Exception as ex:
            print(f"⚠️ خطای اعمال آنیِ ظاهر: {ex}")

    # ═══════════ تنظیمات ═══════════
    def build_settings_page():
        theme = get_theme_colors()
        P = theme["primary"]
        S = theme["success"]
        W = theme["warning"]
        D = theme["danger"]
        BG_MAIN = theme["bg_main"]
        BG_CARD = theme["bg_card"]
        TEXT_MAIN = theme["text_main"]
        TEXT_SECONDARY = theme["text_secondary"]
        TEXT_MUTED = theme["text_muted"]
        DIVIDER = theme["divider"]

        info = get_building_info()

        # ─── اطلاعات ساختمان ───
        bn = ft.TextField(label="نام ساختمان *", width=250, value=info["name"])
        ba = ft.TextField(label="آدرس", width=350, value=info["address"])
        bf = ft.TextField(label="طبقات", width=120, value=str(info["floors"]))
        bu = ft.TextField(label="تعداد واحدها", width=120, value=str(info["total_units"]))

        # ─── اطلاعات بانکی ───
        bc = ft.TextField(label="شماره کارت", width=250, value=get_setting("bank_card", ""))
        bac = ft.TextField(label="شماره حساب", width=250, value=get_setting("bank_account", ""))
        bsh = ft.TextField(label="شماره شبا", width=300, value=get_setting("bank_sheba", ""))
        bon = ft.TextField(label="نام صاحب حساب", width=250, value=get_setting("bank_owner", ""))

        # ─── موجودی اولیه ───
        init_bal = make_amount_field(
            label="موجودی اولیه صندوق", width=250,
            initial_value=get_setting("initial_balance", "0"),
        )

        # ─── واحد پول ───
        CURRENCY_MAP = {"تومان": "toman", "ریال": "rial"}
        CURRENCY_MAP_REVERSE = {v: k for k, v in CURRENCY_MAP.items()}
        current_currency = get_setting("currency", "toman")
        current_currency_text = CURRENCY_MAP_REVERSE.get(current_currency, "تومان")

        currency_selector = ft.Dropdown(
            label="واحد پول", width=250, value=current_currency_text,
            options=[ft.dropdown.Option(text="تومان"), ft.dropdown.Option(text="ریال")],
        )

        # ═══════════ حالت نمایش (تم) ═══════════
        THEME_MAP = {"☀️ حالت روشن": "light", "🌙 حالت تاریک": "dark"}
        THEME_MAP_REVERSE = {v: k for k, v in THEME_MAP.items()}
        current_theme = get_setting("theme_mode", "light")
        current_theme_text = THEME_MAP_REVERSE.get(current_theme, "☀️ حالت روشن")

        theme_selector = ft.Dropdown(
            label="حالت نمایش", width=250, value=current_theme_text,
            options=[ft.dropdown.Option(text="☀️ حالت روشن"),
                     ft.dropdown.Option(text="🌙 حالت تاریک")],
        )

        def on_save_theme(e):
            new_theme = THEME_MAP.get(theme_selector.value, "light")
            if new_theme == current_theme:
                msg("تغییری اعمال نشد", W)
                return
            set_setting("theme_mode", new_theme)
            apply_appearance_change()
            msg(f"✅ {theme_selector.value} فعال شد.", S)

        # ═══════════ لوگو ساختمان ═══════════
        LOGO_COLORS = {
            "🔵 آبی": "#1565C0", "🟢 سبز": "#2E7D32",
            "🟠 نارنجی": "#EF6C00", "🔴 قرمز": "#C62828",
            "🟣 بنفش": "#6A1B9A", "🟡 زرد": "#F9A825",
            "⚫ مشکی": "#212121", "🔷 فیروزه‌ای": "#00838F",
        }
        LOGO_COLORS_REVERSE = {v: k for k, v in LOGO_COLORS.items()}
        current_logo_bg = get_setting("logo_bg_color", "#1565C0")
        current_logo_bg_text = LOGO_COLORS_REVERSE.get(current_logo_bg, "🔵 آبی")

        logo_color_dd = ft.Dropdown(
            label="رنگ پس‌زمینه لوگو", width=200, value=current_logo_bg_text,
            options=[ft.dropdown.Option(text=c) for c in LOGO_COLORS.keys()],
        )

        logo_text_color_dd = ft.Dropdown(
            label="رنگ متن", width=150,
            value=("سفید" if get_setting("logo_text_color", "white") == "white" else "مشکی"),
            options=[ft.dropdown.Option(text="سفید"), ft.dropdown.Option(text="مشکی")],
        )

        def _make_placeholder():
            return ft.Column([
                ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=50, color=TEXT_MUTED),
                ft.Text("لوگویی ساخته نشده", size=12, color=TEXT_MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, spacing=8)

        logo_preview_container = ft.Container(
            width=220, height=220, border_radius=15,
            bgcolor=theme["bg_hover"], padding=10,
            content=_make_placeholder(),
        )

        def load_logo_preview():
            try:
                logo_path = get_logo_path()
                if logo_path and os.path.exists(logo_path):
                    b64 = _read_image_base64(logo_path)
                    if b64:
                        logo_preview_container.content = ft.Image(
                            src=b64, width=200, height=200,
                            fit=ft.BoxFit.CONTAIN,
                            error_content=_make_placeholder(),
                        )
                    else:
                        logo_preview_container.content = _make_placeholder()
                else:
                    logo_preview_container.content = _make_placeholder()
                logo_preview_container.update()
            except Exception as ex:
                print(f"❌ خطای بارگذاری لوگو: {ex}")

        def on_generate_logo(e):
            try:
                import time
                building_name = (bn.value or "ساختمان").strip()
                bg_color = LOGO_COLORS.get(logo_color_dd.value, "#1565C0")
                text_color = "white" if logo_text_color_dd.value == "سفید" else "black"

                logo_path = generate_circular_logo(
                    text=building_name, bg_color=bg_color, text_color=text_color,
                )

                if logo_path:
                    set_setting("logo_bg_color", bg_color)
                    set_setting("logo_text_color", text_color)
                    load_logo_preview()

                    try:
                        sidebar_logo.content = build_logo_image(width=180, height=180)
                        sidebar_logo.update()
                    except Exception as ex:
                        print(f"⚠️ لوگوی سایدبار: {ex}")

                    try:
                        unique_ico = f"icon_{int(time.time() * 1000)}.ico"
                        ico_path = os.path.join(get_icons_dir(), unique_ico)
                        if convert_logo_to_icon(logo_path, ico_path):
                            page.window.icon = ico_path
                            page.update()
                            set_setting("current_icon_path", ico_path)
                            try:
                                if tray_manager.running:
                                    tray_manager.update_icon(ico_path)
                            except Exception:
                                pass
                    except Exception as ex:
                        print(f"⚠️ آیکون: {ex}")

                    msg("✅ لوگو ساخته و اعمال شد!", S)
                else:
                    msg("❌ خطا در ساخت لوگو", D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)
                import traceback
                traceback.print_exc()

        # ═══════════ بکاپ‌گیری ═══════════
        backup_list_col = ft.Column(spacing=8)
        backup_stats_text = ft.Text("", size=13, color=TEXT_SECONDARY)

        def load_backups():
            backup_list_col.controls.clear()
            backups = list_backups()
            stats = get_backup_stats()

            backup_stats_text.value = (
                f"📊 تعداد: {to_persian(str(stats['total']))} "
                f"(خودکار: {to_persian(str(stats['auto']))}, "
                f"دستی: {to_persian(str(stats['manual']))}) | "
                f"حجم: {to_persian(str(stats['total_size_mb']))} MB"
            )

            if not backups:
                backup_list_col.controls.append(
                    ft.Container(
                        padding=20, bgcolor=BG_CARD, border_radius=10,
                        content=ft.Column([
                            ft.Icon(ft.Icons.BACKUP, size=50, color=TEXT_MUTED),
                            ft.Text("بکاپی موجود نیست", color=TEXT_MUTED, size=13),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
                    )
                )
                try:
                    backup_list_col.update()
                    backup_stats_text.update()
                except Exception:
                    pass
                return

            for b in backups[:10]:
                type_color = S if b["type"] == "خودکار" else P
                type_bg = theme["success_bg"] if b["type"] == "خودکار" else theme["primary_bg"]

                def make_restore(filepath, filename):
                    def do_restore(e):
                        show_restore_confirm(filepath, filename)

                    return do_restore

                def make_delete(filepath, filename):
                    def do_delete(e):
                        show_delete_confirm(filepath, filename)

                    return do_delete

                backup_list_col.controls.append(
                    ft.Container(
                        bgcolor=theme["bg_hover"], border_radius=10, padding=12,
                        content=ft.Row([
                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color=P, size=24),
                            ft.Column([
                                ft.Row([
                                    ft.Text(f'{b["date"]} - {b["time"]}', size=13,
                                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                                    ft.Container(
                                        padding=4, border_radius=6, bgcolor=type_bg,
                                        content=ft.Text(b["type"], size=10,
                                                        color=type_color,
                                                        weight=ft.FontWeight.BOLD),
                                    ),
                                ], spacing=8),
                                ft.Text(f'{b["filename"]} - {to_persian(str(b["size_kb"]))} KB',
                                        size=10, color=TEXT_MUTED),
                            ], spacing=3, expand=True),
                            ft.IconButton(icon=ft.Icons.RESTORE, icon_color=S,
                                          tooltip="بازیابی",
                                          on_click=make_restore(b["filepath"], b["filename"])),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_color=D,
                                          tooltip="حذف",
                                          on_click=make_delete(b["filepath"], b["filename"])),
                        ], spacing=8)
                    )
                )
            try:
                backup_list_col.update()
                backup_stats_text.update()
            except Exception:
                pass

        def on_manual_backup(e):
            try:
                result = create_backup(auto=False)
                if result["success"]:
                    msg(f"✅ {result['message']}", S)
                    load_backups()
                else:
                    msg(f"❌ {result['message']}", D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        def show_restore_confirm(filepath, filename):
            def do_restore(e):
                try:
                    result = restore_backup(filepath)
                    confirm_dlg.open = False
                    page.update()
                    if result["success"]:
                        apply_appearance_change()
                        msg(f"✅ {result['message']}", S)
                    else:
                        msg(f"❌ {result['message']}", D)
                except Exception as ex:
                    msg(f"خطا: {ex}", D)

            def close_dlg(e):
                confirm_dlg.open = False
                page.update()

            confirm_dlg = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=W, size=28),
                    ft.Text("تایید بازیابی", weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                content=ft.Container(
                    width=400, bgcolor=BG_CARD,
                    content=ft.Column([
                        ft.Text("آیا مطمئن هستید؟", size=14,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Container(
                            bgcolor=theme["warning_bg"], border_radius=8, padding=10,
                            content=ft.Column([
                                ft.Text("⚠️ اطلاعات فعلی جایگزین می‌شود.", size=12, color=W),
                                ft.Text("💾 یک بکاپ احتیاطی گرفته می‌شود.", size=12, color=S),
                                ft.Text("🔄 بعد از بازیابی، برنامه رو باز کنید.", size=12, color=P),
                            ], spacing=5),
                        ),
                        ft.Text(f"📁 {filename}", size=11, color=TEXT_MUTED),
                    ], tight=True, spacing=10)
                ),
                actions=[
                    ft.Button("بله، بازیابی کن", bgcolor=W, color="white", on_click=do_restore),
                    ft.TextButton("انصراف", on_click=close_dlg),
                ],
            )
            if confirm_dlg not in page.overlay:
                page.overlay.append(confirm_dlg)
            confirm_dlg.open = True
            page.update()

        def show_delete_confirm(filepath, filename):
            def do_delete(e):
                try:
                    result = delete_backup(filepath)
                    del_dlg.open = False
                    page.update()
                    if result["success"]:
                        msg(f"✅ {result['message']}", W)
                        load_backups()
                    else:
                        msg(f"❌ {result['message']}", D)
                except Exception as ex:
                    msg(f"خطا: {ex}", D)

            def close_dlg(e):
                del_dlg.open = False
                page.update()

            del_dlg = ft.AlertDialog(
                title=ft.Text("حذف بکاپ", weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                content=ft.Container(
                    width=350, bgcolor=BG_CARD,
                    content=ft.Text(f"آیا از حذف این بکاپ مطمئن هستید؟\n\n{filename}",
                                    size=13, color=TEXT_SECONDARY)
                ),
                actions=[
                    ft.Button("بله، حذف کن", bgcolor=D, color="white", on_click=do_delete),
                    ft.TextButton("انصراف", on_click=close_dlg),
                ],
            )
            if del_dlg not in page.overlay:
                page.overlay.append(del_dlg)
            del_dlg.open = True
            page.update()

        load_backups()

        # ─── صدور خودکار شارژ ───
        AUTO_METHOD_MAP = {
            "مبلغ ثابت": "manual",
            "بر اساس متراژ": "area",
            "بر اساس نفرات": "person",
        }
        AUTO_METHOD_MAP_REVERSE = {v: k for k, v in AUTO_METHOD_MAP.items()}

        auto_enabled = ft.Checkbox(
            label="فعال‌سازی صدور خودکار شارژ ماهانه",
            value=(get_setting("auto_charge_enabled", "0") == "1"),
        )
        current_auto_method = get_setting("auto_charge_method", "manual")
        current_auto_method_text = AUTO_METHOD_MAP_REVERSE.get(current_auto_method, "مبلغ ثابت")

        auto_method = ft.Dropdown(
            label="روش محاسبه", width=220, value=current_auto_method_text,
            options=[ft.dropdown.Option(text="مبلغ ثابت"),
                     ft.dropdown.Option(text="بر اساس متراژ"),
                     ft.dropdown.Option(text="بر اساس نفرات")],
        )
        auto_value = make_amount_field(
            label="مبلغ / نرخ", width=200,
            initial_value=get_setting("auto_charge_value", "0"),
        )
        auto_issue_day = ft.TextField(
            label="روز صدور شارژ (1-28)", width=180,
            value=get_setting("auto_charge_issue_day", "1"), hint_text="مثال: 1",
        )
        auto_due_day = ft.TextField(
            label="روز مهلت پرداخت (1-28)", width=180,
            value=get_setting("auto_charge_due_day", "15"), hint_text="مثال: 15",
        )

        sms_on_issue = ft.Checkbox(
            label="ارسال پیامک هنگام صدور شارژ",
            value=(get_setting("sms_on_issue", "0") == "1"),
        )
        sms_reminder = ft.Checkbox(
            label="ارسال پیامک یادآوری ۱ روز قبل از سررسید",
            value=(get_setting("sms_reminder", "0") == "1"),
        )
        sms_overdue = ft.Checkbox(
            label="ارسال پیامک پس از عدم پرداخت",
            value=(get_setting("sms_overdue", "0") == "1"),
        )
        sms_thanks_on_payment = ft.Checkbox(
            label="📬 ارسال پیامک تشکر پس از ثبت پرداخت",
            value=(get_setting("sms_thanks_on_payment", "0") == "1"),
        )

        late_fee_enabled = ft.Checkbox(
            label="فعال‌سازی جریمه دیرکرد",
            value=(get_setting("late_fee_enabled", "0") == "1"),
        )
        late_fee_amount = make_amount_field(
            label="مبلغ جریمه", width=200,
            initial_value=get_setting("late_fee_amount", "100000"),
        )

        # ─── شناسه قبض‌ها ───
        water_bill_id = ft.TextField(label="شناسه قبض آب", width=250,
                                     value=get_setting("water_bill_id", ""), hint_text="13 رقمی")
        electricity_bill_id = ft.TextField(label="شناسه قبض برق", width=250,
                                           value=get_setting("electricity_bill_id", ""), hint_text="13 رقمی")
        gas_bill_id = ft.TextField(label="شناسه قبض گاز", width=250,
                                   value=get_setting("gas_bill_id", ""), hint_text="13 رقمی")

        # ─── پیامک SMSGate ───
        smsgate_username = ft.TextField(
            label="نام کاربری SMSGate (ایمیل یا Username)", width=320,
            value=get_setting("smsgate_username", ""),
            hint_text="مثلاً: COCEGG",
        )
        smsgate_password = ft.TextField(
            label="رمز SMSGate", width=400,
            value=get_setting("smsgate_password", ""),
            password=True, can_reveal_password=True,
        )
        sms_test_phone = ft.TextField(
            label="شماره تست (موبایل خودت)", width=250,
            value=get_setting("sms_test_phone", ""), hint_text="09123456789",
        )
        sms_credit_text = ft.Text("", size=13, color=TEXT_SECONDARY)

        b_fields = [(bn, "نام ساختمان", True)]

        # ─── Startup ───
        def get_startup_enabled():
            try:
                return is_startup_enabled()
            except Exception:
                return False

        def toggle_startup(value):
            try:
                if value:
                    result = enable_startup()
                    msg("✅ اجرا با ویندوز فعال شد" if result else "❌ خطا",
                        S if result else D)
                else:
                    result = disable_startup()
                    msg("⛔ اجرا با ویندوز غیرفعال شد" if result else "❌ خطا",
                        W if result else D)
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        def get_tray_enabled():
            try:
                return get_setting("tray_enabled", "1") == "1"
            except Exception:
                return True

        def toggle_tray(value):
            try:
                if value:
                    tray_manager.start()
                    msg("✅ System Tray فعال شد", S)
                else:
                    tray_manager.stop()
                    msg("⛔ System Tray غیرفعال شد", W)
                set_setting("tray_enabled", "1" if value else "0")
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        # ═══════════ توابع ذخیره ═══════════

        def on_save_b(e):
            if not validate(b_fields):
                return
            try:
                update_building_info(bn.value, ba.value, bf.value, bu.value)
                msg("اطلاعات ساختمان ذخیره شد.")
            except Exception as ex:
                msg(str(ex), D)

        def on_save_bank(e):
            set_setting("bank_card", bc.value)
            set_setting("bank_account", bac.value)
            set_setting("bank_sheba", bsh.value)
            set_setting("bank_owner", bon.value)
            msg("اطلاعات بانکی ذخیره شد.")

        def on_save_balance(e):
            try:
                val = read_amount(init_bal.value)
                set_setting("initial_balance", str(int(val)))
                msg("موجودی اولیه ذخیره شد.")
            except (ValueError, TypeError):
                msg("مبلغ وارد شده صحیح نیست!", D)

        def on_save_currency(e):
            new_currency = CURRENCY_MAP.get(currency_selector.value, "toman")
            if new_currency == current_currency:
                msg("تغییری اعمال نشد", W)
                return
            set_setting("currency", new_currency)
            apply_appearance_change()
            msg(f"✅ واحد پول به {currency_selector.value} تغییر کرد.", S)

        def on_save_bill_ids(e):
            set_setting("water_bill_id", water_bill_id.value.strip())
            set_setting("electricity_bill_id", electricity_bill_id.value.strip())
            set_setting("gas_bill_id", gas_bill_id.value.strip())
            msg("شناسه قبض‌ها ذخیره شد.")

        def on_save_auto(e):
            try:
                issue_day = int(auto_issue_day.value or 1)
                due_day = int(auto_due_day.value or 15)
                if not (1 <= issue_day <= 28):
                    msg("روز صدور باید بین 1 تا 28 باشد", D)
                    return
                if not (1 <= due_day <= 28):
                    msg("روز سررسید باید بین 1 تا 28 باشد", D)
                    return
                if due_day <= issue_day:
                    msg("روز سررسید باید بعد از روز صدور باشد", D)
                    return
            except ValueError:
                msg("روزهای وارد شده نامعتبر است", D)
                return

            method_key = AUTO_METHOD_MAP.get(auto_method.value, "manual")

            set_setting("auto_charge_enabled", "1" if auto_enabled.value else "0")
            set_setting("auto_charge_method", method_key)
            set_setting("auto_charge_value", str(int(read_amount(auto_value.value))))
            set_setting("auto_charge_issue_day", str(issue_day))
            set_setting("auto_charge_due_day", str(due_day))
            set_setting("sms_on_issue", "1" if sms_on_issue.value else "0")
            set_setting("sms_reminder", "1" if sms_reminder.value else "0")
            set_setting("sms_overdue", "1" if sms_overdue.value else "0")
            set_setting("sms_thanks_on_payment",
                        "1" if sms_thanks_on_payment.value else "0")
            set_setting("late_fee_enabled", "1" if late_fee_enabled.value else "0")
            set_setting("late_fee_amount",
                        str(int(read_amount(late_fee_amount.value))))
            msg("تنظیمات صدور خودکار ذخیره شد.", S)

        # ═══════════ SMSGate ═══════════

        def on_save_sms(e):
            set_setting("smsgate_username", smsgate_username.value.strip())
            set_setting("smsgate_password", smsgate_password.value.strip())
            set_setting("sms_test_phone", sms_test_phone.value.strip())
            msg("اطلاعات SMSGate ذخیره شد.", S)

        def on_check_credit(e):
            result = get_sms_credit()
            if result and result.get("success"):
                sms_credit_text.value = f"✅ {result.get('message', 'متصل')}"
                sms_credit_text.color = S
            else:
                err = result.get("message", "خطا") if result else "خطا"
                sms_credit_text.value = f"❌ {err}"
                sms_credit_text.color = D
            page.update()

        def on_test_sms(e):
            test_phone = sms_test_phone.value.strip()
            if not test_phone.startswith("09"):
                msg("شماره موبایل معتبر وارد کنید (با 09 شروع بشه)", D)
                return

            set_setting("smsgate_username", smsgate_username.value.strip())
            set_setting("smsgate_password", smsgate_password.value.strip())
            set_setting("sms_test_phone", test_phone)

            simple_text = "🧪 این یک پیام تست از سیستم مدیریت ساختمان است."
            result = send_sms(test_phone, simple_text)

            if result.get("success"):
                msg(f"✅ {result.get('message', 'ارسال شد')}", S)
            else:
                msg(f"❌ {result.get('message', 'خطا')}", D)

        def open_smsgate_site(e):
            try:
                webbrowser.open("https://sms-gate.app")
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        # ═══════════ UI ═══════════
        return ft.Column([
            ft.Text("تنظیمات", size=28, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),

            # ─── اطلاعات ساختمان ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.APARTMENT, color=P, size=24),
                        ft.Text("اطلاعات ساختمان", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([bn, ba], wrap=True),
                    ft.Row([bf, bu], wrap=True),
                    ft.Button("💾 ذخیره", bgcolor=P, color="white", on_click=on_save_b),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── واحد پول ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PAID, color=W, size=24),
                        ft.Text("واحد پول برنامه", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([currency_selector]),
                    ft.Button("💾 ذخیره واحد پول", bgcolor=W, color="white",
                              on_click=on_save_currency),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── حالت نمایش ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PALETTE, color=theme["purple"], size=24),
                        ft.Text("حالت نمایش برنامه", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([theme_selector]),
                    ft.Button("💾 ذخیره حالت نمایش", bgcolor=theme["purple"],
                              color="white", on_click=on_save_theme),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── لوگو ساختمان ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.IMAGE, color=theme["purple"], size=24),
                        ft.Text("لوگو ساختمان", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([logo_color_dd, logo_text_color_dd], wrap=True, spacing=10),
                    ft.Row([
                        ft.Button("🎨 ساخت لوگو", bgcolor=theme["purple"],
                                  color="white", on_click=on_generate_logo,
                                  width=200, height=45),
                    ]),
                    ft.Text("💡 اسم ساختمان از بخش «اطلاعات ساختمان» گرفته می‌شود",
                            size=11, color=TEXT_MUTED, italic=True),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Text("👁️ پیش‌نمایش:", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row([logo_preview_container],
                           alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── اطلاعات بانکی ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CREDIT_CARD, color=P, size=24),
                        ft.Text("اطلاعات بانکی", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Text("این اطلاعات در پیام‌های یادآوری استفاده می‌شود.",
                            size=13, color=TEXT_SECONDARY),
                    ft.Row([bc, bon], wrap=True),
                    ft.Row([bac, bsh], wrap=True),
                    ft.Button("💾 ذخیره", bgcolor=P, color="white", on_click=on_save_bank),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── موجودی اولیه ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=S, size=24),
                        ft.Text("موجودی اولیه صندوق", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([init_bal]),
                    ft.Button("💾 ذخیره موجودی", bgcolor=S, color="white",
                              on_click=on_save_balance),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── صدور خودکار شارژ ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.AUTO_MODE, color=W, size=24),
                        ft.Text("صدور خودکار شارژ ماهانه", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Text("⚙️ تنظیمات صدور:", size=14,
                            weight=ft.FontWeight.BOLD, color=P),
                    auto_enabled,
                    ft.Row([auto_method, auto_value], wrap=True),
                    ft.Row([auto_issue_day, auto_due_day], wrap=True),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Text("📱 پیامک‌های خودکار:", size=14,
                            weight=ft.FontWeight.BOLD, color=P),
                    sms_on_issue,
                    sms_reminder,
                    sms_overdue,
                    sms_thanks_on_payment,
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Text("⚠️ جریمه دیرکرد:", size=14,
                            weight=ft.FontWeight.BOLD, color=D),
                    late_fee_enabled,
                    ft.Row([late_fee_amount]),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Button("💾 ذخیره همه تنظیمات", bgcolor=W, color="white",
                              on_click=on_save_auto, width=250),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── شناسه قبض‌ها ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.RECEIPT, color=W, size=24),
                        ft.Text("شناسه قبض‌های ساختمان", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([water_bill_id, electricity_bill_id], wrap=True),
                    ft.Row([gas_bill_id], wrap=True),
                    ft.Button("💾 ذخیره شناسه‌ها", bgcolor=W, color="white",
                              on_click=on_save_bill_ids),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── بکاپ‌گیری ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.BACKUP, color=P, size=24),
                        ft.Text("بکاپ‌گیری از اطلاعات", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Row([
                        ft.Button("💾 ساخت بکاپ دستی", bgcolor=P, color="white",
                                  on_click=on_manual_backup, width=200, height=45),
                        ft.Container(width=10),
                        backup_stats_text,
                    ]),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Text("📋 لیست بکاپ‌ها (10 مورد آخر):", size=14,
                            weight=ft.FontWeight.BOLD, color=P),
                    backup_list_col,
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── تنظیمات پیشرفته ویندوز ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=theme["purple"], size=24),
                        ft.Text("تنظیمات پیشرفته ویندوز", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Divider(height=1, color=DIVIDER),
                    ft.Row([
                        ft.Checkbox(label="🚀 اجرا با بالا آمدن ویندوز",
                                    value=get_startup_enabled(),
                                    on_change=lambda e: toggle_startup(e.control.value)),
                    ]),
                    ft.Row([
                        ft.Checkbox(label="🖥️ مینیمایز در تسک‌بار (System Tray)",
                                    value=get_tray_enabled(),
                                    on_change=lambda e: toggle_tray(e.control.value)),
                    ]),
                ], spacing=12)
            ),
            ft.Container(height=8),

            # ─── پیامک SMSGate ───
            ft.Container(
                bgcolor=BG_CARD, border_radius=14, padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SMS, color="#00A86B", size=24),
                        ft.Text("پیامک — SMSGate (خط شخصی)", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ]),
                    ft.Container(
                        bgcolor=theme["success_bg"], border_radius=8, padding=10,
                        content=ft.Column([
                            ft.Text("💡 راه‌اندازی:", size=12,
                                    weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                            ft.Text("۱. اپ SMSGate رو روی گوشی اندروید نصب کن",
                                    size=11, color=TEXT_SECONDARY),
                            ft.Text("۲. توی اپ، Cloud server رو روشن کن و Username/Password بگیر",
                                    size=11, color=TEXT_SECONDARY),
                            ft.Text("۳. همون Username و Password رو اینجا وارد کن",
                                    size=11, color=TEXT_SECONDARY),
                            ft.Text("۴. گوشی باید همیشه روشن و به اینترنت وصل باشه",
                                    size=11, color=D, weight=ft.FontWeight.BOLD),
                            ft.Text("۵. وضعیت سرویس توی تب HOME اپ باید Online باشه",
                                    size=11, color=D, weight=ft.FontWeight.BOLD),
                        ], spacing=3)
                    ),
                    ft.Row([smsgate_username], wrap=True),
                    ft.Row([smsgate_password]),
                    ft.Row([sms_test_phone]),
                    sms_credit_text,
                    ft.Row([
                        ft.Button("💾 ذخیره تنظیمات", bgcolor="#00A86B",
                                  color="white", on_click=on_save_sms),
                        ft.Button("🔍 بررسی وضعیت", bgcolor=P, color="white",
                                  on_click=on_check_credit),
                        ft.Button("🧪 تست ارسال", bgcolor=W, color="white",
                                  on_click=on_test_sms),
                        ft.TextButton("🌐 سایت SMSGate", on_click=open_smsgate_site),
                    ], wrap=True),
                ], spacing=12)
            ),
        ], scroll=ft.ScrollMode.AUTO, expand=True)


    # ----------------------------------------------------------------------

    def menu_btn(text, icon, handler):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=P),
                ft.Text(text, size=14)
            ], spacing=8),
            padding=12, border_radius=10,
            on_click=handler, ink=True,
        )

    def nav(builder, e=None):
        """جابجایی بین صفحات با لودینگ Pulse"""

        current_page_builder["builder"] = builder

        # ⭐ کنسل کردن task قبلی
        prev_task = current_nav_task.get("task")
        if prev_task is not None:
            try:
                if not prev_task.done():
                    prev_task.cancel()
            except Exception:
                pass

        # ─── گرفتن رنگ‌های تم ─────
        theme = get_theme_colors()
        BG_MAIN = theme["bg_main"]
        P = theme["primary"]

        # ─── ساخت لوگو ─────
        logo_path = get_logo_or_default()

        if logo_path and os.path.exists(logo_path):
            # نکته: قبلاً اینجا مستقیم src=logo_path (مسیر فایل) داده
            # می‌شد. چون اسم فایل همیشه ثابته، فلاتر تصویر رو از کش
            # داخلی خودش (بر اساس همون مسیر) می‌گرفت، نه از دیسک —
            # برای همین بعد از ساخت لوگوی جدید، همین‌جا (لودینگ
            # جابه‌جایی سایدبار) تا ری‌استارت کامل برنامه لوگوی قدیمی
            # رو نشون می‌داد. با خوندن مستقیم بایت‌های فایل و دادنش
            # به‌صورت base64 (که هر بار محتوای واقعی و به‌روزه)، این
            # مشکل کش رفع می‌شه.
            b64 = _read_image_base64(logo_path)
        else:
            b64 = None

        if b64:
            logo_widget = ft.Image(
                src=b64,
                width=100,
                height=100,
                fit=ft.BoxFit.CONTAIN,
                error_content=ft.Icon(
                    ft.Icons.APARTMENT, size=70, color=P
                ),
            )
        else:
            logo_widget = ft.Icon(
                ft.Icons.APARTMENT,
                size=70,
                color=P,
            )

        logo_animated = ft.Container(
            content=logo_widget,
            animate_scale=ft.Animation(
                700,
                ft.AnimationCurve.EASE_IN_OUT,
            ),
            scale=1.0,
            border_radius=10,  # ← اضافه شد (نصف عرض لوگو)
            clip_behavior=ft.ClipBehavior.HARD_EDGE,  # ← اضافه شد
        )

        loading_content = ft.Container(
            expand=True,
            bgcolor=BG_MAIN,  # ← تغییر: استفاده از رنگ تم
            content=ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    logo_animated,
                    ft.Container(expand=True),
                ]),
                ft.Container(height=20),
                ft.Container(
                    width=500,
                    padding=ft.Padding(left=40, right=40, top=0, bottom=0),
                    content=ft.Text(
                        get_random_tip(),
                        size=13,
                        color=theme["text_secondary"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
                ft.Container(expand=True),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        )

        content_area.content = loading_content
        page.update()

        async def animate_and_load():
            try:
                await asyncio.sleep(0.1)

                # پالس ۱
                logo_animated.scale = 1.3
                page.update()
                await asyncio.sleep(0.75)

                logo_animated.scale = 0.8
                page.update()
                await asyncio.sleep(0.75)

                # پالس ۲
                logo_animated.scale = 1.3
                page.update()
                await asyncio.sleep(0.75)

                logo_animated.scale = 1.0
                page.update()
                await asyncio.sleep(0.75)

                # ⭐ ۲ ثانیه‌ی اضافه (طبق درخواست) قبل از رفتن به صفحه‌ی بعد
                await asyncio.sleep(2)

                # بارگذاری صفحه
                new_content = builder()
                content_area.content = new_content
                page.update()

            except asyncio.CancelledError:
                # task کنسل شده - عادی هست
                pass
            except Exception as ex:
                print(f"❌ خطای انیمیشن: {ex}")
                try:
                    content_area.content = builder()
                    page.update()
                except Exception:
                    pass

        # ⭐ ذخیره task جدید
        current_nav_task["task"] = page.run_task(
            animate_and_load
        )

    # ─── لوگو در سایدبار (Base64 - همیشه کار می‌کند) ─────
    sidebar_logo = ft.Container(
        content=build_logo_image(width=180, height=180),
        width=180,
        height=180,
        alignment=ft.Alignment.CENTER,
        border_radius=10,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )
    # ═══════════ System Tray ═══════════
    tray_manager = SystemTrayManager(page)

    # ─── فعال‌سازی خودکار Tray بر اساس تنظیمات ───
    try:
        tray_enabled = get_setting("tray_enabled", "1") == "1"
        if tray_enabled:
            icon_path = get_setting("current_icon_path", "")
            if not icon_path or not os.path.exists(icon_path):
                # اگر آیکون ذخیره‌شده نبود، از لوگو استفاده کن
                logo_path = get_logo_or_default()
                if logo_path:
                    icon_path = logo_path
            tray_manager.start(icon_path if icon_path else None)
    except Exception as ex:
        print(f"⚠️ خطا در راه‌اندازی Tray: {ex}")

    # ─── مدیریت رویداد بستن پنجره ───
    # ─── دیالوگ «مینیمایز به Tray یا خروج کامل؟» ───
    close_remember_check = ft.Checkbox(
        label="دیگر پرسیده نشود",
        value=False,
    )

    def _do_minimize_to_tray(remember):
        close_confirm_dlg.open = False
        page.update()
        if remember:
            set_setting("close_action", "tray")
        tray_manager.minimize_to_tray()

    def _do_exit_completely(remember):
        close_confirm_dlg.open = False
        page.update()
        if remember:
            set_setting("close_action", "exit")

        async def _really_close():
            # نکته: خودِ window.destroy() باعث بسته شدن ارتباط
            # کلاینت-سرور می‌شه، پس گاهی قبل از برگشتنِ تأییدیه،
            # ارتباط قطع می‌شه و یه RuntimeError("Session closed")
            # بی‌ضرر پرتاب می‌شه (با اینکه بستن واقعاً موفق بوده و
            # برنامه درست می‌بنده). همینه که تو لاگ زشت به‌نظر
            # می‌رسید؛ اینجا خاموشش می‌کنیم.
            try:
                await page.window.destroy()
            except Exception:
                pass

        page.run_task(_really_close)

    def on_minimize_click(e):
        _do_minimize_to_tray(close_remember_check.value)

    def on_exit_click(e):
        _do_exit_completely(close_remember_check.value)

    def on_cancel_close(e):
        close_confirm_dlg.open = False
        page.update()

    close_confirm_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("بستن برنامه"),
        content=ft.Column(
            [
                ft.Text(
                    "می‌خواهید برنامه به‌صورت آیکون کنار ساعت "
                    "(Tray) مینیمایز شود یا کاملاً بسته شود؟"
                ),
                close_remember_check,
            ],
            tight=True,
            spacing=12,
        ),
        actions=[
            ft.TextButton(
                "پنهان کردن (Tray)",
                on_click=on_minimize_click,
            ),
            ft.TextButton(
                "خروج کامل",
                on_click=on_exit_click,
            ),
            ft.TextButton(
                "انصراف",
                on_click=on_cancel_close,
            ),
        ],
    )

    def open_close_confirm_dialog():
        close_remember_check.value = False
        if close_confirm_dlg not in page.overlay:
            page.overlay.append(close_confirm_dlg)
        close_confirm_dlg.open = True
        page.update()

    async def handle_window_event(e):
        """
        مدیریت رویدادهای پنجره - وقتی کاربر ضربدر رو بزنه

        نکته: توی نسخه‌ی جدید flet، به‌جای e.data == "close" باید از
        e.type == ft.WindowEventType.CLOSE استفاده بشه (مستندات فعلی
        flet). چون e.data دیگه هیچ‌وقت "close" نمی‌شد، این تابع عملاً
        هیچ‌وقت اجرا نمی‌شد و درنتیجه پنجره با دکمه‌ی ضربدر اصلاً بسته
        نمی‌شد (چون page.window.prevent_close = True جلوی بسته شدن
        خودکار رو گرفته بود و هیچ‌کس دستور بسته‌شدن واقعی رو نمی‌داد).
        همچنین window.destroy() توی این نسخه async شده، پس باید
        await بشه.

        رفتار جدید: به‌جای تصمیم خودکار (مینیمایز به تری اگه فعال
        بود، وگرنه بسته شدن)، هر بار از کاربر می‌پرسیم — مگر این‌که
        قبلاً با گزینه‌ی «دیگر پرسیده نشود» یه انتخاب ثابت ذخیره کرده
        باشه.
        """
        try:
            if e.type == ft.WindowEventType.CLOSE:
                remembered = get_setting("close_action", "")
                if remembered == "tray" and tray_manager.running:
                    tray_manager.minimize_to_tray()
                elif remembered == "exit":
                    await page.window.destroy()
                elif tray_manager.running:
                    # Tray فعاله، پس دو گزینه‌ی واقعی داریم؛ بپرس
                    open_close_confirm_dialog()
                else:
                    # Tray فعال نیست، مینیمایز کردن معنی نداره
                    await page.window.destroy()
        except Exception as ex:
            print(f"⚠️ خطای window event: {ex}")

    page.window.prevent_close = True  # ⭐ مهم: جلوی بسته شدن خودکار رو بگیر
    page.window.on_event = handle_window_event

    # ═══════════════════════════════════════
    # ═══ سیستم نوتیفیکیشن (قدم 6) ═══
    # ═══════════════════════════════════════
    def show_notifications_panel(e):
        """نمایش پنل نوتیفیکیشن"""
        # قبل از باز شدن پنل، یک بار چک کن
        try:
            check_and_create_note_notifications()
        except Exception:
            pass

        notif_list_col = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        def refresh_panel():
            notifs_new = list_notifications(limit=50)
            print(f"📋 تعداد اعلانات در پنل: {len(notifs_new)}")  # دیباگ
            notif_list_col.controls.clear()

            if not notifs_new:
                notif_list_col.controls.append(
                    ft.Container(
                        padding=30,
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.NOTIFICATIONS_OFF,
                                size=50, color=TEXT_MUTED,
                            ),
                            ft.Text(
                                "اعلانی موجود نیست",
                                color=TEXT_MUTED,
                                size=13
                            ),
                        ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8)
                    )
                )
                try:
                    notif_list_col.update()
                    page.update()
                except Exception:
                    pass
                return

            for n in notifs_new:
                type_colors = {
                    "charge_due": (W, "#FFF3E0"),
                    "debt": (D, "#FFEBEE"),
                    "payment": (S, "#E8F5E9"),
                    "charge_new": (P, "#E3F2FD"),
                    "bill_new": ("#9C27B0", "#F3E5F5"),
                    "custom": (P, "#E3F2FD"),
                }
                type_color, type_bg = type_colors.get(
                    n["type"], (P, "#E3F2FD")
                )

                type_icons = {
                    "charge_due": "⏰",
                    "debt": "⚠️",
                    "payment": "💰",
                    "charge_new": "📋",
                    "bill_new": "🔔",
                    "custom": "📢",
                }
                icon_text = type_icons.get(n["type"], "📢")

                # تاریخ نسبی
                from datetime import datetime
                if n["created_at"]:
                    delta = datetime.now() - n["created_at"]
                    if delta.days > 0:
                        time_ago = f"{delta.days} روز پیش"
                    elif delta.seconds > 3600:
                        h = delta.seconds // 3600
                        time_ago = f"{h} ساعت پیش"
                    elif delta.seconds > 60:
                        m = delta.seconds // 60
                        time_ago = f"{m} دقیقه پیش"
                    else:
                        time_ago = "لحظاتی پیش"
                    time_ago = to_persian(time_ago)
                else:
                    time_ago = ""

                def make_read(nid):
                    def do_read(e):
                        try:
                            mark_notification_read(nid)
                            refresh_panel()
                            update_notif_badge()
                        except Exception as ex:
                            print(f"❌ {ex}")

                    return do_read

                def make_delete(nid):
                    def do_del(e):
                        try:
                            delete_notification(nid)
                            refresh_panel()
                            update_notif_badge()
                        except Exception as ex:
                            print(f"❌ {ex}")

                    return do_del

                is_unread = n["is_read"] == 0

                # ⭐ تنظیم رنگ پس‌زمینه بر اساس حالت تاریک/روشن
                if is_dark_mode():
                    card_bg = type_bg if is_unread else "#2D2D2D"
                else:
                    card_bg = type_bg if is_unread else "#FAFAFA"

                notif_list_col.controls.append(
                    ft.Container(
                        bgcolor=card_bg,
                        border_radius=10,
                        padding=12,
                        content=ft.Row([
                            ft.Text(icon_text, size=24),
                            ft.Column([
                                ft.Row([
                                    ft.Text(
                                        n["title"],
                                        size=13,
                                        weight=ft.FontWeight.BOLD if is_unread else ft.FontWeight.NORMAL,
                                        color=type_color,
                                    ),
                                    ft.Container(expand=True),
                                    ft.Text(
                                        time_ago,
                                        size=9,
                                        color=TEXT_MUTED,
                                    ),
                                ]),
                                ft.Text(
                                    n["message"],
                                    size=11,
                                    color=TEXT_SECONDARY,
                                ) if n["message"] else ft.Container(),
                            ], spacing=4, expand=True),
                            ft.Column([
                                ft.IconButton(
                                    icon=ft.Icons.MARK_EMAIL_READ if is_unread else ft.Icons.CHECK_CIRCLE,
                                    icon_color=S if is_unread else TEXT_MUTED,
                                    icon_size=18,
                                    tooltip="خوانده شد" if is_unread else "خوانده شده",
                                    on_click=make_read(n["id"]),
                                    disabled=not is_unread,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=D,
                                    icon_size=18,
                                    tooltip="حذف",
                                    on_click=make_delete(n["id"]),
                                ),
                            ], spacing=0),
                        ], spacing=10),
                    )
                )

            try:
                notif_list_col.update()
                page.update()  # ⭐ اضافه شد
            except Exception as ex:
                print(f"⚠️ خطای آپدیت پنل: {ex}")

        refresh_panel()

        def close_dlg(e):
            notif_dlg.open = False
            page.update()

        def mark_all_read(e):
            try:
                mark_all_notifications_read()
                refresh_panel()
                update_notif_badge()
                msg("✅ همه علامت‌گذاری شد.", S)
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        def clear_all(e):
            try:
                delete_all_notifications()
                refresh_panel()
                update_notif_badge()
                msg("🗑️ همه اعلان‌ها حذف شد.", W)
            except Exception as ex:
                msg(f"خطا: {ex}", D)

        notif_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS, color=P, size=28),
                ft.Text("اعلانات", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.TextButton("✅ همه رو خواندم", on_click=mark_all_read),
                ft.TextButton("🗑️ حذف همه", on_click=clear_all),
            ]),
            content=ft.Container(
                width=550,
                height=500,
                content=notif_list_col,
            ),
            actions=[
                ft.TextButton("بستن", on_click=close_dlg),
            ],
        )
        if notif_dlg not in page.overlay:
            page.overlay.append(notif_dlg)
        notif_dlg.open = True
        page.update()

    # ─── Badge برای تعداد نوتیفیکیشن ─────
    notif_badge_text = ft.Text(
        "",
        size=10,
        color="white",
        weight=ft.FontWeight.BOLD,
    )

    notif_badge_container = ft.Container(
        content=notif_badge_text,
        bgcolor=D,
        border_radius=10,
        padding=ft.Padding(4, 1, 4, 1),
        visible=False,
    )

    def update_notif_badge():
        """بروزرسانی تعداد نوتیفیکیشن روی آیکون زنگوله"""
        try:
            # چک کردن یادآوری‌های یادداشت
            try:
                check_and_create_note_notifications()
            except Exception as ex:
                print(f"⚠️ خطای ساخت خودکار اعلان یادداشت: {ex}")

            # دریافت تعداد اعلانات خوانده نشده
            count = count_unread_notifications()
            print(f"🔔 تعداد اعلانات خوانده نشده: {count}")  # برای دیباگ

            # بروزرسانی مقدار و visibility
            if count > 0:
                notif_badge_text.value = to_persian(
                    str(count) if count < 100 else "99+"
                )
                notif_badge_container.visible = True
            else:
                notif_badge_container.visible = False

            # به‌روزرسانی اجباری ویجت‌ها و صفحه
            # نکته: بار اول که این تابع صدا زده می‌شه (قبل از ساخت و
            # اضافه‌شدنِ کل چیدمان اصلی به صفحه)، این کنترل‌ها هنوز
            # mount نشدن. توی این نسخه‌ی flet، حتی خوندنِ property مثل
            # ".page" روی کنترل mount‌نشده هم می‌تونه همون خطای
            # "Control must be added to the page first" رو بندازه، نه
            # فقط ".update()". برای همین هرکدوم رو جدا try/except
            # می‌کنیم تا این خطای کاملاً بی‌ضرر (چون مقدار درست همراه
            # رندر اصلی صفحه اعمال می‌شه) دیگه چاپ نشه.
            try:
                notif_badge_container.update()
            except Exception:
                pass
            try:
                notif_badge_text.update()
            except Exception:
                pass
            try:
                if page.controls:
                    page.update()  # ⭐ مهم: صفحه را به‌روز کن
            except Exception:
                pass

        except Exception as ex:
            print(f"❌ خطای badge: {ex}")

    # دکمه زنگوله در سایدبار
    notif_button = ft.Container(
        content=ft.Stack([
            ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS,
                icon_color=P,
                icon_size=26,
                tooltip="اعلانات",
                on_click=show_notifications_panel,
            ),
            ft.Container(
                content=notif_badge_container,
                top=4,
                right=4,
            ),
        ]),
        width=50,
        height=50,
    )

    # بروزرسانی اولیه
    update_notif_badge()
    # ─── سایدبار ───
    # نکته: قبلاً این Column هیچ scroll نداشت؛ روی صفحه‌های کوچیک
    # (رزولوشن پایین یا پنجره‌ی کوچیک‌شده) که ارتفاع همه‌ی آیتم‌های
    # سایدبار از ارتفاع واقعی پنجره بیشتر می‌شد، آیتم‌های پایینی
    # (مثل «تنظیمات» و «خروج از حساب») از دید خارج می‌شدن و هیچ
    # اسکرولی هم برای دیدنشون نبود. با scroll=ft.ScrollMode.AUTO این
    # مشکل رفع می‌شه (اسکرول‌بار فقط وقتی لازم باشه ظاهر می‌شه).
    side = ft.Container(
        width=220,
        bgcolor=BG_SIDEBAR,
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    content=sidebar_logo,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Row([
                    ft.Container(expand=True),
                    notif_button,
                    ft.Container(expand=True),
                ]),
                ft.Container(height=5),
                ft.Container(
                    height=1,
                    bgcolor="#CCCCCC",  # ← رنگ ثابت
                ),
                ft.Container(height=5),
                menu_btn("داشبورد", ft.Icons.DASHBOARD,
                         lambda e: nav(build_dashboard)),
                menu_btn("واحدها", ft.Icons.APARTMENT,
                         lambda e: nav(build_units_page)),
                menu_btn("شارژ و پرداخت", ft.Icons.PAYMENT,
                         lambda e: nav(build_charges_page)),
                menu_btn("هزینه‌ها", ft.Icons.RECEIPT_LONG,
                         lambda e: nav(build_expenses_page)),
                menu_btn("قبوض", ft.Icons.ELECTRIC_BOLT,
                         lambda e: nav(build_bills_page)),
                menu_btn("گزارش مالی", ft.Icons.BAR_CHART,
                         lambda e: nav(build_reports_page)),
                menu_btn("پیامک", ft.Icons.SMS,
                         lambda e: nav(build_sms_page)),
                menu_btn("یادداشت‌ها", ft.Icons.STICKY_NOTE_2,
                         lambda e: nav(build_notes_page)),
                menu_btn("تنظیمات", ft.Icons.SETTINGS,
                         lambda e: nav(build_settings_page)),

                # ─── بخش جدید: خروج و نام کاربر ───
                ft.Container(height=10),
                ft.Container(
                    height=1,
                    bgcolor="#CCCCCC",  # ← رنگ ثابت
                ),
                ft.Container(height=5),

                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT, size=20, color=D),
                        ft.Text("خروج از حساب", size=14, color=D)
                    ], spacing=8),
                    padding=12,
                    border_radius=10,
                    on_click=logout_click,
                    ink=True,
                ),

                ft.Container(height=5),
                ft.Container(
                    height=1,
                    bgcolor="#CCCCCC",  # ← رنگ ثابت
                ),
                ft.Container(height=5),

                ft.Container(
                    content=ft.Text(
                        f"👤 {current_user['full_name'] or current_user['username'] or 'کاربر'}",
                        size=12,
                        color=TEXT_SECONDARY,
                    ),
                    alignment=ft.Alignment.CENTER,
                ),
            ], spacing=4)
    )

    # ══════════════════════════════════════════════
    # 🔔 سیستم پخش صدا و چک کردن زنده (Real-time) 🔔
    # ══════════════════════════════════════════════

    async def background_notification_checker():
        """
        چک‌کننده زنده اعلانات در پس‌زمینه (هر ۲۰ ثانیه)
        با پخش صدا، نوتیفیکیشن ویندوز، SnackBar و آپدیت زنگوله
        """
        from datetime import datetime
        _last_cleanup = datetime.now()

        while True:
            # هر ۲۰ ثانیه یک‌بار دیتابیس رو بدون بلاک کردن UI بررسی کن
            await asyncio.sleep(20)

            try:
                # ─── ۱. چک کردن شارژها و بدهی‌های خودکار ───
                try:
                    auto_res = check_and_create_auto_notifications()
                    auto_count = auto_res.get("count", 0) if auto_res else 0
                    auto_items = auto_res.get("items", []) if auto_res else []
                except Exception as ex:
                    print(f"⚠️ خطای چک شارژ/بدهی: {ex}")
                    auto_count = 0
                    auto_items = []

                # ─── ۲. چک کردن یادداشت‌ها و یادآوری‌ها ───
                try:
                    note_res = check_and_create_note_notifications()
                    note_count = (
                        note_res.get("count", 0) if note_res else 0
                    )
                    note_items = (
                        note_res.get("items", []) if note_res else []
                    )
                except Exception as ex:
                    print(f"⚠️ خطای چک یادداشت: {ex}")
                    note_count = 0
                    note_items = []

                total_new = auto_count + note_count
                # نکته: یادآوری یادداشت‌ها معمولاً برای کاربر مهم‌تر و
                # شخصی‌تره، برای همین اول اونا رو تو نوتیفیکیشن نشون
                # می‌دیم؛ بقیه (شارژ/بدهی خودکار) بعدش میان.
                all_items = note_items + auto_items

                # ─── ۳. اگر اعلان جدیدی در این لحظه ساخته شد ───
                if total_new > 0:
                    # ۳-۱. پخش صدای سیستم ویندوز (بدون کرش)
                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    except Exception:
                        pass

                    # ۳-۲. پیدا کردن آیکون برنامه برای ویندوز
                    ico_path = get_setting("current_icon_path", "")
                    if not ico_path or not os.path.exists(ico_path):
                        ico_path = get_logo_path()

                    # ۳-۳. نمایش نوتیفیکیشن گوشه ویندوز (Toast)
                    # نکته: قبلاً همیشه یه پیام ثابت («برای مشاهده روی
                    # زنگوله کلیک کنید») نشون داده می‌شد، مهم نبود
                    # یادآوری چی بوده. الان اگه فقط یه اعلان جدید باشه،
                    # مستقیم عنوان و متن واقعیِ همون یادآوری/شارژ رو
                    # نشون می‌دیم؛ اگه چندتا باشه، عنوان‌هاشون رو زیر
                    # هم لیست می‌کنیم (حداکثر ۳ تا، بقیه به‌صورت خلاصه).
                    if len(all_items) == 1:
                        toast_title = all_items[0]["title"]
                        toast_message = all_items[0]["message"]
                    elif len(all_items) > 1:
                        toast_title = (
                            f"{to_persian(str(total_new))} اعلان جدید"
                        )
                        shown = all_items[:3]
                        lines = [it["title"] for it in shown]
                        remaining = len(all_items) - len(shown)
                        if remaining > 0:
                            lines.append(
                                f"و {to_persian(str(remaining))} مورد دیگر..."
                            )
                        toast_message = "\n".join(lines)
                    else:
                        # حالتی که total_new از یه منبع دیگه (بدون items)
                        # اومده باشه؛ fallback به پیام قدیمی
                        toast_title = (
                            f"{to_persian(str(total_new))} اعلان جدید"
                        )
                        toast_message = (
                            "برای مشاهده، روی زنگوله اعلانات کلیک کنید"
                        )

                    try:
                        show_windows_notification(
                            title=toast_title,
                            message=toast_message,
                            duration=5,
                            icon_path=ico_path if (ico_path and os.path.exists(ico_path)) else None,
                        )
                    except Exception as ex:
                        print(f"⚠️ خطای نوتیفیکیشن ویندوز: {ex}")

                    # ۳-۴. به‌روزرسانی زنگوله در سایدبار (تعداد قرمز رنگ)
                    update_notif_badge()

                    # ۳-۵. نمایش پیام SnackBar درون برنامه
                    try:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Row([
                                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="white"),
                                ft.Text(
                                    f"🔔 {to_persian(str(total_new))} اعلان جدید دریافت شد!",
                                    color="white",
                                    weight=ft.FontWeight.BOLD
                                )
                            ]),
                            bgcolor=W,
                            duration=4000
                        )
                        page.snack_bar.open = True
                        page.update()
                    except Exception as ex:
                        print(f"⚠️ خطای SnackBar: {ex}")

            except Exception as ex:
                print(f"⚠️ خطای سیستم زنده اعلانات: {ex}")

            # ─── ۴. پاکسازی خودکار اعلانات قدیمی خوانده‌شده (هر ۲۴ ساعت) ───
            try:
                now = datetime.now()
                if (now - _last_cleanup).days >= 1:
                    cleanup_old_notifications(days=30)
                    _last_cleanup = now
                    print("🗑️ پاکسازی خودکار اعلانات قدیمی انجام شد.")
            except Exception:
                pass

    # ─── اجرای task پس‌زمینه ───
    page.run_task(background_notification_checker)

    # ═══════════ ساخت صفحه اصلی (سایدبار + محتوا) ═══════════
    content_area.content = build_dashboard()
    current_page_builder["builder"] = build_dashboard
    main_layout = ft.Row([
        side,
        ft.VerticalDivider(width=1),
        content_area
    ], expand=True)

    # ─── گرفتن رنگ‌های تم ─────
    theme = get_theme_colors()
    P = theme["primary"]
    BG_MAIN = theme["bg_main"]
    TEXT_SECONDARY = theme["text_secondary"]
    TEXT_MUTED = theme["text_muted"]

    # ═══════════ صفحه لودینگ اولیه (Welcome) ═══════════
    welcome_logo = build_logo_image(width=200, height=200)

    logo_animated = ft.Container(
        content=welcome_logo,
        animate_scale=ft.Animation(
            600,
            ft.AnimationCurve.EASE_IN_OUT,
        ),
        scale=1.0,
        border_radius=10,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    welcome_text = ft.Text(
        "خوش آمدید",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=P,
    )

    welcome_text_container = ft.Container(
        content=welcome_text,
        animate_opacity=ft.Animation(
            500,
            ft.AnimationCurve.EASE_IN,
        ),
        opacity=0.0,
    )

    welcome_view = ft.Container(
        expand=True,
        bgcolor=BG_MAIN,
        content=ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                logo_animated,
                ft.Container(expand=True),
            ]),
            ft.Container(height=30),
            ft.Row([
                ft.Container(expand=True),
                welcome_text_container,
                ft.Container(expand=True),
            ]),
            ft.Container(expand=True),
            ft.Row([
                ft.Container(expand=True),
                ft.Text(
                    "© سیستم مدیریت ساختمان",
                    size=11,
                    color=TEXT_MUTED,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=20),
        ], spacing=0),
    )

    page.controls.clear()
    page.add(welcome_view)
    page.update()

    # ═══════════ انیمیشن Pulse + نمایش متن ═══════════
    async def welcome_animation():
        for i in range(4):
            logo_animated.scale = 1.15
            logo_animated.update()
            await asyncio.sleep(0.5)

            logo_animated.scale = 1.0 if i > 0 else 0.95
            logo_animated.update()
            await asyncio.sleep(0.5)

            if i == 0:
                welcome_text_container.opacity = 1.0
                welcome_text_container.update()

        # ⭐ ۲ ثانیه‌ی اضافه (طبق درخواست) به این لودینگ هم اضافه شد
        await asyncio.sleep(2)

    await welcome_animation()

    # ─── ⭐ نمایش صفحه ورود یا ثبت‌نام ───
    page.controls.clear()
    if has_any_user():
        page.add(build_login_screen(page, on_login_success))
    else:
        page.add(build_register_screen(page, on_login_success))
    page.update()


if __name__ == "__main__":
    ft.run(main)