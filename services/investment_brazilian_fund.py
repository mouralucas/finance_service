from rolf_common.schemas.auth import RequiredUser
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from managers.investment_brazilian_fund import InvestmentBrazilianFundManager
from models.investment_brazilian_fund import InvestmentBrazilianFundsModel, InvestmentBrazilianFundsStatementModel
from schemas.investment_brazilian_fund import InvestmentBrazilianFundSchema, InvestmentBrazilianFundStatementSchema
from schemas.request.investment_brazilian_funds import CreateBrazilianFundInvestmentStatementRequest, CreateBrazilianFundInvestmentRequest, GetBrazilianFundInvestmentStatementRequest
from schemas.response.investment_brazilian_funds import CreateBrazilianFundInvestmentResponse, CreateBrazilianFundInvestmentStatementResponse, GetBrazilianFundInvestmentStatementResponse
from services.investment import InvestmentService
from services.utils.datetime import get_period


class InvestmentBrazilianFundService(InvestmentService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session, user)
        self.investment_brazilian_fund_manager = InvestmentBrazilianFundManager(session)

    async def create_brazilian_fund_investment(self, investment: CreateBrazilianFundInvestmentRequest) -> CreateBrazilianFundInvestmentResponse:
        account = await AccountManager(session=self.session).get_account_by_id(account_id=investment.account_id)
        custodian_id = account.bank_id

        new_fund = InvestmentBrazilianFundsModel(**investment.model_dump())
        new_fund.owner_id = self.user['user_id']
        new_fund.custodian_id = custodian_id

        new_fund = await self.investment_brazilian_fund_manager.create_brazilian_fund(investment=new_fund)

        response = CreateBrazilianFundInvestmentResponse(
            fund=InvestmentBrazilianFundSchema.model_validate(new_fund).transform()
        )

        return response

    async def get_brazilian_fund_investments(self):
        pass

    async def create_brazilian_fund_investment_statement(self, statement: CreateBrazilianFundInvestmentStatementRequest):
        # fund: FundsBrModel = await FinanceManager(self.session).get_brazilian_fund_by_id(statement.fund_id)
        fund_investments = await self.investment_brazilian_fund_manager.get_investments_by_fund_id(fund_id=statement.fund_id)

        previous_statements = await self.investment_brazilian_fund_manager.get_statement(fund_id=fund_investments[-1].id)
        last_statement = previous_statements[0] if previous_statements else None

        # If it is the first statement period must be the same as the investment

        new_statement = InvestmentBrazilianFundsStatementModel(**statement.model_dump(exclude={'tax_details', 'fee_details'}))

        # Serialize the tax/fee information
        new_statement.tax_detail = [tax.model_dump(mode='json') for tax in statement.tax_detail] if statement.tax_detail else None
        new_statement.fee_detail = [fee.model_dump(mode='json') for fee in statement.fee_detail] if statement.fee_detail else None

        # Set the tax/fee totals
        new_statement.total_tax = sum(tax.amount for tax in statement.tax_detail) if statement.tax_detail else 0.0
        new_statement.total_fee = sum(fee.amount for fee in statement.fee_detail) if statement.fee_detail else 0.0

        # Link the statement with the user
        new_statement.owner_id = self.user['user_id']

        # If it is the first statement for the fund, there is no previous amount, just the first contribution
        if not last_statement:
            new_statement.contribution = sum(investment.amount for investment in fund_investments)

        # If there is at least one statement, the previous amount for current statement is the gross amount from the last one
        if last_statement:
            new_statement.previous_amount = last_statement.gross_amount

        # If there is at least one statement, but the period for the current statement is the same from the last contribution
        #   than this contribution should appear in the statement
        if last_statement and statement.period == get_period(fund_investments[-1].transaction_date):
            new_statement.contribution = fund_investments[-1].amount

        new_statement = await self.investment_brazilian_fund_manager.create_investment_statement(statement=new_statement)

        response = CreateBrazilianFundInvestmentStatementResponse(
            statement=InvestmentBrazilianFundStatementSchema.model_validate(new_statement)
        )

        return response

    async def get_brazilian_fund_statements(self, params: GetBrazilianFundInvestmentStatementRequest) -> GetBrazilianFundInvestmentStatementResponse:
        statements = await self.investment_brazilian_fund_manager.get_statement(
            fund_id=params.fund_id, period=params.period, start_period=params.start_period, end_period=params.end_period
        )

        response = GetBrazilianFundInvestmentStatementResponse(
            quantity=len(statements) if statements else 0,
            statements=[InvestmentBrazilianFundStatementSchema.model_validate(statement) for statement in statements]
        )

        return response