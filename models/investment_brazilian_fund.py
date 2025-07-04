import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.investment import FundsBrModel, InvestmentBase, InvestmentStatementBaseModel


class InvestmentBrazilianFundsModel(InvestmentBase):
    """
    Created by: Lucas Penha de Moura - 02/04/2025
        This model is used to store the fund investments in Brazil.
        It inherits from the InvestmentBase and adds specific fields for funds investments.
    """
    __tablename__ = 'investment_funds_br'

    fund_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('funds_br.id'))
    fund: Mapped[FundsBrModel] = relationship(foreign_keys=[fund_id], lazy='subquery')
    transaction_date: Mapped[date] = mapped_column('transaction_date', nullable=True)
    investment_quotation_date: Mapped[date] = mapped_column('investment_quotation_date', doc='The day the investment was quoted')
    investment_settlement_date: Mapped[date] = mapped_column('liquidation_settlement_date', doc='The date the investment is liquidated in the fund')  # TODO: check this name
    redemption_quotation_date: Mapped[date] = mapped_column('redemption_quotation_date', nullable=True)
    redemption_settlement_date: Mapped[date] = mapped_column('redemption_settlement_date', nullable=True)
    settlement_amount: Mapped[Decimal] = mapped_column('settlement_amount', Numeric(precision=18, scale=8), default=0)

class InvestmentBrazilianFundsStatementModel(InvestmentStatementBaseModel):
    """
    Created by: Lucas Penha de Moura - 02/04/2025
        This model is used to store the statement of funds investments in Brazil.
        It inherits from the InvestmentStatementBaseModel and adds specific fields for fund investments.
        The statement refers to the fund and not to a specific investment.
    """
    __tablename__ = 'investment_funds_br_statement'

    fund_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('funds_br.id'))
    contribution: Mapped[Decimal] = mapped_column('contribution', Numeric(precision=18, scale=8), default=0.0, doc='The amount of money contributed to the fund in the period')
    price: Mapped[Decimal] = mapped_column('price', Numeric(precision=18, scale=8), doc='The price of the fund in the reference day')
    penalty: Mapped[Decimal] = mapped_column('penalty', Numeric(precision=18, scale=8), default=0.0, doc='The penalty applied to the investment in the period')
