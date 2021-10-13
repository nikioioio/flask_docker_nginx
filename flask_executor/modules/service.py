from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta

# Класс регистрирует подключения к таблицам бд, указанным в settings.py
class TableRegistry(object):

    dict_registry = {}

    def __init__(self, tables):
        for key in tables:
            self.dict_registry[key] = self.get(key ,tables[key])

    def get(self, table_name: str, url: str, **kwargs) -> Table:
        self.engine = create_engine(url, **kwargs)
        metadata = MetaData(self.engine)
        mytable = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
        # session = sessionmaker(bind=self.engine.connect(),autocommit=True,autoflush=True)
        # return [session, mytable]
        return mytable

    def get_session(self):
        sess = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        return sess()

    def getDataFrame(self, sql: str, columns: list) -> pd.DataFrame:
        # result_proxy = self.engine.execute(sql)
        return pd.DataFrame(self.get_session().execute(sql).fetchall(), columns=columns)

    def prepareJson(self, SQL_QUERY, columnsDf, colsPivot, indexPivot, valuesPivot):
        df = self.getDataFrame(sql=SQL_QUERY, columns=columnsDf)
        df['date'] = df['date'].astype('str')
        df = df.pivot_table(columns=colsPivot, index=indexPivot, aggfunc='sum', values=valuesPivot).reset_index()
        df.columns = [x[1] if x[1]!='' else x[0]  for x in df.columns]

        return json.loads(df.to_json(orient="split"))


'''Функция принимает на вход смещение в месяцах, и формирует словарь фильтров для фильтрации данных, которые требуется перезаписать.
На выходе словарь структуры {years:[],months:[]}'''
def get_date_arrs_for_filter(offset_month: int) -> dict:
    one_month = date.today() + relativedelta(months=-offset_month)
    start = one_month
    end = date.today()
    daterange = list(set([datetime( (start + timedelta(days=x)).year, (start + timedelta(days=x)).month ,1  )  for x in range(0, (end-start).days)]))
    return {
        'years': list(set([str(x.year) for x in daterange])),
        'months': list(set([str(x.month) for x in daterange]))
    }

def jwt_error_callback(error):
    print(error)
    return 0



# def get_tables(db,tables):
#     tables_output = {}
#     metadata = MetaData()
#     for table in tables:
#         table_reflection = Table(table, metadata, autoload=True, autoload_with=db.engine, info={'bind_key': 'data_table'})
#         attrs = {"__table__": table_reflection}
#         TableModel = type(table, (db.Model,), attrs)
#         tables_output[table] = TableModel
#
#     return tables_output