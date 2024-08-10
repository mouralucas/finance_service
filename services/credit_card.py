from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.credit_card import CreditCardManager
from models.credit_card import CreditCardModel
from schemas.credit_card import CreditCardSchema
from schemas.request.credit_card import CreateCreditCardRequest
from schemas.response.credit_card import CreateCreditCardResponse


class CreditCardService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session)
        self.user = user.model_dump()

    async def create_credit_card(self, card: CreateCreditCardRequest) -> CreateCreditCardResponse:
        new_credit_card = CreditCardModel(**card.model_dump())
        new_credit_card.owner_id = self.user['user_id']

        new_credit_card = await CreditCardManager(session=self.session).create_credit_card(new_credit_card)

        response = CreateCreditCardResponse(
            credit_card=CreditCardSchema.model_validate(new_credit_card)
        )

        return response
