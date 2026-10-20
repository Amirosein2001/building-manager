# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

import jdatetime
from android_sms_gateway import client, domain
import asyncio
from datetime import datetime, date
from sqlalchemy import func
from database import SessionLocal, engine
from models import (
    Building, Unit, Charge, Payment,
    Expense, UtilityBill, AppSetting
)
from cryptography.fernet import Fernet
import base64
import hashlib
import os
import sys
import shutil
import winreg


# ───────── ماه‌های شمسی ─────────

MONTHS = [
    "", "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]


# ═══════════ سیستم Multi-Building ═══════════

def _get_active_building_id():
    """گرفتن ID ساختمون فعال از تنظیمات"""
    try:
        bid = get_setting("active_building_id", "")
        if bid and str(bid).strip():
            return int(bid)
    except Exception:
        pass
    return None


def set_active_building(building_id):
    """تنظیم ساختمون فعال"""
    set_setting("active_building_id", str(building_id))


def list_buildings():
    """لیست همه ساختمان‌ها"""
    with SessionLocal() as db:
        buildings = db.query(Building).order_by(Building.id.asc()).all()
        active_id = _get_active_building_id()
        return [
            {
                "id": b.id,
                "name": b.name,
                "address": b.address or "",
                "floors": b.floors or 0,
                "total_units": b.total_units or 0,
                "is_active": (b.id == active_id),
            }
            for b in buildings
        ]


def add_building(name, address="", floors=0, total_units=0):
    """اضافه کردن ساختمان جدید"""
    name = str(name or "").strip()
    if not name:
        raise ValueError("نام ساختمان الزامی است.")

    with SessionLocal() as db:
        building = Building(
            name=name,
            address=str(address or "").strip(),
            floors=int(floors or 0),
            total_units=int(total_units or 0),
        )
        db.add(building)
        db.commit()
        db.refresh(building)
        return building.id


def update_building_by_id(building_id, name, address="", floors=0, total_units=0):
    """ویرایش ساختمان"""
    name = str(name or "").strip()
    if not name:
        raise ValueError("نام ساختمان الزامی است.")

    with SessionLocal() as db:
        b = db.query(Building).filter(
            Building.id == int(building_id)
        ).first()
        if not b:
            raise ValueError("ساختمان پیدا نشد.")
        b.name = name
        b.address = str(address or "").strip()
        b.floors = int(floors or 0)
        b.total_units = int(total_units or 0)
        db.commit()
        return True


def delete_building(building_id):
    """حذف ساختمان و همه‌ی داده‌های مرتبط"""
    with SessionLocal() as db:
        b = db.query(Building).filter(
            Building.id == int(building_id)
        ).first()
        if not b:
            raise ValueError("ساختمان پیدا نشد.")

        count = db.query(Building).count()
        if count <= 1:
            raise ValueError("نمی‌توان آخرین ساختمان را حذف کرد.")

        # حذف واحدها (که Charge/Payment از طریق cascade پاک می‌شن)
        units = db.query(Unit).filter(Unit.building_id == b.id).all()
        for u in units:
            db.delete(u)

        # حذف قبوض
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == b.id
        ).all()
        for bill in bills:
            db.delete(bill)

        # حذف هزینه‌ها
        expenses = db.query(Expense).filter(
            Expense.building_id == b.id
        ).all()
        for e in expenses:
            db.delete(e)

        db.delete(b)
        db.commit()

        # اگه ساختمون فعال بود، یه ساختمون دیگه رو active کن
        active_id = _get_active_building_id()
        if active_id == int(building_id):
            first = db.query(Building).first()
            if first:
                set_active_building(first.id)

        return True


def switch_building(building_id):
    """سوییچ به ساختمان دیگه"""
    with SessionLocal() as db:
        b = db.query(Building).filter(
            Building.id == int(building_id)
        ).first()
        if not b:
            raise ValueError("ساختمان پیدا نشد.")
        set_active_building(b.id)
        return True


def count_buildings():
    """تعداد ساختمان‌ها"""
    with SessionLocal() as db:
        return db.query(Building).count()


def to_jalali(d):
    if d is None:
        return ""
    if isinstance(d, str):
        d = parse_date(d)
    if d is None:
        return ""
    j = jdatetime.date.fromgregorian(date=d)
    return f"{j.day} {MONTHS[j.month]} {j.year}"


def to_jalali_short(d):
    if d is None:
        return ""
    if isinstance(d, str):
        d = parse_date(d)
    if d is None:
        return ""
    j = jdatetime.date.fromgregorian(date=d)
    return f"{j.year}/{j.month:02d}/{j.day:02d}"


def today_jalali():
    j = jdatetime.date.today()
    return f"{j.day} {MONTHS[j.month]} {j.year}"


def today_jalali_short():
    j = jdatetime.date.today()
    return f"{j.year}/{j.month:02d}/{j.day:02d}"


def current_jalali_period():
    j = jdatetime.date.today()
    return f"{MONTHS[j.month]} {j.year}"


def get_jalali_year():
    return jdatetime.date.today().year


def get_jalali_month():
    return jdatetime.date.today().month


def jalali_to_gregorian(year, month, day):
    try:
        j = jdatetime.date(int(year), int(month), int(day))
        return j.togregorian()
    except Exception:
        return None


def parse_jalali_date(text):
    if not text or not str(text).strip():
        return None
    text = str(text).strip().replace("/", "-")
    parts = text.split("-")
    if len(parts) != 3:
        return None
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        return jalali_to_gregorian(y, m, d)
    except Exception:
        return None


def parse_date(value):
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    g = parse_jalali_date(text)
    if g:
        return g
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("فرمت تاریخ نادرست. مثال: 1404/04/15")


def _update_charge_status(charge):
    remaining = max(
        (charge.amount or 0) - (charge.paid_amount or 0), 0
    )
    if remaining <= 0:
        charge.status = "تسویه"
    elif (charge.paid_amount or 0) > 0:
        charge.status = "ناقص"
    else:
        charge.status = "پرداخت نشده"

def _period_sort_key(period):
    """
    تبدیل دوره مثل «مهر 1405» به tuple مرتب‌پذیر (سال، ترتیب ماه).
    برای مقایسه‌ی ترتیب واقعی دوره‌ها استفاده می‌شود.
    """
    if not period:
        return (0, 0)
    parts = str(period).strip().split()
    try:
        year = int(parts[-1])
        month_name = parts[0]
        month_order = MONTHS.index(month_name) if month_name in MONTHS else 0
        return (year, month_order)
    except (ValueError, IndexError):
        return (0, 0)


def _bill_sort_key(bill):
    """
    کلید مرتب‌سازی قبض:
    اول بر اساس دوره‌ی شمسی، در نبودش بر اساس from_date،
    بعد to_date، و در نهایت issue_date.
    """
    # ─── اول: period ───
    period = bill.period or ""
    parts = period.strip().split()
    if len(parts) >= 2:
        try:
            year = int(parts[-1])
            month_name = parts[0]
            month_order = MONTHS.index(month_name) if month_name in MONTHS else 0
            return (year, month_order)
        except (ValueError, IndexError):
            pass

    # ─── دوم: from_date ───
    if bill.from_date:
        try:
            j = jdatetime.date.fromgregorian(date=bill.from_date)
            return (j.year, j.month)
        except Exception:
            pass

    # ─── سوم: to_date ───
    if bill.to_date:
        try:
            j = jdatetime.date.fromgregorian(date=bill.to_date)
            return (j.year, j.month)
        except Exception:
            pass

    # ─── چهارم: issue_date ───
    if bill.issue_date:
        try:
            j = jdatetime.date.fromgregorian(date=bill.issue_date)
            return (j.year, j.month)
        except Exception:
            pass

    return (0, 0)
# ───────── ساختمان ─────────

def _get_or_create_building(db):
    """گرفتن ساختمون فعال (یا ساخت اولین ساختمون)"""
    active_id = _get_active_building_id()
    if active_id:
        b = db.query(Building).filter(
            Building.id == active_id
        ).first()
        if b:
            return b

    building = db.query(Building).first()
    if not building:
        building = Building(
            name="ساختمان من", address="",
            floors=5, total_units=10
        )
        db.add(building)
        db.commit()
        db.refresh(building)

    # inline: تنظیم active بدون session جدید
    try:
        row = db.query(AppSetting).filter(
            AppSetting.key == "active_building_id"
        ).first()
        if row:
            row.value = str(building.id)
        else:
            db.add(AppSetting(
                key="active_building_id",
                value=str(building.id),
            ))
        db.commit()
    except Exception:
        pass

    return building


def ensure_default_building():
    with SessionLocal() as db:
        _get_or_create_building(db)


def get_building_info():
    with SessionLocal() as db:
        b = _get_or_create_building(db)
        return {
            "id": b.id, "name": b.name,
            "address": b.address, "floors": b.floors,
            "total_units": b.total_units
        }


def update_building_info(name, address, floors, total_units):
    with SessionLocal() as db:
        b = _get_or_create_building(db)
        b.name = str(name or "").strip() or b.name
        b.address = str(address or "").strip()
        b.floors = int(floors or 0)
        b.total_units = int(total_units or 0)
        db.commit()


# ───────── واحدها ─────────

