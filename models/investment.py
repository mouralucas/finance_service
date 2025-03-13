import uuid
import datetime
from decimal import Decimal

from rolf_common.models import SQLModel
from sqlalchemy import String, ForeignKey, JSON, Numeric, Text, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship, declared_attr


class InvestmentCategoryModel(SQLModel):
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
    """
    __tablename__ = 'investment_type'

    name: Mapped[str] = mapped_column('name', String(200))
    description: Mapped[str] = mapped_column('description', String(200), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_type.id'), nullable=True)
    parent: Mapped['InvestmentTypeModel'] = relationship(foreign_keys=[parent_id], lazy='subquery')
    country_id: Mapped[str] = mapped_column(ForeignKey('country.id'), nullable=True)
    investment_category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_category.id'), nullable=True)
    investment_category: Mapped['InvestmentCategoryModel'] = relationship(foreign_keys=[investment_category_id], lazy='subquery')


class InvestmentModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model stores the investment itself, using the values in the contract.
        It does not show the position of the investment, although you can show the amount at the end (liquidation_amount)
    """
    __tablename__ = 'investment'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    name: Mapped[str] = mapped_column('name', String(200))
    custodian_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    custodiam: Mapped['BankModel'] = relationship(foreign_keys=[custodian_id], lazy='subquery')
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))
    account: Mapped['AccountModel'] = relationship(foreign_keys=[account_id], lazy='subquery')

    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_type.id'))
    type: Mapped[InvestmentTypeModel] = relationship(foreign_keys=[type_id], lazy='subquery')
    transaction_date: Mapped[datetime.date] = mapped_column('transaction_date')
    maturity_date: Mapped[datetime.date] = mapped_column('maturity_date', nullable=True)

    quantity: Mapped[Decimal] = mapped_column('quantity', Numeric(precision=9, scale=3), nullable=True)
    price: Mapped[Decimal] = mapped_column('price', Numeric(precision=15, scale=5), nullable=True)
    amount: Mapped[Decimal] = mapped_column('amount', Numeric(precision=15, scale=5))  # quantity*price
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
    liquidation_amount: Mapped[Decimal] = mapped_column('liquidation_amount', Numeric(precision=15, scale=5), nullable=True)

    country_id: Mapped[str] = mapped_column(ForeignKey('country.id'))
    country: Mapped['CountryModel'] = relationship(foreign_keys=[country_id], lazy='noload')

    observation: Mapped[str] = mapped_column('observation', Text, nullable=True)

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
    previous_amount: Mapped[Decimal] = mapped_column('start_amount', Numeric(precision=15, scale=5), default=0)
    gross_amount: Mapped[Decimal] = mapped_column('gross_amount', Numeric(precision=15, scale=5))
    total_tax: Mapped[Decimal] = mapped_column('total_tax', Numeric(precision=15, scale=5), default=0)
    total_fee: Mapped[Decimal] = mapped_column('total_fee', Numeric(precision=15, scale=5), default=0)
    net_amount: Mapped[Decimal] = mapped_column('net_amount', Numeric(precision=15, scale=5))
    tax_detail: Mapped[list[dict]] = mapped_column('tax_detail', JSON, nullable=True)
    fee_detail: Mapped[list[dict]] = mapped_column('fee_detail', JSON, nullable=True)
    reference_date: Mapped[datetime.date] = mapped_column('reference_date')
    at_maturity: Mapped[bool] = mapped_column('at_maturity', default=False)
    value_change: Mapped[Decimal] = mapped_column('value_change', Numeric(precision=15, scale=5), nullable=True)
    percentage_change: Mapped[Decimal] = mapped_column('percentage_change', Numeric(precision=9, scale=3), nullable=True)
    index_percent_change: Mapped[Decimal] = mapped_column('index_change', Numeric(precision=9, scale=3), nullable=True)  # how much the index changed in the period


class InvestmentObjectiveModel(SQLModel):
    __tablename__ = 'investment_objective'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    title: Mapped[str] = mapped_column('title', String(100))
    description: Mapped[str] = mapped_column('description', String(500), nullable=True)
    amount: Mapped[float] = mapped_column('amount', Numeric(precision=15, scale=5))
    estimated_deadline: Mapped[datetime.date] = mapped_column('estimated_deadline', nullable=True)

    # Investment reverse relation
    investments: Mapped[list['InvestmentModel']] = relationship(back_populates='objective', lazy='subquery')


