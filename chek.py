"""
fix_backfill_v2.py — تخصیص پرداخت‌ها بر اساس تاریخ فیش
قانون: روز ۱-۲۸ ماه M → شارژ ماه M
       روز ۲۹-۳۱ ماه M → شارژ ماه M+1
یک بار اجرا کن، بعد پاکش کن
"""
import jdatetime
from database import SessionLocal
from models import Payment, Charge, Unit

MONTHS = ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]


def payment_target_period(payment_date):
    """تعیین دوره‌ی هدف از روی تاریخ فیش"""
    j = jdatetime.date.fromgregorian(date=payment_date)
    d, m, y = j.day, j.month, j.year
    if d >= 29:
        if m == 12:
            return f"{MONTHS[1]} {y + 1}"
        return f"{MONTHS[m + 1]} {y}"
    return f"{MONTHS[m]} {y}"


with SessionLocal() as db:
    # ─── مرحله ۱: ریست همه چیز ───
    db.query(Payment).update({
        Payment.target_charge_id: None,
        Payment.target_period: None,
    })
    for c in db.query(Charge).all():
        c.paid_amount = 0
        c.status = "پرداخت نشده"
    db.commit()
    print("🔄 همه ریست شد")

    # ─── مرحله ۲: تخصیص بر اساس تاریخ فیش ───
    updated = 0
    failed = 0

    for unit in db.query(Unit).all():
        pays = db.query(Payment).filter(
            Payment.unit_id == unit.id
        ).order_by(
            Payment.payment_date.asc().nulls_last(),
            Payment.created_at.asc().nulls_last(),
            Payment.id.asc(),
        ).all()

        unit_charges = db.query(Charge).filter(
            Charge.unit_id == unit.id
        ).all()
        by_period = {c.period: c for c in unit_charges}

        for pay in pays:
            if pay.payment_date is None:
                failed += 1
                continue

            target_period = payment_target_period(pay.payment_date)
            target = by_period.get(target_period)

            if target is None:
                # شارژ اون دوره وجود نداره — با FIFO روی اولین شارژ بدهکار بچسبون
                first_unpaid = next(
                    (c for c in sorted(unit_charges,
                                       key=lambda x: x.period)
                     if (c.amount or 0) > (c.paid_amount or 0)),
                    None
                )
                if first_unpaid:
                    pay.target_charge_id = first_unpaid.id
                    pay.target_period = first_unpaid.period
                    first_unpaid.paid_amount = (
                        (first_unpaid.paid_amount or 0) + (pay.amount or 0)
                    )
                    updated += 1
                else:
                    failed += 1
                continue

            pay.target_charge_id = target.id
            pay.target_period = target.period
            target.paid_amount = (target.paid_amount or 0) + (pay.amount or 0)
            updated += 1

        # آپدیت status شارژها
        for c in unit_charges:
            rem = (c.amount or 0) - (c.paid_amount or 0)
            if rem <= 0:
                c.status = "تسویه"
            elif (c.paid_amount or 0) > 0:
                c.status = "ناقص"
            else:
                c.status = "پرداخت نشده"

    db.commit()
    print(f"✅ {updated} پرداخت تخصیص، {failed} ناموفق")

    # ─── مرحله ۳: گزارش توزیع ───
    from collections import Counter
    dist = Counter(p.target_period for p in db.query(Payment).all())
    print("\n📊 توزیع جدید target_period:")
    for tp, cnt in sorted(dist.items(), key=lambda x: str(x[0])):
        print(f"  {tp!r}: {cnt}")