def add_unit(number, floor, area, people_count,
             resident_name, phone, resident_type,
             status, notes=""):
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        number = str(number or "").strip()
        if not number:
            raise ValueError("شماره واحد الزامی است.")
        existing = db.query(Unit).filter(
            Unit.building_id == building.id,
            Unit.number == number
        ).first()
        if existing:
            raise ValueError("این شماره واحد قبلاً ثبت شده.")
        unit = Unit(
            building_id=building.id, number=number,
            floor=int(floor or 0),
            area=float(area or 0),
            people_count=int(people_count or 0),
            resident_name=str(resident_name or "").strip(),
            phone=str(phone or "").strip(),
            resident_type=resident_type or "مالک",
            status=status or "ساکن",
            notes=str(notes or "")
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit


def update_unit(unit_id, number, floor, area,
                people_count, resident_name, phone,
                resident_type, status, notes=""):
    with SessionLocal() as db:
        unit = db.query(Unit).filter(
            Unit.id == int(unit_id)
        ).first()
        if not unit:
            raise ValueError("واحد پیدا نشد.")
        number = str(number or "").strip()
        if not number:
            raise ValueError("شماره واحد الزامی است.")
        dup = db.query(Unit).filter(
            Unit.building_id == unit.building_id,
            Unit.number == number,
            Unit.id != unit.id
        ).first()
        if dup:
            raise ValueError("شماره واحد تکراری است.")
        unit.number = number
        unit.floor = int(floor or 0)
        unit.area = float(area or 0)
        unit.people_count = int(people_count or 0)
        unit.resident_name = str(
            resident_name or ""
        ).strip()
        unit.phone = str(phone or "").strip()
        unit.resident_type = resident_type or "مالک"
        unit.status = status or "ساکن"
        unit.notes = str(notes or "")
        db.commit()
        db.refresh(unit)
        return unit


def delete_unit(unit_id):
    with SessionLocal() as db:
        unit = db.query(Unit).filter(
            Unit.id == int(unit_id)
        ).first()
        if not unit:
            raise ValueError("واحد پیدا نشد.")
        db.delete(unit)
        db.commit()


def get_unit_by_id(unit_id):
    with SessionLocal() as db:
        u = db.query(Unit).filter(
            Unit.id == int(unit_id)
        ).first()
        if not u:
            return None
        return {
            "id": u.id, "number": u.number,
            "floor": u.floor, "area": u.area,
            "people_count": u.people_count,
            "resident_name": u.resident_name,
            "phone": u.phone,
            "resident_type": u.resident_type,
            "status": u.status, "notes": u.notes,
        }


def list_units_basic():
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        units = db.query(Unit).filter(
            Unit.building_id == building.id
        ).order_by(
            Unit.floor.asc(), Unit.number.asc()
        ).all()
        return [
            {
                "id": u.id,
                "label": (
                    f"واحد {u.number} - "
                    f"{u.resident_name or 'خالی'}"
                )
            }
            for u in units
        ]


def list_units_with_debt():
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        units = db.query(Unit).filter(
            Unit.building_id == building.id
        ).order_by(
            Unit.floor.asc(), Unit.number.asc()
        ).all()
        result = []
        for u in units:
            charges = db.query(Charge).filter(
                Charge.unit_id == u.id
            ).all()
            debt = sum(
                max(
                    (c.amount or 0) - (c.paid_amount or 0),
                    0
                )
                for c in charges
            )
            result.append({
                "id": u.id, "number": u.number,
                "floor": u.floor, "area": u.area,
                "people_count": u.people_count,
                "resident_name": u.resident_name,
                "phone": u.phone,
                "resident_type": u.resident_type,
                "status": u.status, "notes": u.notes,
                "debt": debt,
            })
        return result


# ───────── شارژ ─────────

def generate_monthly_charges(period, method, value,
                              due_date=None):
    period = str(period or "").strip()
    if not period:
        raise ValueError("دوره شارژ الزامی است.")
    rate = float(value or 0)
    if rate <= 0:
        raise ValueError(
            "مبلغ / نرخ باید بیشتر از صفر باشد."
        )
    due = parse_date(due_date)
    with SessionLocal() as db:
        _get_or_create_building(db)
        units = db.query(Unit).order_by(
            Unit.floor.asc(), Unit.number.asc()
        ).all()
        if not units:
            raise ValueError("اول باید واحد ثبت کنید.")
        created = 0
        for unit in units:
            exists = db.query(Charge).filter(
                Charge.unit_id == unit.id,
                Charge.period == period
            ).first()
            if exists:
                continue
            if method == "manual":
                amount = rate
            elif method == "area":
                amount = float(unit.area or 0) * rate
            elif method == "person":
                amount = float(
                    unit.people_count or 0
                ) * rate
            else:
                raise ValueError("روش محاسبه نامعتبر.")
            charge = Charge(
                unit_id=unit.id, period=period,
                calculation_method=method,
                amount=round(amount, 2),
                paid_amount=0,
                status="پرداخت نشده",
                due_date=due, notes=""
            )
            db.add(charge)
            created += 1
        db.commit()
        return created


def list_charges(period=None):
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        query = db.query(Charge, Unit).join(
            Unit, Charge.unit_id == Unit.id
        ).filter(
            Unit.building_id == building.id
        ).order_by(
            Charge.period.desc(),
            Unit.floor.asc(),
            Unit.number.asc()
        )
        if period and str(period).strip():
            query = query.filter(
                Charge.period == str(period).strip()
            )
        rows = query.all()
        result = []
        for charge, unit in rows:
            remaining = max(
                (charge.amount or 0) -
                (charge.paid_amount or 0), 0
            )

            # بدهی قبلی: مجموع باقی‌مانده‌ی دوره‌های قبل‌تر
            current_key = _period_sort_key(charge.period)
            older_charges = db.query(Charge).filter(
                Charge.unit_id == unit.id,
            ).all()

            previous_debt = 0
            for oc in older_charges:
                if _period_sort_key(oc.period) < current_key:
                    prev_rem = max(
                        (oc.amount or 0) - (oc.paid_amount or 0),
                        0
                    )
                    previous_debt += prev_rem

            result.append({
                "id": charge.id, "unit_id": unit.id,
                "unit_number": unit.number,
                "resident_name": unit.resident_name,
                "phone": unit.phone,
                "area": unit.area,
                "people_count": unit.people_count,
                "floor": unit.floor,
                "period": charge.period,
                "method": charge.calculation_method,
                "amount": charge.amount,
                "paid_amount": charge.paid_amount,
                "remaining": remaining,
                "status": charge.status,
                "due_date": charge.due_date,
                "previous_debt": previous_debt,
            })
        return result


def get_charge_periods():
    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        rows = db.query(Charge.period).join(
            Unit, Charge.unit_id == Unit.id             # ← ⭐ جدید
        ).filter(
            Unit.building_id == building.id             # ← ⭐ جدید
        ).distinct().order_by(
            Charge.period.desc()
        ).all()
        return [r[0] for r in rows]

def delete_charge(charge_id):
    with SessionLocal() as db:
        charge = db.query(Charge).filter(
            Charge.id == int(charge_id)
        ).first()
        if not charge:
            raise ValueError("شارژ پیدا نشد.")
        db.delete(charge)
        db.commit()


def mark_charge_paid(charge_id):
    with SessionLocal() as db:
        charge = db.query(Charge).filter(
            Charge.id == int(charge_id)
        ).first()

        if not charge:
            raise ValueError("شارژ پیدا نشد.")

        remaining = max(
            (charge.amount or 0) - (charge.paid_amount or 0), 0
        )

        if remaining > 0:
            payment = Payment(
                unit_id=charge.unit_id,
                amount=remaining,
                payment_date=date.today(),
                payment_method="تسویه دستی",
                tracking_code="",
                description=f"تسویه دستی شارژ #{charge.id}",
                target_charge_id=charge.id,      # ⭐ این خط مهمه
                target_period=charge.period,     # ⭐ این خط مهمه
            )
            db.add(payment)

        charge.paid_amount = charge.amount
        charge.status = "تسویه"
        db.commit()


def mark_charge_unpaid(charge_id):
    """
    برگرداندن شارژ به حالت پرداخت نشده (تغییر دستی وضعیت)

    توجه: این تابع فقط وضعیت همین شارژ را برمی‌گرداند، مثل
    نقطه‌مقابل mark_charge_paid؛ به رکوردهای Payment واحد
    کاری ندارد (چون آن‌ها با توابع add_payment/delete_payment
    مدیریت می‌شوند).
    """
    with SessionLocal() as db:
        charge = db.query(Charge).filter(
            Charge.id == int(charge_id)
        ).first()

        if not charge:
            raise ValueError("شارژ پیدا نشد.")

        charge.paid_amount = 0
        charge.status = "پرداخت نشده"

        db.commit()

# ───────── پرداخت ─────────

def add_payment(unit_id, amount, payment_date=None,
                payment_method="کارت", tracking_code="",
                description="", target_charge_id=None,
                receipt_image=""):
    amount = float(amount or 0)
    if amount <= 0:
        raise ValueError("مبلغ پرداخت باید بیشتر از صفر باشد.")
    p_date = parse_date(payment_date) or date.today()

    with SessionLocal() as db:
        unit = db.query(Unit).filter(
            Unit.id == int(unit_id)
        ).first()
        if not unit:
            raise ValueError("واحد پیدا نشد.")

        # ───── حالت ۱: پرداخت به شارژ مشخص ─────
        if target_charge_id:
            target = db.query(Charge).filter(
                Charge.id == int(target_charge_id),
                Charge.unit_id == unit.id,
            ).first()
            if not target:
                raise ValueError("شارژ مورد نظر پیدا نشد.")
            target_remaining = max(
                (target.amount or 0) - (target.paid_amount or 0), 0
            )
            if target_remaining <= 0:
                raise ValueError("این شارژ قبلاً تسویه شده است.")
            if amount > target_remaining:
                raise ValueError(
                    f"مبلغ از باقیمانده بیشتر است. "
                    f"باقیمانده: {target_remaining:,.0f}"
                )

            # ⭐⭐ ذخیره target_charge_id و target_period
            payment = Payment(
                unit_id=unit.id, amount=amount,
                payment_date=p_date,
                payment_method=payment_method or "کارت",
                tracking_code=str(tracking_code or "").strip(),
                description=str(description or "").strip(),
                receipt_image=str(receipt_image or ""),
                target_charge_id=target.id,          # ⭐⭐
                target_period=target.period,         # ⭐⭐
            )
            db.add(payment)
            target.paid_amount = (target.paid_amount or 0) + amount
            _update_charge_status(target)
            db.commit()
            db.refresh(payment)

            try:
                remaining_after = max(
                    (target.amount or 0) - (target.paid_amount or 0),
                    0
                )
                send_payment_thanks_sms(
                    unit, amount, remaining_after=remaining_after,
                )
            except Exception as ex:
                print(f"⚠️ خطای پیامک تشکر: {ex}")

            return {
                "payment_id": payment.id,
                "unit_number": unit.number,
                "amount": amount,
                "payment_date": str(payment.payment_date),
                "payment_method": payment.payment_method,
            }

        # ───── حالت ۲: پرداخت آزاد (FIFO) ─────
        unpaid = db.query(Charge).filter(
            Charge.unit_id == unit.id
        ).order_by(
            Charge.created_at.asc(), Charge.id.asc()
        ).all()
        unpaid = [
            c for c in unpaid
            if max((c.amount or 0) - (c.paid_amount or 0), 0) > 0
        ]
        if not unpaid:
            raise ValueError("این واحد بدهی ثبت‌شده‌ای ندارد.")

        total_debt = sum(
            max((c.amount or 0) - (c.paid_amount or 0), 0)
            for c in unpaid
        )
        if amount > total_debt:
            raise ValueError(
                f"مبلغ از بدهی بیشتر است. بدهی: {total_debt:,.0f}"
            )

        # ⭐⭐ اولین شارژ بدهکار = دوره‌ی هدف
        first_unpaid_charge = unpaid[0]

        payment = Payment(
            unit_id=unit.id, amount=amount,
            payment_date=p_date,
            payment_method=payment_method or "کارت",
            tracking_code=str(tracking_code or "").strip(),
            description=str(description or "").strip(),
            receipt_image=str(receipt_image or ""),
            target_charge_id=None,
            target_period=first_unpaid_charge.period,   # ⭐⭐
        )
        db.add(payment)
        remaining_pay = amount
        for charge in unpaid:
            if remaining_pay <= 0:
                break
            charge_rem = max(
                (charge.amount or 0) - (charge.paid_amount or 0), 0
            )
            use = min(remaining_pay, charge_rem)
            charge.paid_amount = (charge.paid_amount or 0) + use
            remaining_pay -= use
            _update_charge_status(charge)
        db.commit()
        db.refresh(payment)

        try:
            total_remaining = 0
            all_charges = db.query(Charge).filter(
                Charge.unit_id == unit.id
            ).all()
            for c in all_charges:
                total_remaining += max(
                    (c.amount or 0) - (c.paid_amount or 0), 0
                )
            send_payment_thanks_sms(
                unit, amount, remaining_after=total_remaining,
            )
        except Exception as ex:
            print(f"⚠️ خطای پیامک تشکر: {ex}")

        return {
            "payment_id": payment.id,
            "unit_number": unit.number,
            "amount": amount,
            "payment_date": str(payment.payment_date),
            "payment_method": payment.payment_method,
        }

def list_payments():
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        rows = db.query(Payment, Unit).join(
            Unit, Payment.unit_id == Unit.id
        ).filter(
            Unit.building_id == building.id
        ).order_by(Payment.created_at.desc()).all()
        return [
            {
                "id": p.id, "unit_number": u.number,
                "resident_name": u.resident_name,
                "amount": p.amount,
                "payment_date": p.payment_date,
                "payment_method": p.payment_method,
                "tracking_code": p.tracking_code,
                "description": p.description,
                "receipt_image": p.receipt_image or "",
                "created_at": p.created_at,
                "target_charge_id": p.target_charge_id,   # ⭐⭐
                "target_period": p.target_period,          # ⭐⭐
            }
            for p, u in rows
        ]

def delete_payment(payment_id):
    with SessionLocal() as db:
        payment = db.query(Payment).filter(
            Payment.id == int(payment_id)
        ).first()
        if not payment:
            raise ValueError("پرداخت پیدا نشد.")

        if payment.receipt_image:
            try:
                if os.path.exists(payment.receipt_image):
                    os.remove(payment.receipt_image)
            except Exception as ex:
                print(f"⚠️ خطای حذف تصویر: {ex}")

        unit_id = payment.unit_id
        db.delete(payment)
        db.flush()

        # ─── همه‌ی شارژهای واحد رو صفر کن ───
        charges = db.query(Charge).filter(
            Charge.unit_id == unit_id
        ).order_by(
            Charge.created_at.asc(), Charge.id.asc()
        ).all()
        for c in charges:
            c.paid_amount = 0
            c.status = "پرداخت نشده"

        # ─── پرداخت‌های باقی‌مونده رو دوباره اعمال کن ───
        # مهم: به جای FIFO کور، به target_charge_id / target_period احترام بذار
        remaining_payments = db.query(Payment).filter(
            Payment.unit_id == unit_id
        ).order_by(
            Payment.payment_date.asc().nulls_last(),
            Payment.created_at.asc().nulls_last(),
            Payment.id.asc(),
        ).all()

        for pay in remaining_payments:
            # ─── مرحله ۱: اگه target_charge_id داره، اول اون ───
            applied = False

            if pay.target_charge_id:
                target = db.query(Charge).filter(
                    Charge.id == pay.target_charge_id,
                    Charge.unit_id == unit_id,
                ).first()
                if target:
                    rem_charge = max(
                        (target.amount or 0) - (target.paid_amount or 0), 0
                    )
                    use = min(pay.amount, rem_charge)
                    if use > 0:
                        target.paid_amount = (target.paid_amount or 0) + use
                        _update_charge_status(target)
                    leftover = pay.amount - use
                    if leftover > 0:
                        for c in charges:
                            if leftover <= 0:
                                break
                            if c.id == target.id:
                                continue
                            r = max((c.amount or 0) - (c.paid_amount or 0), 0)
                            u = min(leftover, r)
                            c.paid_amount = (c.paid_amount or 0) + u
                            leftover -= u
                            _update_charge_status(c)
                    applied = True

            # ─── مرحله ۲: اگه target_period داره ───
            elif pay.target_period:
                target = next(
                    (c for c in charges if c.period == pay.target_period),
                    None
                )
                if target:
                    rem_charge = max(
                        (target.amount or 0) - (target.paid_amount or 0), 0
                    )
                    use = min(pay.amount, rem_charge)
                    if use > 0:
                        target.paid_amount = (target.paid_amount or 0) + use
                        _update_charge_status(target)
                    leftover = pay.amount - use
                    if leftover > 0:
                        for c in charges:
                            if leftover <= 0:
                                break
                            if c.id == target.id:
                                continue
                            r = max((c.amount or 0) - (c.paid_amount or 0), 0)
                            u = min(leftover, r)
                            c.paid_amount = (c.paid_amount or 0) + u
                            leftover -= u
                            _update_charge_status(c)
                    applied = True

            # ─── مرحله ۳: FIFO خالص (فقط اگه هیچ target نداشت) ───
            if not applied:
                rem = pay.amount
                for c in charges:
                    if rem <= 0:
                        break
                    r = max((c.amount or 0) - (c.paid_amount or 0), 0)
                    u = min(rem, r)
                    c.paid_amount = (c.paid_amount or 0) + u
                    rem -= u
                    _update_charge_status(c)

        db.commit()


# ───────── هزینه‌ها ─────────

def add_expense(title, category, amount,
                expense_date=None, description="",
                invoice_image=""):
    title = str(title or "").strip()
    if not title:
        raise ValueError("عنوان هزینه الزامی است.")
    amount = float(amount or 0)
    if amount <= 0:
        raise ValueError("مبلغ هزینه باید بیشتر از صفر باشد.")
    e_date = parse_date(expense_date) or date.today()
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        expense = Expense(
            building_id=building.id,
            title=title,
            category=category or "سایر",
            amount=amount,
            expense_date=e_date,
            description=str(description or "").strip(),
            invoice_image=str(invoice_image or ""),
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense


def update_expense(expense_id, title, category, amount,
                   expense_date=None, description="",
                   invoice_image=None):
    title = str(title or "").strip()
    if not title:
        raise ValueError("عنوان هزینه الزامی است.")
    amount = float(amount or 0)
    if amount <= 0:
        raise ValueError("مبلغ هزینه باید بیشتر از صفر باشد.")
    e_date = parse_date(expense_date) or date.today()

    with SessionLocal() as db:
        expense = db.query(Expense).filter(
            Expense.id == int(expense_id)
        ).first()
        if not expense:
            raise ValueError("هزینه پیدا نشد.")

        expense.title = title
        expense.category = category or "سایر"
        expense.amount = amount
        expense.expense_date = e_date
        expense.description = str(description or "").strip()

        if invoice_image is not None:
            old_img = expense.invoice_image or ""
            new_img = str(invoice_image or "")
            if old_img and old_img != new_img:
                try:
                    if os.path.exists(old_img):
                        os.remove(old_img)
                except Exception as ex:
                    print(f"⚠️ خطای حذف فاکتور قدیمی: {ex}")
            expense.invoice_image = new_img

        db.commit()
        db.refresh(expense)
        return expense

def get_expense_by_id(expense_id):
    with SessionLocal() as db:
        e = db.query(Expense).filter(
            Expense.id == int(expense_id)
        ).first()
        if not e:
            return None
        return {
            "id": e.id, "title": e.title,
            "category": e.category, "amount": e.amount,
            "expense_date": e.expense_date,
            "description": e.description,
            "invoice_image": e.invoice_image or "",
        }

def list_expenses():
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        expenses = db.query(Expense).filter(
            Expense.building_id == building.id
        ).order_by(
            Expense.created_at.desc()
        ).all()
        return [
            {
                "id": e.id, "title": e.title,
                "category": e.category, "amount": e.amount,
                "expense_date": e.expense_date,
                "description": e.description,
                "invoice_image": e.invoice_image or "",
            }
            for e in expenses
        ]

def list_expenses_by_month():
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        expenses = db.query(Expense).filter(
            Expense.building_id == building.id
        ).order_by(
            Expense.expense_date.desc()
        ).all()

        months = {}
        for e in expenses:
            if e.expense_date:
                j = jdatetime.date.fromgregorian(date=e.expense_date)
                key = f"{MONTHS[j.month]} {j.year}"
            else:
                key = "بدون تاریخ"

            if key not in months:
                months[key] = {
                    "label": key, "items": [], "total": 0
                }

            months[key]["items"].append({
                "id": e.id,
                "title": e.title,
                "category": e.category,
                "amount": e.amount,
                "expense_date": e.expense_date,
                "description": e.description,
                "invoice_image": e.invoice_image or "",
            })
            months[key]["total"] += e.amount

        return list(months.values())

def delete_expense(expense_id):
    with SessionLocal() as db:
        expense = db.query(Expense).filter(
            Expense.id == int(expense_id)
        ).first()
        if not expense:
            raise ValueError("هزینه پیدا نشد.")

        if expense.invoice_image:
            try:
                if os.path.exists(expense.invoice_image):
                    os.remove(expense.invoice_image)
            except Exception as ex:
                print(f"⚠️ خطای حذف فاکتور: {ex}")

        db.delete(expense)
        db.commit()

# ───────── قبوض ─────────

def get_last_bill_reading(bill_type):
    """قرائت فعلی آخرین قبض همان نوع را برمی‌گرداند"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        last = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id,     # ← ⭐ جدید
            UtilityBill.bill_type == bill_type,
        ).order_by(
            UtilityBill.created_at.desc()
        ).first()
        if last:
            return last.current_reading or 0
        return 0


def add_utility_bill(bill_type, bill_identifier,
                     pay_identifier, period,
                     from_date, to_date,
                     previous_reading, current_reading,
                     amount, consumption_unit,
                     issue_date=None, due_date=None,
                     description="",
                     owner_name="", address="",
                     postal_code="", usage_type="",
                     meter_number="", file_number="",
                     city="", capacity=0,
                     bill_date="", check_duplicate=True):
    bill_type = str(bill_type or "").strip()
    if not bill_type:
        raise ValueError("نوع قبض الزامی است.")

    # ─── چک تکراری ─────
    if check_duplicate:
        dup_check = check_duplicate_bill(
            bill_type=bill_type,
            from_date=from_date,
            to_date=to_date,
            bill_identifier=bill_identifier,
            period=period,
        )
        if dup_check["exists"]:
            raise ValueError(dup_check["message"])

    from_d = parse_date(from_date)
    to_d = parse_date(to_date)

    days = 0
    if from_d and to_d:
        days = (to_d - from_d).days
        if days < 0:
            raise ValueError(
                "تاریخ پایان باید بعد از شروع باشد."
            )

    prev = float(previous_reading or 0)
    curr = float(current_reading or 0)
    consumption = max(curr - prev, 0)

    amt = float(amount or 0)

    daily_cons = (
        round(consumption / days, 2)
        if days > 0 else 0
    )
    daily_amt = (
        round(amt / days, 2)
        if days > 0 else 0
    )

    with SessionLocal() as db:
        building = _get_or_create_building(db)
        bill = UtilityBill(
            building_id=building.id,
            bill_type=bill_type,
            bill_identifier=str(
                bill_identifier or ""
            ).strip(),
            pay_identifier=str(
                pay_identifier or ""
            ).strip(),
            period=str(period or "").strip(),
            from_date=from_d,
            to_date=to_d,
            days_count=days,
            previous_reading=prev,
            current_reading=curr,
            consumption=consumption,
            daily_avg_consumption=daily_cons,
            amount=amt,
            daily_avg_amount=daily_amt,
            consumption_unit=str(
                consumption_unit or ""
            ).strip(),
            issue_date=parse_date(issue_date),
            due_date=parse_date(due_date),
            description=str(description or "").strip(),
            owner_name=str(owner_name or "").strip(),
            address=str(address or "").strip(),
            postal_code=str(postal_code or "").strip(),
            usage_type=str(usage_type or "").strip(),
            meter_number=str(meter_number or "").strip(),
            file_number=str(file_number or "").strip(),
            city=str(city or "").strip(),
            capacity=float(capacity or 0),
            bill_date=str(bill_date or "").strip(),
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)

        # ═══════════ ثبت خودکار در هزینه‌ها ═══════════
        try:
            expense_amount = amt / 10 if amt else 0

            expense_title = (
                f"قبض {bill_type} - "
                f"{period or bill_date or ''}"
            )

            expense_desc = (
                f"مصرف: {consumption:.0f} "
                f"{consumption_unit} در "
                f"{days} روز"
                if consumption else ""
            )

            expense_date_value = (
                parse_date(due_date)
                or parse_date(issue_date)
            )

            if expense_date_value is None and period:
                try:
                    period_parts = str(period).strip().split()
                    if len(period_parts) >= 2:
                        p_month_name = period_parts[0]
                        p_year = int(period_parts[-1])
                        if p_month_name in MONTHS:
                            p_month_idx = MONTHS.index(p_month_name) + 1
                            j_date = jdatetime.date(
                                p_year, p_month_idx, 1
                            )
                            expense_date_value = j_date.togregorian()
                except Exception as e:
                    print(f"⚠️ خطای تبدیل period به تاریخ: {e}")

            if expense_date_value is None:
                expense_date_value = date.today()

            expense = Expense(
                building_id=building.id,   # ⭐⭐ FIX
                title=expense_title.strip(),
                category=bill_type,
                amount=expense_amount,
                expense_date=expense_date_value,
                description=expense_desc,
            )
            db.add(expense)
            db.commit()
            db.refresh(expense)

            bill.related_expense_id = expense.id
            db.commit()

            print(
                f"✅ هزینه خودکار ثبت شد "
                f"(ID: {expense.id}, building_id: {building.id})"
            )
        except Exception as ex:
            print(f"⚠️ خطای ثبت هزینه خودکار: {ex}")

        return bill

def add_utility_bill_new(
    bill_type, bill_identifier,
    pay_identifier, period,
    from_date, to_date,
    previous_reading, current_reading,
    amount, consumption_unit,
    issue_date=None, due_date=None,
    description="",
    owner_name="", address="",
    postal_code="", usage_type="",
    meter_number="", file_number="",
    city="", capacity=0,
    bill_date="", check_duplicate=True,
    expense_date_override=None,
):
    """مثل add_utility_bill ولی تاریخ هزینه رو دستی می‌گیره"""
    bill_type = str(bill_type or "").strip()
    if not bill_type:
        raise ValueError("نوع قبض الزامی است.")

    if check_duplicate:
        dup_check = check_duplicate_bill(
            bill_type=bill_type,
            from_date=from_date,
            to_date=to_date,
            bill_identifier=bill_identifier,
            period=period,
        )
        if dup_check["exists"]:
            raise ValueError(dup_check["message"])

    from_d = parse_date(from_date)
    to_d = parse_date(to_date)

    days = 0
    if from_d and to_d:
        days = (to_d - from_d).days
        if days < 0:
            raise ValueError("تاریخ پایان باید بعد از شروع باشد.")

    prev = float(previous_reading or 0)
    curr = float(current_reading or 0)
    consumption = max(curr - prev, 0)
    amt = float(amount or 0)

    daily_cons = round(consumption / days, 2) if days > 0 else 0
    daily_amt = round(amt / days, 2) if days > 0 else 0

    with SessionLocal() as db:
        building = _get_or_create_building(db)
        bill = UtilityBill(
            building_id=building.id,
            bill_type=bill_type,
            bill_identifier=str(bill_identifier or "").strip(),
            pay_identifier=str(pay_identifier or "").strip(),
            period=str(period or "").strip(),
            from_date=from_d,
            to_date=to_d,
            days_count=days,
            previous_reading=prev,
            current_reading=curr,
            consumption=consumption,
            daily_avg_consumption=daily_cons,
            amount=amt,
            daily_avg_amount=daily_amt,
            consumption_unit=str(consumption_unit or "").strip(),
            issue_date=parse_date(issue_date),
            due_date=parse_date(due_date),
            description=str(description or "").strip(),
            owner_name=str(owner_name or "").strip(),
            address=str(address or "").strip(),
            postal_code=str(postal_code or "").strip(),
            usage_type=str(usage_type or "").strip(),
            meter_number=str(meter_number or "").strip(),
            file_number=str(file_number or "").strip(),
            city=str(city or "").strip(),
            capacity=float(capacity or 0),
            bill_date=str(bill_date or "").strip(),
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)

        # ─── ثبت خودکار در هزینه‌ها ───
        try:
            expense_amount = amt / 10 if amt else 0
            expense_title = (
                f"قبض {bill_type} - "
                f"{period or bill_date or ''}"
            )
            expense_desc = (
                f"مصرف: {consumption:.0f} "
                f"{consumption_unit} در {days} روز"
                if consumption else ""
            )

            if expense_date_override is not None:
                expense_date_value = expense_date_override
            else:
                expense_date_value = (
                    parse_date(due_date)
                    or parse_date(issue_date)
                    or date.today()
                )

            expense = Expense(
                building_id=building.id,   # ⭐⭐ FIX
                title=expense_title.strip(),
                category=bill_type,
                amount=expense_amount,
                expense_date=expense_date_value,
                description=expense_desc,
            )
            db.add(expense)
            db.commit()
            db.refresh(expense)

            bill.related_expense_id = expense.id
            db.commit()

            print(
                f"✅ هزینه خودکار ثبت شد "
                f"(ID: {expense.id}, building_id: {building.id})"
            )
        except Exception as ex:
            print(f"⚠️ خطای ثبت هزینه خودکار: {ex}")

        return bill

def list_utility_bills(bill_type=None):
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        query = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id
        )
        if bill_type and str(bill_type).strip():
            query = query.filter(
                UtilityBill.bill_type == str(bill_type).strip()
            )
        bills = query.all()

        # مرتب‌سازی بر اساس ترتیب واقعی ماه‌های شمسی
        bills = sorted(bills, key=_bill_sort_key)

        return [
            {
                "id": b.id,
                "bill_type": b.bill_type,
                "bill_identifier": b.bill_identifier,
                "pay_identifier": b.pay_identifier,
                "period": b.period,
                "from_date": b.from_date,
                "to_date": b.to_date,
                "days_count": b.days_count,
                "previous_reading": b.previous_reading,
                "current_reading": b.current_reading,
                "consumption": b.consumption,
                "daily_avg_consumption":
                    b.daily_avg_consumption,
                "amount": b.amount,
                "daily_avg_amount": b.daily_avg_amount,
                "consumption_unit": b.consumption_unit,
                "issue_date": b.issue_date,
                "due_date": b.due_date,
                "description": b.description,
                "owner_name": b.owner_name,
                "address": b.address,
                "postal_code": b.postal_code,
                "usage_type": b.usage_type,
                "meter_number": b.meter_number,
                "file_number": b.file_number,
                "city": b.city,
                "capacity": b.capacity,
                "bill_date": b.bill_date,
            }
            for b in bills
        ]
def get_consumption_chart_data(bill_type):
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id,
            UtilityBill.bill_type == str(bill_type).strip()
        ).all()

        bills = sorted(bills, key=_bill_sort_key)

        return [
            {
                "period": b.period,
                "consumption": b.consumption,
                "amount": b.amount,
                "daily_avg": b.daily_avg_consumption,
            }
            for b in bills
        ]
def delete_utility_bill(bill_id):
    with SessionLocal() as db:
        bill = db.query(UtilityBill).filter(
            UtilityBill.id == int(bill_id)
        ).first()
        if not bill:
            raise ValueError("قبض پیدا نشد.")

        # ⭐ حذف هزینه مرتبط
        if bill.related_expense_id:
            try:
                related_expense = db.query(Expense).filter(
                    Expense.id == bill.related_expense_id
                ).first()
                if related_expense:
                    db.delete(related_expense)
                    print(
                        f"🗑️ هزینه مرتبط حذف شد "
                        f"(ID: {bill.related_expense_id})"
                    )
            except Exception as ex:
                print(f"⚠️ خطای حذف هزینه: {ex}")

        db.delete(bill)
        db.commit()



def _generate_test_bill_data(bill_id, bill_type):
    """داده تستی برای قبض"""
    import random
    from datetime import timedelta

    random.seed(int(bill_id[-6:]))

    base_amounts = {
        "آب": (300000, 800000),
        "برق": (500000, 1500000),
        "گاز": (200000, 700000),
    }
    base_consumption = {
        "آب": (150, 350),
        "برق": (180, 450),
        "گاز": (80, 280),
    }
    consumption_units = {
        "آب": "m³",
        "برق": "kWh",
        "گاز": "m³",
    }

    amount_range = base_amounts.get(
        bill_type, (500000, 1000000)
    )
    cons_range = base_consumption.get(
        bill_type, (100, 300)
    )

    amount = random.randint(*amount_range)
    consumption = random.randint(*cons_range)
    prev_reading = random.randint(1000, 9000)
    current_reading = prev_reading + consumption

    today = jdatetime.date.today()
    from_date = today - timedelta(
        days=random.randint(28, 32)
    )
    to_date = today - timedelta(
        days=random.randint(1, 5)
    )
    due_date = today + timedelta(
        days=random.randint(10, 20)
    )

    pay_id = str(random.randint(
        1000000000000, 9999999999999
    ))

    period_month = MONTHS[from_date.month]
    period = f"{period_month} {from_date.year}"

    return {
        "success": True,
        "message": "✅ استعلام تستی موفق",
        "data": {
            "bill_id": bill_id,
            "pay_id": pay_id,
            "amount": amount,
            "current_reading": current_reading,
            "previous_reading": prev_reading,
            "consumption": consumption,
            "consumption_unit": consumption_units.get(
                bill_type, ""
            ),
            "period": period,
            "from_date": (
                f"{from_date.year}/"
                f"{from_date.month:02d}/"
                f"{from_date.day:02d}"
            ),
            "to_date": (
                f"{to_date.year}/"
                f"{to_date.month:02d}/"
                f"{to_date.day:02d}"
            ),
            "due_date": (
                f"{due_date.year}/"
                f"{due_date.month:02d}/"
                f"{due_date.day:02d}"
            ),
            "days_count": (
                to_date.togregorian() -
                from_date.togregorian()
            ).days,
            "issue_date": (
                f"{to_date.year}/"
                f"{to_date.month:02d}/"
                f"{to_date.day:02d}"
            ),
            "bill_date": (
                f"{to_date.year}/"
                f"{to_date.month:02d}/"
                f"{to_date.day:02d}"
            ),
            "owner_name": "کاربر تست",
            "address": "تهران - آدرس تستی",
            "postal_code": "1234567890",
            "usage_type": "خانگی",
            "meter_number": str(random.randint(
                100000, 999999
            )),
            "file_number": str(random.randint(
                100, 999
            )),
            "city": "تهران",
            "capacity": 25,
        }
    }


def get_bills_summary_by_period():
    """خلاصه قبوض به تفکیک ماه و کل (فقط ساختمون فعال)"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id
        ).order_by(UtilityBill.issue_date.asc().nulls_last()).all()

        monthly = {}
        yearly = {}
        all_time = {"آب": 0, "برق": 0, "گاز": 0, "total": 0}

        for b in bills:
            bill_type = b.bill_type
            amount = b.amount or 0

            if bill_type not in ["آب", "برق", "گاز"]:
                continue

            period = ""
            year = ""

            if b.issue_date:
                j = jdatetime.date.fromgregorian(date=b.issue_date)
                period = f"{MONTHS[j.month]} {j.year}"
                year = str(j.year)
            elif b.period:
                period = b.period
                parts = b.period.split()
                if len(parts) >= 2:
                    year = parts[-1]

            if not period:
                period = "نامشخص"
                year = "نامشخص"

            if period not in monthly:
                monthly[period] = {"آب": 0, "برق": 0, "گاز": 0, "total": 0}
            monthly[period][bill_type] += amount
            monthly[period]["total"] += amount

            if year not in yearly:
                yearly[year] = {"آب": 0, "برق": 0, "گاز": 0, "total": 0}
            yearly[year][bill_type] += amount
            yearly[year]["total"] += amount

            all_time[bill_type] += amount
            all_time["total"] += amount

        return {"monthly": monthly, "yearly": yearly, "all_time": all_time}


def check_duplicate_bill(bill_type, from_date=None,
                         to_date=None, bill_identifier=None,
                         period=None):
    """
    بررسی وجود قبض تکراری (فقط در ساختمون فعال)
    """
    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید

        query = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id,     # ← ⭐ جدید
            UtilityBill.bill_type == bill_type,
        )

        # چک بر اساس شناسه قبض + تاریخ‌ها
        if bill_identifier:
            existing = query.filter(
                UtilityBill.bill_identifier == str(
                    bill_identifier
                ).strip()
            ).all()

            for bill in existing:
                if from_date and to_date:
                    from_d = parse_date(from_date)
                    to_d = parse_date(to_date)
                    if (bill.from_date == from_d and
                            bill.to_date == to_d):
                        return {
                            "exists": True,
                            "existing_id": bill.id,
                            "message": (
                                f"این قبض قبلاً ثبت شده "
                                f"(شناسه قبض: {bill_identifier}، "
                                f"دوره: {bill.period or '-'})"
                            )
                        }

        # چک بر اساس دوره
        if period:
            dup = query.filter(
                UtilityBill.period == str(period).strip()
            ).first()
            if dup:
                return {
                    "exists": True,
                    "existing_id": dup.id,
                    "message": (
                        f"قبض {bill_type} برای دوره "
                        f"«{period}» قبلاً ثبت شده."
                    )
                }

        return {"exists": False}

