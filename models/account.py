import datetime
import uuid
from decimal import Decimal

from rolf_common.models import SQLModel
from sqlalchemy import ForeignKey, String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship



class AccountTypeModel(SQLModel):
    __tablename__ = "account_type"

    type: Mapped[str] = mapped_column('type', String(50))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)


class AccountModel(SQLModel):
    __tablename__ = 'account'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    bank_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    bank: Mapped['BankModel'] = relationship(foreign_keys=[bank_id], lazy='subquery')
    nickname: Mapped[str] = mapped_column('nickname', String(50))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)
    branch: Mapped[str] = mapped_column('branch', String(30), nullable=True)
    number: Mapped[str] = mapped_column('number', String(50), nullable=True)
    open_date: Mapped[datetime.date] = mapped_column('open_date')
    close_date: Mapped[datetime.date] = mapped_column('close_date', nullable=True)
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account_type.id'))
    type: Mapped['AccountTypeModel'] = relationship(foreign_keys=[type_id], lazy='subquery')
    currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[currency_id], lazy='subquery')  # The currency showed on the bill

    # Relations
    credit_cards: Mapped[list['CreditCardModel']] = relationship(back_populates='account', lazy='subquery')


class AccountTransactionModel(SQLModel):
    __tablename__ = 'account_transaction'

    id: Mapped[int] = mapped_column('id', primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))
    account: Mapped[AccountModel] = relationship(foreign_keys=[account_id], lazy='subquery')
    period: Mapped[int] = mapped_column('period', Integer)
    currency_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('currency.id'))
    currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[currency_id], lazy='subquery')  # Should be always the same as the account currency
    amount: Mapped[Decimal] = mapped_column('amount', Numeric(precision=15, scale=5))
    transaction_date: Mapped[datetime.date] = mapped_column('transaction_date')
    # category_id_old: Mapped[str] = mapped_column('category_id_old', nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('category.id'))
    category: Mapped['CategoryModel'] = relationship(foreign_keys=[category_id], lazy='subquery')
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)
    operation_type: Mapped[str] = mapped_column('operation_type', String(15), nullable=True)  # deprecated, now just input positive or negative values

    # Fields for international transactions, like exchange money or by in a currency different from the account
    transaction_currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    transaction_currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[transaction_currency_id], lazy='subquery')  # The currency of transaction
    transaction_amount: Mapped[Decimal] = mapped_column('transaction_amount', Numeric(precision=15, scale=5))

    # Fields for exchange rates and applicable tax and fees
    exchange_rate: Mapped[Decimal] = mapped_column('exchange_rate', Numeric(precision=15, scale=5), nullable=True)  # the rate between default currency and transaction currency
    tax_perc: Mapped[Decimal] = mapped_column('perc_tax', Numeric(precision=10, scale=4), nullable=True)  # the total tax percentage
    tax: Mapped[Decimal] = mapped_column('tax', Numeric(precision=15, scale=5), nullable=True)  # the exchange_rate * tax_perc
    spread_perc: Mapped[Decimal] = mapped_column('spread_perc', Numeric(precision=15, scale=5), nullable=True)  # the percentage of spread applied
    spread: Mapped[Decimal] = mapped_column('spread', Numeric(precision=15, scale=5), nullable=True)  # the exchange_rate * spread_perc
    effective_rate: Mapped[Decimal] = mapped_column('effective_rate', Numeric(precision=15, scale=5), nullable=True)  # the final exchange rate, with tax and fees

    origin: Mapped[str] = mapped_column('origin', String(10))
    is_validated: Mapped[bool] = mapped_column('is_validated', default=True)


class AccountBalanceModel(SQLModel):
    __tablename__ = 'account_balance'

    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))
    period: Mapped[int] = mapped_column('period', Integer)
    previous_balance: Mapped[Decimal] = mapped_column('previous_balance', Numeric(precision=10, scale=2))
    incoming: Mapped[Decimal] = mapped_column('incoming', Numeric(precision=10, scale=2))
    outgoing: Mapped[Decimal] = mapped_column('outgoing', Numeric(precision=10, scale=2))
    transactions: Mapped[Decimal] = mapped_column('transactions', Numeric(precision=10, scale=2))  # incoming - outgoing
    earnings: Mapped[Decimal] = mapped_column('earnings', Numeric(precision=10, scale=2), default=0)
    balance: Mapped[Decimal] = mapped_column('balance', Numeric(precision=10, scale=2))
