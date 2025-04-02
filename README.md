# Finance Service

Microservice for financial management

## Installation for development

There are two ways to run the project. 

```bash
docker compose build
```

```bash
docker compose up
```

This two commands will create the development database and run the project in port 8001.

First step is to create a new virtual environment. There are many ways to do that, 
but the simpler ways is to execute the following command:

```bash
python3 -m venv venv
```

This line will create a virtual environment called venv using the command venv from Python.

Than activate the venv.

```bash
sorce venv/bin/activate
```

To complete the configuration, install all requirements:

```bash
pip3 install -r requirements
```

....

## Logging

For logging errors and information throughout the system some configuration is needed

    1 - Configure lifespan functions to start the process
```python
"""
    This function creates the database connection and set the base logger
    Each microservice defines its own database, and its connection url and name are set in settings
"""

# Instantiate the log database from Rolf Common
mongo_session_manager = NoSqlDatabaseSessionManager(host=settings.log_database_url,
                                                    db_name=settings.log_database_name)
async def start_log_service():
    if settings.log_database_url is None and settings.log_database_name is None:
        return
    else:
        set_db_connection(mongo_session_manager)
        await get_db_connection().initialize()
        set_log_handler(BaseLogDataManager(get_db_connection()))

async def shutdown_log_service():
    if settings.log_database_url is None and settings.log_database_name is None:
        return
    else:
        await mongo_session_manager.close()
```
    
    2 - Then add to the lifespan itself

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        start_log_service(),
    )

    try:
        yield
    finally:
        await asyncio.gather(
            shutdown_log_service(),
        )
```

```python
app = FastAPI(
    # other params
    lifespan=lifespan,
)
```

## Migrations

To run migrations, first create the file with the database changes:

```bash
python3 -m alembic.config revision --autogenerate -m [migration message]
```

Use a migration message that correspond with the changes in SQL models.

Finally, apply the changes into the database using:
```bash
python3 -m alembic.config upgrade head
```

## Used APIs
For finances many APIs are used, but primarily it is used the [Portal de Dados Abertos do Banco Central do Brasil](https://dadosabertos.bcb.gov.br/).

The API uses values from [SGS - Sistema Gerenciador de Séries Temporais](https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries) as references to params.

For Brazilian Funds the following website is used to get official information about the fund.

[Comissão de Valores Mobiliários](https://cvmweb.cvm.gov.br/swb/default.asp?sg_sistema=fundosreg)
[Outro](https://conteudo.cvm.gov.br/menu/regulados/fundos/consultas/fundos.html)

## License

[MIT](https://choosealicense.com/licenses/mit/)