def get_bill_stats(bill_type):
    """آمار قبوض یک نوع خاص (فقط ساختمون فعال)"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id,
            UtilityBill.bill_type == bill_type
        ).all()

        if not bills:
            return None

        total_cons = sum(b.consumption or 0 for b in bills)
        total_amt = sum(b.amount or 0 for b in bills)
        avg_monthly_cons = total_cons / len(bills) if bills else 0
        avg_monthly_amt = total_amt / len(bills) if bills else 0

        max_cons = max((b.consumption or 0 for b in bills), default=0)
        min_cons = min((b.consumption or 0 for b in bills), default=0)
        max_amt = max((b.amount or 0 for b in bills), default=0)
        min_amt = min((b.amount or 0 for b in bills), default=0)

        return {
            "count": len(bills),
            "total_consumption": total_cons,
            "total_amount": total_amt,
            "avg_monthly_consumption": avg_monthly_cons,
            "avg_monthly_amount": avg_monthly_amt,
            "max_consumption": max_cons,
            "min_consumption": min_cons,
            "max_amount": max_amt,
            "min_amount": min_amt,
        }


def get_all_bills_summary():
    """خلاصه کل قبوض (فقط ساختمون فعال)"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        summary = {
            "آب": {"count": 0, "total_amount": 0, "total_consumption": 0},
            "برق": {"count": 0, "total_amount": 0, "total_consumption": 0},
            "گاز": {"count": 0, "total_amount": 0, "total_consumption": 0},
        }

        for bill_type in summary.keys():
            bills = db.query(UtilityBill).filter(
                UtilityBill.building_id == building.id,
                UtilityBill.bill_type == bill_type
            ).all()

            summary[bill_type]["count"] = len(bills)
            summary[bill_type]["total_amount"] = sum(b.amount or 0 for b in bills)
            summary[bill_type]["total_consumption"] = sum(b.consumption or 0 for b in bills)

        summary["total_all"] = sum(
            summary[t]["total_amount"] for t in ["آب", "برق", "گاز"]
        )
        return summary


