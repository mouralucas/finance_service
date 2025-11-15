from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from models.account import AccountModel


class AccountFactory(SQLAlchemyFactory[AccountModel]):
    __check_model__ = False
    __set_relationships__ = False
