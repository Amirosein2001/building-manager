"""
سرویس ارسال پیامک - ملی‌پیامک (REST API)
مستندات رسمی: https://www.melipayamak.com/api/
"""

import requests

BASE_URL = "https://rest.payamak-panel.com/api/SendSMS/%s"

TIMEOUT = 10  # ثانیه


def _post(action, data):
    """ارسال درخواست POST به ملی‌پیامک و برگرداندن نتیجه خام"""
    url = BASE_URL % action
    try:
        r = requests.post(url, data=data, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.Timeout:
        return None, "پاسخی از سرور ملی‌پیامک دریافت نشد (Timeout)."
    except requests.exceptions.ConnectionError:
        return None, "اتصال به سرور ملی‌پیامک برقرار نشد. اینترنت را بررسی کنید."
    except requests.exceptions.RequestException as ex:
        return None, f"خطا در ارتباط با ملی‌پیامک: {ex}"
    except ValueError:
        # پاسخ JSON نبود
        return None, "پاسخ نامعتبر از سرور ملی‌پیامک دریافت شد."


def _is_success_recid(rec_id):
    """
    طبق مستندات ملی‌پیامک: RecId موفق همیشه یک عدد طولانی
    (بیشتر از ۱۰ رقم) است. مقادیر کوچک (منفی یا تک/دو رقمی)
    یعنی کد خطا هستند.
    """
    try:
        rec_str = str(rec_id).strip()
        return rec_str.lstrip("-").isdigit() and len(rec_str) > 10
    except Exception:
        return False


def send_sms_melipayamak(to, text, username, password, from_number):
    """
    ارسال پیامک با استفاده از وب‌سرویس ملی‌پیامک

    Args:
        to: شماره گیرنده (مثال: 09121234567)
        text: متن پیامک
        username: نام کاربری پنل ملی‌پیامک
        password: کلمه عبور یا ApiKey پنل
        from_number: شماره خط ارسال‌کننده

    Returns:
        dict: {"success": bool, "message": str, "recid": str|None}
    """
    to = str(to or "").strip()
    text = str(text or "").strip()
    username = str(username or "").strip()
    password = str(password or "").strip()
    from_number = str(from_number or "").strip()

    if not to:
        return {
            "success": False,
            "message": "شماره گیرنده وارد نشده.",
            "recid": None,
        }
    if not text:
        return {
            "success": False,
            "message": "متن پیامک خالی است.",
            "recid": None,
        }
    if not all([username, password, from_number]):
        return {
            "success": False,
            "message": "نام کاربری، رمز عبور یا شماره خط تنظیم نشده.",
            "recid": None,
        }

    data = {
        "username": username,
        "password": password,
        "to": to,
        "from": from_number,
        "text": text,
        "isFlash": False,
    }

    result, err = _post("SendSMS", data)
    if err:
        return {"success": False, "message": err, "recid": None}

    rec_id = result if not isinstance(result, dict) else result.get("RecId")

    if _is_success_recid(rec_id):
        return {
            "success": True,
            "message": "پیامک با موفقیت ارسال شد.",
            "recid": rec_id,
        }

    return {
        "success": False,
        "message": f"ارسال ناموفق بود (کد خطا: {rec_id}).",
        "recid": None,
    }


def get_credit_melipayamak(username, password):
    """
    دریافت موجودی حساب پیامکی

    Returns:
        dict: {"success": bool, "credit": number|None, "message": str}
    """
    username = str(username or "").strip()
    password = str(password or "").strip()

    if not all([username, password]):
        return {
            "success": False,
            "credit": None,
            "message": "نام کاربری یا رمز عبور تنظیم نشده.",
        }

    data = {"username": username, "password": password}
    result, err = _post("GetCredit", data)
    if err:
        return {"success": False, "credit": None, "message": err}

    try:
        credit = result if not isinstance(result, dict) else result.get("Credit")
        credit_val = float(credit)
    except (TypeError, ValueError):
        return {
            "success": False,
            "credit": None,
            "message": f"دریافت موجودی ناموفق بود (پاسخ: {result}).",
        }

    if credit_val < 0:
        return {
            "success": False,
            "credit": None,
            "message": f"خطا در دریافت موجودی (کد: {credit_val:.0f}).",
        }

    return {
        "success": True,
        "credit": credit_val,
        "message": "موجودی با موفقیت دریافت شد.",
    }


# ═══════════ تست دستی ═══════════

if __name__ == "__main__":
    print("این فایل باید با نام کاربری/رمز واقعی ملی‌پیامک تست شود.")
    print("نمونه استفاده:")
    print(
        'send_sms_melipayamak("09121234567", "سلام تست", '
        '"USERNAME", "PASSWORD", "5000...")'
    )