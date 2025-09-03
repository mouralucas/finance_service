import datetime
import uuid
from decimal import Decimal

from rolf_common.models import SQLModel
from sqlalchemy import ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CurrencyModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 08/08/2024
        This model is used to store the currencies available in the system.
    """

    __tablename__ = "currency"

    id: Mapped[str] = mapped_column("id", String(3), primary_key=True)
    name: Mapped[str] = mapped_column("name", String(50))
    symbol: Mapped[str] = mapped_column("symbol", String(10))


class CategoryModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 08/08/2024
        This model stores all transactions categories, it can be used in all kinds
        of transactions, such account, credit cards and investments
    """

    __tablename__ = "category"

    name: Mapped[str] = mapped_column("name", String(250))
    description: Mapped[str] = mapped_column("description", String(500), nullable=True)
    comment: Mapped[str] = mapped_column("comment", String(500), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("category.id"), nullable=True
    )
    parent: Mapped["CategoryModel"] = relationship(
        foreign_keys=[parent_id], lazy="subquery"
    )
    order: Mapped[int] = mapped_column("order", SmallInteger, nullable=True)


class ExpenseTypeModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 29/10/2024
        This models stores all kinds of expenses types,
            like fixed, variable, recurring, etc
    """

    __tablename__ = "expense_type"

    name: Mapped[str] = mapped_column("name", String(50))
    description: Mapped[str] = mapped_column("description", String(250), nullable=True)


class CategoryExpenseTypeUserModel(SQLModel):
    # TODO: creating cache for this info, if is available get from cache,
    #   update cache when user update this info
    """
    Created by: Lucas Penha de Moura - 29/10/2024
        This model relates the category with an expense type and specific user.
        The user can decide which expense type to use with any of its categories.
        These values are used to build dashboard charts
    """
    __tablename__ = "category_expense_user"

    owner_id: Mapped[uuid.UUID] = mapped_column("owner_id")
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("category.id"))
    expense_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expense_type.id"))


class CountryModel(SQLModel):
    __tablename__ = "country"

    id: Mapped[str] = mapped_column("id", String(5), primary_key=True)
    name: Mapped[str] = mapped_column("name", String(250))
    continent: Mapped[str] = mapped_column("continent", String(5), nullable=True)


class BankModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 08/08/2024
        This model stores the bank information (name and code)
    """

    __tablename__ = "bank"

    name: Mapped[str] = mapped_column("name", String(250))
    code: Mapped[int] = mapped_column("code", SmallInteger, nullable=True)


class IndexerTypeModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 12/08/2024
        This table stores the types of indexes.
        It's a small table that, at first, only stores 3 register
            (fixed, floating and hybrid)
    """

    __tablename__ = "indexer_type"

    name: Mapped[str] = mapped_column("name", String(250))
    description: Mapped[str] = mapped_column("description", String(500), nullable=True)


class IndexerModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model stores all possible indexers.
        For example, in Brazil, there is SELIC, CDI, IPCA, etc
        There is a default option in table when a index is not used
            {name='Índice não definido'}

        TODO: maybe add country
    """

    __tablename__ = "indexer"

    name: Mapped[str] = mapped_column("name", String(250))
    description: Mapped[str] = mapped_column("description", String(500), nullable=True)


class IndexerSeriesModel(SQLModel):
    __tablename__ = "indexer_series"

    indexer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("indexer.id"))
    indexer_name: Mapped[str] = mapped_column(
        "indexer_name", String(100)
    )  # Usually the same as Indexer model, just denormalized
    date: Mapped[datetime.date] = mapped_column("date", nullable=True)
    period: Mapped[int] = mapped_column("period", nullable=True)
    value: Mapped[Decimal] = mapped_column(
        "value", Numeric(precision=15, scale=5), nullable=True
    )
    periodicity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("periodicity.id"))
    periodicity_name: Mapped[str] = mapped_column("periodicity_name", String(100))
    unit: Mapped[str] = mapped_column("unit", String(10))
    # bcb_code: Mapped[str] = mapped_column('bcb_code', String(10),
    #   doc='The code in sgs')


class LiquidityModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model stores liquidity information like if it is "daily", "monthly", etc.

    """

    __tablename__ = "liquidity"

    name: Mapped[str] = mapped_column("name", String(250))
    description: Mapped[str] = mapped_column("description", String(500), nullable=True)


class PeriodicityModel(SQLModel):
    __tablename__ = "periodicity"

    name: Mapped[str] = mapped_column("name", String(100))
    description: Mapped[str] = mapped_column("description", String(250), nullable=True)
    order: Mapped[int] = mapped_column("order", SmallInteger, nullable=True)


class TaxFeeModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 26/08/2024
        This table stores tax descriptions.
        Each country have an infinite of taxes that are applied to
            every transaction made.
    """

    __tablename__ = "tax_fee"

    name: Mapped[str] = mapped_column("name", String(250))
    description: Mapped[str] = mapped_column("description", String(500), nullable=True)
    acronyms: Mapped[str] = mapped_column("acronyms", String(30), nullable=True)
    country_id: Mapped[str] = mapped_column(ForeignKey("country.id"))
    country: Mapped["CountryModel"] = relationship(
        foreign_keys=[country_id], lazy="subquery"
    )
    type: Mapped[str] = mapped_column("type", String(3))  # Can be 'tax' or 'fee'
