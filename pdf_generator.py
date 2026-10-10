# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

"""
سیستم تولید PDF حرفه‌ای برای کاربرگ‌ها
"""

import os
import jdatetime
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, Image, PageBreak,
        KeepTogether
    )
    from reportlab.lib.utils import ImageReader  # این باید باشه
    from reportlab.lib.styles import (
        getSampleStyleSheet, ParagraphStyle
    )
    from reportlab.lib.enums import (
        TA_CENTER, TA_RIGHT, TA_LEFT
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RESHAPER = True
except ImportError:
    HAS_RESHAPER = False


# ═══════════ توابع کمکی ═══════════

PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
}

MONTHS = [
    "", "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]

def to_persian(text):
    if text is None:
        return ""
    text = str(text)
    for en, fa in PERSIAN_DIGITS.items():
        text = text.replace(en, fa)
    return text


def rtl(text):
    if not text:
        return ""
    text = str(text)
    if HAS_RESHAPER:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text


def fmt_money(amount, show_unit=True, unit="ریال"):
    if amount is None:
        return "۰"
    try:
        formatted = f"{int(amount):,}"
        result = to_persian(formatted)
        if show_unit:
            return f"{result} {unit}"
        return result
    except (ValueError, TypeError):
        return "۰"


def _get_fonts_dir():
    """پیدا کردن مسیر فونت‌ها — سازگار با PyInstaller exe و حالت توسعه"""
    if getattr(sys, 'frozen', False):
        # حالت exe: دنبال fonts توی مسیرهای مختلف بگرد
        candidates = []
        if hasattr(sys, '_MEIPASS'):
            candidates.append(os.path.join(sys._MEIPASS, "fonts"))
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "fonts"))
        candidates.append(os.path.join(exe_dir, "_internal", "fonts"))
        for c in candidates:
            if os.path.isdir(c):
                return c
    # حالت توسعه (python app.py)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def register_fonts():
    if not HAS_REPORTLAB:
        return False
    try:
        fonts_dir = _get_fonts_dir()
        print(f"مسیر فونت‌ها: {fonts_dir}")

        regular_path = os.path.join(fonts_dir, "Vazirmatn-Regular.ttf")
        bold_path = os.path.join(fonts_dir, "Vazirmatn-Bold.ttf")
        medium_path = os.path.join(fonts_dir, "Vazirmatn-Medium.ttf")

        if os.path.exists(regular_path):
            pdfmetrics.registerFont(TTFont('Vazirmatn', regular_path))
        if os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('Vazirmatn-Bold', bold_path))
        if os.path.exists(medium_path):
            pdfmetrics.registerFont(TTFont('Vazirmatn-Medium', medium_path))
        return True
    except Exception as ex:
        print(f"خطای فونت: {ex}")
        return False

def get_jalali_date():
    try:
        import jdatetime
        j = jdatetime.datetime.now()
        MONTHS = [
            "", "فروردین", "اردیبهشت", "خرداد",
            "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]
        return to_persian(
            f"{j.day} {MONTHS[j.month]} {j.year}"
        )
    except Exception:
        return ""


def to_jalali_str(gregorian_date):
    if not gregorian_date:
        return "-"
    try:
        import jdatetime
        j = jdatetime.date.fromgregorian(
            date=gregorian_date
        )
        return to_persian(
            f"{j.year}/{j.month:02d}/{j.day:02d}"
        )
    except Exception:
        return "-"


def hex_to_rgb_tuple(hex_color):
    """تبدیل HEX به tuple برای reportlab"""
    try:
        hex_color = hex_color.lstrip('#')
        return colors.HexColor(f"#{hex_color}")
    except Exception:
        return colors.HexColor("#1565C0")


# ═══════════ رنگ‌های روشن‌تر (برای پس‌زمینه) ═══════════

def lighten_color(hex_color, amount=0.9):
    """روشن‌تر کردن رنگ برای پس‌زمینه"""
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)

        return colors.Color(r/255, g/255, b/255)
    except Exception:
        return colors.HexColor("#E3F2FD")


# ═══════════ تابع اصلی: ساخت PDF ═══════════

