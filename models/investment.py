import uuid
import datetime
from rolf_common.models import SQLModel
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship


class InvestmentCategory(SQLModel):
    """
    Created by: Lucas Penha de Moura - 21/09/2024
        This table stores the categories of investments. At first only two:
        Fixed Incoming
        Variable Incoming

        This information is used to filter the 'investment_type' model.
    """
    __tablename__ = 'investment_category'

    name: Mapped[str] = mapped_column('name', String(50))
    description: Mapped[str] = mapped_column('description', String(250), nullable=True)


class InvestmentTypeModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model is used to store all kinds of investment types.
        In Brazil, for example, it can be CDB, LCI, LCA, Tesouro Direto, etc

        TODO: maybe create a field to country, to indicate types by country
    """
    __tablename__ = 'investment_type'

    name: Mapped[str] = mapped_column('name', String(200))
    description: Mapped[str] = mapped_column('description', String(200), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_type.id'), nullable=True)
    parent: Mapped['InvestmentTypeModel'] = relationship(foreign_keys=[parent_id], lazy='subquery')
    investment_category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_category.id'), nullable=True)
    investment_category: Mapped['InvestmentCategory'] = relationship(foreign_keys=[investment_category_id], lazy='subquery')


class InvestmentModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model stores the investment itself, using the values in the contract.
        It does not show the position of the investment, although you can show the amount at the end (liquidation_amount)
    """
    __tablename__ = 'investment'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    custodian_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    custodiam: Mapped['BankModel'] = relationship(foreign_keys=[custodian_id], lazy='subquery')
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'), nullable=True) # TODO: change back to not null after migration
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
    contracted_rate: Mapped[str] = mapped_column('contracted_rate', String(50), nullable=True)

    currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    currency: Mapped['CurrencyModel'] = relationship(foreign_keys=[currency_id], lazy='subquery')

    indexer_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('indexer_type.id'))
    indexer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('indexer.id'))
    indexer: Mapped['IndexerModel'] = relationship(foreign_keys=[indexer_id], lazy='subquery')
    liquidity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('liquidity.id'))
    liquidity: Mapped['LiquidityModel'] = relationship(foreign_keys=[liquidity_id], lazy='subquery')
    is_liquidated: Mapped[bool] = mapped_column('is_liquidated', default=False)
    liquidation_date: Mapped[datetime.date] = mapped_column('liquidation_date', nullable=True)
    liquidation_amount: Mapped[float] = mapped_column('liquidation_amount', nullable=True)

    country_id: Mapped[str] = mapped_column('country_id')  # Will tell what kind of tax will be charged

    objective_id: Mapped[str] = mapped_column(ForeignKey('investment_objective.id'), nullable=True)
    objective: Mapped['InvestmentObjectiveModel'] = relationship('InvestmentObjectiveModel', foreign_keys=[objective_id], lazy='subquery')


class InvestmentStatementModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model stores the values of each investment at the end of each month
        The fee and tax stored here is only for reference, in case the investment were liquidated that day
    """
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
    # TODO: decide if persist this data or calculate when needed
    value_change: Mapped[float] = mapped_column('value_change', nullable=True)
    percentage_change: Mapped[float] = mapped_column('percentage_change', nullable=True)
    index_percent_change: Mapped[float] = mapped_column('index_change', nullable=True)  # how much the index changed in the period


class InvestmentObjectiveModel(SQLModel):
    __tablename__ = 'investment_objective'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    title: Mapped[str] = mapped_column('title', String(100))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)
    amount: Mapped[float] = mapped_column('amount')
    estimated_deadline: Mapped[datetime.date] = mapped_column('estimated_deadline', nullable=True)

    # Investment reverse relation
    investments: Mapped[list['InvestmentModel']] = relationship(back_populates='objective', lazy='subquery')
