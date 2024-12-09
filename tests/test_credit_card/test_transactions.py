import pytest
from starlette import status


@pytest.mark.asyncio
async def test_get_installments_due_dates(client, create_valid_credit_card):
    credit_cards = create_valid_credit_card

    payload = {
        'transactionDate': '2024-11-11',
        'creditCardId': credit_cards[0].id,
        'totInstallments': 3
    }
    response = await client.get('creditcard/transaction/installment/due-date', params=payload)
    assert response.status_code == status.HTTP_200_OK