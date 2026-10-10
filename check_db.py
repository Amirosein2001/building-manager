from services import list_payments, list_charges

print("=" * 60)
print("💰 لیست همه پرداخت‌ها")
print("=" * 60)

payments = list_payments()
for p in payments:
    print(f"ID: {p['id']} | واحد: {p['unit_number']} | مبلغ: {p['amount']:,.0f} | تاریخ: {p['payment_date']}")

print(f"\n📊 تعداد کل پرداخت‌ها: {len(payments)}")
print(f"📊 جمع کل: {sum(p['amount'] for p in payments):,.0f}")

print("\n" + "=" * 60)
print("📋 لیست شارژها")
print("=" * 60)

charges = list_charges()
for c in charges:
    print(f"ID: {c['id']} | واحد: {c['unit_number']} | مبلغ: {c['amount']:,.0f} | پرداختی: {c['paid_amount']:,.0f}")


from services import list_payments, delete_payment

payments = list_payments()

print(f"📊 تعداد پرداخت‌ها: {len(payments)}")

# نگه داشتن پرداخت اصلی و حذف بقیه
for p in payments[1:]:  # همه بجز اولی
    print(f"🗑 حذف پرداخت ID: {p['id']}")
    delete_payment(p["id"])

remaining = list_payments()
print(f"\n✅ باقیمانده: {len(remaining)} پرداخت")
for p in remaining:
    print(f"  ID: {p['id']} | مبلغ: {p['amount']:,.0f}")