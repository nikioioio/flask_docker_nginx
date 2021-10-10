from .modules import service
from flask_executor import app

tables = {
    'table_name': app.config.get('SQLALCHEMY_BINDS')['data_table'],
    'users': app.config.get('SQLALCHEMY_BINDS')['data_table']
}

registry =  service.TableRegistry(tables)


