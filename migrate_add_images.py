# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

import sqlite3
import os

db_path = os.path.join(os.getcwd(), "building_manager.db")

if not os.path.exists(db_path):
    print("❌ فایل دیتابیس پیدا نشد.")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA table_info(payments)")
payment_cols = [row[1] for row in cur.fetchall()]

cur.execute("PRAGMA table_info(expenses)")
expense_cols = [row[1] for row in cur.fetchall()]

if "receipt_image" not in payment_cols:
    cur.execute(
        "ALTER TABLE payments "
        "ADD COLUMN receipt_image VARCHAR(500) DEFAULT ''"
    )
    print("✅ ستون receipt_image به payments اضافه شد")
else:
    print("ℹ️ ستون receipt_image از قبل وجود دارد")

if "invoice_image" not in expense_cols:
    cur.execute(
        "ALTER TABLE expenses "
        "ADD COLUMN invoice_image VARCHAR(500) DEFAULT ''"
    )
    print("✅ ستون invoice_image به expenses اضافه شد")
else:
    print("ℹ️ ستون invoice_image از قبل وجود دارد")

conn.commit()
conn.close()
print("\n✅ مهاجرت کامل شد. این فایل رو می‌تونی پاک کنی.")