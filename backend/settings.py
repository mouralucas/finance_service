from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database and test settings
    finance_database_url: str = 'postgresql+asyncpg://dev-user:password@localhost:5434/finance_dev_db'
    finance_log_database_url: str = "mongodb://dev-user-logs:password@localhost:27017/logs_db?authSource=admin"
    test_database_url: str = 'sqlite+aiosqlite:///:memory:'
    echo_sql: bool = False
    echo_test_sql: bool = True
    test: bool = False

    # Project description
    project_name: str = "Finance Service"
    project_description: str = "Microservice for financial management"
    project_version: str = "0.0.1"


settings = Settings()
