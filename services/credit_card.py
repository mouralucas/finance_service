import datetime

from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.credit_card import CreditCardManager
from models.credit_card import CreditCardModel, CreditCardBillModel
from schemas.credit_card import CreditCardSchema
from schemas.request.credit_card import CreateCreditCardRequest, GetCreditCardRequest, CreateBillEntryRequest, CancelCreditCardRequest
from schemas.response.credit_card import CreateCreditCardResponse, GetCreditCardResponse, CreateBillEntryResponse, CancelCreditCardResponse
from dateutil.relativedelta import relativedelta

from services.utils.datetime import get_period


class CreditCardService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session)
        self.user = user.model_dump()

    async def create_credit_card(self, credit_card: CreateCreditCardRequest) -> CreateCreditCardResponse:
        new_credit_card = CreditCardModel(**credit_card.model_dump())
        new_credit_card.owner_id = self.user['user_id']

        new_credit_card = await CreditCardManager(session=self.session).create_credit_card(new_credit_card)

        response = CreateCreditCardResponse(
            credit_card=CreditCardSchema.model_validate(new_credit_card)
        )

        return response

    async def cancel(self, credit_card: CancelCreditCardRequest) -> CancelCreditCardResponse:
        current_credit_card = await CreditCardManager(session=self.session).get_credit_card_by_id(card_id=credit_card.id)
        if not current_credit_card or not current_credit_card.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Credit card not found or not valid')

        clean_fields = {}
        for key, value in credit_card.model_dump().items():
            if value:
                clean_fields[key] = value
        clean_fields['active'] = False

        updated_credit_card = await CreditCardManager(session=self.session).update_credit_card(current_credit_card, clean_fields)

        response = CancelCreditCardResponse(
            credit_card=CreditCardSchema.model_validate(updated_credit_card)
        )

        return response


    async def get_credit_cards(self, params: GetCreditCardRequest) -> GetCreditCardResponse:
        credit_cards = await CreditCardManager(session=self.session).get_credit_cards(params.model_dump())

        response = GetCreditCardResponse(
            quantity=len(credit_cards) if credit_cards else 0,
            credit_cards=credit_cards
        )

        return response

    async def create_bill_entry(self, bill_entry: CreateBillEntryRequest) -> CreateBillEntryResponse:
        credit_card = await CreditCardManager(session=self.session).get_credit_card_by_id(bill_entry.credit_card_id)
        if not credit_card or not credit_card.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Credit card not valid')

        due_day: int = credit_card.due_day
        close_day: int = credit_card.close_day
        transaction_date = bill_entry.transaction_date
        owner_id = self.user['user_id']
        currency_id = credit_card.currency_id

        entry_list = []
        for i in bill_entry.installments:
            new_bill_entry = CreditCardBillModel(**bill_entry.model_dump(exclude={'installment', 'is_international_transaction', 'tax_detail'}))

            new_bill_entry.owner_id = owner_id
            new_bill_entry.amount = i.amount
            new_bill_entry.currency_id = currency_id
            new_bill_entry.current_installment = i.current_installment
            new_bill_entry.installments = i.installments
            new_bill_entry.due_date = self.set_due_date(transaction_date, close_day, due_day, i.current_installment)
            new_bill_entry.period = get_period(new_bill_entry.due_date)
            new_bill_entry.is_installment = True if len(bill_entry.installments) > 1 else False

            # If it's not an international transaction, currency and amount are the same as the indicated before
            if not bill_entry.is_international_transaction:
                new_bill_entry.transaction_currency_id = currency_id
                new_bill_entry.transaction_amount = i.amount

            entry_list.append(new_bill_entry)

        created_entries = await CreditCardManager(session=self.session).create_bill_entry(entry_list)

        response = CreateBillEntryResponse(
            bill_entry=created_entries
        )

        return response

    @staticmethod
    def set_due_date(transaction_date: datetime.date, close_day: int, due_day: int,
                     installment: int = 1, return_str: bool = False) -> datetime.date | str:
        month = transaction_date.month
        year = transaction_date.year

        if transaction_date.day >= close_day:
            # If bill is already closed, the charge will be set in next month
            month += 1
            if month > 12:
                month = 1
                year += 1

        if close_day > due_day:
            month += 1
            if month > 12:
                month = 1
                year += 1

        due_date = datetime.datetime(year, month, due_day)
        if installment > 1:
            due_date += relativedelta(months=installment-1)

        if return_str:
            return due_date.strftime("%Y-%m-%d")

        return due_date