def get_bills_by_period(bill_type):
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id,
            UtilityBill.bill_type == bill_type
        ).order_by(UtilityBill.from_date.asc().nulls_last()).all()

        return [
            {
                "period": b.period or (b.bill_date or "-"),
                "amount": b.amount or 0,
                "consumption": b.consumption or 0,
                "issue_date": b.issue_date,
            }
            for b in bills
        ]


# ───────── محاسبه‌گر سهم قبوض ─────────

def calculate_bill_shares(bill_type, total_amount):
    """محاسبه سهم هر واحد (فقط ساختمون فعال)"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        units = db.query(Unit).filter(
            Unit.building_id == building.id,
            Unit.status == "ساکن"
        ).order_by(Unit.floor.asc(), Unit.number.asc()).all()

        if not units:
            return []

        total_amount = float(total_amount or 0)
        results = []

        if bill_type == "آب":
            total_people = sum(u.people_count or 0 for u in units)
            if total_people == 0:
                total_people = len(units)
                fallback_equal = True
            else:
                fallback_equal = False

            for u in units:
                people = 1 if fallback_equal else (u.people_count or 0)
                share = round((total_amount / total_people) * people, 0)
                results.append({
                    "unit_number": u.number,
                    "resident_name": u.resident_name,
                    "factor": people,
                    "factor_label": "نفر",
                    "share": share,
                    "total_factor": total_people,
                })

        elif bill_type == "گاز":
            total_area = sum(u.area or 0 for u in units)
            if total_area == 0:
                total_area = len(units)
                fallback_equal = True
            else:
                fallback_equal = False

            for u in units:
                area = 1 if fallback_equal else (u.area or 0)
                share = round((total_amount / total_area) * area, 0)
                results.append({
                    "unit_number": u.number,
                    "resident_name": u.resident_name,
                    "factor": area,
                    "factor_label": "m²",
                    "share": share,
                    "total_factor": total_area,
                })

        else:
            count = len(units)
            share = round(total_amount / count, 0)
            for u in units:
                results.append({
                    "unit_number": u.number,
                    "resident_name": u.resident_name,
                    "factor": 1,
                    "factor_label": "واحد",
                    "share": share,
                    "total_factor": count,
                })

        return results


# ───────── صدور خودکار شارژ ─────────

def check_and_auto_generate_charge():
    """بررسی و صدور خودکار شارژ ماه جاری (فقط ساختمون فعال)"""
    auto_enabled = _bs("auto_charge_enabled", "0")
    if auto_enabled != "1":
        return None

    method = _bs("auto_charge_method", "manual")
    value = _bs("auto_charge_value", "0")

    try:
        rate = float(value or 0)
    except ValueError:
        return None

    if rate <= 0:
        return None

    j = jdatetime.date.today()
    current_period = f"{MONTHS[j.month]} {j.year}"

    with SessionLocal() as db:
        building = _get_or_create_building(db)
        # ⭐ فقط واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        if unit_ids:
            existing = db.query(Charge).filter(
                Charge.unit_id.in_(unit_ids),
                Charge.period == current_period
            ).first()

            if existing:
                return None

    try:
        count = generate_monthly_charges(
            period=current_period,
            method=method,
            value=rate,
        )
        return {
            "period": current_period,
            "count": count,
            "method": method,
            "value": rate,
        }
    except Exception:
        return None

# ───────── پیامک ─────────

def send_sms(to, text):
    """
    ارسال پیامک با اپلیکیشن SMSGate روی گوشی اندروید.
    نسخه: android-sms-gateway 4.3.1
    """
    smsgate_username = _bs("smsgate_username", "").strip()  # ← تغییر
    smsgate_password = _bs("smsgate_password", "").strip()

    if not smsgate_username or not smsgate_password:
        return {
            "success": False,
            "message": "نام کاربری یا رمز SMSGate تنظیم نشده است. "
                       "به تنظیمات پیامک مراجعه کنید.",
            "recid": None
        }

    # ─── پاکسازی شماره به فرمت بین‌المللی ───
    phone = str(to or "").strip().replace(" ", "").replace("-", "")
    phone = phone.replace("(", "").replace(")", "")

    if phone.startswith("0098"):
        phone = "+98" + phone[4:]
    elif phone.startswith("0"):
        phone = "+98" + phone[1:]
    elif phone.startswith("98") and not phone.startswith("+"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+98" + phone

    try:
        from android_sms_gateway import client, domain

        message = domain.Message(
            phone_numbers=[phone],
            text_message=domain.TextMessage(text=text),
        )

        api = client.APIClient(
            smsgate_username,
            smsgate_password,
            base_url="https://api.sms-gate.app/3rdparty/v1",
        )

        with api:
            result = api.send(message)

        msg_id = getattr(result, "id", None)
        status_val = None
        for attr in ("state", "status", "message_state"):
            if hasattr(result, attr):
                status_val = getattr(result, attr)
                break
        status_str = str(status_val).lower() if status_val else ""

        if "fail" in status_str or "error" in status_str:
            return {
                "success": False,
                "message": f"ارسال ناموفق: {status_str}",
                "recid": msg_id,
            }

        return {
            "success": True,
            "message": "پیامک ارسال شد.",
            "recid": msg_id,
        }

    except Exception as ex:
        return {
            "success": False,
            "message": f"خطا در ارتباط با SMSGate: {str(ex)}",
            "recid": None
        }


def get_sms_credit():
    """
    چک کردن وضعیت اتصال SMSGate.
    """
    username = _bs("smsgate_username", "").strip()  # ← تغییر
    password = _bs("smsgate_password", "").strip()

    if not username or not password:
        return {
            "success": False,
            "message": "اطلاعات SMSGate تنظیم نشده",
            "credit": 0,
        }

    return {
        "success": True,
        "message": "اطلاعات SMSGate ذخیره شده (سرویس باید روی گوشی آنلاین باشد)",
        "credit": -1,
    }

def get_sms_template(template_key, unit_info=None, amount=None):
    """
    قالب‌های پیامک — مشترک بین صفحه‌ی پیامک و پیامک‌های خودکار.

    Args:
        template_key: "reminder" | "thanks" | "overdue" | "meeting"
        unit_info: dict یا آبجکت Unit
        amount: مبلغ (اختیاری)
    """
    # ─── اطلاعات پایه ───
    try:
        building_name = get_building_info().get("name") or "ساختمان"
    except Exception:
        building_name = "ساختمان"
    bank_card = _bs("bank_card", "") or "----"

    # ─── استخراج اطلاعات واحد ───
    unit_name = "کاربر"
    unit_number = "-"
    debt = amount or 0

    if unit_info:
        if isinstance(unit_info, dict):
            unit_name = unit_info.get("resident_name") or "کاربر"
            unit_number = str(unit_info.get("number") or "-")
            if amount is None:
                debt = unit_info.get("debt") or 0
        else:
            unit_name = getattr(unit_info, "resident_name", None) or "کاربر"
            unit_number = str(getattr(unit_info, "number", "-"))
            if amount is None:
                debt = getattr(unit_info, "debt", None) or 0

    templates = {
        "reminder": (
            f"🔔 یادآوری شارژ ماهانه\n\n"
            f"سلام {unit_name} عزیز\n"
            f"واحد {unit_number}\n\n"
            f"شارژ ماهانه شما به مبلغ "
            f"{debt:,.0f} می‌باشد.\n"
            f"لطفاً نسبت به پرداخت اقدام فرمایید.\n\n"
            f"💳 شماره کارت:\n{bank_card}\n\n"
            f"مدیریت {building_name}"
        ),
        "thanks": (
            f"🙏 تشکر از پرداخت\n\n"
            f"سلام {unit_name} عزیز\n"
            f"واحد {unit_number}\n\n"
            f"از پرداخت به‌موقع شارژ ماهانه شما "
            f"سپاسگزاریم. 🌷\n"
            f"همراهی شما موجب حفظ کیفیت "
            f"خدمات ساختمان می‌شود.\n\n"
            f"با تشکر\n"
            f"مدیریت {building_name}"
        ),
        "thanks_partial": (
            f"🙏 تشکر از پرداخت شما\n\n"
            f"سلام {unit_name} عزیز\n"
            f"واحد {unit_number}\n\n"
            f"پرداخت شما به مبلغ {debt:,.0f} تومان "
            f"با موفقیت ثبت شد. 🌷\n"
            f"از همراهی و حسن توجه شما سپاسگزاریم.\n\n"
            f"با کمال احترام، به‌نظر می‌رسد شارژ این دوره "
            f"هنوز کامل تسویه نشده است.\n"
            f"اگر فرصت داشتید، در زمان مناسب نسبت به "
            f"تکمیل تسویه اقدام فرمایید. "
            f"قطعاً در جریان امور ساختمان مؤثر خواهد بود.\n\n"
            f"💳 شماره کارت:\n{bank_card}\n\n"
            f"با سپاس فراوان\n"
            f"مدیریت {building_name}"
        ),
        "overdue": (
            f"⚠️ اخطار عدم پرداخت شارژ\n\n"
            f"{unit_name} عزیز - واحد {unit_number}\n\n"
            f"طبق سوابق، شما مبلغ "
            f"{debt:,.0f} بدهی معوق دارید.\n"
            f"خواهشمند است در اسرع وقت نسبت به "
            f"تسویه اقدام فرمایید.\n\n"
            f"💳 شماره کارت:\n{bank_card}\n\n"
            f"با احترام\n"
            f"مدیریت {building_name}"
        ),
        "meeting": (
            f"📅 اعلان جلسه هیئت مدیره\n\n"
            f"{unit_name} عزیز - واحد {unit_number}\n\n"
            f"بدینوسیله به اطلاع می‌رساند جلسه "
            f"هیئت مدیره ساختمان در تاریخ "
            f"[تاریخ] رأس ساعت [ساعت] در محل "
            f"[محل جلسه] برگزار خواهد شد.\n"
            f"حضور جنابعالی موجب امتنان است.\n\n"
            f"دستور جلسه:\n۱- ...\n۲- ...\n\n"
            f"مدیریت {building_name}"
        ),
        "custom": "",
    }

    return templates.get(template_key, "")

def send_payment_thanks_sms(unit, amount, remaining_after=0):
    """
    ارسال پیامک تشکر پس از ثبت پرداخت.
    - remaining_after == 0 → فقط تشکر
    - remaining_after > 0 → تشکر + یادآوری محترمانه
    """
    if _bs("sms_thanks_on_payment", "0") != "1":
        return {"sent": False, "reason": "disabled"}

    phone = (unit.phone or "").strip()
    if not phone:
        return {"sent": False, "reason": "no_phone"}

    try:
        if remaining_after and remaining_after > 0:
            text = get_sms_template("thanks_partial", unit_info=unit, amount=amount)
        else:
            text = get_sms_template("thanks", unit_info=unit)

        result = send_sms(phone, text)
        if result.get("success"):
            return {"sent": True, "reason": "ok"}
        return {
            "sent": False,
            "reason": "send_failed",
            "error": result.get("message", ""),
        }
    except Exception as ex:
        return {"sent": False, "reason": "exception", "error": str(ex)}
# ───────── تنظیمات ─────────

def get_setting(key, default=""):
    with SessionLocal() as db:
        row = db.query(AppSetting).filter(
            AppSetting.key == key
        ).first()
        return row.value if row else default


def set_setting(key, value):
    with SessionLocal() as db:
        row = db.query(AppSetting).filter(
            AppSetting.key == key
        ).first()
        if row:
            row.value = str(value or "")
        else:
            row = AppSetting(
                key=key, value=str(value or "")
            )
            db.add(row)
        db.commit()

# ═══════════ تنظیمات مخصوص هر ساختمان ═══════════

def _bs(key, default=""):
    """
    گرفتن تنظیم مخصوص ساختمون فعال.
    کلید ذخیره: <key>_b<building_id>

    نکته مهم: اگه مقدار per-building پیدا نشد، default برگردون
    (نه مقدار global قدیمی) — وگرنه همه ساختمون‌ها یه مقدار
    مشترک رو نشون می‌دن.
    """
    try:
        bid = _get_active_building_id()
        if bid is not None:
            val = get_setting(f"{key}_b{bid}", None)
            if val is not None and str(val).strip() != "":
                return val
            # ⭐ اگه per-building نبود، default رو برگردون
            return default
    except Exception:
        pass
    return default  # ← نه get_setting(key, default)


def _bsset(key, value):
    """
    ذخیره تنظیم مخصوص ساختمون فعال.
    """
    try:
        bid = _get_active_building_id()
        if bid is not None:
            set_setting(f"{key}_b{bid}", str(value or ""))
            return
    except Exception:
        pass
    set_setting(key, str(value or ""))

def get_charge_periods_list():
    """لیست همه دوره‌های شارژ (برای فیلتر)"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        rows = db.query(Charge.period).join(
            Unit, Charge.unit_id == Unit.id
        ).filter(
            Unit.building_id == building.id
        ).distinct().all()
        result = [p[0] for p in rows if p[0]]
        result.sort(reverse=True)  # جدیدترین اول
        return result

