# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///building_manager.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

Base = declarative_base()


def init_db():
    from models import (
        Building, Unit, Charge, Payment,
        Expense, UtilityBill, AppSetting,
        User, Notification,Note,   # ← اضافه شد
    )
    Base.metadata.create_all(bind=engine)