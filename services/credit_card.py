import datetime

from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.credit_card import CreditCardManager
from models.credit_card import CreditCardModel
from schemas.credit_card import CreditCardSchema
from schemas.request.credit_card import CreateCreditCardRequest, GetCreditCardRequest
from schemas.response.credit_card import CreateCreditCardResponse, GetCreditCardResponse


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

    async def get_credit_cards(self, params: GetCreditCardRequest) -> GetCreditCardResponse:
        credit_cards = await CreditCardManager(session=self.session).get_credit_cards(params.model_dump())

        response = GetCreditCardResponse(
            quantity=len(credit_cards) if credit_cards else 0,
            credit_cards=credit_cards
        )

        return response

    @staticmethod
    def set_due_date(transaction_date: datetime.date, close_day: int, due_day: int, return_str: bool = True) -> datetime.date | str:
        # Get the month and year of transaction
        month = transaction_date.month
        year = transaction_date.year

        if transaction_date.day >= close_day:
            # If bill is already closed, the charge will be set in next month
            month += 1
            if month > 12:
                month = 1
                year += 1

        if close_day > due_day:
            # Se o fechamento é após o vencimento, o vencimento será no mês subsequente
            month += 1
            if month > 12:
                month = 1
                year += 1

        due_date = datetime.datetime(year, month, due_day)

        if return_str:
            return due_date.strftime("%Y-%m-%d")

        return due_date