def check_and_apply_late_fees():
    """اعمال جریمه دیرکرد (فقط ساختمون فعال)"""
    late_fee_enabled = _bs("late_fee_enabled", "0")
    if late_fee_enabled != "1":
        return None

    try:
        fee_amount = float(_bs("late_fee_amount", "100000") or 100000)
    except ValueError:
        fee_amount = 100000

    today = date.today()
    applied_count = 0

    with SessionLocal() as db:
        building = _get_or_create_building(db)
        # ⭐ فقط واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        if not unit_ids:
            return None

        charges = db.query(Charge).filter(
            Charge.unit_id.in_(unit_ids),
            Charge.status.in_(["پرداخت نشده", "ناقص"]),
            Charge.due_date < today
        ).all()

        for charge in charges:
            if charge.notes and "جریمه_دیرکرد" in charge.notes:
                continue
            charge.amount = (charge.amount or 0) + fee_amount
            charge.notes = (
                (charge.notes or "") +
                f"|جریمه_دیرکرد:{fee_amount:.0f}"
            )
            applied_count += 1

        db.commit()

    if applied_count > 0:
        return {"count": applied_count, "fee_amount": fee_amount}
    return None


def get_dashboard_advanced_data():
    """داده‌های پیشرفته داشبورد (فقط ساختمون فعال)"""
    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ ID واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        j = jdatetime.date.today()
        current_period = f"{MONTHS[j.month]} {j.year}"

        # ─── شارژهای ماه جاری همین ساختمون ───
        current_charges = []
        if unit_ids:
            current_charges = db.query(Charge).filter(
                Charge.unit_id.in_(unit_ids),
                Charge.period == current_period
            ).all()

        current_total = sum(c.amount or 0 for c in current_charges)
        current_paid = sum(c.paid_amount or 0 for c in current_charges)
        current_unpaid = current_total - current_paid
        current_percent = (
            (current_paid / current_total * 100)
            if current_total > 0 else 0
        )

        # ─── ماه قبل ───
        prev_month = j.month - 1
        prev_year = j.year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        prev_period = f"{MONTHS[prev_month]} {prev_year}"

        prev_charges = []
        if unit_ids:
            prev_charges = db.query(Charge).filter(
                Charge.unit_id.in_(unit_ids),
                Charge.period == prev_period
            ).all()
        prev_total = sum(c.amount or 0 for c in prev_charges)
        prev_paid = sum(c.paid_amount or 0 for c in prev_charges)

        # ─── ۶ ماه اخیر پرداخت‌ها ───
        payments_by_month = {}
        if unit_ids:
            payments = db.query(Payment).filter(
                Payment.unit_id.in_(unit_ids)
            ).order_by(Payment.payment_date.desc()).limit(200).all()

            for p in payments:
                if p.payment_date:
                    jp = jdatetime.date.fromgregorian(date=p.payment_date)
                    key = f"{MONTHS[jp.month]}"
                    if key not in payments_by_month:
                        payments_by_month[key] = 0
                    payments_by_month[key] += (p.amount or 0)

        # ─── هزینه‌های اخیر همین ساختمون ───
        expenses = db.query(Expense).filter(
            Expense.building_id == building.id
        ).order_by(Expense.created_at.desc()).limit(5).all()

        recent_expenses = [
            {
                "title": e.title,
                "amount": e.amount,
                "category": e.category,
                "date": e.expense_date,
            }
            for e in expenses
        ]

        return {
            "current_period": current_period,
            "current_total": current_total,
            "current_paid": current_paid,
            "current_unpaid": current_unpaid,
            "current_percent": current_percent,
            "prev_period": prev_period,
            "prev_total": prev_total,
            "prev_paid": prev_paid,
            "payments_by_month": payments_by_month,
            "recent_expenses": recent_expenses,
        }
# ───────── داشبورد ─────────

def get_dashboard_data():
    with SessionLocal() as db:
        building = _get_or_create_building(db)
        units = list_units_with_debt()

        total_units = len(units)
        occupied = len(
            [u for u in units if u["status"] == "ساکن"]
        )
        vacant = len(
            [u for u in units if u["status"] == "خالی"]
        )
        debtors = len(
            [u for u in units if u["debt"] > 0]
        )
        total_debt = sum(u["debt"] for u in units)

        unit_ids = [u["id"] for u in units]

        # ─── جمع پرداخت‌های همین ساختمون ───
        payments_total = 0
        if unit_ids:
            payments_total = db.query(
                func.coalesce(func.sum(Payment.amount), 0)
            ).filter(
                Payment.unit_id.in_(unit_ids)
            ).scalar() or 0

        # ─── جمع شارژهای همین ساختمون ───
        charges_total = 0
        if unit_ids:
            charges_total = db.query(
                func.coalesce(func.sum(Charge.amount), 0)
            ).filter(
                Charge.unit_id.in_(unit_ids)
            ).scalar() or 0

        # ─── جمع هزینه‌های همین ساختمون ───
        expenses_total = db.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.building_id == building.id
        ).scalar() or 0

        initial_balance = float(
            _bs("initial_balance", "0") or 0
        )

        cash_balance = (
            initial_balance + payments_total -
            expenses_total
        )

        return {
            "building_name": building.name,
            "total_units": total_units,
            "occupied_units": occupied,
            "vacant_units": vacant,
            "debtors": debtors,
            "total_debt": total_debt,
            "payments_total": payments_total,
            "expenses_total": expenses_total,
            "charges_total": charges_total,
            "initial_balance": initial_balance,
            "cash_balance": cash_balance,
        }
# ═══════════ بکاپ‌گیری از دیتابیس ═══════════

import shutil
import os


def get_backups_dir():
    """گرفتن مسیر پوشه بکاپ‌ها"""
    backups_dir = os.path.join(
        os.getcwd(), "backups"
    )
    os.makedirs(backups_dir, exist_ok=True)
    return backups_dir


def get_db_path():
    """گرفتن مسیر فایل دیتابیس"""
    return os.path.join(
        os.getcwd(), "building_manager.db"
    )


def create_backup(auto=False):
    """
    ساخت بکاپ از دیتابیس

    Args:
        auto: آیا بکاپ خودکار هست؟

    Returns:
        {"success": bool, "path": str, "message": str}
    """
    try:
        db_path = get_db_path()

        if not os.path.exists(db_path):
            return {
                "success": False,
                "path": None,
                "message": "فایل دیتابیس پیدا نشد.",
            }

        backups_dir = get_backups_dir()

        # نام فایل با تاریخ شمسی
        j = jdatetime.datetime.now()
        prefix = "auto" if auto else "manual"
        filename = (
            f"backup_{prefix}_"
            f"{j.year}-{j.month:02d}-{j.day:02d}_"
            f"{j.hour:02d}-{j.minute:02d}-{j.second:02d}"
            f".db"
        )

        backup_path = os.path.join(
            backups_dir, filename
        )

        # کپی فایل
        shutil.copy2(db_path, backup_path)

        return {
            "success": True,
            "path": backup_path,
            "message": f"بکاپ با موفقیت ساخته شد.",
            "filename": filename,
        }

    except Exception as ex:
        return {
            "success": False,
            "path": None,
            "message": f"خطای بکاپ: {ex}",
        }


def list_backups():
    """
    لیست همه بکاپ‌ها به همراه اطلاعات
    """
    try:
        backups_dir = get_backups_dir()
        backups = []

        for filename in os.listdir(backups_dir):
            if not filename.endswith('.db'):
                continue

            filepath = os.path.join(
                backups_dir, filename
            )

            # اطلاعات فایل
            stat = os.stat(filepath)
            size_kb = stat.st_size / 1024
            mtime = stat.st_mtime

            # تبدیل timestamp به تاریخ شمسی
            from datetime import datetime
            greg_date = datetime.fromtimestamp(mtime)
            j_date = jdatetime.datetime.fromgregorian(
                datetime=greg_date
            )

            # نوع بکاپ
            backup_type = "خودکار"
            if "manual" in filename:
                backup_type = "دستی"

            backups.append({
                "filename": filename,
                "filepath": filepath,
                "size_kb": round(size_kb, 2),
                "date": (
                    f"{j_date.year}/"
                    f"{j_date.month:02d}/"
                    f"{j_date.day:02d}"
                ),
                "time": (
                    f"{j_date.hour:02d}:"
                    f"{j_date.minute:02d}"
                ),
                "type": backup_type,
                "timestamp": mtime,
            })

        # مرتب‌سازی بر اساس زمان (جدیدترین اول)
        backups.sort(
            key=lambda x: x["timestamp"], reverse=True
        )

        return backups

    except Exception as ex:
        print(f"❌ خطای لیست بکاپ‌ها: {ex}")
        return []


def restore_backup(backup_path):
    """
    بازیابی از بکاپ

    Args:
        backup_path: مسیر فایل بکاپ

    Returns:
        {"success": bool, "message": str}
    """
    try:
        if not os.path.exists(backup_path):
            return {
                "success": False,
                "message": "فایل بکاپ پیدا نشد.",
            }

        db_path = get_db_path()

        # اول یه بکاپ از حالت فعلی بگیر (احتیاطی)
        if os.path.exists(db_path):
            safety_backup = create_backup(auto=True)
            print(
                f"🛡️ بکاپ احتیاطی: "
                f"{safety_backup.get('filename')}"
            )

        # جایگزینی
        shutil.copy2(backup_path, db_path)

        # نکته: بدون این خط، اتصال‌های بازِ SQLAlchemy (connection
        # pool) هنوز به فایل قدیمیِ دیتابیس اشاره داشتن، پس کوئری‌های
        # بعدی توی همون اجرای برنامه ممکن بود همچنان داده‌ی قدیمی رو
        # نشون بدن — دقیقاً همون چیزی که باعث می‌شد بازیابی «آنی»
        # نباشه و کاربر مجبور بشه کل برنامه رو ببنده و باز کنه.
        # dispose() تمام اتصال‌های باز رو می‌بنده تا کوئری بعدی، یه
        # اتصال تازه به فایل تازه‌ی روی دیسک بگیره.
        engine.dispose()

        return {
            "success": True,
            "message": "بکاپ با موفقیت بازیابی شد.",
        }

    except Exception as ex:
        return {
            "success": False,
            "message": f"خطای بازیابی: {ex}",
        }