### New Investment Models ###
class InvestmentBase(SQLModel):
    __abstract__ = True

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    name: Mapped[str] = mapped_column('name', String(200))

    custodian_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bank.id'))
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'))

    price: Mapped[float] = mapped_column('price', Numeric(precision=18, scale=8), doc='Price per unit/share of an investment')
    quantity: Mapped[float] = mapped_column('quantity', Numeric(precision=18, scale=8), doc='Quantity acquired')
    amount: Mapped[float] = mapped_column('amount', Numeric(precision=18, scale=8))

    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('investment_type.id'))
    currency_id: Mapped[str] = mapped_column(ForeignKey('currency.id'))
    country_id: Mapped[str] = mapped_column(ForeignKey('country.id'))
    objective_id: Mapped[str] = mapped_column(ForeignKey('investment_objective.id'), nullable=True)
    is_liquidated: Mapped[bool] = mapped_column('is_liquidated', default=False)

    tax: Mapped[list[dict]] = mapped_column('tax', type_=JSON, nullable=True, doc='Tax information. What taxes are levied on investments and its rates')
    fee: Mapped[list[dict]] = mapped_column('fee', type_=JSON, nullable=True, doc='Fee information. What fees are levied on investments and its rates')

    observation: Mapped[str] = mapped_column('observation', Text, nullable=True)


# class InvestmentStatementBase(SQLModel):
#     __abstract__ = True
#
#     period: Mapped[int] = mapped_column('period', Integer)
#     start_amount: Mapped[float] = mapped_column('start_amount', Numeric(precision=18, scale=8))
#     monthly_contribution: Mapped[float] = mapped_column('monthly_contribution', Numeric(precision=18, scale=8))
#
#
# class InvestmentFixedIncomeBrazilModel(InvestmentBase):
#     __tablename__ = 'investment_fixed_income_br'
#
#     issue_date: Mapped[datetime.date] = mapped_column('issue_date')
#     transaction_date: Mapped[datetime.date] = mapped_column('transaction_date')
#     maturity_date: Mapped[datetime.date] = mapped_column('maturity_date')
#     grace_period_date: Mapped[datetime.date] = mapped_column('grace_period_date', nullable=True)
#     contracted_rate: Mapped[str] = mapped_column('contracted_rate', String(50))
#
#     registered_at: Mapped[str] = mapped_column('registered_at', nullable=True, doc='Actual custodian, like B3')
#
#     indexer_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('indexer_type.id'))
#     indexer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('indexer.id'))
#
#     ticker: Mapped[str] = mapped_column('ticker', nullable=True)

# class FundsBr(SQLModel):
#     name: Mapped[str] = mapped_column('name', String(200))
    

class InvestmentFundsBrazilModel(InvestmentBase):
    __tablename__ = 'investment_funds_br'

    investment_quotation_date: Mapped[datetime.date] = mapped_column('investment_quotation_date', doc='The day the investment was quoted')
    investment_settlement_date: Mapped[datetime.date] = mapped_column('liquidation_settlement_date', doc='The date the investment is liquidated in the fund') # TODO: check this name
    redemption_quotation_range: Mapped[str] = mapped_column('redemption_quotation_range', doc='How many days for the settlement be quoted')
    redemption_quotation_date: Mapped[datetime.date] = mapped_column('redemption_quotation_date', nullable=True)
    redemption_settlement_range: Mapped[str] = mapped_column('redemption_settlement_range', doc='How many days for the amount be available after the quotation date')
    redemption_settlement_date: Mapped[datetime.date] = mapped_column('redemption_settlement_date', nullable=True)

    minimum_balance: Mapped[float] = mapped_column('minimum_balance', Numeric(precision=18, scale=8), doc='The minimum amount to be in the fund')
    minimum_transaction: Mapped[float] = mapped_column('minimum_transaction', Numeric(precision=18, scale=8), doc='The minimum amount for every transaction in the fund')
    initial_investment: Mapped[float] = mapped_column('initial_investment', Numeric(precision=18, scale=8), doc='The initial amount to be in the fund')

    benchmark: Mapped[str] = mapped_column('benchmark', String(50), nullable=True)

# class TreasuryInvestmentBrazil(InvestmentBase):
#     __tablename__ = 'investment_treasury_br'
#
#     pass
