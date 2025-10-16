from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.account import AccountManager
from managers.investment_brazilian_fund import InvestmentBrazilianFundManager
from models.investment_brazilian_fund import (
    InvestmentBrazilianFundsModel,
    InvestmentBrazilianFundsStatementModel,
)
from schemas.investment_brazilian_fund import (
    InvestmentBrazilianFundSchema,
    InvestmentBrazilianFundStatementSchema,
)
from schemas.request.investment import GetBrazilianFundInvestmentsRequest
from schemas.request.investment_brazilian_funds import (
    CreateBrazilianFundInvestmentRequest,
    CreateBrazilianFundInvestmentStatementRequest,
    GetBrazilianFundInvestmentStatementRequest,
)
from schemas.response.investment_brazilian_funds import (
    CreateBrazilianFundInvestmentResponse,
    CreateBrazilianFundInvestmentStatementResponse,
    GetBrazilianFundInvestmentsResponse,
    GetBrazilianFundInvestmentStatementResponse,
)
from services.investment_deprecated import InvestmentServiceDeprecated
from services.utils.datetime import get_period


class InvestmentBrazilianFundService(InvestmentServiceDeprecated):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session, user)
        self.investment_brazilian_fund_manager = InvestmentBrazilianFundManager(session)

    async def create_brazilian_fund_investment(
        self, investment: CreateBrazilianFundInvestmentRequest
    ) -> CreateBrazilianFundInvestmentResponse:
        account = await AccountManager(session=self.session).get_account_by_id(
            account_id=investment.account_id
        )
        custodian_id = account.bank_id

        new_fund = InvestmentBrazilianFundsModel(**investment.model_dump())
        new_fund.owner_id = self.user["user_id"]
        new_fund.custodian_id = custodian_id

        new_fund = await self.investment_brazilian_fund_manager.create_brazilian_fund(
            investment=new_fund
        )

        response = CreateBrazilianFundInvestmentResponse(
            fund=InvestmentBrazilianFundSchema.model_validate(new_fund).transform()
        )

        return response

    async def get_brazilian_fund_investments(
        self, params: GetBrazilianFundInvestmentsRequest
    ) -> GetBrazilianFundInvestmentsResponse:
        statements = (
            await self.investment_brazilian_fund_manager.get_brazilian_fund_investment(
                owner_id=self.user["user_id"],
                investment_id=params.id, 
                is_settled=params.is_settled
            )
        )

        response = GetBrazilianFundInvestmentsResponse(
            quantity=len(statements) if statements else 0,
            investments=(
                [
                    InvestmentBrazilianFundSchema.model_validate(statement).transform()
                    for statement in statements
                ]
                if statements
                else []
            ),
        )

        return response

    async def create_brazilian_fund_investment_statement(
        self, statement: CreateBrazilianFundInvestmentStatementRequest
    ):
        fund_investments = (
            await self.investment_brazilian_fund_manager.get_investments_by_fund_id(
                owner_id=self.user["user_id"],
                fund_id=statement.fund_id
            )
        )
        if not fund_investments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No investment found for this fund",
            )

        previous_statements = (
            await self.investment_brazilian_fund_manager.get_statement(
                fund_id=fund_investments[0].fund_id
            )
        )
        last_statement = previous_statements[0] if previous_statements else None

        # If it is the first statement period must be the same as the investment
        if not last_statement and statement.period != get_period(
            fund_investments[0].transaction_date
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="The period for the first statement must be\
                    the same as the investment",
            )

        # Add the statement information to a new statement object
        new_statement = InvestmentBrazilianFundsStatementModel(
            **statement.model_dump(exclude={"tax_details", "fee_details"})
        )

        # Serialize the tax/fee information and add to the new statement
        new_statement.tax_detail = (
            [tax.model_dump(mode="json") for tax in statement.tax_detail]
            if statement.tax_detail
            else None
        )
        new_statement.fee_detail = (
            [fee.model_dump(mode="json") for fee in statement.fee_detail]
            if statement.fee_detail
            else None
        )

        # Set the tax/fee totals and add to the new statement
        new_statement.total_tax = (
            sum(tax.amount for tax in statement.tax_detail)
            if statement.tax_detail
            else 0.0
        )
        new_statement.total_fee = (
            sum(fee.amount for fee in statement.fee_detail)
            if statement.fee_detail
            else 0.0
        )

        # Link the new statement with the user
        new_statement.owner_id = self.user["user_id"]

        # If there is at least one statement, the previous amount for the current
        #   statement is the gross amount from the last one
        if last_statement:
            new_statement.previous_amount = last_statement.gross_amount

        # Check if in the statement period there are any contributions
        period_contribution = [
            tx.amount
            for tx in fund_investments
            if get_period(tx.transaction_date) == statement.period
        ]
        total_period_contribution = (
            sum(a for a in period_contribution) if period_contribution else 0.0
        )
        new_statement.contribution = total_period_contribution

        # Create the entry in the database
        new_statement = (
            await self.investment_brazilian_fund_manager.create_investment_statement(
                statement=new_statement
            )
        )

        response = CreateBrazilianFundInvestmentStatementResponse(
            statement=InvestmentBrazilianFundStatementSchema.model_validate(
                new_statement
            )
        )

        return response

    async def get_brazilian_fund_statements(
        self, params: GetBrazilianFundInvestmentStatementRequest
    ) -> GetBrazilianFundInvestmentStatementResponse:
        statements = await self.investment_brazilian_fund_manager.get_statement(
            fund_id=params.fund_id,
            period=params.period,
            start_period=params.start_period,
            end_period=params.end_period,
        )

        response = GetBrazilianFundInvestmentStatementResponse(
            quantity=len(statements) if statements else 0,
            statements=(
                [
                    InvestmentBrazilianFundStatementSchema.model_validate(statement)
                    for statement in statements
                ]
                if statements
                else []
            ),
        )

        return response
