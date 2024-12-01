import datetime

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.credit_card import CreditCardManager
from models.credit_card import CreditCardModel, CreditCardTransactionModel
from schemas.credit_card import CreditCardSchema, CreditCardTransactionSchema, CreditCardBillSchema
from schemas.request.credit_card import CreateCreditCardRequest, GetCreditCardRequest, CreateCreditCardTransactionRequest, CancelCreditCardRequest, GetCreditCardBillRequest, GetCreditCardTransactionsRequest
from schemas.response.credit_card import CreateCreditCardResponse, GetCreditCardResponse, CreateCreditCardTransactionResponse, CancelCreditCardResponse, GetCreditCardTransactionResponse, GetCreditCardBillConsolidatedResponse, GetCreditCardBillByCardResponse
from services.utils.datetime import get_period, get_period_range


class CreditCardService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session)
        self.user = user.model_dump()
        self.credit_card_manager = CreditCardManager(session=self.session)

    async def create_credit_card(self, credit_card: CreateCreditCardRequest) -> CreateCreditCardResponse:
        new_credit_card = CreditCardModel(**credit_card.model_dump())
        new_credit_card.owner_id = self.user['user_id']

        new_credit_card = await CreditCardManager(session=self.session).create_credit_card(new_credit_card)

        response = CreateCreditCardResponse(
            credit_card=CreditCardSchema.model_validate(new_credit_card)
        )

        return response

    async def cancel_credit_card(self, credit_card: CancelCreditCardRequest) -> CancelCreditCardResponse:
        current_credit_card = await CreditCardManager(session=self.session).get_credit_card_by_id(card_id=credit_card.id)
        if not current_credit_card or not current_credit_card.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Credit card not found or not valid')

        # TODO: user model_dump(exclude_unset=True)
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
            credit_cards=[CreditCardSchema.model_validate(data) for data in credit_cards]
        )

        return response

    # Credit card transactions
    async def create_transaction(self, bill_entry: CreateCreditCardTransactionRequest) -> CreateCreditCardTransactionResponse:
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
            new_bill_entry = CreditCardTransactionModel(**bill_entry.model_dump(exclude={'installment', 'is_international_transaction', 'tax_detail'}))

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

        created_entries = await CreditCardManager(session=self.session).create_credit_card_transaction(entry_list)

        response = CreateCreditCardTransactionResponse(
            transaction=created_entries
        )

        return response

    async def get_transactions(self, params: GetCreditCardTransactionsRequest) -> GetCreditCardTransactionResponse:
        transactions = await CreditCardManager(session=self.session).get_credit_card_transactions(owner_id=self.user['user_id'],
                                                                                                  start_period=params.start_period,
                                                                                                  end_period=params.end_period)

        response = GetCreditCardTransactionResponse(
            quantity=len(transactions) if transactions else 0,
            transactions=[CreditCardTransactionSchema(**transaction) for transaction in transactions] if transactions else []
        )

        return response

    async def get_credit_card_bill_consolidated(self, params: GetCreditCardBillRequest) -> GetCreditCardBillConsolidatedResponse:
        bill_consolidated = await self.credit_card_manager.get_bill_history_aggregated(owner_id=self.user['user_id'], start_period=params.start_period, end_period=params.end_period)
        average = sum(item['total_amount'] for item in bill_consolidated) / len(bill_consolidated) if bill_consolidated else 0

        response = GetCreditCardBillConsolidatedResponse(
            bill=[CreditCardBillSchema.model_validate(bill) for bill in bill_consolidated] if bill_consolidated else None,
            average=average,
            period_range=get_period_range(201801, 202506),
            goal=2300,
        )

        return response

    async def get_credit_card_bill_by_card(self, params: GetCreditCardBillRequest) -> GetCreditCardBillByCardResponse:
        bill_by_card = await self.credit_card_manager.get_bill_history_by_card(owner_id=self.user['user_id'], start_period=params.start_period, end_period=params.end_period)
        distinct_cards = set(d['credit_card'] for d in bill_by_card)

        a = {}
        for i in bill_by_card:
            period = i['period']
            card = i['credit_card']
            total_amount = i['total_amount']

            if period not in a:
                a[period] = {
                    'id': period,
                    'period': period,
                    'total': 0
                }

            a[period][card] = total_amount
            a[period]['total'] += total_amount

        b = list(a.values())

        response = GetCreditCardBillByCardResponse(
            bill=b,
            cards=list(distinct_cards)
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
            due_date += relativedelta(months=installment - 1)

        if return_str:
            return due_date.strftime("%Y-%m-%d")

        return due_date
