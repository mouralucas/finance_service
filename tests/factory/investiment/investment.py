import random

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from models.investment import InvestmentModel

_faker = Faker()

investment_names = [
    "Fundo Aurora Capital",
    "CDB Horizonte Plus",
    "Tesouro Atlas IPCA",
    "Ação Vértice Energia",
    "FII Solaris Prime",
    "ETF Nexus Global",
    "LCI Safira Premium",
    "Fundo Imobiliário Orion Towers",
    "Debênture Vale do Norte",
    "Fundo Alpha Estratégia Total",
]


class InvestmentFactory(SQLAlchemyFactory[InvestmentModel]):
    __check_model__ = False
    __set_relationships__ = False

    name = lambda: random.choice(investment_names)
