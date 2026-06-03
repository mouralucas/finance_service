import datetime
import uuid
from decimal import Decimal

from rolf_common.models.base import SQLModel
from sqlalchemy import JSON, ForeignKey, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CreditCardModel(SQLModel):
    __tablename__ = "credit_card"

    owner_id: Mapped[uuid.UUID] = mapped_column("owner_id")
    nickname: Mapped[str] = mapped_column("nickname", String(50))
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account.id"), nullable=True
    )
    account: Mapped["AccountModel"] = relationship(  # noqa: F821
        back_populates="credit_cards", lazy="subquery"
    )
    issue_date: Mapped[datetime.date] = mapped_column("issue_date", nullable=True)
    cancellation_date: Mapped[datetime.date] = mapped_column(
        "cancellation_date", nullable=True
    )
    due_day: Mapped[int] = mapped_column("due_day", SmallInteger, nullable=True)
    close_day: Mapped[int] = mapped_column("close_day", SmallInteger, nullable=True)
    currency_id: Mapped[str] = mapped_column(
        ForeignKey("currency.id")
    )  # Default currency
    currency: Mapped["CurrencyModel"] = relationship(  # noqa: F821
        foreign_keys=[currency_id], lazy="subquery"
    )


class CreditCardTransactionModel(SQLModel):
    __tablename__ = "credit_card_transaction"

    id: Mapped[int] = mapped_column("id", primary_key=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column("owner_id")
    credit_card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("credit_card.id"))
    credit_card: Mapped[CreditCardModel] = relationship(
        foreign_keys=[credit_card_id], lazy="subquery"
    )
    period: Mapped[int] = mapped_column("period", Integer)
    due_date: Mapped[datetime.date] = mapped_column("due_date")
    transaction_date: Mapped[datetime.date] = mapped_column("transaction_date")
    amount: Mapped[Decimal] = mapped_column(
        "amount", Numeric(precision=15, scale=5), doc="The amount of the bill entry"
    )
    # category_id_old: Mapped[str] = mapped_column('category_id_old', nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("category.id"))
    category: Mapped["CategoryModel"] = relationship(  # noqa: F821
        foreign_keys=[category_id], lazy="subquery"
    )
    currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"))
    currency: Mapped["CurrencyModel"] = relationship(  # noqa: F821
        foreign_keys=[currency_id],
        lazy="subquery",
        doc="# The currency showed on the bill",
    )

    transaction_currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"))
    transaction_currency: Mapped["CurrencyModel"] = relationship(  # noqa: F821
        foreign_keys=[transaction_currency_id],
        lazy="subquery",
        doc="The original currency of the transaction",
    )
    transaction_amount: Mapped[Decimal] = mapped_column(
        "transaction_amount", Numeric(precision=15, scale=5)
    )

    # This fields only required when transaction currency is different
    #   from the bill currency
    # In the front-end put a check-box "compra internacional"
    #   then open a box with this info
    dollar_exchange_rate: Mapped[Decimal] = mapped_column(
        "dollar_exchange_rate",
        Numeric(precision=15, scale=5),
        nullable=True,
        doc="The rate between card currency and dollar",
    )
    currency_dollar_exchange_rate: Mapped[Decimal] = mapped_column(
        "currency_dollar_ex_rate",
        Numeric(precision=15, scale=5),
        nullable=True,
        doc="The rate between transaction currency and dollar",
    )
    total_tax: Mapped[Decimal] = mapped_column(
        "total_tax", Numeric(precision=15, scale=5), nullable=True
    )
    tax_details: Mapped[dict] = mapped_column("tax_details", JSON, nullable=True)

    is_installment: Mapped[bool] = mapped_column("is_installment", default=False)
    current_installment: Mapped[int] = mapped_column(
        "current_installment", SmallInteger, default=1
    )
    installments: Mapped[int] = mapped_column("installments", SmallInteger, default=1)
    total_amount: Mapped[Decimal] = mapped_column(
        "total_amount", Numeric(precision=15, scale=5)
    )  # The total amount of transaction
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("credit_card_transaction.id"), nullable=True
    )
    parent: Mapped["CreditCardTransactionModel"] = relationship(
        foreign_keys=[parent_id], lazy="subquery"
    )

    description: Mapped[str] = mapped_column("description", String(500), nullable=True)

    origin: Mapped[str] = mapped_column("origin", String(10))
    is_validated: Mapped[bool] = mapped_column("is_validated", default=True)

    operation_type: Mapped[str] = mapped_column(
        "operation_type", String(15), nullable=True
    )  # Deprecated, will be removed soon