def generate_unit_report_pdf(
    report_data,
    building_name="",
    building_info=None,
    bank_info=None,
    output_path=None,
    currency_label="ریال",
    logo_path=None,
    theme_color="#1565C0",
):
    """
    ساخت PDF حرفه‌ای کاربرگ

    Args:
        report_data: خروجی get_unit_full_report
        building_name: نام ساختمان
        building_info: {"address": "", "floors": 0, "total_units": 0}
        bank_info: {"card": "", "owner": "", "sheba": ""}
        output_path: مسیر خروجی
        currency_label: واحد پول
        logo_path: مسیر لوگو
        theme_color: رنگ اصلی (HEX)
    """
    if not HAS_REPORTLAB:
        return {
            "success": False,
            "path": None,
            "message": "reportlab نصب نیست.",
        }

    try:
        register_fonts()

        # مسیر خروجی
        if not output_path:
            reports_dir = os.path.join(
                os.getcwd(), "reports"
            )
            os.makedirs(
                reports_dir, exist_ok=True
            )
            unit_number = report_data["unit"][
                "number"
            ]
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            filename = (
                f"unit_{unit_number}_"
                f"{timestamp}.pdf"
            )
            output_path = os.path.join(
                reports_dir, filename
            )

        # ─── رنگ‌ها ─────
        PRIMARY = hex_to_rgb_tuple(theme_color)
        PRIMARY_LIGHT = lighten_color(
            theme_color, 0.85
        )
        PRIMARY_LIGHTER = lighten_color(
            theme_color, 0.95
        )
        SUCCESS = colors.HexColor("#2E7D32")
        SUCCESS_LIGHT = colors.HexColor("#E8F5E9")
        WARNING = colors.HexColor("#EF6C00")
        WARNING_LIGHT = colors.HexColor("#FFF3E0")
        DANGER = colors.HexColor("#C62828")
        DANGER_LIGHT = colors.HexColor("#FFEBEE")
        GRAY = colors.HexColor("#666666")
        LIGHT_GRAY = colors.HexColor("#F5F5F5")
        BORDER = colors.HexColor("#E0E0E0")


        # ─── داکیومنت ─────
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm,
        )

        elements = []

        # ─── استایل‌ها ─────
        normal = ParagraphStyle(
            'Normal',
            fontName='Vazirmatn',
            fontSize=10,
            alignment=TA_RIGHT,
            leading=14,
        )

        normal_center = ParagraphStyle(
            'NormalCenter',
            fontName='Vazirmatn',
            fontSize=10,
            alignment=TA_CENTER,
            leading=14,
        )

        bold = ParagraphStyle(
            'Bold',
            fontName='Vazirmatn-Bold',
            fontSize=10,
            alignment=TA_RIGHT,
            leading=14,
        )

        bold_center = ParagraphStyle(
            'BoldCenter',
            fontName='Vazirmatn-Bold',
            fontSize=10,
            alignment=TA_CENTER,
            leading=14,
        )

        small_gray = ParagraphStyle(
            'SmallGray',
            fontName='Vazirmatn',
            fontSize=8,
            alignment=TA_RIGHT,
            textColor=GRAY,
        )

        section_title = ParagraphStyle(
            'SectionTitle',
            fontName='Vazirmatn-Bold',
            fontSize=13,
            alignment=TA_RIGHT,
            textColor=PRIMARY,
            spaceAfter=8,
            spaceBefore=12,
        )

        big_title = ParagraphStyle(
            'BigTitle',
            fontName='Vazirmatn-Bold',
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.white,
            leading=22,
        )

        subtitle_white = ParagraphStyle(
            'SubtitleWhite',
            fontName='Vazirmatn',
            fontSize=11,
            alignment=TA_CENTER,
            textColor=colors.white,
        )

        # ══════════════════════════════════
        # ═══════════ هدر ═══════════
        # ══════════════════════════════════

        # ─── نوار بالای هدر ─────
        header_cells = []

        # ستون چپ: تاریخ و لوگو
        left_col = [
            Paragraph(
                rtl(get_jalali_date()),
                ParagraphStyle(
                    'DateStyle',
                    fontName='Vazirmatn',
                    fontSize=10,
                    alignment=TA_LEFT,
                    textColor=colors.white,
                )
            )
        ]

        # ستون وسط: عنوان
        center_col = [
            Paragraph(
                rtl(building_name or "ساختمان"),
                big_title,
            ),
            Spacer(1, 3),
            Paragraph(
                rtl(
                    f"کاربرگ واحد {to_persian(str(report_data['unit']['number']))}"
                ),
                subtitle_white,
            ),
        ]

        # ستون راست: لوگو یا آیکون
        right_col = []
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image(
                    logo_path,
                    width=2.2 * cm,
                    height=2.2 * cm,
                )
                right_col.append(img)
            except Exception:
                right_col.append(
                    Paragraph("🏢", bold_center)
                )
        else:
            right_col.append(
                Paragraph(
                    "🏢",
                    ParagraphStyle(
                        'IconStyle',
                        fontName='Vazirmatn',
                        fontSize=40,
                        alignment=TA_CENTER,
                        textColor=colors.white,
                    )
                )
            )

        header_data = [[
            left_col, center_col, right_col
        ]]

        header_table = Table(
            header_data,
            colWidths=[
                3 * cm, 12.6 * cm, 3 * cm
            ],
            rowHeights=[2.5 * cm],
        )
        header_table.setStyle(TableStyle([
            (
                'BACKGROUND', (0, 0), (-1, -1),
                PRIMARY
            ),
            (
                'VALIGN', (0, 0), (-1, -1), 'MIDDLE'
            ),
            (
                'ALIGN', (0, 0), (0, 0), 'LEFT'
            ),
            (
                'ALIGN', (2, 0), (2, 0), 'CENTER'
            ),
            (
                'LEFTPADDING', (0, 0), (-1, -1), 10
            ),
            (
                'RIGHTPADDING', (0, 0), (-1, -1), 10
            ),
            (
                'TOPPADDING', (0, 0), (-1, -1), 8
            ),
            (
                'BOTTOMPADDING', (0, 0), (-1, -1), 8
            ),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.3 * cm))

        # ══════════════════════════════════
        # ═══════════ اطلاعات ساختمان ═══════════
        # ══════════════════════════════════

        if building_info:
            building_data = [[
                Paragraph(
                    rtl(
                        to_persian(str(
                            building_info.get(
                                "total_units", 0
                            )
                        ))
                    ),
                    bold_center,
                ),
                Paragraph(
                    rtl("واحد"),
                    small_gray,
                ),
                Paragraph(
                    rtl(
                        to_persian(str(
                            building_info.get(
                                "floors", 0
                            )
                        ))
                    ),
                    bold_center,
                ),
                Paragraph(
                    rtl("طبقه"),
                    small_gray,
                ),
                Paragraph(
                    rtl(
                        building_info.get(
                            "address", "-"
                        ) or "-"
                    ),
                    bold,
                ),
                Paragraph(
                    rtl("📍 آدرس:"),
                    bold,
                ),
            ]]

            building_table = Table(
                building_data,
                colWidths=[
                    1.3 * cm, 1 * cm,
                    1.3 * cm, 1 * cm,
                    10.5 * cm, 2.5 * cm
                ],
            )
            building_table.setStyle(TableStyle([
                (
                    'BACKGROUND', (0, 0), (-1, -1),
                    PRIMARY_LIGHTER
                ),
                (
                    'VALIGN', (0, 0), (-1, -1),
                    'MIDDLE'
                ),
                (
                    'BOX', (0, 0), (-1, -1),
                    0.5, BORDER
                ),
                (
                    'PADDING', (0, 0), (-1, -1), 8
                ),
            ]))
            elements.append(building_table)
            elements.append(Spacer(1, 0.3 * cm))

        # ══════════════════════════════════
        # ═══════════ اطلاعات ساکن ═══════════
        # ══════════════════════════════════

        elements.append(Paragraph(
            rtl("👤 اطلاعات ساکن"),
            section_title,
        ))

        u = report_data["unit"]

        resident_data = [
            [
                Paragraph(
                    rtl(u["resident_name"] or "-"),
                    bold,
                ),
                Paragraph(
                    rtl("نام و نام خانوادگی:"),
                    normal,
                ),
                Paragraph(
                    rtl(
                        to_persian(u["phone"] or "-")
                    ),
                    bold,
                ),
                Paragraph(
                    rtl("موبایل:"),
                    normal,
                ),
            ],
            [
                Paragraph(
                    rtl(u["resident_type"] or "-"),
                    bold,
                ),
                Paragraph(
                    rtl("نوع سکونت:"),
                    normal,
                ),
                Paragraph(
                    rtl(
                        to_persian(str(u["number"]))
                    ),
                    bold,
                ),
                Paragraph(
                    rtl("شماره واحد:"),
                    normal,
                ),
            ],
            [
                Paragraph(
                    rtl(
                        f"{to_persian(str(u['people_count']))} نفر"
                    ),
                    bold,
                ),
                Paragraph(
                    rtl("تعداد نفرات:"),
                    normal,
                ),
                Paragraph(
                    rtl(
                        f"{to_persian(str(u['area']))} m²"
                    ),
                    bold,
                ),
                Paragraph(
                    rtl("متراژ:"),
                    normal,
                ),
            ],
        ]

        resident_table = Table(
            resident_data,
            colWidths=[
                5.5 * cm, 3 * cm,
                5.5 * cm, 3 * cm
            ],
        )
        resident_table.setStyle(TableStyle([
            (
                'VALIGN', (0, 0), (-1, -1), 'MIDDLE'
            ),
            (
                'BACKGROUND', (1, 0), (1, -1),
                LIGHT_GRAY
            ),
            (
                'BACKGROUND', (3, 0), (3, -1),
                LIGHT_GRAY
            ),
            (
                'GRID', (0, 0), (-1, -1), 0.5, BORDER
            ),
            (
                'PADDING', (0, 0), (-1, -1), 7
            ),
        ]))
        elements.append(resident_table)

        # ══════════════════════════════════
        # ═══════════ خلاصه مالی ═══════════
        # ══════════════════════════════════

        summary = report_data["summary"]

        elements.append(Paragraph(
            rtl("💰 خلاصه مالی"),
            section_title,
        ))

        pct = summary["collection_percent"]

        summary_data = [
            [
                Paragraph(
                    rtl(
                        f'{to_persian(f"{pct:.1f}")}٪'
                    ),
                    ParagraphStyle(
                        'PctStyle',
                        fontName='Vazirmatn-Bold',
                        fontSize=16,
                        alignment=TA_CENTER,
                        textColor=(
                            SUCCESS if pct >= 90
                            else WARNING if pct >= 50
                            else DANGER
                        ),
                    )
                ),
                Paragraph(
                    rtl(
                        fmt_money(
                            summary["total_debt"],
                            show_unit=False,
                        )
                    ),
                    ParagraphStyle(
                        'DebtStyle',
                        fontName='Vazirmatn-Bold',
                        fontSize=14,
                        alignment=TA_CENTER,
                        textColor=DANGER,
                    )
                ),
                Paragraph(
                    rtl(
                        fmt_money(
                            summary["total_paid"],
                            show_unit=False,
                        )
                    ),
                    ParagraphStyle(
                        'PaidStyle',
                        fontName='Vazirmatn-Bold',
                        fontSize=14,
                        alignment=TA_CENTER,
                        textColor=SUCCESS,
                    )
                ),
                Paragraph(
                    rtl(
                        fmt_money(
                            summary["total_charges"],
                            show_unit=False,
                        )
                    ),
                    ParagraphStyle(
                        'ChargeStyle',
                        fontName='Vazirmatn-Bold',
                        fontSize=14,
                        alignment=TA_CENTER,
                        textColor=PRIMARY,
                    )
                ),
            ],
            [
                Paragraph(
                    rtl("درصد وصول"),
                    small_gray,
                ),
                Paragraph(
                    rtl(f"بدهی ({currency_label})"),
                    small_gray,
                ),
                Paragraph(
                    rtl(f"پرداختی ({currency_label})"),
                    small_gray,
                ),
                Paragraph(
                    rtl(f"شارژ کل ({currency_label})"),
                    small_gray,
                ),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                4.15 * cm, 4.15 * cm,
                4.15 * cm, 4.15 * cm
            ],
        )
        summary_table.setStyle(TableStyle([
            (
                'VALIGN', (0, 0), (-1, -1), 'MIDDLE'
            ),
            (
                'ALIGN', (0, 0), (-1, -1), 'CENTER'
            ),
            (
                'BACKGROUND', (0, 0), (0, 0),
                (
                    SUCCESS_LIGHT if pct >= 90
                    else WARNING_LIGHT if pct >= 50
                    else DANGER_LIGHT
                )
            ),
            (
                'BACKGROUND', (1, 0), (1, 0),
                DANGER_LIGHT
            ),
            (
                'BACKGROUND', (2, 0), (2, 0),
                SUCCESS_LIGHT
            ),
            (
                'BACKGROUND', (3, 0), (3, 0),
                PRIMARY_LIGHT
            ),
            (
                'BACKGROUND', (0, 1), (-1, 1),
                LIGHT_GRAY
            ),
            (
                'GRID', (0, 0), (-1, -1), 0.5, BORDER
            ),
            (
                'TOPPADDING', (0, 0), (-1, 0), 12
            ),
            (
                'BOTTOMPADDING', (0, 0), (-1, 0), 12
            ),
            (
                'TOPPADDING', (0, 1), (-1, 1), 6
            ),
            (
                'BOTTOMPADDING', (0, 1), (-1, 1), 6
            ),
        ]))
        elements.append(summary_table)

        # ══════════════════════════════════
        # ═══════════ لیست شارژها ═══════════
        # ══════════════════════════════════

        elements.append(Paragraph(
            rtl(
                f"📋 لیست شارژها ({to_persian(str(summary['charges_count']))} مورد)"
            ),
            section_title,
        ))

        if report_data["charges"]:
            charges_data = [
                [
                    Paragraph(
                        rtl("وضعیت"), bold_center
                    ),
                    Paragraph(
                        rtl("باقیمانده"), bold_center
                    ),
                    Paragraph(
                        rtl("پرداختی"), bold_center
                    ),
                    Paragraph(
                        rtl("مبلغ"), bold_center
                    ),
                    Paragraph(
                        rtl("دوره"), bold_center
                    ),
                ],
            ]

            for c in report_data["charges"]:
                status_color = {
                    "تسویه": SUCCESS,
                    "ناقص": WARNING,
                    "پرداخت نشده": DANGER,
                }.get(c["status"], GRAY)

                charges_data.append([
                    Paragraph(
                        rtl(c["status"] or "-"),
                        ParagraphStyle(
                            'StatusStyle',
                            fontName=(
                                'Vazirmatn-Bold'
                            ),
                            fontSize=9,
                            alignment=TA_CENTER,
                            textColor=status_color,
                        )
                    ),
                    Paragraph(
                        rtl(
                            fmt_money(
                                c["remaining"],
                                show_unit=False,
                            )
                        ),
                        ParagraphStyle(
                            'RemStyle',
                            fontName='Vazirmatn',
                            fontSize=9,
                            alignment=TA_CENTER,
                            textColor=(
                                DANGER
                                if c["remaining"] > 0
                                else SUCCESS
                            ),
                        )
                    ),
                    Paragraph(
                        rtl(
                            fmt_money(
                                c["paid_amount"],
                                show_unit=False,
                            )
                        ),
                        normal_center,
                    ),
                    Paragraph(
                        rtl(
                            fmt_money(
                                c["amount"],
                                show_unit=False,
                            )
                        ),
                        bold_center,
                    ),
                    Paragraph(
                        rtl(c["period"] or "-"),
                        bold_center,
                    ),
                ])

            charges_table = Table(
                charges_data,
                colWidths=[
                    2.8 * cm, 3.2 * cm,
                    3.2 * cm, 3.2 * cm, 4.2 * cm
                ],
            )
            charges_table.setStyle(TableStyle([
                (
                    'BACKGROUND', (0, 0), (-1, 0),
                    PRIMARY
                ),
                (
                    'TEXTCOLOR', (0, 0), (-1, 0),
                    colors.white
                ),
                (
                    'VALIGN', (0, 0), (-1, -1),
                    'MIDDLE'
                ),
                (
                    'ROWBACKGROUNDS',
                    (0, 1), (-1, -1),
                    [colors.white, LIGHT_GRAY]
                ),
                (
                    'GRID', (0, 0), (-1, -1),
                    0.5, BORDER
                ),
                (
                    'PADDING', (0, 0), (-1, -1), 7
                ),
            ]))
            elements.append(charges_table)
        else:
            elements.append(Paragraph(
                rtl("شارژی ثبت نشده است."),
                normal_center,
            ))

        # ══════════════════════════════════
        # ═══════════ لیست پرداخت‌ها ═══════════
        # ══════════════════════════════════

        elements.append(Paragraph(
            rtl(
                f"💳 لیست پرداخت‌ها ({to_persian(str(summary['payments_count']))} مورد)"
            ),
            section_title,
        ))

        if report_data["payments"]:
            payments_data = [
                [
                    Paragraph(
                        rtl("پیگیری"), bold_center
                    ),
                    Paragraph(
                        rtl("روش"), bold_center
                    ),
                    Paragraph(
                        rtl("مبلغ"), bold_center
                    ),
                    Paragraph(
                        rtl("تاریخ"), bold_center
                    ),
                ],
            ]

            for p in report_data["payments"]:
                payments_data.append([
                    Paragraph(
                        rtl(
                            to_persian(
                                p["tracking_code"]
                                or "-"
                            )
                        ),
                        normal_center,
                    ),
                    Paragraph(
                        rtl(
                            p["payment_method"]
                            or "-"
                        ),
                        normal_center,
                    ),
                    Paragraph(
                        rtl(
                            fmt_money(
                                p["amount"],
                                show_unit=False,
                            )
                        ),
                        ParagraphStyle(
                            'PayAmountStyle',
                            fontName=(
                                'Vazirmatn-Bold'
                            ),
                            fontSize=10,
                            alignment=TA_CENTER,
                            textColor=SUCCESS,
                        )
                    ),
                    Paragraph(
                        rtl(
                            to_jalali_str(
                                p["payment_date"]
                            )
                        ),
                        bold_center,
                    ),
                ])

            payments_table = Table(
                payments_data,
                colWidths=[
                    4.2 * cm, 3.2 * cm,
                    4.2 * cm, 5 * cm
                ],
            )
            payments_table.setStyle(TableStyle([
                (
                    'BACKGROUND', (0, 0), (-1, 0),
                    SUCCESS
                ),
                (
                    'TEXTCOLOR', (0, 0), (-1, 0),
                    colors.white
                ),
                (
                    'VALIGN', (0, 0), (-1, -1),
                    'MIDDLE'
                ),
                (
                    'ROWBACKGROUNDS',
                    (0, 1), (-1, -1),
                    [colors.white, LIGHT_GRAY]
                ),
                (
                    'GRID', (0, 0), (-1, -1),
                    0.5, BORDER
                ),
                (
                    'PADDING', (0, 0), (-1, -1), 7
                ),
            ]))
            elements.append(payments_table)
        else:
            elements.append(Paragraph(
                rtl("پرداختی ثبت نشده است."),
                normal_center,
            ))

        # ══════════════════════════════════
        # ═══════════ اطلاعات بانکی ═══════════
        # ══════════════════════════════════

        if bank_info and (
            bank_info.get("card") or
            bank_info.get("sheba")
        ):
            elements.append(Paragraph(
                rtl("💳 اطلاعات پرداخت"),
                section_title,
            ))

            bank_rows = []

            if bank_info.get("card"):
                bank_rows.append([
                    Paragraph(
                        rtl(
                            to_persian(
                                bank_info["card"]
                            )
                        ),
                        bold_center,
                    ),
                    Paragraph(
                        rtl("💳 شماره کارت:"),
                        bold,
                    ),
                ])

            if bank_info.get("owner"):
                bank_rows.append([
                    Paragraph(
                        rtl(bank_info["owner"]),
                        bold_center,
                    ),
                    Paragraph(
                        rtl("👤 صاحب حساب:"),
                        bold,
                    ),
                ])

            if bank_info.get("sheba"):
                bank_rows.append([
                    Paragraph(
                        rtl(
                            to_persian(
                                bank_info["sheba"]
                            )
                        ),
                        bold_center,
                    ),
                    Paragraph(
                        rtl("🏦 شماره شبا:"),
                        bold,
                    ),
                ])

            if bank_rows:
                bank_table = Table(
                    bank_rows,
                    colWidths=[
                        13 * cm, 3.6 * cm
                    ],
                )
                bank_table.setStyle(TableStyle([
                    (
                        'BACKGROUND', (0, 0), (-1, -1),
                        SUCCESS_LIGHT
                    ),
                    (
                        'BACKGROUND', (1, 0), (1, -1),
                        SUCCESS_LIGHT
                    ),
                    (
                        'VALIGN', (0, 0), (-1, -1),
                        'MIDDLE'
                    ),
                    (
                        'GRID', (0, 0), (-1, -1),
                        0.5, colors.HexColor(
                            "#A5D6A7"
                        )
                    ),
                    (
                        'PADDING', (0, 0), (-1, -1), 8
                    ),
                ]))
                elements.append(bank_table)

        # ══════════════════════════════════
        # ═══════════ امضاها ═══════════
        # ══════════════════════════════════

        elements.append(Spacer(1, 1 * cm))

        signature_data = [
            [
                Paragraph(
                    rtl("امضای ساکن"),
                    bold_center,
                ),
                "",
                Paragraph(
                    rtl("مهر و امضای مدیریت"),
                    bold_center,
                ),
            ],
            ["", "", ""],
            ["", "", ""],
        ]

        signature_table = Table(
            signature_data,
            colWidths=[
                6.5 * cm, 3 * cm, 6.5 * cm
            ],
            rowHeights=[
                0.7 * cm, 1.5 * cm, 0.3 * cm
            ],
        )
        signature_table.setStyle(TableStyle([
            (
                'VALIGN', (0, 0), (-1, -1), 'MIDDLE'
            ),
            (
                'ALIGN', (0, 0), (-1, -1), 'CENTER'
            ),
            (
                'LINEBELOW', (0, 1), (0, 1),
                0.5, GRAY
            ),
            (
                'LINEBELOW', (2, 1), (2, 1),
                0.5, GRAY
            ),
        ]))
        elements.append(signature_table)

        # ══════════════════════════════════
        # ═══════════ فوتر ═══════════
        # ══════════════════════════════════

        elements.append(Spacer(1, 0.5 * cm))

        footer_line = Table(
            [[""]],
            colWidths=[16.6 * cm],
            rowHeights=[0.02 * cm],
        )
        footer_line.setStyle(TableStyle([
            (
                'BACKGROUND', (0, 0), (-1, -1),
                PRIMARY
            ),
        ]))
        elements.append(footer_line)

        elements.append(Spacer(1, 0.2 * cm))

        footer_text = Paragraph(
            rtl(
                f"© {building_name or 'ساختمان'} - "
                f"تولید شده توسط سیستم مدیریت ساختمان"
            ),
            ParagraphStyle(
                'FooterStyle',
                fontName='Vazirmatn',
                fontSize=8,
                alignment=TA_CENTER,
                textColor=GRAY,
            )
        )
        elements.append(footer_text)

        # ─── ساخت PDF ─────
        doc.build(elements)

        return {
            "success": True,
            "path": output_path,
            "message": "PDF با موفقیت ساخته شد.",
        }

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "path": None,
            "message": f"خطای PDF: {ex}",
        }

# ═══════════ تابع دوم: PDF گزارش مالی کلی ساختمان ═══════════

