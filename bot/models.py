from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OrderStatus(StrEnum):
    PENDING_PRICE = "PENDING_PRICE"    # получили количество, считаем цену
    PRICE_READY = "PRICE_READY"        # цена рассчитана и показана пользователю
    WAITING_PAYMENT = "WAITING_PAYMENT"
    PAID = "PAID"
    GIFT_SENT = "GIFT_SENT"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PARTIAL = "PARTIAL"
    TIMEOUT = "TIMEOUT"
    REFUNDED = "REFUNDED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    language: Mapped[str] = mapped_column(String(8), default="ru")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Внешний ид заказа для комментария/матча платежа (UUID/ulid в будущем)
    order_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user: Mapped["User"] = relationship(back_populates="orders")

    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # на кого дарим (если скрыт, обработаем отдельно)
    quantity: Mapped[int] = mapped_column(Integer)  # 50..1_000_000

    # Цена с Fragment и конечная цена к оплате (TON), точность 9 знаков
    price_fragment_ton: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 9), nullable=True)
    price_out_ton: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 9), nullable=True)

    status: Mapped[str] = mapped_column(String(32), default=OrderStatus.PENDING_PRICE)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments: Mapped[list["Payment"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    order: Mapped["Order"] = relationship(back_populates="payments")

    status: Mapped[str] = mapped_column(String(16), default=PaymentStatus.PENDING)

    # Матч по сумме и комменту (order_key)
    amount_ton: Mapped[Decimal] = mapped_column(Numeric(20, 9))
    comment: Mapped[str] = mapped_column(String(128))

    # Хеш транзакции (ton tx hash / lt+hash)
    tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True)

    # Сырые данные провайдера (TonAPI/TonCenter)
    raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Полезные индексы
Index("ix_orders_status_created", Order.status, Order.created_at)
Index("ix_payments_status_created", Payment.status, Payment.created_at)