def delete_backup(backup_path):
    """حذف یک فایل بکاپ"""
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return {
                "success": True,
                "message": "بکاپ حذف شد.",
            }
        return {
            "success": False,
            "message": "فایل پیدا نشد.",
        }
    except Exception as ex:
        return {
            "success": False,
            "message": f"خطا: {ex}",
        }


def cleanup_old_backups(days=30):
    """
    حذف بکاپ‌های قدیمی‌تر از N روز
    """
    try:
        import time
        current_time = time.time()
        cutoff = current_time - (days * 24 * 60 * 60)

        backups_dir = get_backups_dir()
        deleted_count = 0

        for filename in os.listdir(backups_dir):
            if not filename.endswith('.db'):
                continue

            filepath = os.path.join(
                backups_dir, filename
            )

            # فقط بکاپ‌های خودکار قدیمی رو حذف کن
            if "auto" not in filename:
                continue

            file_mtime = os.path.getmtime(filepath)
            if file_mtime < cutoff:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception:
                    pass

        return deleted_count

    except Exception as ex:
        print(f"❌ خطای cleanup: {ex}")
        return 0


def get_backup_stats():
    """آمار بکاپ‌ها"""
    try:
        backups = list_backups()
        total_size = sum(b["size_kb"] for b in backups)

        auto_count = len(
            [b for b in backups if b["type"] == "خودکار"]
        )
        manual_count = len(
            [b for b in backups if b["type"] == "دستی"]
        )

        return {
            "total": len(backups),
            "auto": auto_count,
            "manual": manual_count,
            "total_size_kb": round(total_size, 2),
            "total_size_mb": round(
                total_size / 1024, 2
            ),
        }
    except Exception:
        return {
            "total": 0,
            "auto": 0,
            "manual": 0,
            "total_size_kb": 0,
            "total_size_mb": 0,
        }
# ═══════════ سیستم کاربری ═══════════

import hashlib
import re


def hash_password(password):
    """Hash کردن رمز عبور با SHA-256"""
    return hashlib.sha256(
        password.encode('utf-8')
    ).hexdigest()


def validate_password(password):
    """
    اعتبارسنجی رمز عبور:
    - حداقل 8 کاراکتر
    - شامل حداقل یک حرف
    - شامل حداقل یک عدد
    """
    if not password or len(password) < 8:
        return {
            "valid": False,
            "message": "رمز باید حداقل 8 کاراکتر باشد.",
        }

    if not re.search(r'[a-zA-Z]', password):
        return {
            "valid": False,
            "message": "رمز باید شامل حداقل یک حرف انگلیسی باشد.",
        }

    if not re.search(r'[0-9]', password):
        return {
            "valid": False,
            "message": "رمز باید شامل حداقل یک عدد باشد.",
        }

    return {"valid": True, "message": "رمز معتبر است."}


def has_any_user():
    """آیا حداقل یک کاربر ثبت شده؟"""
    from models import User
    with SessionLocal() as db:
        count = db.query(User).count()
        return count > 0


def create_user(
    username,
    password,
    full_name="",
    security_question="",
    security_answer="",
    role="admin",
):
    """
    ساخت کاربر جدید
    """
    from models import User

    username = str(username or "").strip().lower()
    password = str(password or "")
    full_name = str(full_name or "").strip()
    security_question = str(
        security_question or ""
    ).strip()
    security_answer = str(
        security_answer or ""
    ).strip().lower()

    # اعتبارسنجی نام کاربری
    if not username:
        raise ValueError("نام کاربری الزامی است.")

    if len(username) < 3:
        raise ValueError(
            "نام کاربری باید حداقل 3 کاراکتر باشد."
        )

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError(
            "نام کاربری فقط شامل حروف انگلیسی، اعداد و _ باشد."
        )

    # اعتبارسنجی رمز
    pwd_check = validate_password(password)
    if not pwd_check["valid"]:
        raise ValueError(pwd_check["message"])

    # اعتبارسنجی سوال امنیتی
    if not security_question or not security_answer:
        raise ValueError(
            "سوال امنیتی و پاسخ آن الزامی است."
        )

    with SessionLocal() as db:
        # چک تکراری نبودن
        existing = db.query(User).filter(
            User.username == username
        ).first()

        if existing:
            raise ValueError(
                "این نام کاربری قبلاً ثبت شده است."
            )

        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            security_question=security_question,
            security_answer_hash=hash_password(
                security_answer
            ),
            role=role,
            is_active=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
        }


def authenticate(username, password):
    """
    احراز هویت کاربر

    Returns:
        {"success": bool, "user": dict|None, "message": str}
    """
    from models import User

    username = str(username or "").strip().lower()
    password = str(password or "")

    if not username or not password:
        return {
            "success": False,
            "user": None,
            "message": "نام کاربری و رمز الزامی است.",
        }

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            return {
                "success": False,
                "user": None,
                "message": "نام کاربری یا رمز اشتباه است.",
            }

        if user.is_active != 1:
            return {
                "success": False,
                "user": None,
                "message": "این حساب غیرفعال است.",
            }

        if user.password_hash != hash_password(password):
            return {
                "success": False,
                "user": None,
                "message": "نام کاربری یا رمز اشتباه است.",
            }

        # بروزرسانی زمان آخرین ورود
        user.last_login = datetime.now()
        db.commit()

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "security_question": (
                    user.security_question
                ),
            },
            "message": "ورود موفق.",
        }


def get_security_question(username):
    """گرفتن سوال امنیتی کاربر"""
    from models import User

    username = str(username or "").strip().lower()

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            return {
                "success": False,
                "question": None,
                "message": "کاربر پیدا نشد.",
            }

        return {
            "success": True,
            "question": user.security_question,
            "message": "",
        }


def verify_security_answer(username, answer):
    """بررسی پاسخ سوال امنیتی"""
    from models import User

    username = str(username or "").strip().lower()
    answer = str(answer or "").strip().lower()

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            return {
                "success": False,
                "message": "کاربر پیدا نشد.",
            }

        if user.security_answer_hash != hash_password(
            answer
        ):
            return {
                "success": False,
                "message": "پاسخ اشتباه است.",
            }

        return {
            "success": True,
            "message": "پاسخ صحیح.",
        }


def reset_password(username, new_password):
    """
    ریست رمز (بعد از تایید سوال امنیتی)
    """
    from models import User

    username = str(username or "").strip().lower()

    pwd_check = validate_password(new_password)
    if not pwd_check["valid"]:
        raise ValueError(pwd_check["message"])

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            raise ValueError("کاربر پیدا نشد.")

        user.password_hash = hash_password(new_password)
        db.commit()

        return True


def change_password(user_id, old_password, new_password):
    """تغییر رمز کاربر (نیاز به رمز قدیمی)"""
    from models import User

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.id == int(user_id)
        ).first()

        if not user:
            raise ValueError("کاربر پیدا نشد.")

        # بررسی رمز قدیمی
        if user.password_hash != hash_password(
            old_password
        ):
            raise ValueError("رمز فعلی اشتباه است.")

        # اعتبارسنجی رمز جدید
        pwd_check = validate_password(new_password)
        if not pwd_check["valid"]:
            raise ValueError(pwd_check["message"])

        user.password_hash = hash_password(new_password)
        db.commit()

        return True


def update_user_profile(user_id, full_name=None):
    """بروزرسانی اطلاعات کاربر"""
    from models import User

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.id == int(user_id)
        ).first()

        if not user:
            raise ValueError("کاربر پیدا نشد.")

        if full_name is not None:
            user.full_name = str(full_name).strip()

        db.commit()
        return True


def get_user_by_id(user_id):
    """گرفتن اطلاعات کاربر"""
    from models import User

    with SessionLocal() as db:
        user = db.query(User).filter(
            User.id == int(user_id)
        ).first()

        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "security_question": user.security_question,
            "is_active": user.is_active,
            "last_login": user.last_login,
        }


# ═══════════ ذخیره session (مرا به خاطر بسپار) ═══════════

def save_remember_me(user_id, password=None):
    """ذخیره ID کاربر و رمز عبور (رمزنگاری‌شده) برای Remember Me"""
    set_setting("remembered_user_id", str(user_id))
    if password:
        encrypted_password = encrypt_text(str(password))
        set_setting("remembered_password", encrypted_password)
    else:
        set_setting("remembered_password", "")
def get_remembered_user():
    """گرفتن کاربر ذخیره شده و رمز عبور (رمزگشایی‌شده)"""
    user_id = get_setting("remembered_user_id", "")
    encrypted_password = get_setting("remembered_password", "")
    if user_id:
        try:
            user = get_user_by_id(int(user_id))
            if user:
                password = decrypt_text(encrypted_password) if encrypted_password else ""
                return {"user": user, "password": password}
        except Exception:
            return None
    return None
def clear_remember_me():
    """پاک کردن Remember Me (هم کاربر و هم رمز)"""
    set_setting("remembered_user_id", "")
    set_setting("remembered_password", "")
# ═══════════ کاربرگ واحد ═══════════

def get_unit_full_report(unit_id):
    with SessionLocal() as db:
        unit = db.query(Unit).filter(
            Unit.id == int(unit_id)
        ).first()

        if not unit:
            return None

        charges = db.query(Charge).filter(
            Charge.unit_id == unit.id
        ).order_by(Charge.created_at.desc()).all()

        charges_list = []
        total_charges = 0
        total_paid = 0

        for c in charges:
            remaining = max(
                (c.amount or 0) - (c.paid_amount or 0), 0
            )
            total_charges += c.amount or 0
            total_paid += c.paid_amount or 0

            charges_list.append({
                "id": c.id,
                "period": c.period,
                "method": c.calculation_method,
                "amount": c.amount,
                "paid_amount": c.paid_amount,
                "remaining": remaining,
                "status": c.status,
                "due_date": c.due_date,
                "created_at": c.created_at,
            })

        payments = db.query(Payment).filter(
            Payment.unit_id == unit.id
        ).order_by(
            Payment.payment_date.desc().nulls_last(),
            Payment.created_at.desc()
        ).all()

        payments_list = []
        total_payments = 0

        for p in payments:
            total_payments += p.amount or 0
            payments_list.append({
                "id": p.id,
                "amount": p.amount,
                "payment_date": p.payment_date,
                "payment_method": p.payment_method,
                "tracking_code": p.tracking_code,
                "description": p.description,
                "receipt_image": p.receipt_image or "",
                "created_at": p.created_at,
            })

        total_debt = max(total_charges - total_paid, 0)
        collection_percent = (
            (total_paid / total_charges * 100)
            if total_charges > 0 else 0
        )

        return {
            "unit": {
                "id": unit.id,
                "number": unit.number,
                "floor": unit.floor,
                "area": unit.area,
                "people_count": unit.people_count,
                "resident_name": unit.resident_name,
                "phone": unit.phone,
                "resident_type": unit.resident_type,
                "status": unit.status,
                "notes": unit.notes,
            },
            "summary": {
                "total_charges": total_charges,
                "total_paid": total_paid,
                "total_payments": total_payments,
                "total_debt": total_debt,
                "collection_percent": collection_percent,
                "charges_count": len(charges_list),
                "payments_count": len(payments_list),
            },
            "charges": charges_list,
            "payments": payments_list,
        }

# ═══════════ سیستم نوتیفیکیشن ═══════════

def add_notification(
    type,
    title,
    message="",
    priority="normal",
    related_unit_id=None,
    related_charge_id=None,
):
    """اضافه کردن نوتیفیکیشن جدید"""
    from models import Notification

    with SessionLocal() as db:
        notif = Notification(
            type=type,
            title=str(title or "").strip(),
            message=str(message or "").strip(),
            priority=priority,
            related_unit_id=related_unit_id,
            related_charge_id=related_charge_id,
            is_read=0,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif.id


def list_notifications(unread_only=False, limit=50):
    """لیست نوتیفیکیشن‌ها"""
    from models import Notification

    with SessionLocal() as db:
        query = db.query(Notification).order_by(
            Notification.created_at.desc()
        )

        if unread_only:
            query = query.filter(
                Notification.is_read == 0
            )

        notifs = query.limit(limit).all()

        return [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "priority": n.priority,
                "is_read": n.is_read,
                "related_unit_id": n.related_unit_id,
                "related_charge_id": (
                    n.related_charge_id
                ),
                "created_at": n.created_at,
                "read_at": n.read_at,
            }
            for n in notifs
        ]


def count_unread_notifications():
    """تعداد نوتیفیکیشن‌های خوانده نشده"""
    from models import Notification

    with SessionLocal() as db:
        count = db.query(Notification).filter(
            Notification.is_read == 0
        ).count()
        return count


def mark_notification_read(notif_id):
    """علامت گذاری به عنوان خوانده شده"""
    from models import Notification

    with SessionLocal() as db:
        notif = db.query(Notification).filter(
            Notification.id == int(notif_id)
        ).first()

        if notif:
            notif.is_read = 1
            notif.read_at = datetime.now()
            db.commit()
            return True
        return False


def mark_all_notifications_read():
    """همه رو خوانده شده کن"""
    from models import Notification

    with SessionLocal() as db:
        db.query(Notification).filter(
            Notification.is_read == 0
        ).update({
            "is_read": 1,
            "read_at": datetime.now(),
        })
        db.commit()


def delete_notification(notif_id):
    """حذف نوتیفیکیشن"""
    from models import Notification

    with SessionLocal() as db:
        notif = db.query(Notification).filter(
            Notification.id == int(notif_id)
        ).first()

        if notif:
            db.delete(notif)
            db.commit()
            return True
        return False


def delete_all_notifications():
    """حذف همه نوتیفیکیشن‌ها"""
    from models import Notification

    with SessionLocal() as db:
        db.query(Notification).delete()
        db.commit()


def cleanup_old_notifications(days=30):
    """حذف نوتیفیکیشن‌های قدیمی خوانده شده"""
    from models import Notification
    from datetime import timedelta

    cutoff = datetime.now() - timedelta(days=days)

    with SessionLocal() as db:
        deleted = db.query(Notification).filter(
            Notification.is_read == 1,
            Notification.created_at < cutoff
        ).delete()
        db.commit()
        return deleted


# ═══════════ چک خودکار نوتیفیکیشن‌ها ═══════════

