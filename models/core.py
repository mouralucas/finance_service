import uuid

from rolf_common.models import SQLModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, SmallInteger


class CurrencyModel(SQLModel):
    __tablename__ = 'currency'

    id: Mapped[str] = mapped_column('id', String(3), primary_key=True)
    name: Mapped[str] = mapped_column('name', String(50))
    symbol: Mapped[str] = mapped_column('symbol', String(10))


class CategoryModel(SQLModel):
    __tablename__ = 'category'

    name: Mapped[str] = mapped_column('name', String(250))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)
    comment: Mapped[str] = mapped_column('comment', String(500), nullable=True)
    # parent_id: Mapped[uuid.UUID] =
    # parent: Mapped[Category]...
    order: Mapped[int] = mapped_column('order', SmallInteger, nullable=True)
    # more necessary fields


class BankModel(SQLModel):
    __tablename__ = 'bank'

    name: Mapped[str] = mapped_column('name', String(250))
    code: Mapped[int] = mapped_column('code', SmallInteger)


class IndexTypeModel(SQLModel):
    __tablename__ = 'index_type'

    name: Mapped[str] = mapped_column('name', String(250))
    description: Mapped[str] = mapped_column('description', String(500))


class IndexModel(SQLModel):
    __tablename__ = 'index'

    name: Mapped[str] = mapped_column('name', String(250))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)


class LiquidityModel(SQLModel):
    __tablename__ = 'liquidity'

    name: Mapped[str] = mapped_column('name', String(250))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)