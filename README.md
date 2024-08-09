# Finance Service

Microservice for financial management

## Installation for development

There are two ways to run the project. 

```bash
sudo docker compose build
```

```bash
sudo docker compose up
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
