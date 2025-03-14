from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.credit_card import CreditCardManager
from models.credit_card import CreditCardModel, CreditCardTransactionModel
from schemas.credit_card import CreditCardSchema, CreditCardTransactionSchema, CreditCardBillSchema, CreditCardBillHistorySchema, InstallmentsDueDates
from schemas.request.credit_card import CreateCreditCardRequest, GetCreditCardRequest, CreateCreditCardTransactionRequest, CancelCreditCardRequest, GetCreditCardBillRequest, GetCreditCardTransactionsRequest, GetInstallmentsDueDatesRequest
from schemas.response.credit_card import CreateCreditCardResponse, GetCreditCardResponse, CreateCreditCardTransactionResponse, CancelCreditCardResponse, GetCreditCardTransactionResponse, GetCreditCardBillConsolidatedResponse, \
    GetCreditCardBillHistoryResponse, GetInstallmentsDueDatesResponse
from services.utils.datetime import get_period, get_period_range, get_installments_due_dates


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
        credit_cards = await (CreditCardManager(session=self.session)
                              .get_credit_cards(owner_id=self.user['user_id'], credit_card_id=params.id, is_active=params.active))

        response = GetCreditCardResponse(
            quantity=len(credit_cards) if credit_cards else 0,
            credit_cards=[CreditCardSchema.model_validate(data) for data in credit_cards] if credit_cards else [],
        )

        return response

    # Credit card transactions
    async def create_transaction(self, transaction: CreateCreditCardTransactionRequest, entry=None) -> CreateCreditCardTransactionResponse:
        credit_card = await CreditCardManager(session=self.session).get_credit_card_by_id(transaction.credit_card_id)
        if not credit_card or not credit_card.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Credit card not valid')

        owner_id = self.user['user_id']
        currency_id = credit_card.currency_id
        tot_installments = transaction.tot_installments

        entry_list = []
        for i in transaction.installments:
            new_bill_entry = CreditCardTransactionModel(**transaction.model_dump(exclude={'installment', 'is_international_transaction', 'tax_detail', 'tot_installments'}))

            new_bill_entry.owner_id = owner_id
            new_bill_entry.amount = i.amount  # TODO: check this warning
            new_bill_entry.currency_id = currency_id
            new_bill_entry.current_installment = i.current_installment
            new_bill_entry.installments = tot_installments
            new_bill_entry.due_date = i.due_date
            new_bill_entry.period = get_period(new_bill_entry.due_date)
            new_bill_entry.is_installment = True if len(transaction.installments) > 1 else False

            # If it's not an international transaction, currency and amount are the same as the indicated before
            if not transaction.is_international_transaction:
                new_bill_entry.transaction_currency_id = currency_id
                new_bill_entry.transaction_amount = i.amount

            entry_list.append(new_bill_entry)

        created_entries = await CreditCardManager(session=self.session).create_credit_card_transaction(entry_list)
        if len(transaction.installments) > 1:
            [setattr(entry, 'parent_id', created_entries[0].id) for entry in created_entries]

        response = CreateCreditCardTransactionResponse(
            transaction=[CreditCardTransactionSchema.model_validate(entry) for entry in created_entries]
        )

        return response

    async def get_transactions(self, params: GetCreditCardTransactionsRequest) -> GetCreditCardTransactionResponse:
        transactions = await CreditCardManager(session=self.session).get_credit_card_transactions(owner_id=self.user['user_id'],
                                                                                                  start_period=params.start_period,
                                                                                                  end_period=params.end_period,
                                                                                                  parent_id=params.parent_id)

        response = GetCreditCardTransactionResponse(
            quantity=len(transactions) if transactions else 0,
            transactions=[CreditCardTransactionSchema(**transaction) for transaction in transactions] if transactions else []
        )

        return response

    async def get_credit_card_bill_evolution(self, params: GetCreditCardBillRequest) -> GetCreditCardBillConsolidatedResponse:
        bill_consolidated = await self.credit_card_manager.get_bill_history_aggregated(owner_id=self.user['user_id'], start_period=params.start_period, end_period=params.end_period)
        average = sum(item['total_amount'] for item in bill_consolidated) / len(bill_consolidated) if bill_consolidated else 0

        response = GetCreditCardBillConsolidatedResponse(
            bill=[CreditCardBillSchema.model_validate(bill) for bill in bill_consolidated] if bill_consolidated else [],
            average=average,
            goal=2300,
        )

        return response

    async def get_credit_card_bill_by_card(self, params: GetCreditCardBillRequest) -> GetCreditCardBillHistoryResponse:
        bill_by_card = await self.credit_card_manager.get_bill_history_by_card(owner_id=self.user['user_id'], start_period=params.start_period, end_period=params.end_period)
        distinct_cards = set(d['credit_card'] for d in bill_by_card) if bill_by_card else []

        a = {}
        for i in bill_by_card:
            period = i['period']
            card = i['credit_card']
            total_amount = i['total_amount']
            currency_symbol = i['currency_symbol']

            if period not in a:
                a[period] = {
                    'id': period,
                    'period': period,
                    'total_amount': [],
                    'credit_cards': [],
                }


            # a[period]['total_amount'] += total_amount
            for dic in a[period]['total_amount']:
                if dic['currency_symbol'] == currency_symbol:
                    dic['total'] += total_amount
                    break
                else:
                    a[period]['total_amount'].append({'currency_symbol': currency_symbol, 'total': total_amount})
            else:
                a[period]['total_amount'].append({'currency_symbol': currency_symbol, 'total': total_amount})


            a[period]['credit_cards'].append({
                'nickname': card,
                'currency_symbol': currency_symbol,
                'total': total_amount,
            })

        b = list(a.values())

        response = GetCreditCardBillHistoryResponse(
            credit_card_bill_history=[CreditCardBillHistorySchema.model_validate(i) for i in b],
        )

        return response

    async def get_installments_due_date(self, params: GetInstallmentsDueDatesRequest) -> GetInstallmentsDueDatesResponse:
        credit_card = await CreditCardManager(session=self.session).get_credit_card_by_id(params.credit_card_id)

        installments_due_dates = get_installments_due_dates(transaction_date=params.transaction_date, due_day=credit_card.due_day, close_day=credit_card.close_day,
                                                            tot_installments=params.tot_installments)

        response = GetInstallmentsDueDatesResponse(
            due_dates=[InstallmentsDueDates.model_validate(due_date) for due_date in installments_due_dates],
        )

        return response

    @staticmethod
    def set_due_date(transaction_date: date, close_day: int, due_day: int,
                     installment: int = 1, return_str: bool = False) -> date | str:
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

        due_date = datetime(year, month, due_day)
        if installment > 1:
            due_date += relativedelta(months=installment - 1)

        if return_str:
            return due_date.strftime("%Y-%m-%d")

        return due_date
