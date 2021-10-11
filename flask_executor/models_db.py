from .modules import service
from flask_executor import app

tables = {
    'data': app.config.get('SQLALCHEMY_BINDS')['data'],
    'users': app.config.get('SQLALCHEMY_BINDS')['users']
}

registry =  service.TableRegistry(tables)


