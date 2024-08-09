import datetime
import uuid

from rolf_common.models import SQLModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.core import BankModel


class AccountTypeModel(SQLModel):
    __tablename__ = "account_type"

    type: Mapped[str] = mapped_column('type', String(50))
    description: Mapped[str] = mapped_column('description', String(500))


class AccountModel(SQLModel):
    __tablename__ = 'account'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    bank_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    bank: Mapped[BankModel] = relationship(foreign_keys=[bank_id], lazy='subquery')
    nickname: Mapped[str] = mapped_column('nickname', String(50))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)
    branch: Mapped[str] = mapped_column('branch', String(30), nullable=True)
    number: Mapped[str] = mapped_column('number', String(50), nullable=True)
    open_date: Mapped[datetime.date] = mapped_column('open_date')
    close_date: Mapped[datetime.date] = mapped_column('close_date', nullable=True)
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account_type.id'))
    type: Mapped['AccountTypeModel'] = relationship(foreign_keys=[type_id], lazy='subquery')


class AccountStatementModel(SQLModel):
    __tablename__ = 'account_statement'

    id: Mapped[int] = mapped_column('id', primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))
    account: Mapped[AccountModel] = relationship(foreign_keys=[account_id], lazy='subquery')

