# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

"""
Parser هوشمند قبوض
پشتیبانی از:
- قبضینو (وب و اپ)
- آپ (وب و اپ)
- سایت‌های رسمی (آبفا، توانیر، گاز)
"""

import re


# ═══════════ تبدیل اعداد ═══════════

def normalize_digits(text):
    """تبدیل اعداد فارسی/عربی به انگلیسی"""
    if not text:
        return ""
    text = str(text)
    persian = "۰۱۲۳۴۵۶۷۸۹"
    arabic = "٠١٢٣٤٥٦٧٨٩"
    english = "0123456789"
    for p, e in zip(persian, english):
        text = text.replace(p, e)
    for a, e in zip(arabic, english):
        text = text.replace(a, e)
    return text


def clean_number(value):
    """پاکسازی و تبدیل به عدد"""
    if value is None or value == "":
        return 0
    value = normalize_digits(str(value))
    value = re.sub(r'[,،\s]|ریال|تومان', '', value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0


# ═══════════ تشخیص نوع قبض ═══════════

def detect_bill_type(text):
    """تشخیص هوشمند نوع قبض از متن"""
    text_lower = text.lower()

    # کلمات کلیدی برای هر نوع قبض
    water_keywords = [
        "قبض آب", "آب و فاضلاب", "آبفا",
        "آب بها", "آب مصرفی", "فاضلاب",
        "قطر انشعاب آب", "شرکت آب",
        "پرداخت قبض آب"
    ]

    electricity_keywords = [
        "قبض برق", "توانیر", "برق مصرفی",
        "برق منطقه", "کیلووات", "kwh",
        "شرکت برق", "پرداخت قبض برق",
        "قدرت قراردادی", "دیماند"
    ]

    gas_keywords = [
        "قبض گاز", "شرکت گاز", "گاز مصرفی",
        "شرکت ملی گاز", "کارکرد شمارشگر",
        "پرداخت قبض گاز", "بهای گاز",
        "شماره اشتراک گاز"
    ]

    # شمارش کلمات کلیدی
    water_count = sum(
        1 for kw in water_keywords
        if kw in text
    )
    elec_count = sum(
        1 for kw in electricity_keywords
        if kw in text
    )
    gas_count = sum(
        1 for kw in gas_keywords
        if kw in text
    )

    # بیشترین امتیاز
    scores = {
        "آب": water_count,
        "برق": elec_count,
        "گاز": gas_count,
    }

    max_type = max(scores, key=scores.get)
    if scores[max_type] > 0:
        return max_type

    return None


# ═══════════ استخراج فیلدها ═══════════

def find_value_after_label(text, labels, max_lines=3, skip_zero=False):
    """
    پیدا کردن مقدار بعد از یک برچسب.

    Args:
        skip_zero: اگه True باشه، مقادیر صفر/خالی نادیده گرفته می‌شن
                   و جستجو ادامه پیدا می‌کنه.
    """
    lines = text.split("\n")

    for label in labels:
        for i, line in enumerate(lines):
            line_clean = line.strip().rstrip(":").strip()

            # ─── تطابق دقیق ───
            if line_clean == label:
                for j in range(1, max_lines + 1):
                    if i + j < len(lines):
                        next_line = lines[i + j].strip()
                        if next_line:
                            if skip_zero:
                                # اگه مقدار صفره، نادیده بگیر
                                num = clean_number(next_line)
                                if num == 0:
                                    continue
                            return next_line

            # ─── برچسب + مقدار در یک خط ───
            if label in line and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    value = parts[1].strip()
                    if value:
                        if skip_zero:
                            num = clean_number(value)
                            if num == 0:
                                continue
                        return value

    return ""


def extract_field(text, label_patterns,
                   is_number=False, skip_zero=False):
    """استخراج فیلد با الگوهای مختلف"""
    value = find_value_after_label(
        text, label_patterns, skip_zero=skip_zero
    )

    if is_number:
        return clean_number(value)
    return value

def extract_bill_id_from_text(text):
    """پیدا کردن اولین عدد ۱۳ رقمی"""
    text_clean = normalize_digits(text)
    match = re.search(r'\b(\d{13})\b', text_clean)
    if match:
        return match.group(1)

    # اگه ۱۳ رقمی نبود، ۱۰-۱۳ رقمی
    match = re.search(r'\b(\d{10,13})\b', text_clean)
    if match:
        return match.group(1)

    return ""


def calculate_days_between(from_date_str, to_date_str):
    """محاسبه تعداد روز بین دو تاریخ شمسی"""
    try:
        import jdatetime

        def parse_j_date(s):
            s = normalize_digits(s).replace("-", "/")
            parts = s.split("/")
            if len(parts) != 3:
                return None
            return jdatetime.date(
                int(parts[0]),
                int(parts[1]),
                int(parts[2])
            )

        from_d = parse_j_date(from_date_str)
        to_d = parse_j_date(to_date_str)

        if from_d and to_d:
            delta = (
                to_d.togregorian() -
                from_d.togregorian()
            )
            return delta.days
    except Exception:
        pass
    return 0


# ═══════════ Parser اصلی ═══════════

def parse_bill_text(text, forced_type=None):
    """
    Parse متن قبض

    Args:
        text: متن کپی شده
        forced_type: نوع قبض (اگه کاربر مشخص کرده)

    Returns:
        dict یا None
    """
    if not text or len(text.strip()) < 20:
        return None

    # تشخیص نوع قبض
    detected_type = detect_bill_type(text)

    # اگه نوع مشخص نشده و forced_type هم نداریم
    bill_type = forced_type or detected_type
    if not bill_type:
        bill_type = "آب"  # پیش‌فرض

    # نرمالایز متن
    text_normalized = normalize_digits(text)

    result = {
        "bill_type": bill_type,
        "bill_id": "",
        "pay_id": "",
        "owner_name": "",
        "address": "",
        "postal_code": "",
        "amount": 0,
        "period": "",
        "from_date": "",
        "to_date": "",
        "due_date": "",
        "issue_date": "",
        "bill_date": "",
        "days_count": 0,
        "previous_reading": 0,
        "current_reading": 0,
        "consumption": 0,
        "consumption_unit": (
            "m³" if bill_type in ["آب", "گاز"]
            else "kWh"
        ),
        "usage_type": "",
        "meter_number": "",
        "city": "",
        "capacity": 0,
    }

    # ─── نام مالک ───
    result["owner_name"] = extract_field(
        text_normalized,
        [
            "نام مشترک",
            "نام مالک",
            "مشترک گرامی",
            "نام و نام خانوادگی",
            "به نام",
            "صاحب اشتراک",
        ]
    )

    # اگه نبود، بگرد دنبال خطی که قبل از عدد ۱۳ رقمی هست
    if not result["owner_name"]:
        lines = text_normalized.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if (
                    re.match(r'^\d{10,13}$', next_line)
                    and len(line) > 5
                    and not line.isdigit()
                    and "قبض" not in line
                    and "شناسه" not in line
                    and len(line) < 80
                ):
                    result["owner_name"] = line
                    break

    # ─── مبلغ ───
    # ─── مبلغ ───
    # ترتیب: اول مبالغ قطعی و نهایی، بعد بقیه
    # skip_zero=True → مقادیر صفر (قبض تسویه‌شده) نادیده گرفته می‌شن
    result["amount"] = extract_field(
        text_normalized,
        [
            "مبلغ",
            "مبلغ نهایی",
            "مبلغ کل قبض",
            "مبلغ صورتحساب",
            "جمع صورتحساب",
            "جمع صورت حساب دوره",
            "مبلغ بدهی",
            "مبلغ قابل پرداخت",
            "قابل پرداخت",
            "مبلغ کل بدهی",
        ],
        is_number=True,
        skip_zero=True,  # ⭐
    )

    # ⭐ اگه هنوز صفره، برای گاز دنبال هزینه/بهای مصرف بگرد
    if result["amount"] == 0 and bill_type == "گاز":
        result["amount"] = extract_field(
            text_normalized,
            [
                "هزینه گاز مصرفی",
                "بهای گاز مصرفی",
                "مبلغ گاز مصرفی",
                "بهای گاز",
                "هزینه گاز",
            ],
            is_number=True,
            skip_zero=True,
        )

    # ⭐ برای آب، اگه صفر بود
    if result["amount"] == 0 and bill_type == "آب":
        result["amount"] = extract_field(
            text_normalized,
            [
                "هزینه آب مصرفی",
                "بهای آب مصرفی",
                "مبلغ آب مصرفی",
                "بهای آب",
                "آب بها",
            ],
            is_number=True,
            skip_zero=True,
        )

    # ⭐ برای برق، اگه صفر بود
    if result["amount"] == 0 and bill_type == "برق":
        result["amount"] = extract_field(
            text_normalized,
            [
                "هزینه برق مصرفی",
                "بهای برق مصرفی",
                "مبلغ برق مصرفی",
                "بهای برق",
            ],
            is_number=True,
            skip_zero=True,
        )
    # ─── مهلت پرداخت ───
    result["due_date"] = extract_field(
        text_normalized,
        [
            "مهلت پرداخت",
            "تاریخ سررسید",
            "سررسید",
            "آخرین مهلت",
            "مهلت",
        ]
    )
    result["due_date"] = normalize_digits(
        result["due_date"]
    )

    # ─── تاریخ صدور ───
    result["issue_date"] = extract_field(
        text_normalized,
        [
            "تاریخ صدور",
            "تاریخ چاپ",
            "تاریخ ثبت",
            "تاریخ قبض",
        ]
    )
    result["issue_date"] = normalize_digits(
        result["issue_date"]
    )

    # ─── تاریخ قرائت‌ها ───
    result["from_date"] = extract_field(
        text_normalized,
        [
            "تاریخ قرائت پیشین",
            "تاریخ قرائت قبلی",
            "قرائت قبلی",
            "از تاریخ",
            "تاریخ کارکرد قبلی",
        ]
    )
    result["from_date"] = normalize_digits(
        result["from_date"]
    )

    result["to_date"] = extract_field(
        text_normalized,
        [
            "تاریخ قرائت کنونی",
            "تاریخ قرائت فعلی",
            "قرائت فعلی",
            "قرائت جاری",
            "تا تاریخ",
            "تاریخ کارکرد فعلی",
        ]
    )
    result["to_date"] = normalize_digits(
        result["to_date"]
    )

    result["bill_date"] = (
        result["issue_date"] or result["to_date"]
    )

    # ─── تعداد روز ───
    days_val = extract_field(
        text_normalized,
        ["تعداد روز", "روز مصرف", "مدت"],
        is_number=True
    )
    result["days_count"] = int(days_val)

    # محاسبه از تاریخ‌ها
    if (result["days_count"] == 0
            and result["from_date"]
            and result["to_date"]):
        result["days_count"] = calculate_days_between(
            result["from_date"],
            result["to_date"]
        )

    # ─── قرائت‌ها ───
    result["previous_reading"] = extract_field(
        text_normalized,
        [
            "رقم قرائت قبلی",
            "رقم شمارشگر پیشین",
            "کنتور قبلی",
            "قرائت قبلی کنتور",
            "شمارشگر پیشین",
            "عدد قرائت قبلی",
        ],
        is_number=True
    )

    result["current_reading"] = extract_field(
        text_normalized,
        [
            "رقم قرائت فعلی",
            "رقم شمارشگر فعلی",
            "کنتور فعلی",
            "قرائت فعلی کنتور",
            "شمارشگر فعلی",
            "عدد قرائت فعلی",
        ],
        is_number=True
    )

    # ─── مصرف ───
    result["consumption"] = extract_field(
        text_normalized,
        [
            "مصرف کل",
            "کارکرد شمارشگر",
            "کارکرد کنتور",
            "میزان مصرف",
            "مقدار مصرف",
            "مصرف دوره",
        ],
        is_number=True
    )

    # محاسبه از قرائت‌ها
    if (result["consumption"] == 0
            and result["current_reading"] > 0
            and result["previous_reading"] > 0):
        result["consumption"] = (
            result["current_reading"] -
            result["previous_reading"]
        )

    # ─── آدرس ───
    result["address"] = extract_field(
        text_normalized,
        [
            "نشانی",
            "آدرس",
            "محل سکونت",
            "نشانی مشترک",
        ]
    )

    # ─── کد پستی ───
    result["postal_code"] = extract_field(
        text_normalized,
        ["کد پستی", "کدپستی"]
    )
    result["postal_code"] = normalize_digits(
        result["postal_code"]
    )

    # ─── نوع مصرف / تعرفه ───
    result["usage_type"] = extract_field(
        text_normalized,
        [
            "تعرفه",
            "نوع مصرف",
            "نوع تعرفه",
            "کاربری",
            "نوع صورتحساب",
            "نوع صورت حساب",
        ]
    )

    # ─── شماره کنتور ───
    result["meter_number"] = extract_field(
        text_normalized,
        [
            "شماره بدنه کنتور",
            "شماره کنتور",
            "سریال کنتور",
            "کد کنتور",
            "شماره سریال",
        ]
    )
    result["meter_number"] = normalize_digits(
        result["meter_number"]
    )

    # ─── شناسه پرداخت ───
    result["pay_id"] = extract_field(
        text_normalized,
        [
            "شناسه پرداخت",
            "شناسه قبض پرداخت",
        ]
    )
    result["pay_id"] = normalize_digits(
        result["pay_id"]
    )

    # ─── شناسه قبض ───
    result["bill_id"] = extract_field(
        text_normalized,
        [
            "شناسه قبض",
            "شناسه صورتحساب",
        ]
    )
    result["bill_id"] = normalize_digits(
        result["bill_id"]
    )

    # اگه نبود، اولین عدد ۱۳ رقمی
    if not result["bill_id"]:
        result["bill_id"] = extract_bill_id_from_text(
            text_normalized
        )

    # ─── ظرفیت ───
    result["capacity"] = extract_field(
        text_normalized,
        ["ظرفیت قراردادی", "ظرفیت"],
        is_number=True
    )

    # ─── شهر ───
    if result["address"]:
        cities = [
            "تهران", "مشهد", "اصفهان", "شیراز",
            "تبریز", "کرج", "قم", "اهواز",
            "کرمانشاه", "ارومیه", "رشت", "زاهدان",
            "همدان", "کرمان", "یزد", "اردبیل",
            "بندرعباس", "اراک", "زنجان", "سنندج",
            "قزوین", "خرم آباد", "گرگان", "ساری",
            "بابل", "بوشهر", "بیرجند", "بجنورد",
            "ایلام", "شهرکرد", "یاسوج", "سمنان",
        ]
        for city in cities:
            if city in result["address"]:
                result["city"] = city
                break

    # ─── دوره ───
    if result["issue_date"] or result["to_date"]:
        date_str = (
            result["issue_date"] or result["to_date"]
        )
        try:
            parts = date_str.split("/")
            if len(parts) >= 2:
                months = [
                    "",
                    "فروردین", "اردیبهشت", "خرداد",
                    "تیر", "مرداد", "شهریور",
                    "مهر", "آبان", "آذر",
                    "دی", "بهمن", "اسفند"
                ]
                month_num = int(parts[1])
                if 1 <= month_num <= 12:
                    result["period"] = (
                        f"{months[month_num]} "
                        f"{parts[0]}"
                    )
        except Exception:
            pass

    # ─── بررسی نهایی ───
    important_fields = (
        result["amount"] > 0
        or result["owner_name"]
        or result["current_reading"] > 0
        or result["bill_id"]
    )

    if not important_fields:
        return None

    return result


# ═══════════ تست ═══════════

if __name__ == "__main__":
    # تست با نمونه گاز
    sample_gas = """
    قبض گاز
    حبیب اله رفیع زاده
    0147070106230
    مبلغ:
    50000
    مهلت پرداخت:
    1405/05/04
    تاریخ صدور:
    1405/04/25
    تاریخ قرائت کنونی:
    1405/04/09
    تاریخ قرائت پیشین:
    1405/02/23
    شماره اشتراک:
    357260955742
    سریال کنتور:
    109
    رقم شمارشگر پیشین:
    530,753
    رقم شمارشگر فعلی:
    532,574
    کارکرد شمارشگر:
    1,821
    """

    print("=" * 60)
    print("🧪 تست Parser با نمونه گاز")
    print("=" * 60)

    result = parse_bill_text(sample_gas)
    if result:
        print(
            f"✅ نوع قبض تشخیص داده شده: {result['bill_type']}"
        )
        print("-" * 60)
        for key, value in result.items():
            if value:
                print(f"  {key}: {value}")
    else:
        print("❌ چیزی استخراج نشد")

    print("=" * 60)