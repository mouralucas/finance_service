import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.investment_deprecated import (
    InvestmentBaseModel,
    InvestmentStatementBaseModel,
)


class InvestmentModel(InvestmentBaseModel):
    __tablename__ = "investment"

    transaction_date: Mapped[date] = mapped_column("transaction_date")
    maturity_date: Mapped[date] = mapped_column("maturity_date", nullable=True)

    contracted_rate: Mapped[str] = mapped_column(
        "contracted_rate", String(50), nullable=True
    )

    indexer_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("indexer_type.id"))
    indexer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("indexer.id"))
    indexer: Mapped["IndexerModel"] = relationship(  # noqa: F821
        foreign_keys=[indexer_id], lazy="subquery"
    )
    liquidity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("liquidity.id"))
    liquidity: Mapped["LiquidityModel"] = relationship(  # noqa: F821
        foreign_keys=[liquidity_id], lazy="subquery"
    )
    settlement_date: Mapped[date] = mapped_column("settlement_date", nullable=True)
    settlement_amount: Mapped[Decimal] = mapped_column(
        "settlement_amount", Numeric(precision=18, scale=8), nullable=True
    )
    # TODO: check where this is used and remove the dependency
    objective: Mapped["InvestmentObjectiveModel"] = relationship(  # noqa: F821
        "InvestmentObjectiveModel",
        foreign_keys="InvestmentModel.objective_id",
        lazy="subquery",
    )


class InvestmentStatementModel(InvestmentStatementBaseModel):
    __tablename__ = "investment_statement"

    investment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investment.id"))
    investment: Mapped["InvestmentModel"] = relationship(
        foreign_keys=[investment_id], lazy="subquery"
    )
    at_maturity: Mapped[bool] = mapped_column("at_maturity", default=False)
    contribution: Mapped[Decimal] = mapped_column(
        "incoming",
        Numeric(precision=18, scale=8),
        server_default=text("0"),
        doc="The amount of money that went in the investment in the period",
    )
    withdrawn: Mapped[Decimal] = mapped_column(
        "outgoing",
        Numeric(precision=18, scale=8),
        server_default=text("0"),
        doc="The amount of money that went out of the investment in the period",
    )
