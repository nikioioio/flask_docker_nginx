import datetime
from os import environ,path
basedir = path.abspath(path.dirname(__file__))

PASS = environ.get('PASS')
# SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') + path.join(basedir, 'identifier.sqlite')



SQLALCHEMY_BINDS = {
    'users': 'postgresql+psycopg2://'+environ.get('PG_USERNAME')+':'+environ.get('PG_PASSWORD')+'@localhost:5432/habrdb',
    'data': 'postgresql+psycopg2://'+environ.get('PG_USERNAME')+':'+environ.get('PG_PASSWORD')+'@localhost:5432/habrdb',
    # 'data_table':      'sqlite:///' + path.join(basedir, 'identifier.sqlite')
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES  = datetime.timedelta(seconds=1000*60)

