import uuid
from datetime import date
from decimal import Decimal

from rolf_common.models import SQLModel
from sqlalchemy import JSON, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class InvestmentCategoryModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 21/09/2024
        This table stores the categories of investments. At first only two:
        Fixed Incoming
        Variable Incoming

        This information is used to filter the 'investment_type' model.
    """

    __tablename__ = "investment_category"

    name: Mapped[str] = mapped_column("name", String(50))
    description: Mapped[str] = mapped_column("description", String(250), nullable=True)


class InvestmentTypeModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model is used to store all kinds of investment types.
        In Brazil, for example, it can be CDB, LCI, LCA, Tesouro Direto, etc
    """

    __tablename__ = "investment_type"

    name: Mapped[str] = mapped_column("name", String(200))
    description: Mapped[str] = mapped_column("description", String(200), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investment_type.id"), nullable=True
    )
    parent: Mapped["InvestmentTypeModel"] = relationship(
        foreign_keys=[parent_id], lazy="subquery"
    )
    country_id: Mapped[str] = mapped_column(ForeignKey("country.id"), nullable=True)
    investment_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investment_category.id"), nullable=True
    )
    investment_category: Mapped["InvestmentCategoryModel"] = relationship(
        foreign_keys=[investment_category_id], lazy="subquery"
    )


class InvestmentStatementModel(SQLModel):
    """
    Created by: Lucas Penha de Moura - 11/08/2024
        This model stores the values of each investment at the end of each month
        The fee and tax stored here is only for reference, in case the investment
            were liquidated that day
    """

    __tablename__ = "investment_statement"

    investment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investment.id"))
    investment: Mapped["InvestmentModel"] = relationship(
        foreign_keys=[investment_id], lazy="subquery"
    )
    period: Mapped[int] = mapped_column("period")
    previous_amount: Mapped[Decimal] = mapped_column(
        "start_amount", Numeric(precision=15, scale=5), default=0
    )
    gross_amount: Mapped[Decimal] = mapped_column(
        "gross_amount", Numeric(precision=15, scale=5)
    )
    total_tax: Mapped[Decimal] = mapped_column(
        "total_tax", Numeric(precision=15, scale=5), default=0
    )
    total_fee: Mapped[Decimal] = mapped_column(
        "total_fee", Numeric(precision=15, scale=5), default=0
    )
    net_amount: Mapped[Decimal] = mapped_column(
        "net_amount", Numeric(precision=15, scale=5)
    )
    tax_detail: Mapped[list[dict]] = mapped_column("tax_detail", JSON, nullable=True)
    fee_detail: Mapped[list[dict]] = mapped_column("fee_detail", JSON, nullable=True)
    reference_date: Mapped[date] = mapped_column("reference_date")
    at_maturity: Mapped[bool] = mapped_column("at_maturity", default=False)
    value_change: Mapped[Decimal] = mapped_column(
        "value_change", Numeric(precision=15, scale=5), nullable=True
    )
    percentage_change: Mapped[Decimal] = mapped_column(
        "percentage_change", Numeric(precision=9, scale=3), nullable=True
    )
    index_percent_change: Mapped[Decimal] = mapped_column(
        "index_change",
        Numeric(precision=9, scale=3),
        nullable=True,
        doc="How mach the index changed in the period",
    )


class InvestmentObjectiveModel(SQLModel):
    __tablename__ = "investment_objective"

    owner_id: Mapped[uuid.UUID] = mapped_column("owner_id")
    title: Mapped[str] = mapped_column("title", String(100))
    description: Mapped[str] = mapped_column("description", String(500), nullable=True)
    amount: Mapped[Decimal] = mapped_column("amount", Numeric(precision=15, scale=5))
    estimated_deadline: Mapped[date] = mapped_column(
        "estimated_deadline", nullable=True
    )
    currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"))

    # Investment reverse relation
    investments: Mapped[list["InvestmentModel"]] = relationship(
        back_populates="objective", lazy="subquery"
    )


