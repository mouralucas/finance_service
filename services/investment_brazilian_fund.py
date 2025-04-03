from rolf_common.schemas.auth import RequiredUser
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from managers.investment_brazilian_fund import InvestmentBrazilianFundManager
from models.investment_brazilian_fund import InvestmentFundsBrazilModel
from schemas.investment_brazilian_fund import InvestmentBrazilianFundSchema
from schemas.request.investment_brazilian_funds import CreateBrazilianFundInvestmentStatementRequest, CreateBrazilianFundInvestmentRequest
from schemas.response.investment_brazilian_funds import CreateBrazilianFundInvestmentResponse
from services.investment import InvestmentService


class InvestmentBrazilianFundService(InvestmentService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session, user)
        self.investment_brazilian_fund_manager = InvestmentBrazilianFundManager(session)

    async def create_brazilian_fund_investment(self, investment: CreateBrazilianFundInvestmentRequest) -> CreateBrazilianFundInvestmentResponse:
        account = await AccountManager(session=self.session).get_account_by_id(account_id=investment.account_id)
        custodian_id = account.bank_id

        new_fund = InvestmentFundsBrazilModel(**investment.model_dump())
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
        fund_investment = InvestmentBrazilianFundManager(self.session).get_investment_fund_by_id(statement.investment_id)

