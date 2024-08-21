import uuid
import datetime
from rolf_common.models import SQLModel
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship


class InvestmentTypeModel(SQLModel):
    __tablename__ = 'investment_type'

    name: Mapped[str] = mapped_column('name', String(200))
    description: Mapped[str] = mapped_column('description', String(200))
    # parent_id


class InvestmentModel(SQLModel):
    __tablename__ = 'investment'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    custodian_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    custodiam: Mapped['BankModel'] = relationship(foreign_keys=[custodian_id], lazy='subquery')
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))
    account: Mapped['AccountModel'] = relationship(foreign_keys=[account_id], lazy='subquery')
    name: Mapped[str] = mapped_column('name', String(200))
    description: Mapped[str] = mapped_column('description', String(200), nullable=True)
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_type.id'))
    type: Mapped[InvestmentTypeModel] = relationship(foreign_keys=[type_id], lazy='subquery')
    transaction_date: Mapped[datetime.date] = mapped_column('transaction_date')
    maturity_date: Mapped[datetime.date] = mapped_column('maturity_date', nullable=True)

    quantity: Mapped[float] = mapped_column('quantity', nullable=True)
    price: Mapped[float] = mapped_column('price', nullable=True)
    amount: Mapped[float] = mapped_column('amount')  # quantity*price

    currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[currency_id], lazy='subquery')

    index_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('index_type.id'))  # pre-fixado, pos, hibrido, etc MAYBE A TABLE?
    index_type: Mapped['IndexTypeModel'] = relationship(foreign_keys=[index_type_id], lazy='subquery')
    index_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('index.id'))  # criar tabela
    index: Mapped['IndexModel'] = relationship(foreign_keys=[index_id], lazy='subquery')
    liquidity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('liquidity.id'))
    liquidity: Mapped['LiquidityModel'] = relationship(foreign_keys=[liquidity_id], lazy='subquery')
    is_liquidated: Mapped[bool] = mapped_column('is_liquidated', default=False)
    liquidation_date: Mapped[datetime.date] = mapped_column('liquidation_date', nullable=True)
    liquidation_amount: Mapped[float] = mapped_column('liquidation_amount', default=0.0)

    country_id: Mapped[str] = mapped_column('country_id')  # Will tell what kind of tax will be charged