class FundsBrModel(SQLModel):
    __tablename__ = "funds_br"

    name: Mapped[str] = mapped_column("name", String(200))
    fund_cnpj: Mapped[str] = mapped_column("fund_cnpj", String(18))
    administrator: Mapped[str] = mapped_column("administrator", String(250))
    administrator_cnpj: Mapped[str] = mapped_column("administrator_cnpj", String(18))
    status: Mapped[str] = mapped_column("status", String(150), nullable=True)
    start_date: Mapped[date] = mapped_column(
        "start_date", doc="The day that the fund start"
    )

    minimum_balance: Mapped[Decimal] = mapped_column(
        "minimum_balance",
        Numeric(precision=18, scale=8),
        doc="The minimum amount to be in the fund",
    )
    minimum_investment: Mapped[Decimal] = mapped_column(
        "minimum_investment",
        Numeric(precision=18, scale=8),
        doc="The minimum amount for every transaction in the fund",
    )
    minimum_withdraw: Mapped[Decimal] = mapped_column(
        "minimum_withdraw",
        Numeric(precision=18, scale=8),
        doc="The minimum amount for every transaction in the fund",
    )
    initial_investment: Mapped[Decimal] = mapped_column(
        "initial_investment",
        Numeric(precision=18, scale=8),
        doc="The initial amount to be in the fund",
    )

    investment_quotation: Mapped[str] = mapped_column(
        "investment_quotation",
        String(25),
        doc="The number of days until the quotation after the investment",
    )
    redemption_quotation: Mapped[str] = mapped_column(
        "redemption_quotation",
        String(25),
        doc="The number of days until the quotation after the redemption",
    )
    redemption_settlement: Mapped[str] = mapped_column(
        "redemption_settlement",
        String(25),
        doc="The number of days until the redemption is settled to the investor",
    )

    fees: Mapped[list[dict]] = mapped_column(
        "fees", JSON, doc="The list of fees that apply to the investment"
    )

    benchmark: Mapped[str] = mapped_column("benchmark", String(50), nullable=True)


### New Investment Models ###
class InvestmentBaseModel(SQLModel):
    __abstract__ = True

    owner_id: Mapped[uuid.UUID] = mapped_column("owner_id")
    name: Mapped[str] = mapped_column("name", String(200))

    custodian_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bank.id"))
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account.id"))

    price: Mapped[Decimal] = mapped_column(
        "price",
        Numeric(precision=18, scale=8),
        doc="Price per unit/share of an investment",
    )
    quantity: Mapped[Decimal] = mapped_column(
        "quantity", Numeric(precision=18, scale=8), doc="Quantity acquired"
    )
    amount: Mapped[Decimal] = mapped_column("amount", Numeric(precision=18, scale=8))

    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investment_type.id"))
    currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"))
    country_id: Mapped[str] = mapped_column(ForeignKey("country.id"))
    objective_id: Mapped[str] = mapped_column(
        ForeignKey("investment_objective.id"), nullable=True
    )
    is_settled: Mapped[bool] = mapped_column("is_settled", default=False)

    tax: Mapped[list[dict]] = mapped_column(
        "tax",
        type_=JSON,
        nullable=True,
        doc="Tax information. What taxes are levied on investments and its rates",
    )
    fee: Mapped[list[dict]] = mapped_column(
        "fee",
        type_=JSON,
        nullable=True,
        doc="Fee information. What fees are levied on investments and its rates",
    )

    observation: Mapped[str] = mapped_column("observation", Text, nullable=True)


class InvestmentStatementBaseModel(SQLModel):
    __abstract__ = True

    period: Mapped[int] = mapped_column("period")
    previous_amount: Mapped[Decimal] = mapped_column(
        "start_amount", Numeric(precision=15, scale=5), default=0
    )
    gross_amount: Mapped[Decimal] = mapped_column(
        "gross_amount", Numeric(precision=15, scale=5)
    )
    total_tax: Mapped[Decimal] = mapped_column(
        "total_tax", Numeric(precision=15, scale=5), default=0
    )
    total_fee: Mapped[Decimal] = mapped_column(
        "total_fee", Numeric(precision=15, scale=5), default=0
    )
    net_amount: Mapped[Decimal] = mapped_column(
        "net_amount", Numeric(precision=15, scale=5)
    )
    tax_detail: Mapped[list[dict]] = mapped_column("tax_detail", JSON, nullable=True)
    fee_detail: Mapped[list[dict]] = mapped_column("fee_detail", JSON, nullable=True)
    reference_date: Mapped[date] = mapped_column("reference_date")


"""
Criar a tabela FundsBr que conterá as informações básica do fundo
(ver canal oficial para essas informações)
Ao adicionar um extrato, verificar na tabela InvestmentFundsBr se
houve um investimento naquele mes, se sim, incluir no "aporte do mes"
na tabela
    do extrato, assim ao calcular a evolução essa valor é somado ao valor
    inicial do mês e não distorce o cálculo da performance
"""