def generate_financial_report_pdf(
    report_data,
    building_name="",
    building_info=None,
    bank_info=None,
    output_path=None,
    currency_label="ریال",
    logo_path=None,
    theme_color="#1565C0",
):
    """ساخت PDF گزارش مالی کامل — نسخه نهایی با پشتیبانی کامل واحد پول"""
    if not HAS_REPORTLAB:
        return {"success": False, "path": None,
                "message": "reportlab نصب نیست."}

    try:
        register_fonts()

        # ─── استخراج داده ───
        label = report_data.get("label", "گزارش مالی")
        summary = report_data.get("summary", {}) or {}
        charges = report_data.get("charges", []) or []
        payments = report_data.get("payments", []) or []
        expenses = report_data.get("expenses", []) or []
        bills = report_data.get("bills", []) or []
        debtors = report_data.get("debtors", []) or []
        all_payers = report_data.get("all_payers", []) or []
        top_payers = report_data.get("top_payers", []) or []
        late_payers = report_data.get("late_payers", []) or []
        categories = report_data.get("categories", []) or []
        methods = report_data.get("methods", []) or []
        expense_chart_path = report_data.get("expense_chart_path")
        method_chart_path = report_data.get("method_chart_path")
        trend_chart_path = report_data.get("trend_chart_path")

        # ⭐⭐⭐ تشخیص واحد پول سیستم ⭐⭐⭐
        is_rial = "ریال" in str(currency_label)
        print(f"💰 واحد پول PDF: {currency_label} | is_rial={is_rial}")

        def _disp_t(val):
            """Toman → واحد نمایش (اگر ریال باشه ×۱۰)."""
            try:
                v = float(val or 0)
            except Exception:
                v = 0
            return v * 10 if is_rial else v

        def _disp_r(val):
            """Rial → واحد نمایش (اگر تومان باشه ÷۱۰)."""
            try:
                v = float(val or 0)
            except Exception:
                v = 0
            return v if is_rial else v / 10

        # ⭐ پیش‌پردازش: تبدیل همه مقادیر به واحد نمایش
        # charges/payments/expenses/summary/debtors: Toman source
        # bills: Rial source

        # Copy و scale charges
        charges = [
            {**c,
             "amount": _disp_t(c.get("amount")),
             "paid_amount": _disp_t(c.get("paid_amount")),
             "remaining": _disp_t(c.get("remaining"))}
            for c in charges
        ]
        # Copy و scale payments
        payments = [
            {**p, "amount": _disp_t(p.get("amount"))}
            for p in payments
        ]
        # Copy و scale expenses
        expenses = [
            {**e, "amount": _disp_t(e.get("amount"))}
            for e in expenses
        ]
        # Copy و scale bills (Rial source)
        bills = [
            {**b, "amount": _disp_r(b.get("amount"))}
            for b in bills
        ]
        # Copy و scale summary
        summary = {**summary}
        for k in ("total_charges", "total_payments", "total_expenses",
                  "net", "total_remaining"):
            if k in summary:
                summary[k] = _disp_t(summary.get(k))
        # Copy و scale debtors
        debtors = [
            {**d, "debt": _disp_t(d.get("debt"))}
            for d in debtors
        ]
        # Copy و scale categories
        categories = [
            {**c, "total": _disp_t(c.get("total"))}
            for c in categories
        ]
        # Copy و scale methods
        methods = [
            {**m, "total": _disp_t(m.get("total"))}
            for m in methods
        ]

        # ─── مسیر خروجی ───
        if not output_path:
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = "financial_" + timestamp + ".pdf"
            output_path = os.path.join(reports_dir, filename)

        # ─── رنگ‌ها ───
        PRIMARY = hex_to_rgb_tuple(theme_color)
        PRIMARY_LIGHT = lighten_color(theme_color, 0.85)
        SUCCESS = colors.HexColor("#2E7D32")
        SUCCESS_LIGHT = colors.HexColor("#E8F5E9")
        WARNING = colors.HexColor("#EF6C00")
        WARNING_LIGHT = colors.HexColor("#FFF3E0")
        DANGER = colors.HexColor("#C62828")
        DANGER_LIGHT = colors.HexColor("#FFEBEE")
        WATER = colors.HexColor("#00BCD4")
        WATER_LIGHT = colors.HexColor("#E0F7FA")
        POWER = colors.HexColor("#FFC107")
        POWER_LIGHT = colors.HexColor("#FFF8E1")
        GAS = colors.HexColor("#FF5722")
        GAS_LIGHT = colors.HexColor("#FBE9E7")
        GOLD = colors.HexColor("#FFD700")
        GOLD_DARK = colors.HexColor("#B8860B")
        SILVER = colors.HexColor("#C0C0C0")
        SILVER_DARK = colors.HexColor("#607D8B")
        BRONZE = colors.HexColor("#CD7F32")
        BRONZE_DARK = colors.HexColor("#8D6E63")
        GRAY = colors.HexColor("#666666")
        LIGHT_GRAY = colors.HexColor("#F5F5F5")
        BORDER = colors.HexColor("#E0E0E0")

        S = SUCCESS
        W = WARNING
        D = DANGER

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=0.8 * cm, leftMargin=0.8 * cm,
            topMargin=0.6 * cm, bottomMargin=0.6 * cm,
        )

        elements = []

        # ─── استایل‌ها ───
        t_right = ParagraphStyle('FR_R', fontName='Vazirmatn',
            fontSize=8, alignment=TA_RIGHT, leading=10)
        t_center = ParagraphStyle('FR_C', fontName='Vazirmatn',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_bold_r = ParagraphStyle('FR_BR', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_RIGHT, leading=10)
        t_bold_c = ParagraphStyle('FR_BC', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_th = ParagraphStyle('FR_TH', fontName='Vazirmatn-Bold',
            fontSize=7, alignment=TA_CENTER,
            textColor=colors.white, leading=9)
        t_small = ParagraphStyle('FR_SM', fontName='Vazirmatn',
            fontSize=6.5, alignment=TA_CENTER, textColor=GRAY, leading=8)
        section = ParagraphStyle('FR_SEC', fontName='Vazirmatn-Bold',
            fontSize=10, alignment=TA_RIGHT, textColor=PRIMARY,
            spaceAfter=4, spaceBefore=6)

        # ═══ هدر ═══
        date_str = rtl(get_jalali_date())
        left_col = [Paragraph(date_str, ParagraphStyle('FR_DS',
            fontName='Vazirmatn', fontSize=8,
            alignment=TA_LEFT, textColor=colors.white))]

        center_col = [
            Paragraph(rtl(building_name or "ساختمان"),
                ParagraphStyle('FR_BT', fontName='Vazirmatn-Bold',
                    fontSize=14, alignment=TA_CENTER,
                    textColor=colors.white, leading=16)),
            Paragraph(rtl("گزارش مالی: " + label),
                ParagraphStyle('FR_ST', fontName='Vazirmatn',
                    fontSize=9, alignment=TA_CENTER,
                    textColor=colors.white)),
        ]

        right_col = []
        if logo_path and os.path.exists(logo_path):
            try:
                right_col.append(Image(logo_path,
                    width=1.6 * cm, height=1.6 * cm))
            except Exception:
                right_col.append(Paragraph("🏢", t_bold_c))
        else:
            right_col.append(Paragraph("🏢",
                ParagraphStyle('FR_IC', fontName='Vazirmatn',
                    fontSize=28, alignment=TA_CENTER,
                    textColor=colors.white)))

        header_table = Table(
            [[left_col, center_col, right_col]],
            colWidths=[2.5 * cm, 13.2 * cm, 2.5 * cm],
            rowHeights=[1.6 * cm],
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2 * cm))

        # ─── اطلاعات ساختمان ───
        if building_info:
            binfo = Table(
                [[
                    Paragraph(rtl(building_info.get("address", "-") or "-"), t_bold_r),
                    Paragraph(rtl("آدرس:"), t_small),
                    Paragraph(rtl(to_persian(str(building_info.get("floors", 0)))), t_bold_c),
                    Paragraph(rtl("طبقه"), t_small),
                    Paragraph(rtl(to_persian(str(building_info.get("total_units", 0)))), t_bold_c),
                    Paragraph(rtl("واحد"), t_small),
                ]],
                colWidths=[7.6 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm],
            )
            binfo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            elements.append(binfo)
            elements.append(Spacer(1, 0.25 * cm))

        # ═══ ۱. خلاصه مالی ═══
        elements.append(Paragraph(rtl("خلاصه مالی"), section))

        total_charges = summary.get("total_charges", 0)
        total_payments = summary.get("total_payments", 0)
        total_expenses = summary.get("total_expenses", 0)
        net_amount = summary.get("net", 0)
        total_remaining = summary.get("total_remaining", 0)
        pct = summary.get("collection_percent", 0)

        if pct >= 90:
            pct_color = SUCCESS
        elif pct >= 50:
            pct_color = WARNING
        else:
            pct_color = DANGER

        if pct >= 90:
            pct_bg = SUCCESS_LIGHT
        elif pct >= 50:
            pct_bg = WARNING_LIGHT
        else:
            pct_bg = DANGER_LIGHT

        def stat_cell(title, amount, color, bg):
            return [
                Paragraph(rtl(title), t_small),
                Paragraph(
                    rtl(fmt_money(amount, show_unit=False) + " " + currency_label),
                    ParagraphStyle('FR_SV', fontName='Vazirmatn-Bold',
                        fontSize=10, alignment=TA_CENTER,
                        textColor=color, leading=12),
                ),
            ]

        stats_table = Table(
            [[
                stat_cell("کل شارژ صادره", total_charges, PRIMARY, PRIMARY_LIGHT),
                stat_cell("کل دریافتی", total_payments, SUCCESS, SUCCESS_LIGHT),
                stat_cell("کل هزینه", total_expenses, WARNING, WARNING_LIGHT),
                stat_cell("خالص", net_amount,
                    PRIMARY if net_amount >= 0 else DANGER,
                    PRIMARY_LIGHT if net_amount >= 0 else DANGER_LIGHT),
                stat_cell("بدهی باقی‌مانده", total_remaining, DANGER, DANGER_LIGHT),
            ]],
            colWidths=[3.9 * cm, 3.9 * cm, 3.9 * cm, 3.9 * cm, 3.4 * cm],
        )
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), PRIMARY_LIGHT),
            ('BACKGROUND', (1, 0), (1, 0), SUCCESS_LIGHT),
            ('BACKGROUND', (2, 0), (2, 0), WARNING_LIGHT),
            ('BACKGROUND', (3, 0), (3, 0), PRIMARY_LIGHT),
            ('BACKGROUND', (4, 0), (4, 0), DANGER_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ]))
        elements.append(stats_table)

        collection_text = (
            "درصد وصول شارژها: " +
            to_persian(str(round(pct, 1))) + "٪"
        )
        collection_bar = Table(
            [[
                Paragraph(rtl(collection_text),
                    ParagraphStyle('FR_CB', fontName='Vazirmatn-Bold',
                        fontSize=9, alignment=TA_RIGHT, textColor=pct_color)),
                Paragraph(
                    rtl(
                        "تسویه " + to_persian(str(summary.get("paid_count", 0))) +
                        " | ناقص " + to_persian(str(summary.get("partial_count", 0))) +
                        " | پرداخت‌نشده " + to_persian(str(summary.get("unpaid_count", 0)))
                    ),
                    ParagraphStyle('FR_CB2', fontName='Vazirmatn',
                        fontSize=8, alignment=TA_LEFT, textColor=GRAY),
                ),
            ]],
            colWidths=[10 * cm, 8.2 * cm],
        )
        collection_bar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pct_bg),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, pct_color),
        ]))
        elements.append(Spacer(1, 0.15 * cm))
        elements.append(collection_bar)
        elements.append(Spacer(1, 0.3 * cm))

        # ═══ ۲. روند ۶ ماه ═══
        if trend_chart_path and os.path.exists(trend_chart_path):
            elements.append(Paragraph(rtl("روند ۶ ماه اخیر"), section))
            try:
                trend_img = Image(trend_chart_path,
                    width=17 * cm, height=5 * cm)
                elements.append(trend_img)
                elements.append(Spacer(1, 0.3 * cm))
            except Exception as ex:
                print("⚠️ خطای درج نمودار روند: " + str(ex))

        # ═══ Helper: پرداخت‌های یک واحد در یک دوره ═══
        def _payments_for_unit_period(unit_number, period_str):
            if not period_str:
                return []
            try:
                parts = period_str.strip().split()
                if len(parts) < 2:
                    return []
                month_name = parts[0]
                year = int(parts[-1])
                if month_name not in MONTHS:
                    return []
                month_idx = MONTHS.index(month_name)
            except Exception:
                return []

            result = []
            for p in payments:
                if p.get("unit_number") != unit_number:
                    continue
                pd = p.get("payment_date")
                if pd is None:
                    continue
                try:
                    j = jdatetime.date.fromgregorian(date=pd)
                except Exception:
                    continue

                d = j.day
                m = j.month
                y = j.year
                if d >= 29:
                    m += 1
                    if m > 12:
                        m = 1
                        y += 1

                if y == year and m == month_idx:
                    result.append(p)

            def _srt_key(x):
                pdt = x.get("payment_date")
                if pdt is None:
                    return (1, 0)
                return (0, pdt.toordinal())

            result.sort(key=_srt_key)
            return result

        # ═══ ۳. جدول ادغام‌شده شارژ + پرداخت ═══
        if charges:
            elements.append(Paragraph(
                rtl("گزارش شارژ و پرداخت (" +
                    to_persian(str(len(charges))) + " شارژ)"),
                section,
            ))

            from collections import OrderedDict as _OrderedDict
            charges_by_period = _OrderedDict()

            for c in charges:
                period_key = c.get("period", "-") or "-"
                charges_by_period.setdefault(period_key, []).append(c)

            def _period_sort_key(period_str):
                try:
                    parts = period_str.strip().split()
                    y = int(parts[-1])
                    idx = MONTHS.index(parts[0]) if parts[0] in MONTHS else 0
                    return (y, idx)
                except Exception:
                    return (0, 0)

            sorted_periods = sorted(
                charges_by_period.keys(),
                key=_period_sort_key,
                reverse=True,
            )

            ch_header = [
                Paragraph(rtl("وضعیت"), t_th),
                Paragraph(rtl("باقی"), t_th),
                Paragraph(rtl("پرداختی"), t_th),
                Paragraph(rtl("مبلغ"), t_th),
                Paragraph(rtl("تاریخ پرداخت"), t_th),
                Paragraph(rtl("پیگیری"), t_th),
                Paragraph(rtl("ساکن"), t_th),
                Paragraph(rtl("واحد"), t_th),
            ]

            ch_rows = [ch_header]
            style_cmds = [
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]

            row_idx = 1
            for period_key in sorted_periods:
                period_charges = charges_by_period[period_key]

                ch_rows.append([
                    Paragraph(
                        rtl(f"📅 دوره: {period_key}"),
                        ParagraphStyle('FR_PGR', fontName='Vazirmatn-Bold',
                            fontSize=8, alignment=TA_RIGHT,
                            textColor=PRIMARY, leading=10),
                    ),
                    Paragraph("", t_center),
                    Paragraph("", t_center),
                    Paragraph("", t_center),
                    Paragraph("", t_center),
                    Paragraph("", t_center),
                    Paragraph("", t_center),
                    Paragraph(
                        rtl(to_persian(str(len(period_charges))) + " واحد"),
                        ParagraphStyle('FR_PGR2', fontName='Vazirmatn-Bold',
                            fontSize=7, alignment=TA_CENTER,
                            textColor=PRIMARY, leading=9),
                    ),
                ])
                style_cmds.append(
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), PRIMARY_LIGHT)
                )
                style_cmds.append(
                    ('SPAN', (0, row_idx), (6, row_idx))
                )
                row_idx += 1

                def _charge_sort_by_payment(c):
                    unit_num = c.get("unit_number", "")
                    pp = _payments_for_unit_period(unit_num, period_key)
                    if pp:
                        first_pd = pp[0].get("payment_date")
                        if first_pd is not None:
                            try:
                                return (0, first_pd.toordinal(), 0)
                            except Exception:
                                pass
                    try:
                        u = int(str(unit_num) or "0")
                    except Exception:
                        u = 0
                    return (1, 0, u)

                try:
                    period_sorted = sorted(
                        period_charges,
                        key=_charge_sort_by_payment
                    )
                except Exception:
                    period_sorted = period_charges

                for local_i, c in enumerate(period_sorted):
                    st = c.get("status", "-")
                    if st == "تسویه":
                        sc = SUCCESS
                    elif st == "ناقص":
                        sc = WARNING
                    elif st == "پرداخت نشده":
                        sc = DANGER
                    else:
                        sc = GRAY

                    remaining_val = c.get("remaining", 0)
                    rem_color = DANGER if remaining_val > 0 else SUCCESS

                    unit_num = c.get("unit_number", "")
                    period_payments = _payments_for_unit_period(
                        unit_num, period_key
                    )

                    if period_payments:
                        first_p = period_payments[0]
                        pay_date_str = to_jalali_str(
                            first_p.get("payment_date")
                        )
                        codes = []
                        for pp in period_payments:
                            tc = pp.get("tracking_code") or ""
                            if tc:
                                codes.append(to_persian(tc))
                        if codes:
                            tc_str = " • ".join(codes)
                        else:
                            tc_str = "—"
                        if len(period_payments) > 1:
                            pay_date_str += (
                                f" (+{to_persian(str(len(period_payments) - 1))})"
                            )
                    else:
                        pay_date_str = "—"
                        tc_str = "—"

                    ch_rows.append([
                        Paragraph(rtl(st),
                            ParagraphStyle('FR_CS', fontName='Vazirmatn-Bold',
                                fontSize=7, alignment=TA_CENTER, textColor=sc)),
                        Paragraph(rtl(fmt_money(remaining_val, show_unit=False)),
                            ParagraphStyle('FR_CRM', fontName='Vazirmatn-Bold',
                                fontSize=7, alignment=TA_CENTER,
                                textColor=rem_color)),
                        Paragraph(rtl(fmt_money(c.get("paid_amount", 0), show_unit=False)),
                            ParagraphStyle('FR_PA2', fontName='Vazirmatn',
                                fontSize=7, alignment=TA_CENTER, leading=9)),
                        Paragraph(rtl(fmt_money(c.get("amount", 0), show_unit=False)),
                            t_bold_c),
                        Paragraph(rtl(pay_date_str),
                            ParagraphStyle('FR_PD', fontName='Vazirmatn',
                                fontSize=7, alignment=TA_CENTER, leading=9)),
                        Paragraph(rtl(tc_str),
                            ParagraphStyle('FR_TC', fontName='Vazirmatn',
                                fontSize=6, alignment=TA_CENTER,
                                textColor=GRAY, leading=8)),
                        Paragraph(rtl(c.get("resident_name", "-") or "-"),
                            t_bold_c),
                        Paragraph(rtl(to_persian(str(c.get("unit_number", "-")))),
                            t_bold_c),
                    ])

                    if local_i % 2 == 1:
                        style_cmds.append(
                            ('BACKGROUND', (0, row_idx), (-1, row_idx),
                             colors.HexColor("#FAFAFA"))
                        )
                    row_idx += 1

            ch_table = Table(
                ch_rows,
                colWidths=[
                    1.6 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm,
                    2.6 * cm, 2.4 * cm, 3.6 * cm, 1.4 * cm,
                ],
                repeatRows=1,
            )
            ch_table.setStyle(TableStyle(style_cmds))
            elements.append(ch_table)
        else:
            elements.append(Paragraph(rtl("شارژی ثبت نشده است."), t_center))

        elements.append(Spacer(1, 0.3 * cm))

        # ═══ ۴. ریز هزینه‌ها (گروه‌بندی ماه) ═══
        if expenses:
            elements.append(Paragraph(
                rtl("ریز هزینه‌ها (" + to_persian(str(len(expenses))) + " مورد)"),
                section,
            ))

            from collections import OrderedDict as _OrderedDict2
            expenses_by_month = _OrderedDict2()

            for e in expenses:
                ed = e.get("expense_date")
                if ed:
                    try:
                        j = jdatetime.date.fromgregorian(date=ed)
                        month_key = f"{MONTHS[j.month]} {j.year}"
                    except Exception:
                        month_key = "بدون تاریخ"
                else:
                    month_key = "بدون تاریخ"
                expenses_by_month.setdefault(month_key, []).append(e)

            def _month_sort_key(month_str):
                try:
                    parts = month_str.strip().split()
                    y = int(parts[-1])
                    idx = MONTHS.index(parts[0]) if parts[0] in MONTHS else 0
                    return (y, idx)
                except Exception:
                    return (0, 0)

            sorted_months = sorted(
                expenses_by_month.keys(),
                key=_month_sort_key,
                reverse=True,
            )

            exp_header = [
                Paragraph(rtl(f"مبلغ ({currency_label})"), t_th),
                Paragraph(rtl("تاریخ"), t_th),
                Paragraph(rtl("دسته"), t_th),
                Paragraph(rtl("عنوان"), t_th),
                Paragraph(rtl("ردیف"), t_th),
            ]

            exp_rows = [exp_header]
            total_exp_all = 0

            style_exp = [
                ('BACKGROUND', (0, 0), (-1, 0), WARNING),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]

            exp_row_idx = 1
            row_counter = 1

            for month_key in sorted_months:
                month_expenses = expenses_by_month[month_key]

                def _exp_srt(x):
                    ed = x.get("expense_date")
                    if ed is None:
                        return (1, 0)
                    return (0, -ed.toordinal())

                try:
                    month_expenses_sorted = sorted(
                        month_expenses, key=_exp_srt
                    )
                except Exception:
                    month_expenses_sorted = month_expenses

                month_total = sum(
                    (e.get("amount", 0) or 0)
                    for e in month_expenses_sorted
                )
                total_exp_all += month_total

                exp_rows.append([
                    Paragraph(rtl(f"📅 {month_key}"),
                        ParagraphStyle('FR_MH', fontName='Vazirmatn-Bold',
                            fontSize=8, alignment=TA_RIGHT,
                            textColor=WARNING, leading=10)),
                    Paragraph("", t_center),
                    Paragraph("", t_center),
                    Paragraph(
                        rtl(f"{to_persian(str(len(month_expenses_sorted)))} مورد • "
                            f"{fmt_money(month_total, show_unit=False)} {currency_label}"),
                        ParagraphStyle('FR_MH2', fontName='Vazirmatn-Bold',
                            fontSize=7, alignment=TA_CENTER,
                            textColor=WARNING, leading=9),
                    ),
                    Paragraph("", t_center),
                ])
                style_exp.append(
                    ('BACKGROUND', (0, exp_row_idx), (-1, exp_row_idx),
                     WARNING_LIGHT)
                )
                style_exp.append(
                    ('SPAN', (0, exp_row_idx), (2, exp_row_idx))
                )
                style_exp.append(
                    ('SPAN', (3, exp_row_idx), (4, exp_row_idx))
                )
                exp_row_idx += 1

                for local_i, e in enumerate(month_expenses_sorted):
                    amt = e.get("amount", 0) or 0
                    exp_rows.append([
                        Paragraph(rtl(fmt_money(amt, show_unit=False)),
                            ParagraphStyle('FR_EA', fontName='Vazirmatn-Bold',
                                fontSize=7.5, alignment=TA_CENTER,
                                textColor=WARNING)),
                        Paragraph(rtl(to_jalali_str(e.get("expense_date"))),
                            t_center),
                        Paragraph(rtl(e.get("category") or "-"), t_center),
                        Paragraph(rtl(e.get("title") or "-"), t_bold_r),
                        Paragraph(rtl(to_persian(str(row_counter))), t_small),
                    ])
                    row_counter += 1

                    if local_i % 2 == 1:
                        style_exp.append(
                            ('BACKGROUND', (0, exp_row_idx), (-1, exp_row_idx),
                             colors.HexColor("#FAFAFA"))
                        )
                    exp_row_idx += 1

            exp_rows.append([
                Paragraph(rtl(fmt_money(total_exp_all, show_unit=False) + " " + currency_label),
                    ParagraphStyle('FR_ET', fontName='Vazirmatn-Bold',
                        fontSize=8, alignment=TA_CENTER, textColor=PRIMARY)),
                Paragraph("", t_center),
                Paragraph("", t_center),
                Paragraph(rtl("جمع کل"), t_bold_r),
                Paragraph("", t_center),
            ])
            style_exp.append(
                ('BACKGROUND', (0, exp_row_idx), (-1, exp_row_idx), PRIMARY_LIGHT)
            )

            exp_table = Table(
                exp_rows,
                colWidths=[3.0 * cm, 2.8 * cm, 3.2 * cm, 8.2 * cm, 1.4 * cm],
                repeatRows=1,
            )
            exp_table.setStyle(TableStyle(style_exp))
            elements.append(exp_table)
            elements.append(Spacer(1, 0.3 * cm))
        else:
            elements.append(Paragraph(rtl("گزارش هزینه‌ها"), section))
            elements.append(Paragraph(rtl("هزینه‌ای ثبت نشده است."), t_center))
            elements.append(Spacer(1, 0.3 * cm))

        # ═══ ۵. خلاصه هزینه‌ها بر اساس دسته ═══
        if categories:
            elements.append(Paragraph(
                rtl("خلاصه هزینه‌ها بر اساس دسته"),
                section,
            ))

            if expense_chart_path and os.path.exists(expense_chart_path):
                try:
                    exp_img = Image(expense_chart_path,
                        width=6 * cm, height=6 * cm)
                    exp_table_img = Table(
                        [[exp_img, ""]],
                        colWidths=[6 * cm, 12.2 * cm],
                        rowHeights=[6 * cm],
                    )
                    exp_table_img.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    elements.append(exp_table_img)
                    elements.append(Spacer(1, 0.15 * cm))
                except Exception as ex:
                    print("⚠️ خطای درج نمودار هزینه: " + str(ex))

            cat_header = [
                Paragraph(rtl("درصد"), t_th),
                Paragraph(rtl("تعداد"), t_th),
                Paragraph(rtl(f"مبلغ ({currency_label})"), t_th),
                Paragraph(rtl("دسته"), t_th),
            ]

            cat_rows = [cat_header]
            for c in categories:
                pct_str = to_persian(str(round(c.get("percent", 0)))) + "٪"
                cat_rows.append([
                    Paragraph(rtl(pct_str), t_center),
                    Paragraph(rtl(to_persian(str(c.get("count", 0))) + " مورد"),
                        t_center),
                    Paragraph(rtl(fmt_money(c.get("total", 0), show_unit=False)),
                        ParagraphStyle('FR_CA', fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=WARNING)),
                    Paragraph(rtl(c.get("category", "-")), t_bold_c),
                ])

            cat_table = Table(
                cat_rows,
                colWidths=[2.5 * cm, 2.5 * cm, 3.5 * cm, 9.7 * cm],
                repeatRows=1,
            )
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), WARNING),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                    [colors.white, LIGHT_GRAY]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(cat_table)
            elements.append(Spacer(1, 0.3 * cm))

        # ═══ ۶. ریز قبوض ═══
        if bills:
            elements.append(Paragraph(
                rtl("ریز قبوض (" + to_persian(str(len(bills))) + " قبض)"),
                section,
            ))

            def _bill_sort_key(b):
                bt_order = {"آب": 1, "برق": 2, "گاز": 3}
                bt = b.get("bill_type", "سایر")
                bt_idx = bt_order.get(bt, 99)
                period = b.get("period") or ""
                try:
                    parts = period.strip().split()
                    y = int(parts[-1]) if len(parts) >= 2 else 0
                    m_idx = (MONTHS.index(parts[0])
                             if parts[0] in MONTHS else 0)
                except Exception:
                    y = 0
                    m_idx = 0
                return (bt_idx, -y, -m_idx)

            try:
                sorted_bills = sorted(bills, key=_bill_sort_key)
            except Exception:
                sorted_bills = bills

            bl_header = [
                Paragraph(rtl(f"مبلغ ({currency_label})"), t_th),
                Paragraph(rtl("دوره"), t_th),
                Paragraph(rtl("نوع قبض"), t_th),
                Paragraph(rtl("ردیف"), t_th),
            ]

            bl_rows = [bl_header]
            total_bills_display = 0
            type_counts = {}
            type_totals_display = {"آب": 0, "برق": 0, "گاز": 0}

            style_bl = [
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]

            for i, b in enumerate(sorted_bills, 1):
                bt = b.get("bill_type", "سایر")
                period = b.get("period") or "-"
                amount_display = b.get("amount", 0) or 0  # already scaled

                total_bills_display += amount_display
                type_counts[bt] = type_counts.get(bt, 0) + 1
                if bt in type_totals_display:
                    type_totals_display[bt] += amount_display

                if bt == "آب":
                    icon = "💧"
                    bt_color = WATER
                elif bt == "برق":
                    icon = "⚡"
                    bt_color = POWER
                elif bt == "گاز":
                    icon = "🔥"
                    bt_color = GAS
                else:
                    icon = "📋"
                    bt_color = PRIMARY

                bl_rows.append([
                    Paragraph(
                        rtl(fmt_money(amount_display, show_unit=False)),
                        ParagraphStyle('FR_BLA', fontName='Vazirmatn-Bold',
                            fontSize=8, alignment=TA_CENTER,
                            textColor=bt_color, leading=10),
                    ),
                    Paragraph(rtl(period), t_bold_c),
                    Paragraph(
                        rtl(f"{icon} {bt}"),
                        ParagraphStyle('FR_BLT', fontName='Vazirmatn-Bold',
                            fontSize=8, alignment=TA_CENTER,
                            textColor=colors.black, leading=10),
                    ),
                    Paragraph(rtl(to_persian(str(i))), t_small),
                ])

                if i % 2 == 0:
                    style_bl.append(
                        ('BACKGROUND', (0, i), (-1, i),
                         colors.HexColor("#FAFAFA"))
                    )

            total_row_idx = len(bl_rows)
            bl_rows.append([
                Paragraph(
                    rtl(fmt_money(total_bills_display, show_unit=False)),
                    ParagraphStyle('FR_BLTT', fontName='Vazirmatn-Bold',
                        fontSize=9, alignment=TA_CENTER,
                        textColor=PRIMARY, leading=11),
                ),
                Paragraph("", t_center),
                Paragraph(rtl("جمع کل"), t_bold_c),
                Paragraph(
                    rtl(to_persian(str(len(sorted_bills)))),
                    ParagraphStyle('FR_BLC', fontName='Vazirmatn-Bold',
                        fontSize=8, alignment=TA_CENTER,
                        textColor=PRIMARY, leading=10),
                ),
            ])
            style_bl.append(
                ('BACKGROUND', (0, total_row_idx), (-1, total_row_idx),
                 PRIMARY_LIGHT)
            )

            bl_table = Table(
                bl_rows,
                colWidths=[4.0 * cm, 4.5 * cm, 8.2 * cm, 1.5 * cm],
                repeatRows=1,
            )
            bl_table.setStyle(TableStyle(style_bl))
            elements.append(bl_table)

            # خلاصه به تفکیک نوع
            elements.append(Spacer(1, 0.15 * cm))
            type_summary_cells = []
            for bt in ["آب", "برق", "گاز"]:
                if bt not in type_counts:
                    continue
                bt_total = type_totals_display[bt]  # already in display unit

                if bt == "آب":
                    icon = "💧"
                    c_color = WATER
                elif bt == "برق":
                    icon = "⚡"
                    c_color = POWER
                else:
                    icon = "🔥"
                    c_color = GAS

                type_summary_cells.append([
                    Paragraph(
                        rtl(fmt_money(bt_total, show_unit=False) +
                            f" {currency_label}"),
                        ParagraphStyle('FR_TS1', fontName='Vazirmatn-Bold',
                            fontSize=9, alignment=TA_CENTER,
                            textColor=c_color, leading=11),
                    ),
                    Paragraph(
                        rtl(f"{icon} {bt} ({to_persian(str(type_counts[bt]))} قبض)"),
                        ParagraphStyle('FR_TS2', fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=GRAY, leading=9),
                    ),
                ])

            if type_summary_cells:
                n_cols = len(type_summary_cells)
                col_w = 18.2 / n_cols
                ts_table = Table(
                    [type_summary_cells],
                    colWidths=[col_w * cm] * n_cols,
                )
                ts_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
                    ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
                    ('INNERGRID', (0, 0), (-1, -1), 0.3, BORDER),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(ts_table)

            elements.append(Spacer(1, 0.3 * cm))

        # ═══ ۷. رتبه‌بندی نظم پرداخت ═══
        ranking_data = all_payers
        if not ranking_data:
            seen_units = set()
            ranking_data = []
            for p in top_payers:
                u = p.get("unit_number")
                if u not in seen_units:
                    seen_units.add(u)
                    ranking_data.append(p)
            for p in late_payers:
                u = p.get("unit_number")
                if u not in seen_units:
                    seen_units.add(u)
                    ranking_data.append(p)

        if ranking_data:
            elements.append(Paragraph(
                rtl("🏆 رتبه‌بندی نظم پرداخت (" +
                    to_persian(str(len(ranking_data))) + " واحد)"),
                section,
            ))

            guide_table = Table(
                [[Paragraph(
                    rtl("امتیاز پایه هر پرداخت: ۱۰ | زودتر از سررسید: +۱ در روز (تا +۱۰) | "
                        "با تأخیر: −۱ در روز (تا −۱۰) | امتیاز نهایی = میانگین"),
                    ParagraphStyle('FR_RG', fontName='Vazirmatn',
                        fontSize=7, alignment=TA_RIGHT,
                        textColor=GRAY, leading=9),
                )]],
                colWidths=[18.2 * cm],
            )
            guide_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.4, BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(guide_table)
            elements.append(Spacer(1, 0.15 * cm))

            rank_header = [
                Paragraph(rtl("رتبه"), t_th),
                Paragraph(rtl("واحد"), t_th),
                Paragraph(rtl("ساکن"), t_th),
                Paragraph(rtl("پرداخت"), t_th),
                Paragraph(rtl("امتیاز (از ۲۰)"), t_th),
            ]

            rank_rows = [rank_header]
            style_rank = [
                ('BACKGROUND', (0, 0), (-1, 0), SUCCESS),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]

            for idx, u in enumerate(ranking_data, 1):
                score = u.get("avg_score", 0)

                if score >= 15:
                    score_color = SUCCESS
                elif score >= 12:
                    score_color = PRIMARY
                elif score >= 8:
                    score_color = WARNING
                else:
                    score_color = DANGER

                if idx == 1:
                    row_bg = colors.HexColor("#FFF8E1")
                    rank_text_color = GOLD_DARK
                    rank_bg_color = GOLD
                elif idx == 2:
                    row_bg = colors.HexColor("#F5F5F5")
                    rank_text_color = SILVER_DARK
                    rank_bg_color = SILVER
                elif idx == 3:
                    row_bg = colors.HexColor("#FBEEE6")
                    rank_text_color = BRONZE_DARK
                    rank_bg_color = BRONZE
                else:
                    row_bg = (colors.white if idx % 2 == 0
                              else colors.HexColor("#FAFAFA"))
                    rank_text_color = PRIMARY
                    rank_bg_color = None

                rank_style = ParagraphStyle(
                    f'FR_RK_{idx}',
                    fontName='Vazirmatn-Bold',
                    fontSize=11 if idx <= 3 else 9,
                    alignment=TA_CENTER,
                    textColor=rank_text_color,
                    leading=13,
                )

                rank_rows.append([
                    Paragraph(rtl(to_persian(str(idx))), rank_style),
                    Paragraph(
                        rtl(to_persian(str(u.get("unit_number", "-")))),
                        t_bold_c,
                    ),
                    Paragraph(
                        rtl(u.get("resident_name") or "-"),
                        t_bold_c,
                    ),
                    Paragraph(
                        rtl(to_persian(str(u.get("payments_count", 0)))),
                        t_center,
                    ),
                    Paragraph(
                        rtl(to_persian(f"{score:.1f}")),
                        ParagraphStyle(f'FR_SC_{idx}', fontName='Vazirmatn-Bold',
                            fontSize=10, alignment=TA_CENTER,
                            textColor=score_color, leading=12),
                    ),
                ])

                style_rank.append(
                    ('BACKGROUND', (0, idx), (-1, idx), row_bg)
                )

                if rank_bg_color is not None:
                    style_rank.append(
                        ('BACKGROUND', (0, idx), (0, idx), rank_bg_color)
                    )

            rank_table = Table(
                rank_rows,
                colWidths=[1.5 * cm, 1.8 * cm, 8.9 * cm, 2.5 * cm, 3.5 * cm],
                repeatRows=1,
            )
            rank_table.setStyle(TableStyle(style_rank))
            elements.append(rank_table)
            elements.append(Spacer(1, 0.3 * cm))

        # ═══ ۸. لیست بدهکاران ═══
        if debtors:
            elements.append(Paragraph(
                rtl("گزارش بدهکاران (" +
                    to_persian(str(len(debtors))) + " واحد)"),
                section,
            ))

            total_debt = 0
            for x in debtors:
                total_debt += x.get("debt", 0)

            total_debt_table = Table(
                [[
                    Paragraph(rtl(fmt_money(total_debt, show_unit=False) + " " + currency_label),
                        ParagraphStyle('FR_TD', fontName='Vazirmatn-Bold',
                            fontSize=11, alignment=TA_CENTER,
                            textColor=DANGER)),
                    Paragraph(rtl("کل بدهی:"),
                        ParagraphStyle('FR_TDL', fontName='Vazirmatn-Bold',
                            fontSize=9, alignment=TA_CENTER,
                            textColor=DANGER)),
                ]],
                colWidths=[6 * cm, 12.2 * cm],
            )
            total_debt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), DANGER_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 0.5, DANGER),
            ]))
            elements.append(total_debt_table)
            elements.append(Spacer(1, 0.15 * cm))

            range_style = ParagraphStyle(
                'FR_DR', fontName='Vazirmatn-Bold',
                fontSize=7.5, alignment=TA_CENTER,
                textColor=DANGER, leading=9,
            )
            count_style = ParagraphStyle(
                'FR_DC', fontName='Vazirmatn',
                fontSize=6, alignment=TA_CENTER,
                textColor=GRAY, leading=8,
            )

            deb_header = [
                Paragraph(rtl("بازه بدهی"), t_th),
                Paragraph(rtl("موبایل"), t_th),
                Paragraph(rtl(f"بدهی ({currency_label})"), t_th),
                Paragraph(rtl("ساکن"), t_th),
                Paragraph(rtl("واحد"), t_th),
            ]

            deb_rows = [deb_header]
            for d in debtors:
                periods_cnt = d.get(
                    "periods_count", len(d.get("periods", []))
                )
                first_p = d.get("first_period") or "-"
                last_p = d.get("last_period") or "-"

                if periods_cnt <= 1 or first_p == last_p:
                    date_range = "از " + str(first_p)
                else:
                    date_range = "از " + str(first_p) + " تا " + str(last_p)

                periods_label = to_persian(str(periods_cnt)) + " دوره"

                range_cell = [
                    Paragraph(rtl(date_range), range_style),
                    Paragraph(rtl(periods_label), count_style),
                ]

                deb_rows.append([
                    range_cell,
                    Paragraph(rtl(to_persian(d.get("phone") or "-")), t_center),
                    Paragraph(rtl(fmt_money(d.get("debt", 0), show_unit=False)),
                        ParagraphStyle('FR_DB', fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=DANGER)),
                    Paragraph(rtl(d.get("resident_name") or "-"), t_bold_c),
                    Paragraph(rtl(to_persian(str(d.get("unit_number", "-")))),
                        t_bold_c),
                ])

            deb_table = Table(
                deb_rows,
                colWidths=[4.0 * cm, 2.5 * cm, 2.8 * cm, 5.0 * cm, 3.9 * cm],
                repeatRows=1,
            )
            deb_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), DANGER),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                    [colors.white, DANGER_LIGHT]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(deb_table)
            elements.append(Spacer(1, 0.3 * cm))

        # ═══ اطلاعات بانکی ═══
        if bank_info and (bank_info.get("card") or bank_info.get("sheba")):
            elements.append(Paragraph(rtl("اطلاعات واریز"), section))

            bank_rows = []
            if bank_info.get("owner"):
                bank_rows.append([
                    Paragraph(rtl(bank_info["owner"]), t_bold_r),
                    Paragraph(rtl("صاحب حساب:"), t_small),
                ])
            if bank_info.get("card"):
                bank_rows.append([
                    Paragraph(rtl(to_persian(bank_info["card"])), t_bold_r),
                    Paragraph(rtl("شماره کارت:"), t_small),
                ])
            if bank_info.get("sheba"):
                bank_rows.append([
                    Paragraph(rtl(to_persian(bank_info["sheba"])), t_bold_r),
                    Paragraph(rtl("شماره شبا:"), t_small),
                ])

            if bank_rows:
                bank_table = Table(bank_rows, colWidths=[14.5 * cm, 3.7 * cm])
                bank_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), SUCCESS_LIGHT),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('BOX', (0, 0), (-1, -1), 0.5,
                     colors.HexColor("#A5D6A7")),
                    ('INNERGRID', (0, 0), (-1, -1), 0.3,
                     colors.HexColor("#A5D6A7")),
                ]))
                elements.append(bank_table)
                elements.append(Spacer(1, 0.3 * cm))

        # ═══ فوتر ═══
        elements.append(Spacer(1, 0.3 * cm))
        footer_line = Table([[""]], colWidths=[18.2 * cm],
            rowHeights=[0.02 * cm])
        footer_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ]))
        elements.append(footer_line)
        elements.append(Spacer(1, 0.1 * cm))

        footer_text = (
            "© " + (building_name or "ساختمان") +
            " - تولید شده توسط سیستم مدیریت ساختمان"
        )
        elements.append(Paragraph(rtl(footer_text),
            ParagraphStyle('FR_FT', fontName='Vazirmatn',
                fontSize=7, alignment=TA_CENTER, textColor=GRAY)))

        doc.build(elements)

        return {
            "success": True,
            "path": output_path,
            "message": "PDF با موفقیت ساخته شد.",
        }

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "path": None,
            "message": f"خطای PDF: {ex}",
        }

