import random

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from models.core import BankModel, CategoryModel, CountryModel, CurrencyModel

_faker = Faker()


class BankFactory(SQLAlchemyFactory[BankModel]):
    __check_model__ = False
    __set_relationships__ = False

    name = lambda: _faker.company()
    code = lambda: random.randint(1000, 9999)


class CurrencyFactory(SQLAlchemyFactory[CurrencyModel]):
    __check_model__ = False
    __set_relationships__ = False

    id = lambda: _faker.pystr(min_chars=3, max_chars=3).upper()
    name = lambda: _faker.currency_name()
    symbol = lambda: _faker.currency_symbol()


class CategoryFactory(SQLAlchemyFactory[CategoryModel]):
    # TODO: how to create with self relation
    __check_model__ = False
    __set_relationships__ = False

    name = lambda: _faker.vehicle_category
    description = lambda: _faker.text(max_nb_chars=300)


class CountryFactory(SQLAlchemyFactory[CountryModel]):
    __check_model__ = False
    __set_relationships__ = False

    id = lambda: _faker.country_code()
    name = lambda: _faker.country()
