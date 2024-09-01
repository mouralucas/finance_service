import uuid
import datetime
from rolf_common.models import SQLModel
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship


class InvestmentTypeModel(SQLModel):
    __tablename__ = 'investment_type'

    name: Mapped[str] = mapped_column('name', String(200))
    description: Mapped[str] = mapped_column('description', String(200), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_type.id'), nullable=True)
    parent: Mapped['InvestmentTypeModel'] = relationship(foreign_keys=[parent_id], lazy='subquery')


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

    objective_id: Mapped[str] = mapped_column(ForeignKey('investment_objective.id'), nullable=True)
    objective: Mapped['InvestmentObjectiveModel'] = relationship('InvestmentObjectiveModel', foreign_keys=[objective_id], lazy='subquery')


class InvestmentStatementModel(SQLModel):
    __tablename__ = 'investment_statement'

    investment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment.id'))
    investment: Mapped['InvestmentModel'] = relationship(foreign_keys=[investment_id], lazy='subquery')
    period: Mapped[int] = mapped_column('period')
    previous_amount: Mapped[float] = mapped_column('start_amount', default=0)
    gross_amount: Mapped[float] = mapped_column('gross_amount')
    total_tax: Mapped[float] = mapped_column('total_tax', default=0)
    total_fee: Mapped[float] = mapped_column('total_fee', default=0)
    net_amount: Mapped[float] = mapped_column('net_amount')
    tax_detail: Mapped[dict] = mapped_column('tax_detail', JSON, nullable=True)
    fee_detail: Mapped[dict] = mapped_column('fee_detail', JSON, nullable=True)


class InvestmentObjectiveModel(SQLModel):
    __tablename__ = 'investment_objective'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    title: Mapped[str] = mapped_column('title', String(100))
    description: Mapped[str] = mapped_column('description', String(500))
    estimated_deadline: Mapped[datetime.date] = mapped_column('estimated_deadline', nullable=True)

    # Investment reverse relation
    investments: Mapped[list['InvestmentModel']] = relationship(back_populates='objective', lazy='subquery')
