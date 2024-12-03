from pydantic import Field, BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel
from rolf_common.schemas import SuccessResponseBase

from schemas.core import CurrencySchema, BankSchema, IndexerTypeSchema, IndexerSchema, LiquiditySchema


class GetSummaryResponse(SuccessResponseBase):
    total_invested: float = Field(..., serialization_alias='totalInvested', description='The total amount invested in the period')
    total_credit_card: float = Field(..., serialization_alias='totalCreditCard', description='The total amount spent in credit card in the period')
    incoming: float = Field(..., serialization_alias='incoming', description='The total amount incoming in the period')
    outgoing: float = Field(..., serialization_alias='outgoing', description='The total amount outgoing in the period')
    balance: float = Field(..., serialization_alias='balance', description='The total amount in the period')


class GetCurrencyResponse(SuccessResponseBase):
    currencies: list[CurrencySchema]


class GetBankResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    banks: list[BankSchema]


class GetIndexerTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    quantity: int = Field(..., description='How many indexer types are available in the request')
    indexer_types: list[IndexerTypeSchema] = Field(..., description='The list of indexer types')


class GetIndexerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    quantity: int = Field(..., description='How many indexer are available in the request')
    indexers: list[IndexerSchema] = Field(..., description='The list of indexers')


class GetLiquidityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    quantity: int = Field(..., description='How many liquidity options are available in the request')
    liquidity: list[LiquiditySchema] = Field(..., description='The list of liquidity options')