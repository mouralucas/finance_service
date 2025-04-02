from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from managers.investment_brazilian_fund import InvestmentBrazilianFundManager
from models.investment import InvestmentFundsBrazilModel
from schemas.investment import InvestmentFundBrSchema
from schemas.request.investment import CreateFundInvestmentBrazilRequest
from schemas.response.investment import CreateInvestmentFundsBrSchema
from services.investment import InvestmentService


class InvestmentBrazilianFundService(InvestmentService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session, user)
        self.investment_brazilian_fund_manager = InvestmentBrazilianFundManager(session)

    async def create_fund_br_investment(self, investment: CreateFundInvestmentBrazilRequest) -> CreateInvestmentFundsBrSchema:
        account = await AccountManager(session=self.session).get_account_by_id(account_id=investment.account_id)
        custodian_id = account.bank_id

        new_fund = InvestmentFundsBrazilModel(**investment.model_dump())
        new_fund.owner_id = self.user['user_id']
        new_fund.custodian_id = custodian_id

        new_fund = await self.investment_brazilian_fund_manager.create_brazilian_fund(investment=new_fund)

        response = CreateInvestmentFundsBrSchema(
            fund=InvestmentFundBrSchema.model_validate(new_fund).transform()
        )

        return response