def check_and_create_auto_notifications():
    """چک و ساخت نوتیفیکیشن‌های خودکار (فقط ساختمون فعال)"""
    from models import Notification, Charge, Unit
    from datetime import timedelta

    created = []
    created_items = []
    today = date.today()

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ شارژهای سررسید نزدیک همین ساختمون
        soon_deadline = today + timedelta(days=3)

        near_due_charges = db.query(Charge, Unit).join(
            Unit, Charge.unit_id == Unit.id
        ).filter(
            Unit.building_id == building.id,
            Charge.status.in_(["پرداخت نشده", "ناقص"]),
            Charge.due_date <= soon_deadline,
            Charge.due_date >= today,
        ).all()

        for charge, unit in near_due_charges:
            existing = db.query(Notification).filter(
                Notification.type == "charge_due",
                Notification.related_charge_id == charge.id,
            ).first()

            if existing:
                continue

            days_left = (charge.due_date - today).days
            title = "⏰ شارژ نزدیک به سررسید"
            message = (
                f"شارژ واحد {unit.number} "
                f"({charge.period}) "
                f"در {days_left} روز آینده سررسید می‌شود.\n"
                f"مبلغ باقیمانده: "
                f"{max((charge.amount or 0) - (charge.paid_amount or 0), 0):,.0f}"
            )

            notif = Notification(
                type="charge_due",
                title=title,
                message=message,
                priority="normal",
                related_unit_id=unit.id,
                related_charge_id=charge.id,
                is_read=0,
            )
            db.add(notif)
            created.append("charge_due")
            created_items.append({"title": title, "message": message})

        # ─── بدهی معوق همین ساختمون ───
        overdue_charges = db.query(Charge, Unit).join(
            Unit, Charge.unit_id == Unit.id
        ).filter(
            Unit.building_id == building.id,
            Charge.status.in_(["پرداخت نشده", "ناقص"]),
            Charge.due_date < today,
        ).all()

        for charge, unit in overdue_charges:
            existing = db.query(Notification).filter(
                Notification.type == "debt",
                Notification.related_charge_id == charge.id,
            ).first()

            if existing:
                continue

            days_overdue = (today - charge.due_date).days
            title = "⚠️ بدهی معوق"
            message = (
                f"واحد {unit.number} "
                f"({charge.period}) "
                f"{days_overdue} روز از سررسید گذشته.\n"
                f"مبلغ بدهی: "
                f"{max((charge.amount or 0) - (charge.paid_amount or 0), 0):,.0f}"
            )

            notif = Notification(
                type="debt",
                title=title,
                message=message,
                priority="high",
                related_unit_id=unit.id,
                related_charge_id=charge.id,
                is_read=0,
            )
            db.add(notif)
            created.append("debt")
            created_items.append({"title": title, "message": message})

        db.commit()

    return {
        "count": len(created),
        "types": created,
        "items": created_items,
    }
# ═══════════ رمزنگاری رمز عبور برای Remember Me ═══════════

def _get_encryption_key():
    """
    ایجاد یا بازیابی کلید رمزنگاری از تنظیمات
    اگر کلید وجود نداشته باشد، یک کلید جدید ساخته می‌شود
    """
    key = get_setting("encryption_key", "")
    if not key:
        # ساخت کلید جدید با استفاده از یک عبارت ثابت + salt
        # این کار باعث می‌شود کلید در هر بار اجرا یکسان باشد
        secret = "MyBuildingManagerSecretKey2024!@#$"  # می‌توانید این را تغییر دهید
        key = base64.urlsafe_b64encode(
            hashlib.sha256(secret.encode()).digest()
        ).decode()
        set_setting("encryption_key", key)
    return key.encode()


def encrypt_text(text):
    """رمزنگاری متن"""
    if not text:
        return ""
    try:
        key = _get_encryption_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception:
        return ""


def decrypt_text(encrypted_text):
    """رمزگشایی متن"""
    if not encrypted_text:
        return ""
    try:
        key = _get_encryption_key()
        cipher = Fernet(key)
        decrypted = cipher.decrypt(
            base64.urlsafe_b64decode(encrypted_text.encode())
        )
        return decrypted.decode()
    except Exception:
        return ""

# ═══════════ اعلان‌های داشبورد ═══════════

def get_dashboard_alerts():
    """اعلان‌های مهم برای بالای داشبورد (فقط ساختمون فعال)"""
    from datetime import timedelta

    today = date.today()
    alerts = []

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ فقط واحدهای ساختمون فعال
        units = db.query(Unit).filter(
            Unit.building_id == building.id
        ).all()

        # ⭐ فقط قبض‌های ساختمون فعال
        # (unitهای قبلی)

        debtors_count = 0
        total_debt = 0

        for unit in units:
            charges = db.query(Charge).filter(
                Charge.unit_id == unit.id
            ).all()
            debt = sum(
                max((c.amount or 0) - (c.paid_amount or 0), 0)
                for c in charges
            )
            if debt > 0:
                debtors_count += 1
                total_debt += debt

        if debtors_count > 0:
            alerts.append({
                "type": "danger",
                "icon": "⚠️",
                "title": f"{debtors_count} واحد بدهکار",
                "value": total_debt,
                "action": "units",
            })

        # ⭐ شارژهای این ساختمون
        unit_ids = [u.id for u in units]

        if unit_ids:
            near_deadline = today + timedelta(days=7)
            near_due = db.query(Charge).filter(
                Charge.unit_id.in_(unit_ids),
                Charge.status.in_(["پرداخت نشده", "ناقص"]),
                Charge.due_date <= near_deadline,
                Charge.due_date >= today,
            ).count()

            if near_due > 0:
                alerts.append({
                    "type": "warning",
                    "icon": "⏰",
                    "title": f"{near_due} شارژ نزدیک سررسید",
                    "value": None,
                    "action": "charges",
                })

            overdue = db.query(Charge).filter(
                Charge.unit_id.in_(unit_ids),
                Charge.status.in_(["پرداخت نشده", "ناقص"]),
                Charge.due_date < today,
            ).count()

            if overdue > 0:
                alerts.append({
                    "type": "danger",
                    "icon": "🔴",
                    "title": f"{overdue} شارژ معوق",
                    "value": None,
                    "action": "charges",
                })

        # ⭐ آخرین قبض همین ساختمون
        last_bill = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id
        ).order_by(UtilityBill.created_at.desc()).first()

        if last_bill:
            from datetime import datetime
            days_since = (datetime.now() - last_bill.created_at).days
            if days_since > 30:
                alerts.append({
                    "type": "info",
                    "icon": "📄",
                    "title": f"{days_since} روز از آخرین قبض",
                    "value": None,
                    "action": "bills",
                })

        if not alerts:
            alerts.append({
                "type": "success",
                "icon": "✅",
                "title": "همه چیز مرتب است",
                "value": None,
                "action": None,
            })

    return alerts


# ═══════════ تقویم مالی ═══════════

def get_financial_calendar(days=30):
    """رویدادهای مالی ۳۰ روز آینده (فقط ساختمون فعال)"""
    from datetime import timedelta

    today = date.today()
    end_date = today + timedelta(days=days)
    events = []

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ ID واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        # ─── سررسید شارژها ───
        if unit_ids:
            charges = db.query(Charge, Unit).join(
                Unit, Charge.unit_id == Unit.id
            ).filter(
                Unit.building_id == building.id,
                Charge.status.in_(["پرداخت نشده", "ناقص"]),
                Charge.due_date >= today,
                Charge.due_date <= end_date,
            ).all()

            charge_by_date = {}
            for c, u in charges:
                d = c.due_date
                if d not in charge_by_date:
                    charge_by_date[d] = {"count": 0, "amount": 0}
                charge_by_date[d]["count"] += 1
                charge_by_date[d]["amount"] += max(
                    (c.amount or 0) - (c.paid_amount or 0), 0
                )

            for d, info in charge_by_date.items():
                days_left = (d - today).days
                events.append({
                    "type": "charge_due",
                    "date": d,
                    "days_left": days_left,
                    "title": f"{info['count']} شارژ سررسید",
                    "amount": info["amount"],
                    "icon": "📋",
                })

        # ⭐ سررسید قبض‌ها (همین ساختمون)
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id,
            UtilityBill.due_date >= today,
            UtilityBill.due_date <= end_date,
        ).all()

        for b in bills:
            days_left = (b.due_date - today).days
            events.append({
                "type": "bill_due",
                "date": b.due_date,
                "days_left": days_left,
                "title": f"سررسید قبض {b.bill_type}",
                "amount": b.amount,
                "icon": (
                    "💧" if b.bill_type == "آب"
                    else "⚡" if b.bill_type == "برق"
                    else "🔥" if b.bill_type == "گاز"
                    else "📄"
                ),
            })

    events.sort(key=lambda x: x["date"])
    return events


# ═══════════ پیش‌بینی مالی ═══════════

def get_financial_forecast():
    """پیش‌بینی مالی ماه آینده (فقط ساختمون فعال)"""
    from models import Charge, Expense
    from sqlalchemy import func
    from datetime import timedelta

    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ ID واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        # ⭐ کل شارژ صادره ماه جاری (این ساختمون)
        current_month_charges = 0
        if unit_ids:
            current_month_charges = db.query(
                func.coalesce(func.sum(Charge.amount), 0)
            ).filter(
                Charge.unit_id.in_(unit_ids),
                Charge.created_at >= thirty_days_ago,
            ).scalar() or 0

        # ⭐ کل هزینه ماه گذشته (این ساختمون)
        total_expenses_last_month = db.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.building_id == building.id,
            Expense.expense_date >= thirty_days_ago,
        ).scalar() or 0

        # ⭐ تعداد هزینه‌های ماه گذشته
        expense_count = db.query(Expense).filter(
            Expense.building_id == building.id,
            Expense.expense_date >= thirty_days_ago,
        ).count()

        # موجودی فعلی (از داشبورد)
        current_data = get_dashboard_data()
        current_balance = current_data["cash_balance"]

        predicted_income = current_month_charges
        predicted_expenses = total_expenses_last_month
        predicted_balance = (
            current_balance
            + predicted_income
            - predicted_expenses
        )

        return {
            "current_balance": current_balance,
            "predicted_income": predicted_income,
            "predicted_expenses": predicted_expenses,
            "predicted_balance": predicted_balance,
            "monthly_expenses_avg": total_expenses_last_month,
            "expense_count": expense_count,
        }

# ═══════════ تایم لاین فعالیت‌ها ═══════════

def get_activity_timeline(limit=10):
    """آخرین فعالیت‌ها (فقط ساختمون فعال)"""
    from models import Payment, Expense, Charge, UtilityBill, Unit

    activities = []

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ ID واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        # ─── پرداخت‌ها ───
        if unit_ids:
            payments = db.query(Payment, Unit).join(
                Unit, Payment.unit_id == Unit.id
            ).filter(
                Unit.building_id == building.id
            ).order_by(Payment.created_at.desc()).limit(5).all()

            for p, u in payments:
                activities.append({
                    "type": "payment",
                    "icon": "💰",
                    "title": f"پرداخت واحد {u.number}",
                    "description": f"{u.resident_name or '-'} - {p.payment_method}",
                    "amount": p.amount,
                    "color": "success",
                    "timestamp": p.created_at,
                })

        # ─── هزینه‌ها ───
        expenses = db.query(Expense).filter(
            Expense.building_id == building.id
        ).order_by(Expense.created_at.desc()).limit(5).all()

        for e in expenses:
            activities.append({
                "type": "expense",
                "icon": "💸",
                "title": e.title,
                "description": e.category,
                "amount": e.amount,
                "color": "warning",
                "timestamp": e.created_at,
            })

        # ─── شارژها ───
        if unit_ids:
            charges = db.query(Charge).filter(
                Charge.unit_id.in_(unit_ids)
            ).order_by(Charge.created_at.desc()).limit(5).all()

            seen_periods = set()
            for c in charges:
                if c.period in seen_periods:
                    continue
                seen_periods.add(c.period)

                period_charges = db.query(Charge).filter(
                    Charge.period == c.period,
                    Charge.unit_id.in_(unit_ids),
                ).all()

                total = sum(pc.amount or 0 for pc in period_charges)

                activities.append({
                    "type": "charge",
                    "icon": "📋",
                    "title": f"صدور شارژ {c.period}",
                    "description": f"{len(period_charges)} واحد",
                    "amount": total,
                    "color": "primary",
                    "timestamp": c.created_at,
                })

        # ─── قبض‌ها ───
        bills = db.query(UtilityBill).filter(
            UtilityBill.building_id == building.id
        ).order_by(UtilityBill.created_at.desc()).limit(3).all()

        for b in bills:
            activities.append({
                "type": "bill",
                "icon": (
                    "💧" if b.bill_type == "آب"
                    else "⚡" if b.bill_type == "برق"
                    else "🔥" if b.bill_type == "گاز"
                    else "📄"
                ),
                "title": f"ثبت قبض {b.bill_type}",
                "description": f"{b.period or '-'}",
                "amount": (b.amount or 0) / 10,
                "color": "info",
                "timestamp": b.created_at,
            })

    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]


# ═══════════ نمودار روند مالی ═══════════

def get_financial_trend(months=6):
    """روند مالی ماه‌های اخیر (فقط ساختمون فعال)"""
    from models import Payment, Expense
    from sqlalchemy import func

    trend = []
    today = jdatetime.date.today()

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        # ⭐ ID واحدهای این ساختمون
        unit_ids = [
            u.id for u in db.query(Unit.id).filter(
                Unit.building_id == building.id
            ).all()
        ]

        for i in range(months - 1, -1, -1):
            target_month = today.month - i
            target_year = today.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1

            j_start = jdatetime.date(target_year, target_month, 1)
            next_m = target_month + 1
            next_y = target_year
            if next_m > 12:
                next_m = 1
                next_y += 1
            j_end = jdatetime.date(next_y, next_m, 1)

            g_start = j_start.togregorian()
            g_end = j_end.togregorian()

            # ⭐ درآمد (پرداخت‌های این ساختمون)
            income = 0
            if unit_ids:
                income = db.query(
                    func.coalesce(func.sum(Payment.amount), 0)
                ).filter(
                    Payment.unit_id.in_(unit_ids),
                    Payment.payment_date >= g_start,
                    Payment.payment_date < g_end,
                ).scalar() or 0

            # ⭐ هزینه‌های این ساختمون
            expense = db.query(
                func.coalesce(func.sum(Expense.amount), 0)
            ).filter(
                Expense.building_id == building.id,
                Expense.expense_date >= g_start,
                Expense.expense_date < g_end,
            ).scalar() or 0

            trend.append({
                "month": MONTHS[target_month],
                "year": target_year,
                "income": income,
                "expense": expense,
                "net": income - expense,
            })

    return trend

