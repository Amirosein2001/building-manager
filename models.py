# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date,
    DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default="ساختمان من")
    address = Column(String(255), default="")
    floors = Column(Integer, default=0)
    total_units = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    units = relationship("Unit", back_populates="building",
                          cascade="all, delete-orphan")
    bills = relationship("UtilityBill", back_populates="building",
                          cascade="all, delete-orphan")


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("building_id", "number",
                          name="uq_building_unit_number"),
    )

    id = Column(Integer, primary_key=True)
    building_id = Column(Integer,
                          ForeignKey("buildings.id"),
                          nullable=False)
    number = Column(String(20), nullable=False)
    floor = Column(Integer, default=0)
    area = Column(Float, default=0)
    people_count = Column(Integer, default=0)
    resident_name = Column(String(100), default="")
    phone = Column(String(20), default="")
    resident_type = Column(String(20), default="مالک")
    status = Column(String(20), default="ساکن")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)

    building = relationship("Building", back_populates="units")
    charges = relationship("Charge", back_populates="unit",
                            cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="unit",
                             cascade="all, delete-orphan")


class Charge(Base):
    __tablename__ = "charges"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.id"),
                      nullable=False)
    period = Column(String(20), nullable=False)
    calculation_method = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False, default=0)
    paid_amount = Column(Float, default=0)
    status = Column(String(20), default="پرداخت نشده")
    due_date = Column(Date, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)

    unit = relationship("Unit", back_populates="charges")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.id"),
                      nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=True)
    payment_method = Column(String(30), default="کارت")
    tracking_code = Column(String(100), default="")
    description = Column(Text, default="")
    receipt_image = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.now)

    unit = relationship("Unit", back_populates="payments")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    category = Column(String(50), default="سایر")
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, nullable=True)
    description = Column(Text, default="")
    invoice_image = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.now)


class UtilityBill(Base):
    __tablename__ = "utility_bills"

    id = Column(Integer, primary_key=True)
    building_id = Column(Integer,
                          ForeignKey("buildings.id"),
                          nullable=False)
    bill_type = Column(String(20), nullable=False)
    bill_identifier = Column(String(50), default="")
    pay_identifier = Column(String(50), default="")
    period = Column(String(30), default="")

    from_date = Column(Date, nullable=True)
    to_date = Column(Date, nullable=True)
    days_count = Column(Integer, default=0)

    previous_reading = Column(Float, default=0)
    current_reading = Column(Float, default=0)
    consumption = Column(Float, default=0)
    daily_avg_consumption = Column(Float, default=0)

    amount = Column(Float, default=0)
    daily_avg_amount = Column(Float, default=0)

    consumption_unit = Column(String(20), default="")
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    description = Column(Text, default="")

    owner_name = Column(String(100), default="")
    address = Column(Text, default="")
    postal_code = Column(String(20), default="")
    usage_type = Column(String(50), default="")
    meter_number = Column(String(50), default="")
    file_number = Column(String(50), default="")
    city = Column(String(50), default="")
    capacity = Column(Float, default=0)
    bill_date = Column(String(20), default="")

    related_expense_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    building = relationship("Building", back_populates="bills")


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), default="")

    security_question = Column(String(255), default="")
    security_answer_hash = Column(String(255), default="")

    role = Column(String(20), default="admin")

    is_active = Column(Integer, default=1)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    type = Column(String(30), nullable=False)

    title = Column(String(200), nullable=False)
    message = Column(Text, default="")

    related_unit_id = Column(
        Integer, ForeignKey("units.id"), nullable=True
    )
    related_charge_id = Column(
        Integer, ForeignKey("charges.id"), nullable=True
    )

    priority = Column(String(20), default="normal")

    is_read = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)
    read_at = Column(DateTime, nullable=True)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")

    category = Column(String(30), default="یادآوری")
    priority = Column(String(20), default="normal")
    color = Column(String(20), default="yellow")

    is_pinned = Column(Integer, default=0)
    is_done = Column(Integer, default=0)

    reminder_at = Column(DateTime, nullable=True)
    reminder_sent_day_before = Column(Integer, default=0)
    reminder_sent_hour_before = Column(Integer, default=0)
    reminder_sent_on_time = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)