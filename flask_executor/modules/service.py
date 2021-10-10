from sqlalchemy import Table, MetaData, create_engine
import pandas as pd


class TableRegistry(object):

    dict_registry = {}

    def __init__(self, tables):
        for key in tables:
            self.dict_registry[key] = self.get(key ,tables[key])

    def get(self, table_name: str, url: str, **kwargs) -> Table:
        self.engine = create_engine(url, **kwargs)
        metadata = MetaData(self.engine)
        mytable = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
        return mytable

    def getDataFrame(self, sql: str, columns: list) -> pd.DataFrame:
        result_proxy = self.engine.execute(sql)
        return pd.DataFrame(result_proxy.fetchall(), columns=columns)





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