def get_expenses_by_category():
    """مجموع هزینه‌ها بر اساس دسته‌بندی"""
    from sqlalchemy import func

    with SessionLocal() as db:
        building = _get_or_create_building(db)
        results = db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        ).filter(
            Expense.building_id == building.id
        ).group_by(
            Expense.category
        ).order_by(
            func.sum(Expense.amount).desc()
        ).all()

        total_all = sum(r.total or 0 for r in results)

        return [
            {
                "category": r.category or "سایر",
                "total": r.total or 0,
                "count": r.count,
                "percent": (
                    (r.total or 0) / total_all * 100
                    if total_all > 0 else 0
                ),
            }
            for r in results
        ]

# ═══════════ تبدیل تاریخ و ساعت شمسی به datetime میلادی ═══════════

def parse_jalali_datetime(text):
    """
    ورودی: "1404/05/28 14:30"
    خروجی: datetime میلادی
    """
    if not text or not str(text).strip():
        return None
    try:
        parts = str(text).strip().split()
        date_str = parts[0]
        time_str = parts[1] if len(parts) > 1 else "12:00"

        g_date = parse_date(date_str)
        if not g_date:
            return None

        t_parts = time_str.split(":")
        h = int(t_parts[0])
        m = int(t_parts[1]) if len(t_parts) > 1 else 0

        return datetime(g_date.year, g_date.month, g_date.day, h, m)
    except Exception as ex:
        print(f"⚠️ خطای پارس تاریخ/ساعت: {ex}")
        return None

# ═══════════ سیستم یادداشت ═══════════

def add_note(
    title,
    content="",
    category="یادآوری",
    priority="normal",
    color="yellow",
    is_pinned=False,
    reminder_at=None,
):
    from models import Note

    title = str(title or "").strip()
    if not title:
        raise ValueError("عنوان الزامی است.")

    reminder_dt = None
    if reminder_at:
        if isinstance(reminder_at, str):
            reminder_dt = parse_jalali_datetime(reminder_at)
        elif hasattr(reminder_at, 'year'):
            reminder_dt = reminder_at

    with SessionLocal() as db:
        building = _get_or_create_building(db)      # ← ⭐ این خط اضافه شد
        note = Note(
            building_id=building.id,                # ← ⭐ این خط اضافه شد
            title=title,
            content=str(content or "").strip(),
            category=category or "یادآوری",
            priority=priority or "normal",
            color=color or "yellow",
            is_pinned=1 if is_pinned else 0,
            reminder_at=reminder_dt,
            is_done=0,
        )
        db.add(note)
        db.commit()
        db.refresh(note)

        try:
            check_and_create_note_notifications()
        except Exception:
            pass

        return note.id


def update_note(
    note_id,
    title=None,
    content=None,
    category=None,
    priority=None,
    color=None,
    reminder_at=None,
):
    from models import Note

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        note = db.query(Note).filter(
            Note.id == int(note_id),
            Note.building_id == building.id,             # ← ⭐ جدید
        ).first()
        if not note:
            raise ValueError("یادداشت پیدا نشد.")

        if title is not None:
            note.title = str(title).strip()
        if content is not None:
            note.content = str(content).strip()
        if category is not None:
            note.category = category
        if priority is not None:
            note.priority = priority
        if color is not None:
            note.color = color

        if reminder_at is not None:
            if not reminder_at:
                note.reminder_at = None
                note.reminder_sent_day_before = 0
                note.reminder_sent_hour_before = 0
                note.reminder_sent_on_time = 0
            elif isinstance(reminder_at, str):
                new_dt = parse_jalali_datetime(reminder_at)
                if note.reminder_at != new_dt:
                    note.reminder_sent_day_before = 0
                    note.reminder_sent_hour_before = 0
                    note.reminder_sent_on_time = 0
                note.reminder_at = new_dt

        note.updated_at = datetime.now()
        db.commit()

        try:
            check_and_create_note_notifications()
        except Exception:
            pass

        return True


def delete_note(note_id):
    """حذف یادداشت"""
    from models import Note

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        note = db.query(Note).filter(
            Note.id == int(note_id),
            Note.building_id == building.id,             # ← ⭐ جدید
        ).first()

        if note:
            db.delete(note)
            db.commit()
            return True
        return False


def toggle_note_done(note_id):
    """تغییر وضعیت انجام شده"""
    from models import Note

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        note = db.query(Note).filter(
            Note.id == int(note_id),
            Note.building_id == building.id,             # ← ⭐ جدید
        ).first()

        if note:
            note.is_done = 0 if note.is_done else 1
            note.updated_at = datetime.now()
            db.commit()
            return True
        return False

def toggle_note_pin(note_id):
    """تغییر وضعیت پین"""
    from models import Note

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        note = db.query(Note).filter(
            Note.id == int(note_id),
            Note.building_id == building.id,             # ← ⭐ جدید
        ).first()

        if note:
            note.is_pinned = (
                0 if note.is_pinned else 1
            )
            note.updated_at = datetime.now()
            db.commit()
            return True
        return False

def list_notes(
    category=None,
    only_pinned=False,
    only_with_reminder=False,
    only_done=False,
    only_undone=False,
    search=None,
):
    """لیست یادداشت‌ها با فیلتر"""
    from models import Note

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        query = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ حالا درست شد
        )

        if category:
            query = query.filter(
                Note.category == category
            )

        if only_pinned:
            query = query.filter(Note.is_pinned == 1)

        if only_with_reminder:
            query = query.filter(
                Note.reminder_at.isnot(None)
            )

        if only_done:
            query = query.filter(Note.is_done == 1)

        if only_undone:
            query = query.filter(Note.is_done == 0)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Note.title.like(search_pattern)) |
                (Note.content.like(search_pattern))
            )

        # مرتب‌سازی: پین‌شده‌ها اول، بعد جدیدترین
        notes = query.order_by(
            Note.is_pinned.desc(),
            Note.created_at.desc(),
        ).all()

        return [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "category": n.category,
                "priority": n.priority,
                "color": n.color,
                "is_pinned": n.is_pinned,
                "is_done": n.is_done,
                "reminder_at": n.reminder_at,
                "created_at": n.created_at,
                "updated_at": n.updated_at,
            }
            for n in notes
        ]

def get_note_by_id(note_id):
    """گرفتن یک یادداشت"""
    from models import Note

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید
        n = db.query(Note).filter(
            Note.id == int(note_id),
            Note.building_id == building.id,             # ← ⭐ جدید
        ).first()

        if not n:
            return None

        return {
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "category": n.category,
            "priority": n.priority,
            "color": n.color,
            "is_pinned": n.is_pinned,
            "is_done": n.is_done,
            "reminder_at": n.reminder_at,
            "created_at": n.created_at,
            "updated_at": n.updated_at,
        }

def get_notes_stats():
    """آمار یادداشت‌ها"""
    from models import Note
    from datetime import datetime, timedelta

    with SessionLocal() as db:
        building = _get_or_create_building(db)

        total = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ جدید
        ).count()

        done = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ جدید
            Note.is_done == 1,
        ).count()

        with_reminder = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ جدید
            Note.reminder_at.isnot(None),
            Note.is_done == 0,
        ).count()

        # یادداشت‌های امروز و فردا
        now = datetime.now()
        end_of_tomorrow = (
            now + timedelta(days=2)
        ).replace(hour=0, minute=0, second=0)

        today_reminders = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ جدید
            Note.reminder_at.isnot(None),
            Note.reminder_at <= end_of_tomorrow,
            Note.reminder_at >= now,
            Note.is_done == 0,
        ).count()

        return {
            "total": total,
            "done": done,
            "undone": total - done,
            "with_reminder": with_reminder,
            "today_reminders": today_reminders,
        }
def get_today_notes(limit=5):
    """
    یادداشت‌های امروز/فردا برای نمایش در داشبورد
    """
    from models import Note
    from datetime import datetime, timedelta

    now = datetime.now()
    end_of_tomorrow = (
        now + timedelta(days=2)
    ).replace(hour=0, minute=0, second=0)

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید

        # اول: یادداشت‌های با یادآوری امروز/فردا
        notes = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ جدید
            Note.reminder_at.isnot(None),
            Note.reminder_at <= end_of_tomorrow,
            Note.is_done == 0,
        ).order_by(
            Note.reminder_at.asc()
        ).limit(limit).all()

        # اگه کم بود، پین‌شده‌ها رو هم اضافه کن
        if len(notes) < limit:
            remaining = limit - len(notes)
            note_ids = [n.id for n in notes]
            pinned = db.query(Note).filter(
                Note.building_id == building.id,         # ← ⭐ جدید
                Note.is_pinned == 1,
                Note.is_done == 0,
                ~Note.id.in_(note_ids)
                if note_ids else True,
            ).order_by(
                Note.created_at.desc()
            ).limit(remaining).all()

            notes.extend(pinned)

        return [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "category": n.category,
                "priority": n.priority,
                "color": n.color,
                "is_pinned": n.is_pinned,
                "reminder_at": n.reminder_at,
            }
            for n in notes
        ]

def check_and_create_note_notifications():
    """
    چک دقیق و انعطاف‌پذیر زمان یادآوری‌ها
    """
    from models import Note, Notification
    from datetime import datetime, timedelta

    now = datetime.now()
    created = 0
    created_items = []

    with SessionLocal() as db:
        building = _get_or_create_building(db)          # ← ⭐ جدید

        # تمام یادداشت‌های انجام‌نشده دارای زمان یادآوری
        notes = db.query(Note).filter(
            Note.building_id == building.id,             # ← ⭐ جدید
            Note.reminder_at.isnot(None),
            Note.is_done == 0,
        ).all()

        for note in notes:
            r = note.reminder_at
            if not r:
                continue

            # ۱. آیا زمان اصلی یادآوری رسیده یا گذشته؟
            if now >= r and not note.reminder_sent_on_time:
                notif = Notification(
                    type="custom",
                    title=f"🔔 زمان یادآوری: {note.title}",
                    message=note.content or note.title,
                    priority="urgent",
                    is_read=0,
                )
                db.add(notif)
                note.reminder_sent_on_time = 1
                note.reminder_sent_hour_before = 1
                note.reminder_sent_day_before = 1
                created += 1
                created_items.append({"title": notif.title, "message": notif.message})

            # ۲. آیا ۱ ساعت قبل رسیده؟
            elif now >= (r - timedelta(hours=1)) and not note.reminder_sent_hour_before:
                notif = Notification(
                    type="custom",
                    title=f"⏰ ۱ ساعت تا یادآوری: {note.title}",
                    message=note.content or note.title,
                    priority="high",
                    is_read=0,
                )
                db.add(notif)
                note.reminder_sent_hour_before = 1
                note.reminder_sent_day_before = 1
                created += 1
                created_items.append({"title": notif.title, "message": notif.message})

            # ۳. آیا ۱ روز قبل رسیده؟
            elif now >= (r - timedelta(days=1)) and not note.reminder_sent_day_before:
                notif = Notification(
                    type="custom",
                    title=f"📝 یادآوری فردا: {note.title}",
                    message=f"فردا {r.strftime('%H:%M')}: {note.content or note.title}",
                    priority="normal",
                    is_read=0,
                )
                db.add(notif)
                note.reminder_sent_day_before = 1
                created += 1
                created_items.append({"title": notif.title, "message": notif.message})

        db.commit()

    return {
        "count": created,
        "items": created_items,
    }

# ═══════════ مدیریت Startup ═══════════

def get_startup_folder():
    """گرفتن مسیر پوشه Startup ویندوز"""
    return os.path.join(
        os.getenv('APPDATA'),
        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
    )


def get_executable_path():
    """گرفتن مسیر فایل اجرایی برنامه"""
    if getattr(sys, 'frozen', False):
        # برنامه به EXE تبدیل شده
        return sys.executable
    else:
        # در حال توسعه
        return os.path.abspath(sys.argv[0])


def is_startup_enabled():
    """
    بررسی آیا برنامه در Startup فعال است
    دو روش: پوشه Startup و رجیستری
    """
    # روش ۱: پوشه Startup
    startup_path = os.path.join(
        get_startup_folder(),
        "مدیریت ساختمان.lnk"
    )
    if os.path.exists(startup_path):
        return True

    # روش ۲: رجیستری
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, "مدیریت ساختمان")
        winreg.CloseKey(key)
        return bool(value)
    except WindowsError:
        return False

    return False


def enable_startup():
    """
    فعال‌سازی اجرا با بالا آمدن ویندوز
    (هر دو روش پوشه Startup و رجیستری)
    """
    exe_path = get_executable_path()

    # روش ۱: پوشه Startup (ایجاد Shortcut)
    try:
        import pythoncom
        from win32com.client import Dispatch
        import winshell

        startup_path = get_startup_folder()
        shortcut_path = os.path.join(startup_path, "مدیریت ساختمان.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.Save()

        print(f"✅ لینک Startup ساخته شد: {shortcut_path}")
        return True
    except Exception as ex:
        print(f"⚠️ خطا در ساخت لینک Startup: {ex}")

    # روش ۲: رجیستری
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key,
            "مدیریت ساختمان",
            0,
            winreg.REG_SZ,
            f'"{exe_path}"'
        )
        winreg.CloseKey(key)
        print("✅ رجیستری Startup تنظیم شد")
        return True
    except Exception as ex:
        print(f"⚠️ خطا در تنظیم رجیستری: {ex}")

    return False


def disable_startup():
    """غیرفعال‌سازی اجرا با بالا آمدن ویندوز"""
    # حذف از پوشه Startup
    try:
        startup_path = os.path.join(
            get_startup_folder(),
            "مدیریت ساختمان.lnk"
        )
        if os.path.exists(startup_path):
            os.remove(startup_path)
            print("✅ لینک Startup حذف شد")
    except Exception as ex:
        print(f"⚠️ خطا در حذف لینک: {ex}")

    # حذف از رجیستری
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "مدیریت ساختمان")
        winreg.CloseKey(key)
        print("✅ رجیستری Startup حذف شد")
        return True
    except WindowsError:
        # مقدار وجود نداشت
        return True
    except Exception as ex:
        print(f"⚠️ خطا در حذف رجیستری: {ex}")
        return False