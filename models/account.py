import datetime
import uuid

from rolf_common.models import SQLModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.core import Bank


class AccountType(SQLModel):
    __tablename__ = "account_type"

    type: Mapped[str] = mapped_column('type', String(50))
    description: Mapped[str] = mapped_column('description', String(500))


class Account(SQLModel):
    __tablename__ = 'account'

    owner: Mapped[uuid.UUID] = mapped_column('owner')
    bank_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    bank: Mapped[Bank] = relationship(foreign_keys=[bank_id], lazy='subquery')
    nickname: Mapped[str] = mapped_column('nickname', String(50))
    description: Mapped[str] = mapped_column('description', String(500))
    branch: Mapped[str] = mapped_column('branch', String(30))
    number: Mapped[str] = mapped_column('number', String(50))
    open_date: Mapped[datetime.date] = mapped_column('open_date')
    close_date: Mapped[datetime.date] = mapped_column('close_date')
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account_type.id'))
    type: Mapped['AccountType'] = relationship(foreign_keys=[type_id], lazy='subquery')


class AccountStatement(SQLModel):
    __tablename__ = 'account_statement'

    id: Mapped[int] = mapped_column('id', primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))
    account: Mapped[Account] = relationship(foreign_keys=[account_id], lazy='subquery')