def generate_month_invoices_pdf(
    month_label,
    expenses,
    payments=None,
    building_name="",
    building_info=None,
    output_path=None,
    currency_label="ریال",
    logo_path=None,
    theme_color="#1565C0",
    include_receipts=False,
):
    """چاپ فاکتورها به صورت گرید ۲×۲ (۴ فاکتور در هر A4)"""
    if not HAS_REPORTLAB:
        return {"success": False, "path": None, "message": "reportlab نصب نیست."}

    try:
        register_fonts()
        import jdatetime

        if not output_path:
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_month = str(month_label).replace(" ", "_")
            suffix = "invoices_receipts" if include_receipts else "invoices"
            filename = f"{suffix}_{safe_month}_{ts}.pdf"
            output_path = os.path.join(reports_dir, filename)

        PRIMARY = hex_to_rgb_tuple(theme_color)
        PRIMARY_LIGHT = lighten_color(theme_color, 0.85)
        SUCCESS = colors.HexColor("#2E7D32")
        SUCCESS_LIGHT = colors.HexColor("#E8F5E9")
        WARNING = colors.HexColor("#EF6C00")
        WARNING_LIGHT = colors.HexColor("#FFF3E0")
        GRAY = colors.HexColor("#666666")
        LIGHT_GRAY = colors.HexColor("#F5F5F5")
        BORDER = colors.HexColor("#E0E0E0")

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=0.6 * cm, leftMargin=0.6 * cm,
            topMargin=0.5 * cm, bottomMargin=0.5 * cm,
        )

        elements = []

        t_title = ParagraphStyle('minv_t', fontName='Vazirmatn-Bold',
            fontSize=9, alignment=TA_CENTER, leading=11,
            textColor=colors.black)
        t_meta = ParagraphStyle('minv_m', fontName='Vazirmatn',
            fontSize=7, alignment=TA_CENTER, leading=9,
            textColor=GRAY)
        t_amt = ParagraphStyle('minv_amt', fontName='Vazirmatn-Bold',
            fontSize=9, alignment=TA_CENTER, leading=11,
            textColor=WARNING)
        t_header = ParagraphStyle('minv_h', fontName='Vazirmatn-Bold',
            fontSize=11, alignment=TA_CENTER,
            textColor=colors.white, leading=14)

        try:
            from PIL import Image as PILImage
        except Exception:
            PILImage = None

        # ─── جمع‌آوری آیتم‌ها ───
        all_items = []
        for e in (expenses or []):
            if e.get("invoice_image") and os.path.exists(e["invoice_image"]):
                all_items.append({"type": "invoice", "data": e})

        if include_receipts and payments:
            for p in payments:
                if p.get("receipt_image") and os.path.exists(p["receipt_image"]):
                    all_items.append({"type": "receipt", "data": p})

        if not all_items:
            elements.append(Paragraph(
                rtl("هیچ فاکتوری برای این ماه ثبت نشده."),
                ParagraphStyle('minv_empty', fontName='Vazirmatn',
                    fontSize=12, alignment=TA_CENTER, textColor=GRAY),
            ))
            doc.build(elements)
            return {"success": True, "path": output_path,
                    "message": "PDF خالی ساخته شد."}

        # ─── ابعاد سلول (A4 = 21×29.7، با حاشیه 0.6) ───
        usable_w = 19.8 * cm
        cell_w = usable_w / 2 - 0.1 * cm   # ~9.8 cm
        cell_h = 13.4 * cm
        header_h = 1.5 * cm
        img_h_max = cell_h - header_h - 0.15 * cm

        def make_cell(item):
            """یک سلول گرید"""
            if item["type"] == "invoice":
                exp = item["data"]
                img_path = exp["invoice_image"]
                title = str(exp.get("title") or "فاکتور")
                amount = exp.get("amount", 0) or 0
                category = exp.get("category") or "-"
                icon = "🧾"
                badge = WARNING
                date_src = exp.get("expense_date")
            else:
                pay = item["data"]
                img_path = pay["receipt_image"]
                unit_num = to_persian(str(pay.get("unit_number", "-")))
                title = f"فیش واحد {unit_num}"
                amount = pay.get("amount", 0) or 0
                category = pay.get("payment_method") or "-"
                icon = "💳"
                badge = SUCCESS
                date_src = pay.get("payment_date")

            # تاریخ
            date_str = "-"
            if date_src:
                try:
                    j = jdatetime.date.fromgregorian(date=date_src)
                    date_str = to_persian(
                        f"{j.year}/{j.month:02d}/{j.day:02d}"
                    )
                except Exception:
                    pass

            # aspect ratio
            aspect = 1.0
            if PILImage is not None:
                try:
                    with PILImage.open(img_path) as im:
                        w_px, h_px = im.size
                    if h_px:
                        aspect = w_px / h_px
                except Exception:
                    pass

            max_w = cell_w - 0.3 * cm
            max_h = img_h_max
            img_w = max_w
            img_h = img_w / aspect if aspect else max_w
            if img_h > max_h:
                img_h = max_h
                img_w = img_h * aspect

            # ─── هدر سلول ───
            head_para = Paragraph(
                rtl(f"{icon} {title[:40]}"),
                t_title,
            )
            amount_para = Paragraph(
                rtl(fmt_money(amount, show_unit=False) + " " + currency_label),
                t_amt,
            )
            meta_para = Paragraph(
                rtl(f"📅 {date_str} • 🏷️ {category}"),
                t_meta,
            )

            head_tbl = Table(
                [[head_para], [amount_para], [meta_para]],
                colWidths=[cell_w],
            )
            head_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
                ('BOX', (0, 0), (-1, -1), 0.4, BORDER),
                ('LINEBELOW', (0, 0), (0, 0), 0.3, badge),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))

            # ─── تصویر ───
            img_widget = Image(img_path, width=img_w, height=img_h)

            img_cell = Table(
                [[img_widget]],
                colWidths=[cell_w],
                rowHeights=[img_h_max],
            )
            img_cell.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.4, BORDER),
                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))

            # ─── ترکیب سلول ───
            cell = Table(
                [[head_tbl], [img_cell]],
                colWidths=[cell_w],
            )
            cell.setStyle(TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            return cell

        # ─── صفحات ۴ تایی ───
        PER_PAGE = 4

        def empty_cell():
            return Table([[""]], colWidths=[cell_w], rowHeights=[cell_h],
                style=TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0.3, BORDER),
                ]))

        total_pages = (len(all_items) + PER_PAGE - 1) // PER_PAGE

        for page_i in range(total_pages):
            batch = all_items[page_i * PER_PAGE: (page_i + 1) * PER_PAGE]

            # هدر صفحه
            hdr = Table(
                [[Paragraph(
                    rtl(f"🧾 اسناد {month_label} — "
                        f"صفحه {to_persian(str(page_i + 1))} از "
                        f"{to_persian(str(total_pages))} — "
                        f"{building_name or 'ساختمان'}"),
                    t_header)]],
                colWidths=[usable_w],
                rowHeights=[0.9 * cm],
            )
            hdr.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(hdr)
            elements.append(Spacer(1, 0.15 * cm))

            # ساخت سلول‌ها
            cells = [make_cell(it) for it in batch]
            while len(cells) < PER_PAGE:
                cells.append(empty_cell())

            # گرید ۲×۲
            grid = Table(
                [
                    [cells[0], cells[1]],
                    [cells[2], cells[3]],
                ],
                colWidths=[cell_w, cell_w],
                rowHeights=[cell_h, cell_h],
            )
            grid.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            elements.append(grid)

            if page_i < total_pages - 1:
                elements.append(PageBreak())

        doc.build(elements)
        return {"success": True, "path": output_path,
                "message": "✅ PDF فاکتورها ساخته شد."}

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {"success": False, "path": None, "message": f"خطای PDF: {ex}"}

