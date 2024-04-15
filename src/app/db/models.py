from __future__ import annotations

import enum
from sqlalchemy import String, Enum, Boolean, ForeignKey, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str]

    # account: Mapped[Account] = relationship(secondary="role_account", back_populates="role", cascade="delete")
    account: Mapped[list["Account"]] = relationship(secondary="role_account", back_populates="role", cascade="delete")


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(30), nullable=True)
    psw_hash: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String(30), nullable=True)
    mid_name: Mapped[str] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # role: Mapped[Role] = relationship(secondary="role_account", back_populates="account", cascade="delete")
    role: Mapped[list["Role"]] = relationship(secondary="role_account", back_populates="account", cascade="delete")


class RoleAccount(Base):
    __tablename__ = 'role_account'

    account_id: Mapped[int] = mapped_column(ForeignKey(Account.id), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey(Role.id), primary_key=True)

