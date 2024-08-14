from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.investment import InvestmentManager
from models.investment import InvestmentModel
from schemas.investment import InvestmentSchema
from schemas.request.investment import CreateInvestmentRequest, GetInvestmentRequest, LiquidateInvestmentRequest
from schemas.response.investment import CreateInvestmentResponse, GetInvestmentResponse, LiquidateInvestmentResponse


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()

    async def create_investment(self, investment: CreateInvestmentRequest) -> CreateInvestmentResponse:
        new_investment = InvestmentModel(**investment.model_dump())
        new_investment.owner_id = self.user['user_id']
        # TODO: if liquidation date <= today and liquidation amount set is_liquidated to true
        new_investment = await InvestmentManager(session=self.session).create_investment(new_investment)

        response = CreateInvestmentResponse(
            investment=InvestmentSchema.model_validate(new_investment),
        )

        return response

    async def get_investments(self, params: GetInvestmentRequest) -> GetInvestmentResponse:
        investments = await InvestmentManager(self.session).get_investments(params.model_dump())

        response = GetInvestmentResponse(
            quantity=len(investments),
            investments=InvestmentSchema.model_validate(investments),
        )

        return response

    async def liquidate_investment(self, investment: LiquidateInvestmentRequest) -> LiquidateInvestmentResponse:
        current_investment = await InvestmentManager(self.session).get_investment_by_id(investment.id)

        fields = investment.model_dump()
        fields['is_liquidated'] = True

        liquidated_investment = await InvestmentManager(session=self.session).update_investment(current_investment, fields)

        response = LiquidateInvestmentResponse(
            investment=InvestmentSchema.model_validate(liquidated_investment),
        )

        return response
