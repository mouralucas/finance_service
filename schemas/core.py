import uuid

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_snake


class BankSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        ..., serialization_alias="bankId", description="The unique id og the bank"
    )
    name: str = Field(
        ..., serialization_alias="bankName", description="The name of the bank"
    )
    code: int | None = Field(None, description="The code of the bank")


class CountrySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    id: str = Field(
        ..., serialization_alias="countryId", description="The unique id of the country"
    )
    name: str = Field(
        ..., serialization_alias="countryName", description="The name of the country"
    )


class CurrencySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
    )

    id: str = Field(
        ..., serialization_alias="currencyId", json_schema_extra={"example": "BRL"}
    )
    name: str = Field(..., json_schema_extra={"example": "Brazilian Real"})
    symbol: str = Field(..., json_schema_extra={"example": "R$"})


class TaxSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        ..., serialization_alias="taxId", json_schema_extra={"example": uuid.uuid4()}
    )
    name: str = Field(..., description="The name of the tax")
    description: str | None = Field(None, description="The description of the tax")
    country_id: str = Field(..., description="The country of the tax")


class IndexerTypeSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        ...,
        serialization_alias="indexerTypeId",
        description="The unique id of the index type",
    )
    name: str = Field(
        ...,
        serialization_alias="indexerTypeName",
        description="The name of the index type",
    )
    description: str | None = Field(
        None, description="The description of the index type"
    )


class IndexerSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        serialization_alias="indexerId",
        description=" The unique identification of the index",
        json_schema_extra={"example": uuid.uuid4()},
    )
    name: str = Field(
        ..., serialization_alias="indexerName", description="The name of the index"
    )
    description: str | None = Field(None, description="The description of the index")


class LiquiditySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        ...,
        serialization_alias="liquidityId",
        description="The unique id of the liquidity",
    )
    name: str = Field(
        ...,
        serialization_alias="liquidityName",
        description="The name of the liquidity",
    )
    description: str | None = Field(
        None, description="The description of the liquidity"
    )


class CategorySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        ...,
        serialization_alias="categoryId",
        description="The unique id of the category",
    )
    name: str = Field(
        ..., serialization_alias="categoryName", description="The name of the category"
    )
    description: str | None = Field(None, description="The description of the category")
    comment: str | None = Field(None, description="The comments of the category")
    order: int | None = Field(None, description="The order of the category")


class TaxFeeSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    id: uuid.UUID = Field(
        ..., serialization_alias="taxFeeId", description="The unique id of the tax"
    )
    name: str = Field(..., description="The name of the tax or fee")
    description: str | None = Field(
        None, description="The description of the tax of fee"
    )
    acronyms: str | None = Field(None, description="The acronyms of the tax or fee")
    country_id: str = Field(..., description="The country of the tax or fee")
    type: str = Field(..., description="Whether id tax or fee")


class TaxFeeDetailSchema(BaseModel):
    id: str = Field(..., description="The unique id of the tax or fee")
    currency_id: str = Field(..., description="The currency of the tax or fee")
    amount: float = Field(..., description="The amount of the tax or fee")


class ExpensesByCategory(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    category_id: uuid.UUID = Field(..., description="The category id")
    category_name: str = Field(..., description="The category name")
    total: float = Field(..., description="The total amount by category")


class PeriodicitySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    id: uuid.UUID = Field(...)
    description: str | None = Field(None)
    order: int | None = Field(None)


# Default Series schema for charts:
class ChartSeriesSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    value: str = Field(..., description="The value of series")
    name: str = Field(..., description="The name of the series")


class ChartSeriesSchemaV2(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )

    data: list[float] = Field(...)
    label: str = Field(...)
