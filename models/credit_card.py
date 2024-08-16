import datetime
import uuid

from rolf_common.models import SQLModel
from sqlalchemy import String, ForeignKey, SmallInteger, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CreditCardModel(SQLModel):
    __tablename__ = 'credit_card'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    nickname: Mapped[str] = mapped_column('nickname', String(50))
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'), nullable=True)
    account: Mapped["AccountModel"] = relationship(foreign_keys=[account_id], lazy='subquery')
    issue_date: Mapped[datetime.date] = mapped_column('issue_date', nullable=True)
    cancellation_date: Mapped[datetime.date] = mapped_column('cancellation_date', nullable=True)
    due_day: Mapped[int] = mapped_column('due_day', SmallInteger, nullable=True)
    close_day: Mapped[int] = mapped_column('close_day', SmallInteger, nullable=True)
    currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id')) # Default currency
    currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[currency_id], lazy='subquery')


class CreditCardBillModel(SQLModel):
    __tablename__ = 'credit_card_bill'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    credit_card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('credit_card.id'))
    credit_card: Mapped[CreditCardModel] = relationship(foreign_keys=[credit_card_id], lazy='subquery')
    period: Mapped[int] = mapped_column('period', Integer)
    due_date: Mapped[datetime.date] = mapped_column('due_date')
    transaction_date: Mapped[datetime.date] = mapped_column('transaction_date')
    amount: Mapped[float] = mapped_column('amount')
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('category.id'), nullable=True)
    category: Mapped['CategoryModel'] = relationship(foreign_keys=[category_id], lazy='subquery')
    currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[currency_id], lazy='subquery')  # The currency showed on the bill

    transaction_currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    transaction_currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[transaction_currency_id], lazy='subquery')  # The currency of transaction
    transaction_amount: Mapped[float] = mapped_column('transaction_amount')

    # This fields only required when transaction currency is different from the bill currency
    # In the front-end put a check-box "compra internacional" then open a box with this info
    dollar_exchange_rate: Mapped[float] = mapped_column('dollar_exchange_rate', nullable=True)  # the dollar rate with the currency on the bill
    currency_dollar_exchange_rate: Mapped[float] = mapped_column('transaction_currency_dollar_ex_rate', nullable=True)  # The rate between transaction currency and dollar
    total_tax: Mapped[float] = mapped_column('total_tax', nullable=True)
    tax_details: Mapped[dict] = mapped_column('tax_details', JSON, nullable=True)

    installment: Mapped[int] = mapped_column('installment', SmallInteger, default=1)
    tot_installment: Mapped[int] = mapped_column('tot_installment', SmallInteger, default=1)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('credit_card_bill.id'), nullable=True)
    parent: Mapped['CreditCardBillModel'] = relationship(foreign_keys=[parent_id], lazy='subquery')

    description: Mapped[str] = mapped_column('description', String(500))
    operation_type: Mapped[str] = mapped_column('operation_type', String(15))  # whether is incoming or outgoing

    origin: Mapped[str] = mapped_column('origin', String(10))
    is_validated: Mapped[bool] = mapped_column('is_validated', default=False)
