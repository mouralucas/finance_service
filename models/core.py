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
    description: Mapped[str] = mapped_column('description', String(500))
    comment: Mapped[str] = mapped_column('comment', String(500))
    # parent_id: Mapped[uuid.UUID] =
    # parent: Mapped[Category]...
    order: Mapped[int] = mapped_column('order', SmallInteger)
    # more necessary fields


class BankModel(SQLModel):
    __tablename__ = 'bank'

    name: Mapped[str] = mapped_column('name', String(250))
    code: Mapped[int] = mapped_column('code', SmallInteger)




