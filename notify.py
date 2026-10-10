# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

"""
سیستم نوتیفیکیشن ویندوز (Toast Notifications)
"""

import os
import time

try:
    from win10toast import ToastNotifier
    HAS_WIN10TOAST = True
except ImportError:
    HAS_WIN10TOAST = False

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


def get_icon_path():
    """گرفتن مسیر آیکون معتبر برای نوتیفیکیشن"""
    ico_path = os.path.join(os.getcwd(), "app_icon.ico")
    if os.path.exists(ico_path):
        return ico_path

    ico_path = os.path.join(os.getcwd(), "assets", "app_icon.ico")
    if os.path.exists(ico_path):
        return ico_path

    return None


def show_windows_notification(title, message, duration=5, icon_path=None):
    """
    نمایش نوتیفیکیشن در ویندوز
    """
    if icon_path is None:
        icon_path = get_icon_path()

    if icon_path and not os.path.exists(icon_path):
        icon_path = None

    # روش اول: win10toast
    if HAS_WIN10TOAST:
        try:
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                duration=duration,
                icon_path=icon_path,
                threaded=True,
            )
            print(f"🔔 نوتیفیکیشن ارسال شد (win10toast): {title}")
            return True
        except Exception as ex:
            print(f"⚠️ خطای win10toast: {ex}")

    # روش دوم: plyer
    if HAS_PLYER:
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=duration,
                app_icon=icon_path,
                app_name="مدیریت ساختمان"
            )
            print(f"🔔 نوتیفیکیشن ارسال شد (plyer): {title}")
            return True
        except Exception as ex:
            print(f"⚠️ خطای plyer: {ex}")

    # روش سوم: ctypes
    # نکته: نسخه‌ی قبلی این بخش از ctypes.GUID استفاده می‌کرد که
    # اصلاً در ماژول استاندارد ctypes وجود نداره (AttributeError)،
    # پس این روش همیشه با خطا مواجه می‌شد و بی‌صدا رد می‌شد. به‌جای
    # تعریف GUID با c_byte * 16 جایگزینش می‌کنیم که واقعاً کار می‌کنه.
    try:
        import ctypes
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [("data", ctypes.c_byte * 16)]

        class NOTIFYICONDATA(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("hWnd", wintypes.HWND),
                ("uID", wintypes.UINT),
                ("uFlags", wintypes.UINT),
                ("uCallbackMessage", wintypes.UINT),
                ("hIcon", wintypes.HANDLE),
                ("szTip", wintypes.WCHAR * 128),
                ("dwState", wintypes.DWORD),
                ("dwStateMask", wintypes.DWORD),
                ("szInfo", wintypes.WCHAR * 256),
                ("uTimeout", wintypes.UINT),
                ("szInfoTitle", wintypes.WCHAR * 64),
                ("dwInfoFlags", wintypes.DWORD),
                ("guidItem", GUID),
                ("hBalloonIcon", wintypes.HANDLE),
            ]

        NIF_INFO = 0x00000010
        NIIF_INFO = 0x00000001

        nid = NOTIFYICONDATA()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
        nid.uFlags = NIF_INFO
        nid.szInfo = message[:256]
        nid.szInfoTitle = title[:64]
        nid.dwInfoFlags = NIIF_INFO
        nid.uTimeout = duration * 1000

        ctypes.windll.user32.Shell_NotifyIconW(0x00000001, ctypes.byref(nid))
        print(f"🔔 نوتیفیکیشن ارسال شد (ctypes): {title}")
        return True

    except Exception as ex:
        print(f"⚠️ خطای ctypes: {ex}")

    # روش نهایی: صدا
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        print(f"🔔 {title}: {message}")
        return True
    except Exception:
        return False


def send_bulk_notifications(notifications, delay=2):
    """
    ارسال چند نوتیفیکیشن با فاصله

    Args:
        notifications: لیست (title, message)
        delay: فاصله بین هر کدام (ثانیه)
    """
    for title, msg in notifications:
        show_windows_notification(title, msg)
        time.sleep(delay)