def generate_month_expenses_pdf(
    month_label,
    expenses,
    building_name="",
    building_info=None,
    output_path=None,
    currency_label="ریال",
    logo_path=None,
    theme_color="#1565C0",
):
    """گزارش هزینه‌های یک ماه با جزئیات کامل"""
    if not HAS_REPORTLAB:
        return {"success": False, "path": None, "message": "reportlab نصب نیست."}

    try:
        register_fonts()
        import jdatetime

        if not output_path:
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_month = str(month_label).replace(" ", "_")
            filename = f"expenses_{safe_month}_{ts}.pdf"
            output_path = os.path.join(reports_dir, filename)

        PRIMARY = hex_to_rgb_tuple(theme_color)
        PRIMARY_LIGHT = lighten_color(theme_color, 0.85)
        SUCCESS = colors.HexColor("#2E7D32")
        SUCCESS_LIGHT = colors.HexColor("#E8F5E9")
        WARNING = colors.HexColor("#EF6C00")
        WARNING_LIGHT = colors.HexColor("#FFF3E0")
        GRAY = colors.HexColor("#666666")
        LIGHT_GRAY = colors.HexColor("#F5F5F5")
        BORDER = colors.HexColor("#E0E0E0")

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=0.8 * cm, leftMargin=0.8 * cm,
            topMargin=0.6 * cm, bottomMargin=0.6 * cm,
        )

        elements = []

        t_th = ParagraphStyle('me_th', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_CENTER,
            textColor=colors.white, leading=10)
        t_c = ParagraphStyle('me_c', fontName='Vazirmatn',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_b = ParagraphStyle('me_b', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_amt = ParagraphStyle('me_amt', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_CENTER,
            textColor=WARNING, leading=10)
        section = ParagraphStyle('me_sec', fontName='Vazirmatn-Bold',
            fontSize=11, alignment=TA_RIGHT,
            textColor=PRIMARY, spaceAfter=4, spaceBefore=6)

        # ─── هدر ───
        header_table = Table(
            [[
                Paragraph(rtl(get_jalali_date()), ParagraphStyle(
                    'me_date', fontName='Vazirmatn', fontSize=8,
                    alignment=TA_LEFT, textColor=colors.white)),
                Paragraph(rtl(f"گزارش هزینه‌های {month_label}"),
                    ParagraphStyle('me_t', fontName='Vazirmatn-Bold',
                        fontSize=13, alignment=TA_CENTER,
                        textColor=colors.white, leading=16)),
                Paragraph(rtl(building_name or "ساختمان"),
                    ParagraphStyle('me_bn', fontName='Vazirmatn',
                        fontSize=8, alignment=TA_RIGHT,
                        textColor=colors.white)),
            ]],
            colWidths=[4 * cm, 10.2 * cm, 4 * cm],
            rowHeights=[1.3 * cm],
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.25 * cm))

        # ─── خلاصه ───
        total = sum((e.get("amount", 0) or 0) for e in expenses)
        count = len(expenses)

        cats = {}
        for e in expenses:
            c = e.get("category", "سایر")
            cats[c] = cats.get(c, 0) + (e.get("amount", 0) or 0)

        summary_table = Table(
            [[
                [Paragraph(rtl("تعداد هزینه‌ها"),
                    ParagraphStyle('sc_l', fontName='Vazirmatn', fontSize=8,
                        alignment=TA_CENTER, textColor=GRAY)),
                 Paragraph(rtl(to_persian(str(count))),
                    ParagraphStyle('sc_v', fontName='Vazirmatn-Bold',
                        fontSize=14, alignment=TA_CENTER,
                        textColor=PRIMARY))],
                [Paragraph(rtl("جمع کل"),
                    ParagraphStyle('sc_l2', fontName='Vazirmatn', fontSize=8,
                        alignment=TA_CENTER, textColor=GRAY)),
                 Paragraph(rtl(fmt_money(total, show_unit=False)),
                    ParagraphStyle('sc_v2', fontName='Vazirmatn-Bold',
                        fontSize=14, alignment=TA_CENTER,
                        textColor=WARNING))],
                [Paragraph(rtl("تعداد دسته"),
                    ParagraphStyle('sc_l3', fontName='Vazirmatn', fontSize=8,
                        alignment=TA_CENTER, textColor=GRAY)),
                 Paragraph(rtl(to_persian(str(len(cats)))),
                    ParagraphStyle('sc_v3', fontName='Vazirmatn-Bold',
                        fontSize=14, alignment=TA_CENTER,
                        textColor=SUCCESS))],
            ]],
            colWidths=[6.06 * cm, 6.06 * cm, 6.08 * cm],
        )
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * cm))

        # ─── جدول هزینه‌ها ───
        elements.append(Paragraph(
            rtl(f"لیست هزینه‌ها ({to_persian(str(count))} مورد)"),
            section,
        ))

        if expenses:
            rows = [[
                Paragraph(rtl("ردیف"), t_th),
                Paragraph(rtl("مبلغ"), t_th),
                Paragraph(rtl("تاریخ"), t_th),
                Paragraph(rtl("دسته"), t_th),
                Paragraph(rtl("عنوان"), t_th),
            ]]
            for i, e in enumerate(expenses, 1):
                date_str = "-"
                if e.get("expense_date"):
                    try:
                        j = jdatetime.date.fromgregorian(date=e["expense_date"])
                        date_str = to_persian(f"{j.year}/{j.month:02d}/{j.day:02d}")
                    except Exception:
                        pass
                rows.append([
                    Paragraph(rtl(to_persian(str(i))), t_c),
                    Paragraph(rtl(fmt_money(e.get("amount", 0), show_unit=False)), t_amt),
                    Paragraph(rtl(date_str), t_c),
                    Paragraph(rtl(e.get("category") or "-"), t_c),
                    Paragraph(rtl(e.get("title") or "-"), t_b),
                ])

            tbl = Table(rows,
                colWidths=[1.2 * cm, 3.2 * cm, 3 * cm, 3 * cm, 8.8 * cm],
                repeatRows=1,
            )
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                    [colors.white, LIGHT_GRAY]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(tbl)
        else:
            elements.append(Paragraph(rtl("هزینه‌ای ثبت نشده."), t_c))

        # ─── جمع بر اساس دسته ───
        if cats:
            elements.append(Spacer(1, 0.3 * cm))
            elements.append(Paragraph(rtl("جمع بر اساس دسته"), section))

            cat_rows = [[
                Paragraph(rtl("درصد"), t_th),
                Paragraph(rtl("مبلغ"), t_th),
                Paragraph(rtl("دسته"), t_th),
            ]]
            total_c = sum(cats.values()) or 1
            for cat, amt in sorted(cats.items(), key=lambda x: -x[1]):
                pct = (amt / total_c) * 100
                cat_rows.append([
                    Paragraph(rtl(to_persian(f"{pct:.0f}") + "٪"), t_c),
                    Paragraph(rtl(fmt_money(amt, show_unit=False)), t_amt),
                    Paragraph(rtl(cat), t_b),
                ])
            cat_tbl = Table(cat_rows,
                colWidths=[3 * cm, 4 * cm, 12.2 * cm],
                repeatRows=1,
            )
            cat_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), WARNING),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                    [colors.white, WARNING_LIGHT]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(cat_tbl)

        # ─── فوتر ───
        elements.append(Spacer(1, 0.3 * cm))
        foot = Table([[""]], colWidths=[18.2 * cm], rowHeights=[0.02 * cm])
        foot.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), PRIMARY)]))
        elements.append(foot)
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(Paragraph(
            rtl("© " + (building_name or "ساختمان") +
                " - سیستم مدیریت ساختمان"),
            ParagraphStyle('mf', fontName='Vazirmatn', fontSize=7,
                alignment=TA_CENTER, textColor=GRAY),
        ))

        doc.build(elements)
        return {"success": True, "path": output_path,
                "message": "✅ PDF گزارش هزینه‌ها ساخته شد."}

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {"success": False, "path": None, "message": f"خطای PDF: {ex}"}
# ═══════════ تابع سوم: PDF گزارش یک دوره شارژ (نسخه فشرده) ═══════════

