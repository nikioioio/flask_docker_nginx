from .modules import service
from flask_executor import app

tables = {
    'margin_input_instock_balance_d': app.config.get('SQLALCHEMY_BINDS')['margin_input_instock_balance_d'],
    'margin_input_instock_balance': app.config.get('SQLALCHEMY_BINDS')['margin_input_instock_balance']
    # 'users': app.config.get('SQLALCHEMY_BINDS')['users']
}

registry =  service.TableRegistry(tables)



