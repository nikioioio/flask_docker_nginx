import datetime
from os import environ,path
basedir = path.abspath(path.dirname(__file__))

PASS = environ.get('PASS')
# SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') + path.join(basedir, 'identifier.sqlite')



SQLALCHEMY_BINDS = {
    # 'users':        'mysqldb://localhost/users',
    'data_table':      environ.get('DATABASE_URL') + path.join(basedir, 'identifier.sqlite')
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_SECRET_KEY = environ.get('DATABASE_URL')
JWT_ACCESS_TOKEN_EXPIRES  = datetime.timedelta(seconds=1000*60)