def generate_period_report_pdf(
    report_data,
    building_name="",
    building_info=None,
    bank_info=None,
    output_path=None,
    currency_label="ریال",
    logo_path=None,
    theme_color="#1565C0",
):
    """ساخت PDF فشرده و کامل از یک دوره شارژ (با ستون فیش)"""
    if not HAS_REPORTLAB:
        return {
            "success": False,
            "path": None,
            "message": "reportlab نصب نیست.",
        }

    try:
        register_fonts()

        period = report_data.get("period", "-")
        charges = report_data.get("charges", [])
        payments = report_data.get("payments", [])
        summary = report_data.get("summary", {})

        # ─── مسیر خروجی ─────
        if not output_path:
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_period = period.replace(" ", "_").replace("/", "-")
            filename = f"period_{safe_period}_{timestamp}.pdf"
            output_path = os.path.join(reports_dir, filename)

        # ─── رنگ‌ها ─────
        PRIMARY = hex_to_rgb_tuple(theme_color)
        PRIMARY_LIGHT = lighten_color(theme_color, 0.85)
        PRIMARY_LIGHTER = lighten_color(theme_color, 0.95)
        SUCCESS = colors.HexColor("#2E7D32")
        SUCCESS_LIGHT = colors.HexColor("#E8F5E9")
        WARNING = colors.HexColor("#EF6C00")
        WARNING_LIGHT = colors.HexColor("#FFF3E0")
        DANGER = colors.HexColor("#C62828")
        DANGER_LIGHT = colors.HexColor("#FFEBEE")
        GRAY = colors.HexColor("#666666")
        DARK_GRAY = colors.HexColor("#333333")
        LIGHT_GRAY = colors.HexColor("#F5F5F5")
        BORDER = colors.HexColor("#E0E0E0")

        S = SUCCESS
        W = WARNING
        D = DANGER

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.8 * cm,
            leftMargin=0.8 * cm,
            topMargin=0.6 * cm,
            bottomMargin=0.6 * cm,
        )

        elements = []

        # ─── استایل‌های فشرده ─────
        t_right = ParagraphStyle('TR', fontName='Vazirmatn',
            fontSize=8, alignment=TA_RIGHT, leading=10)
        t_center = ParagraphStyle('TC', fontName='Vazirmatn',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_bold_r = ParagraphStyle('TBR', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_RIGHT, leading=10)
        t_bold_c = ParagraphStyle('TBC', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_th = ParagraphStyle('TTH', fontName='Vazirmatn-Bold',
            fontSize=7.5, alignment=TA_CENTER,
            textColor=colors.white, leading=9)
        t_small = ParagraphStyle('TSM', fontName='Vazirmatn',
            fontSize=6.5, alignment=TA_CENTER,
            textColor=GRAY, leading=8)
        section = ParagraphStyle('SEC', fontName='Vazirmatn-Bold',
            fontSize=10, alignment=TA_RIGHT,
            textColor=PRIMARY, spaceAfter=4, spaceBefore=6)

        # ─── هدر ─────
        date_str = rtl(get_jalali_date())
        left_col = [Paragraph(date_str, ParagraphStyle('DS',
            fontName='Vazirmatn', fontSize=8,
            alignment=TA_LEFT, textColor=colors.white))]

        center_col = [
            Paragraph(rtl(building_name or "ساختمان"),
                ParagraphStyle('BT', fontName='Vazirmatn-Bold',
                    fontSize=14, alignment=TA_CENTER,
                    textColor=colors.white, leading=16)),
            Paragraph(rtl(f"گزارش شارژ دوره {period}"),
                ParagraphStyle('ST', fontName='Vazirmatn',
                    fontSize=9, alignment=TA_CENTER,
                    textColor=colors.white)),
        ]

        right_col = []
        if logo_path and os.path.exists(logo_path):
            try:
                right_col.append(Image(logo_path,
                    width=1.6 * cm, height=1.6 * cm))
            except Exception:
                right_col.append(Paragraph("🏢", t_bold_c))
        else:
            right_col.append(Paragraph("🏢",
                ParagraphStyle('IC', fontName='Vazirmatn',
                    fontSize=28, alignment=TA_CENTER,
                    textColor=colors.white)))

        header_table = Table(
            [[left_col, center_col, right_col]],
            colWidths=[2.5 * cm, 13.2 * cm, 2.5 * cm],
            rowHeights=[1.6 * cm],
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2 * cm))

        # ─── اطلاعات ساختمان ─────
        if building_info:
            binfo = Table(
                [[
                    Paragraph(rtl(building_info.get("address", "-") or "-"), t_bold_r),
                    Paragraph(rtl("آدرس:"), t_small),
                    Paragraph(rtl(to_persian(str(building_info.get("floors", 0)))), t_bold_c),
                    Paragraph(rtl("طبقه"), t_small),
                    Paragraph(rtl(to_persian(str(building_info.get("total_units", 0)))), t_bold_c),
                    Paragraph(rtl("واحد"), t_small),
                ]],
                colWidths=[7.6 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm],
            )
            binfo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_LIGHTER),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            elements.append(binfo)
            elements.append(Spacer(1, 0.25 * cm))

        # ═══════════════════════════════════
        # ═══ خلاصه‌ی مالی ═══
        # ═══════════════════════════════════
        elements.append(Paragraph(rtl("خلاصه‌ی مالی دوره"), section))

        pct = summary.get("collection_percent", 0)
        pct_color = SUCCESS if pct >= 90 else WARNING if pct >= 50 else DANGER
        pct_bg = (SUCCESS_LIGHT if pct >= 90
                  else WARNING_LIGHT if pct >= 50
                  else DANGER_LIGHT)

        def s_cell(title, value, color, unit_str=None):
            if unit_str:
                txt = f"{to_persian(value)} {unit_str}"
            else:
                txt = to_persian(value)
            return [
                Paragraph(rtl(title), t_small),
                Paragraph(rtl(txt),
                    ParagraphStyle('SV', fontName='Vazirmatn-Bold',
                        fontSize=10, alignment=TA_CENTER,
                        textColor=color, leading=12)),
            ]

        stats_table = Table(
            [[
                s_cell("کل شارژ",
                       fmt_money(summary.get("total_amount", 0), show_unit=False),
                       PRIMARY, currency_label),
                s_cell("دریافتی",
                       fmt_money(summary.get("total_paid", 0), show_unit=False),
                       SUCCESS, currency_label),
                s_cell("معوق",
                       fmt_money(summary.get("total_remaining", 0), show_unit=False),
                       DANGER, currency_label),
                s_cell("تسویه",
                       f'{summary.get("paid_count", 0)} از {summary.get("units_count", 0)}',
                       S),
                s_cell("ناقص", str(summary.get("partial_count", 0)), W),
                s_cell("پرداخت‌نشده", str(summary.get("unpaid_count", 0)), D),
                s_cell("درصد وصول", f'{pct:.1f}٪', pct_color),
            ]],
            colWidths=[3.4 * cm, 2.9 * cm, 2.9 * cm, 2.0 * cm, 1.4 * cm, 1.7 * cm, 2.3 * cm],
        )
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), PRIMARY_LIGHT),
            ('BACKGROUND', (1, 0), (1, 0), SUCCESS_LIGHT),
            ('BACKGROUND', (2, 0), (2, 0), DANGER_LIGHT),
            ('BACKGROUND', (3, 0), (3, 0), SUCCESS_LIGHT),
            ('BACKGROUND', (4, 0), (4, 0), WARNING_LIGHT),
            ('BACKGROUND', (5, 0), (5, 0), DANGER_LIGHT),
            ('BACKGROUND', (6, 0), (6, 0), pct_bg),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3 * cm))

        # ═══════════════════════════════════
        # ═══ جدول شارژهای واحدها ═══
        # ═══════════════════════════════════
        elements.append(Paragraph(
            rtl(f"📋 شارژ واحدها ({to_persian(str(len(charges)))} واحد)"),
            section,
        ))

        if charges:
            header_row = [
                Paragraph(rtl("وضعیت"), t_th),
                Paragraph(rtl("باقی"), t_th),
                Paragraph(rtl("پرداختی"), t_th),
                Paragraph(rtl("مبلغ کل"), t_th),
                Paragraph(rtl("ساکن"), t_th),
                Paragraph(rtl("واحد"), t_th),
                Paragraph(rtl("ردیف"), t_th),
            ]

            charge_rows = [header_row]

            for idx, c in enumerate(charges, 1):
                status_color = {
                    "تسویه": SUCCESS,
                    "ناقص": WARNING,
                    "پرداخت نشده": DANGER,
                }.get(c["status"], GRAY)

                charge_rows.append([
                    Paragraph(rtl(c["status"] or "-"),
                        ParagraphStyle('CS', fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=status_color)),
                    Paragraph(rtl(fmt_money(c["remaining"], show_unit=False)),
                        ParagraphStyle('CRM', fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=DANGER if c["remaining"] > 0 else SUCCESS)),
                    Paragraph(rtl(fmt_money(c["paid_amount"], show_unit=False)), t_center),
                    Paragraph(rtl(fmt_money(c["amount"], show_unit=False)), t_bold_c),
                    Paragraph(rtl(c["resident_name"] or "-"), t_bold_c),
                    Paragraph(rtl(to_persian(str(c["unit_number"]))), t_bold_c),
                    Paragraph(rtl(to_persian(str(idx))), t_small),
                ])

            charges_table = Table(
                charge_rows,
                colWidths=[1.9 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 3.8 * cm, 1.6 * cm, 1.0 * cm],
                repeatRows=1,
            )
            charges_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(charges_table)
        else:
            elements.append(Paragraph(rtl("شارژی ثبت نشده است."), t_center))

        elements.append(Spacer(1, 0.3 * cm))

        # ═══════════════════════════════════
        # ═══ پرداخت‌ها (با ستون فیش) ═══
        # ═══════════════════════════════════
        if payments:
            elements.append(Paragraph(
                rtl(f"💳 پرداخت‌ها ({to_persian(str(len(payments)))} مورد)"),
                section,
            ))

            pay_header = [
                Paragraph(rtl("فیش"), t_th),
                Paragraph(rtl("توضیحات"), t_th),
                Paragraph(rtl("پیگیری"), t_th),
                Paragraph(rtl("روش"), t_th),
                Paragraph(rtl("تاریخ"), t_th),
                Paragraph(rtl("مبلغ"), t_th),
                Paragraph(rtl("واحد"), t_th),
            ]

            pay_rows = [pay_header]

            total_paid_amount = 0
            for p in payments:
                total_paid_amount += p.get("amount", 0)

                # ⭐ سلول فیش: تصویر بندانگشتی
                receipt_path = p.get("receipt_image") or ""
                if receipt_path and os.path.exists(receipt_path):
                    try:
                        # ⭐ سایز بزرگ‌تر
                        MAX_DIM = 2.5 * cm  # قبلاً 1.3 بود
                        img_w = MAX_DIM
                        img_h = MAX_DIM
                        try:
                            from PIL import Image as PILImage
                            with PILImage.open(receipt_path) as im:
                                w_px, h_px = im.size
                            if h_px:
                                ratio = w_px / h_px
                                if ratio > 1:
                                    img_h = img_w / ratio
                                else:
                                    img_w = img_h * ratio
                        except Exception:
                            pass

                        receipt_cell = Image(
                            receipt_path,
                            width=img_w,
                            height=img_h,
                        )
                    except Exception as ex:
                        print(f"⚠️ خطای thumbnail: {ex}")
                        receipt_cell = Paragraph(rtl("—"), t_center)
                else:
                    receipt_cell = Paragraph(rtl("—"), t_center)

                pay_rows.append([
                    receipt_cell,
                    Paragraph(rtl(p.get("description") or "-"), t_small),
                    Paragraph(rtl(to_persian(p.get("tracking_code") or "-")), t_center),
                    Paragraph(rtl(p.get("payment_method") or "-"), t_center),
                    Paragraph(rtl(to_jalali_str(p.get("payment_date"))), t_bold_c),
                    Paragraph(rtl(fmt_money(p.get("amount", 0), show_unit=False)),
                        ParagraphStyle('PA', fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=SUCCESS)),
                    Paragraph(rtl(to_persian(str(p.get("unit_number", "-")))),
                        t_bold_c),
                ])

            # ─── ردیف جمع کل ───
            pay_rows.append([
                Paragraph("", t_center),
                Paragraph(rtl("جمع کل"), t_bold_c),
                Paragraph("", t_center),
                Paragraph("", t_center),
                Paragraph("", t_center),
                Paragraph(rtl(fmt_money(total_paid_amount, show_unit=False)),
                    ParagraphStyle('PT', fontName='Vazirmatn-Bold',
                        fontSize=8, alignment=TA_CENTER,
                        textColor=PRIMARY)),
                Paragraph("", t_center),
            ])

            pay_table = Table(
                pay_rows,
                colWidths=[
                    3.0 * cm,  # فیش (بزرگ‌تر)
                    4.5 * cm,  # توضیحات
                    2.7 * cm,  # پیگیری
                    1.8 * cm,  # روش
                    2.5 * cm,  # تاریخ
                    2.5 * cm,  # مبلغ
                    1.2 * cm,  # واحد
                ],
                repeatRows=1,
            )
            pay_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), SUCCESS),
                ('BACKGROUND', (0, len(pay_rows) - 1), (-1, len(pay_rows) - 1), PRIMARY_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, len(pay_rows) - 2),
                    [colors.white, LIGHT_GRAY]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(pay_table)
            elements.append(Spacer(1, 0.25 * cm))

        # ═══════════════════════════════════
        # ═══ اطلاعات بانکی + امضا ═══
        # ═══════════════════════════════════
        has_bank = bank_info and (bank_info.get("card") or bank_info.get("sheba"))

        if has_bank:
            elements.append(Paragraph(rtl("اطلاعات واریز و امضا"), section))

            bank_rows = []
            if bank_info.get("owner"):
                bank_rows.append([
                    Paragraph(rtl(bank_info["owner"]), t_bold_r),
                    Paragraph(rtl("صاحب حساب:"), t_small),
                ])
            if bank_info.get("card"):
                bank_rows.append([
                    Paragraph(rtl(to_persian(bank_info["card"])), t_bold_r),
                    Paragraph(rtl("شماره کارت:"), t_small),
                ])
            if bank_info.get("sheba"):
                bank_rows.append([
                    Paragraph(rtl(to_persian(bank_info["sheba"])), t_bold_r),
                    Paragraph(rtl("شماره شبا:"), t_small),
                ])

            bank_table = Table(bank_rows, colWidths=[9.5 * cm, 2.7 * cm])
            bank_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), SUCCESS_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#A5D6A7")),
                ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor("#A5D6A7")),
            ]))
            elements.append(bank_table)

        # ─── امضاها ─────
        elements.append(Spacer(1, 0.6 * cm))

        signature_data = [
            [
                Paragraph(rtl("امضای ساکن"), t_bold_c),
                "",
                Paragraph(rtl("مهر و امضای مدیریت"), t_bold_c),
            ],
            ["", "", ""],
        ]

        sig_table = Table(
            signature_data,
            colWidths=[6.7 * cm, 3 * cm, 6.5 * cm],
            rowHeights=[0.5 * cm, 1.2 * cm],
        )
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 1), (0, 1), 0.5, GRAY),
            ('LINEBELOW', (2, 1), (2, 1), 0.5, GRAY),
        ]))
        elements.append(sig_table)

        # ─── فوتر ─────
        elements.append(Spacer(1, 0.2 * cm))

        footer_line = Table([[""]], colWidths=[18.2 * cm],
                            rowHeights=[0.02 * cm])
        footer_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ]))
        elements.append(footer_line)
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(Paragraph(
            rtl(f"© {building_name or 'ساختمان'} - تولید شده توسط سیستم مدیریت ساختمان"),
            ParagraphStyle('FT', fontName='Vazirmatn', fontSize=7,
                alignment=TA_CENTER, textColor=GRAY),
        ))

        doc.build(elements)

        return {
            "success": True,
            "path": output_path,
            "message": "PDF با موفقیت ساخته شد.",
        }

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "path": None,
            "message": f"خطای PDF: {ex}",
        }

