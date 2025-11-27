from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from rolf_common.schemas import SuccessResponseBase

from schemas.core import (
    BankSchema,
    ExpensesByCategory,
    IndexerSchema,
    IndexerTypeSchema,
    LiquiditySchema,
    TaxFeeSchema,
)
from schemas.finance import FundsBrSchema, IndexerSeries


class GetSummaryResponse(SuccessResponseBase):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    total_invested: float = Field(
        ..., description="The total amount invested in the period"
    )
    total_credit_card: float = Field(
        ..., description="The total amount spent in credit card in the period"
    )
    incoming: float = Field(..., description="The total amount incoming in the period")
    outgoing: float = Field(..., description="The total amount outgoing in the period")
    balance: float = Field(..., description="The total amount in the period")


class GetBankResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity: int = Field(..., description="The total of banks available")
    banks: list[BankSchema] = Field(..., description="The list of banks available")


class GetIndexerTypeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    quantity: int = Field(
        ..., description="How many indexer types are available in the request"
    )
    indexer_types: list[IndexerTypeSchema] = Field(
        ..., description="The list of indexer types"
    )


class GetIndexerResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    quantity: int = Field(
        ..., description="How many indexer are available in the request"
    )
    indexers: list[IndexerSchema] = Field(..., description="The list of indexers")


class GetIndexerSeriesResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    quantity: int = Field(..., description="The quantity of data available in response")
    series: list[IndexerSeries] = Field(..., description="The list of indexer series")


class GetLiquidityResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    quantity: int = Field(
        ..., description="How many liquidity options are available in the request"
    )
    liquidity: list[LiquiditySchema] = Field(
        ..., description="The list of liquidity options"
    )


class GetExpensesByCategoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    expenses_by_category: list[ExpensesByCategory] = Field(...)


class GetTaxFeeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    tax_fee: list[TaxFeeSchema] = Field(..., description="The tax or fee list")


class CreateBrazilianFundResponse(BaseModel):
    fund: FundsBrSchema = Field(..., description="The created fund")


class GetBrazilianFundsResponse(BaseModel):
    quantity: int = Field(..., description="The quantity of funds available")
    funds: list[FundsBrSchema] = Field(..., description="The available funds")