def generate_bills_report_pdf(
    bill_type,
    bills,
    building_name="",
    building_info=None,
    output_path=None,
    currency_label="ریال",
    logo_path=None,
    theme_color="#1565C0",
    stats=None,
    chart_paths=None,
):
    """
    PDF کامل قبوض با نمودارها (مصرف + مبلغ) و جدول تفصیلی.

    Args:
        bill_type: "آب" | "برق" | "گاز"
        bills: لیست dict از list_utility_bills
        chart_paths: dict مثل
            {
                "bar_3d": "/path/...",
                "area": "/path/...",
                "bubble": "/path/...",
                "bar_3d_amount": "/path/...",
            }
    """
    if not HAS_REPORTLAB:
        return {"success": False, "path": None,
                "message": "reportlab نصب نیست."}

    try:
        register_fonts()
        from reportlab.lib.utils import ImageReader

        if not output_path:
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_t = str(bill_type).replace(" ", "_")
            output_path = os.path.join(
                reports_dir, f"bills_{safe_t}_{ts}.pdf"
            )

        # ═══════════ رنگ‌ها ═══════════
        PRIMARY = hex_to_rgb_tuple(theme_color)
        PRIMARY_LIGHT = lighten_color(theme_color, 0.85)
        PRIMARY_LIGHTER = lighten_color(theme_color, 0.95)
        SUCCESS = colors.HexColor("#2E7D32")
        SUCCESS_LIGHT = colors.HexColor("#E8F5E9")
        WARNING = colors.HexColor("#EF6C00")
        WARNING_LIGHT = colors.HexColor("#FFF3E0")
        DANGER = colors.HexColor("#C62828")
        DANGER_LIGHT = colors.HexColor("#FFEBEE")
        GRAY = colors.HexColor("#666666")
        LIGHT_GRAY = colors.HexColor("#F5F5F5")
        BORDER = colors.HexColor("#E0E0E0")

        TYPE_COLORS = {
            "آب":  (colors.HexColor("#00BCD4"),
                    colors.HexColor("#E0F7FA")),
            "برق": (colors.HexColor("#FFC107"),
                    colors.HexColor("#FFF8E1")),
            "گاز": (colors.HexColor("#FF5722"),
                    colors.HexColor("#FBE9E7")),
        }
        TYPE_ICONS = {"آب": "💧", "برق": "⚡", "گاز": "🔥"}
        type_color, type_light = TYPE_COLORS.get(
            bill_type, (PRIMARY, PRIMARY_LIGHT)
        )
        type_icon = TYPE_ICONS.get(bill_type, "📋")

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=0.8 * cm, leftMargin=0.8 * cm,
            topMargin=0.6 * cm, bottomMargin=0.6 * cm,
        )
        elements = []

        # ═══════════ استایل‌ها ═══════════
        t_r = ParagraphStyle('br_r', fontName='Vazirmatn',
            fontSize=8, alignment=TA_RIGHT, leading=10)
        t_c = ParagraphStyle('br_c', fontName='Vazirmatn',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_br = ParagraphStyle('br_br', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_RIGHT, leading=10)
        t_bc = ParagraphStyle('br_bc', fontName='Vazirmatn-Bold',
            fontSize=8, alignment=TA_CENTER, leading=10)
        t_th = ParagraphStyle('br_th', fontName='Vazirmatn-Bold',
            fontSize=7.5, alignment=TA_CENTER,
            textColor=colors.white, leading=9)
        t_sm = ParagraphStyle('br_sm', fontName='Vazirmatn',
            fontSize=6.5, alignment=TA_CENTER,
            textColor=GRAY, leading=8)
        section = ParagraphStyle('br_sec', fontName='Vazirmatn-Bold',
            fontSize=11, alignment=TA_RIGHT,
            textColor=PRIMARY, spaceAfter=4, spaceBefore=6)

        # ═══════════ هدر ═══════════
        date_str = rtl(get_jalali_date())
        header_table = Table(
            [[
                Paragraph(date_str, ParagraphStyle('br_ds',
                    fontName='Vazirmatn', fontSize=8,
                    alignment=TA_LEFT, textColor=colors.white)),
                Paragraph(rtl(f"{type_icon} گزارش قبوض {bill_type}"),
                    ParagraphStyle('br_bt', fontName='Vazirmatn-Bold',
                        fontSize=14, alignment=TA_CENTER,
                        textColor=colors.white, leading=16)),
                Paragraph(rtl(building_name or "ساختمان"),
                    ParagraphStyle('br_bn', fontName='Vazirmatn',
                        fontSize=8, alignment=TA_RIGHT,
                        textColor=colors.white)),
            ]],
            colWidths=[3.5 * cm, 11.2 * cm, 3.5 * cm],
            rowHeights=[1.4 * cm],
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), type_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.25 * cm))

        # ═══════════ اطلاعات ساختمان ═══════════
        if building_info:
            binfo = Table(
                [[
                    Paragraph(rtl(building_info.get("address", "-") or "-"), t_br),
                    Paragraph(rtl("آدرس:"), t_sm),
                    Paragraph(rtl(to_persian(str(building_info.get("floors", 0)))), t_bc),
                    Paragraph(rtl("طبقه"), t_sm),
                    Paragraph(rtl(to_persian(str(building_info.get("total_units", 0)))), t_bc),
                    Paragraph(rtl("واحد"), t_sm),
                ]],
                colWidths=[7.6 * cm, 1.4 * cm, 1.4 * cm,
                           1.4 * cm, 1.4 * cm, 1.4 * cm],
            )
            binfo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_LIGHTER),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            elements.append(binfo)
            elements.append(Spacer(1, 0.3 * cm))

        # ═══════════ خلاصه‌ی آماری ═══════════
        if stats:
            elements.append(Paragraph(
                rtl(f"📊 خلاصه‌ی آماری {bill_type}"), section))
            unit_label = ("m³" if bill_type in ["آب", "گاز"] else "kWh")

            def stat_cell(title, value, color):
                return [
                    Paragraph(rtl(title), t_sm),
                    Paragraph(rtl(value),
                        ParagraphStyle('br_sv', fontName='Vazirmatn-Bold',
                            fontSize=10, alignment=TA_CENTER,
                            textColor=color, leading=12)),
                ]

            s_table = Table(
                [[
                    stat_cell("جمع مصرف",
                        f'{stats.get("total_consumption", 0):,.0f} ' + unit_label,
                        type_color),
                    stat_cell("میانگین مصرف",
                        f'{stats.get("avg_monthly_consumption", 0):,.1f} ' + unit_label,
                        PRIMARY),
                    stat_cell("بیشترین مصرف",
                        f'{stats.get("max_consumption", 0):,.0f} ' + unit_label,
                        DANGER),
                    stat_cell("کمترین مصرف",
                        f'{stats.get("min_consumption", 0):,.0f} ' + unit_label,
                        SUCCESS),
                    stat_cell("تعداد قبوض",
                        to_persian(str(stats.get("count", 0))),
                        PRIMARY),
                ]],
                colWidths=[3.7 * cm, 3.7 * cm, 3.7 * cm,
                           3.7 * cm, 3.4 * cm],
            )
            s_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), type_light),
                ('BACKGROUND', (1, 0), (1, 0), PRIMARY_LIGHT),
                ('BACKGROUND', (2, 0), (2, 0), DANGER_LIGHT),
                ('BACKGROUND', (3, 0), (3, 0), SUCCESS_LIGHT),
                ('BACKGROUND', (4, 0), (4, 0), PRIMARY_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            elements.append(s_table)
            elements.append(Spacer(1, 0.2 * cm))

            def money_cell(title, value, color):
                return [
                    Paragraph(rtl(title), t_sm),
                    Paragraph(
                        rtl(fmt_money(value, show_unit=False) + " " + currency_label),
                        ParagraphStyle('br_mv', fontName='Vazirmatn-Bold',
                            fontSize=11, alignment=TA_CENTER,
                            textColor=color, leading=13)),
                ]

            m_table = Table(
                [[
                    money_cell("جمع کل مبلغ",
                        stats.get("total_amount", 0) / 10, type_color),
                    money_cell("میانگین ماهانه",
                        stats.get("avg_monthly_amount", 0) / 10, PRIMARY),
                    money_cell("بیشترین مبلغ",
                        stats.get("max_amount", 0) / 10, DANGER),
                    money_cell("کمترین مبلغ",
                        stats.get("min_amount", 0) / 10, SUCCESS),
                ]],
                colWidths=[4.6 * cm, 4.6 * cm, 4.6 * cm, 4.4 * cm],
            )
            m_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), type_light),
                ('BACKGROUND', (1, 0), (1, 0), PRIMARY_LIGHT),
                ('BACKGROUND', (2, 0), (2, 0), DANGER_LIGHT),
                ('BACKGROUND', (3, 0), (3, 0), SUCCESS_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            elements.append(m_table)
            elements.append(Spacer(1, 0.3 * cm))

        # ═══════════ نمودارها ═══════════
        print(f"📄 PDF: chart_paths = "
              f"{list(chart_paths.keys()) if chart_paths else 'None'}")

        if chart_paths:
            elements.append(Spacer(1, 0.3 * cm))
            elements.append(Paragraph(
                rtl("📉 نمودارها"),
                ParagraphStyle('br_sect2', fontName='Vazirmatn-Bold',
                    fontSize=13, alignment=TA_RIGHT,
                    textColor=PRIMARY, spaceAfter=6, spaceBefore=4),
            ))

            chart_titles = {
                "bar_3d":        "📊 مصرف — میله سه‌بعدی",
                "area":          "📈 مصرف — نمودار ناحیه‌ای",
                "bubble":        "🫧 مصرف — نمودار حبابی",
                "bar_3d_amount": "💰 مبلغ — میله سه‌بعدی",
            }

            for key in ["bar_3d", "area", "bubble", "bar_3d_amount"]:
                path = chart_paths.get(key)
                if not path:
                    continue
                if not os.path.exists(path):
                    print(f"  ⚠️ {key}: فایل وجود ندارد → {path}")
                    continue

                # ─── محاسبه‌ی اندازه با حفظ نسبت ───
                try:
                    img_obj = ImageReader(path)
                    iw, ih = img_obj.getSize()
                except Exception as ex:
                    print(f"  ❌ {key}: خطا در خواندن → {ex}")
                    continue

                # هدف: عرض 17cm، سقف ارتفاع 6.5cm
                target_w = 17 * cm
                target_h = target_w * (ih / iw)
                if target_h > 6.5 * cm:
                    target_h = 6.5 * cm
                    target_w = target_h * (iw / ih)

                print(f"  ✅ {key}: {iw}x{ih} px → "
                      f"{target_w/cm:.1f}×{target_h/cm:.1f} cm")

                # ─── KeepTogether: عنوان + تصویر یکجا ───
                block = [
                    Paragraph(rtl(chart_titles.get(key, key)),
                        ParagraphStyle(f'br_cht_{key}',
                            fontName='Vazirmatn-Bold',
                            fontSize=10, alignment=TA_RIGHT,
                            textColor=PRIMARY,
                            spaceAfter=3, spaceBefore=6)),
                    Image(path, width=target_w, height=target_h),
                    Spacer(1, 0.35 * cm),
                ]
                elements.append(KeepTogether(block))

            elements.append(Spacer(1, 0.3 * cm))
        else:
            print("⚠️ PDF: chart_paths خالی است!")

        # ═══════════ جدول قبوض ═══════════
        elements.append(Paragraph(
            rtl(f"📋 لیست قبوض ({to_persian(str(len(bills)))} مورد)"),
            section))

        if bills:
            unit_label = "m³" if bill_type in ["آب", "گاز"] else "kWh"
            hdr = [
                Paragraph(rtl("مبلغ"), t_th),
                Paragraph(rtl("مصرف"), t_th),
                Paragraph(rtl("روزانه"), t_th),
                Paragraph(rtl("فعلی"), t_th),
                Paragraph(rtl("قبلی"), t_th),
                Paragraph(rtl("روز"), t_th),
                Paragraph(rtl("از"), t_th),
                Paragraph(rtl("تا"), t_th),
                Paragraph(rtl("دوره"), t_th),
                Paragraph(rtl("ردیف"), t_th),
            ]
            rows = [hdr]
            total_amt = 0
            total_cons = 0

            for idx, b in enumerate(bills, 1):
                amt = (b.get("amount", 0) or 0) / 10
                cons = b.get("consumption", 0) or 0
                total_amt += amt
                total_cons += cons

                rows.append([
                    Paragraph(rtl(fmt_money(amt, show_unit=False)),
                        ParagraphStyle('br_amt',
                            fontName='Vazirmatn-Bold',
                            fontSize=7.5, alignment=TA_CENTER,
                            textColor=type_color)),
                    Paragraph(rtl(f'{cons:,.0f}'), t_bc),
                    Paragraph(rtl(f'{(b.get("daily_avg_consumption", 0) or 0):,.2f}'), t_c),
                    Paragraph(rtl(f'{(b.get("current_reading", 0) or 0):,.0f}'), t_c),
                    Paragraph(rtl(f'{(b.get("previous_reading", 0) or 0):,.0f}'), t_c),
                    Paragraph(rtl(to_persian(str(b.get("days_count", 0) or 0))), t_c),
                    Paragraph(rtl(to_jalali_str(b.get("from_date"))), t_c),
                    Paragraph(rtl(to_jalali_str(b.get("to_date"))), t_c),
                    Paragraph(rtl(b.get("period") or "-"), t_bc),
                    Paragraph(rtl(to_persian(str(idx))), t_sm),
                ])

            # ردیف جمع
            rows.append([
                Paragraph(rtl(fmt_money(total_amt, show_unit=False)),
                    ParagraphStyle('br_at', fontName='Vazirmatn-Bold',
                        fontSize=8, alignment=TA_CENTER,
                        textColor=PRIMARY)),
                Paragraph(rtl(f'{total_cons:,.0f}'),
                    ParagraphStyle('br_ct', fontName='Vazirmatn-Bold',
                        fontSize=8, alignment=TA_CENTER,
                        textColor=PRIMARY)),
                Paragraph("", t_c), Paragraph("", t_c), Paragraph("", t_c),
                Paragraph("", t_c), Paragraph("", t_c), Paragraph("", t_c),
                Paragraph(rtl("جمع کل"), t_bc),
                Paragraph("", t_c),
            ])

            tbl = Table(
                rows,
                colWidths=[
                    2.3 * cm, 1.8 * cm, 1.8 * cm, 2.0 * cm, 2.0 * cm,
                    1.0 * cm, 2.1 * cm, 2.1 * cm, 2.4 * cm, 1.0 * cm,
                ],
                repeatRows=1,
            )
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), type_color),
                ('BACKGROUND', (0, len(rows) - 1), (-1, len(rows) - 1),
                 PRIMARY_LIGHT),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, len(rows) - 2),
                    [colors.white, LIGHT_GRAY]),
                ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(tbl)
        else:
            elements.append(Paragraph(
                rtl("قبضی ثبت نشده است."), t_c))

        # ═══════════ فوتر ═══════════
        elements.append(Spacer(1, 0.4 * cm))
        foot = Table([[""]], colWidths=[18.2 * cm], rowHeights=[0.02 * cm])
        foot.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), type_color)]))
        elements.append(foot)
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(Paragraph(
            rtl(f"© {building_name or 'ساختمان'} - سیستم مدیریت ساختمان"),
            ParagraphStyle('br_ft', fontName='Vazirmatn',
                fontSize=7, alignment=TA_CENTER, textColor=GRAY),
        ))

        doc.build(elements)
        return {"success": True, "path": output_path,
                "message": "PDF قبوض ساخته شد."}
    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {"success": False, "path": None,
                "message": f"خطای PDF: {ex}"}