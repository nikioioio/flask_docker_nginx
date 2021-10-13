#!flask/bin/python
import json

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_accept import accept
from .modules.service import get_date_arrs_for_filter
from flask_executor import app
import pandas as pd
from .models_db import registry
from sqlalchemy import select, and_, insert, func, extract, delete
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import datetime
from os import environ,path






jwt = JWTManager(app)

@app.route("/api/margin/production/login", methods=['POST'])
@accept('application/json')
def login():
    # password = '2203'
    # hashAndSalt = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    # username = request.json.get("username")
    # password = request.json.get("password")
    # db = registry.dict_registry['users']
    # SQL_QUERY = select(db.columns['username'],db.columns['password']).where(db.columns['username'] == username)
    # username_pass_from_db = registry.engine.execute(SQL_QUERY).fetchall()
    # username_from_db = username_pass_from_db[0][0]
    # password_from_db = username_pass_from_db[0][1]
    # valid = bcrypt.checkpw(password.encode('utf8'), str.encode(password_from_db))
    # if username!=username_from_db or valid==False:
    #     return jsonify({"production": "Bad username or password"}), 401
    access_token = create_access_token(environ.get('PG_USERNAME'))
    return jsonify(access_token=access_token)


"""
Функция принимает имя пользователя и должна искать пароль и сравнивать его с тем что пришло из req
username: параметр
"""
@jwt.expired_token_loader
def my_expired_token_callback():
    return jsonify({'production': 'The token has expired'}), 401


@jwt.user_lookup_error_loader
def customized_error_handler(error):
    return jsonify({
                       'message': error.description,
                       'code': error.status_code
                   }), error.status_code


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'production': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'production': 'Not found'}), 404)



"""
Функция принимает...
Возвращает .....
curl --location --request GET 'http://localhost:5000/api/margin/production' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer ...' \
--data-raw ''
"""
@app.route('/api/margin/production', methods=['GET'])
@accept('application/json')
@jwt_required()
def get_tasks():
    columns = ['id', 'vendor_code', 'prod_name', 'date', 'value']
    db = registry.dict_registry['margin_input_instock_balance']
    SQL_QUERY = select(db)
    jsonUpload = registry.prepareJson(SQL_QUERY=SQL_QUERY, columnsDf=columns, colsPivot=['date'], indexPivot=['id','vendor_code','prod_name'],
                         valuesPivot=['value'])
    return jsonify({'production': jsonUpload})



"""
curl --location --request GET 'http://localhost:5000/api/margin/production/2021' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer ''''''
curl --location --request GET 'http://localhost:5000/api/margin/production/2021' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer ''''''
Входной параметр <int:year> это год за который ходим получить данные 
На выходе {"production":{"columns":[],"data":[],"index":[]}}
"""
@app.route('/api/margin/production/<int:year>', methods=['GET'])
@accept('application/json')
@jwt_required()
def get_task(year):
    db_clean = registry.dict_registry['margin_input_instock_balance']
    columns = [x.key for x in db_clean.columns]
    # Отдаем json для дальнейшей работы
    SQL_QUERY = select(db_clean).where(extract('year', db_clean.columns['date']) == year)
    jsonUpload = registry.prepareJson(SQL_QUERY=SQL_QUERY, columnsDf=columns, colsPivot=['date'], indexPivot=['id'],
                                      valuesPivot=['value'])
    return jsonify({'production': jsonUpload}), 200


"""
curl --location --request POST 'http://localhost:5000/api/margin/production' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer... \
--header 'Content-Type: application/json' \
--data-raw '{
    "Obj":{"vendor_code":"test", "prod_name":"test","date":"2021.06.22","value": 5848481.1}
    }'
На выходе {"production":[id,id2...]} , где id это возврат из бд id о подтверждений записи.
"""
@app.route('/api/margin/production', methods=['POST'])
@accept('application/json')
@jwt_required()
def create_task():

    if not request.json:
        abort(400)

    db = registry.dict_registry['margin_input_instock_balance_d']
    json_body = [request.json[x] for x in request.json]
    SQL_QUERY = insert(db).returning(db.columns['id']).values(json_body)
    response = registry.get_session().execute(SQL_QUERY).fetchall()

    return jsonify({'production': [x[0] for x in response]}), 201


"""
curl --location --request PUT 'http://localhost:5000/api/margin/production/3' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer '
Входной параметр <int:offset_replace> смещение по месяцам(к примеру 3 обозначает что под замену пойдет данные которые начниаются с -3 месяцев от текущего момента)
На выходе {"production":[id,id2...]} , где id это возврат из бд id о подтверждений записи.
"""
@app.route('/api/margin/production/<int:offset_replace>', methods=['PUT'])
@accept('application/json')
@jwt_required()
def update_task(offset_replace):
    db_dirt = registry.dict_registry['margin_input_instock_balance_d']
    db_clean = registry.dict_registry['margin_input_instock_balance']
    columns = [x.key for x in db_dirt.columns]


    # выбираем из грязной таблицы данные с глубиной REWRITING_DEPTH
    filetr_date_arr = get_date_arrs_for_filter(offset_replace)
    SQL_QUERY = select(db_dirt).where(and_(extract('year', db_dirt.columns['date']).in_(filetr_date_arr['years']),
                                           extract('month', db_dirt.columns['date']).in_(filetr_date_arr['months'])
                                           )
                                      )

    # Рассчитываем бизнес логику
    df = registry.getDataFrame(SQL_QUERY, columns).drop('id', axis=1)
    df['date'] = df['date'].astype('str')

    # /////////////////////////////////////////

    # Постобработка
    json_upl = json.loads(df.to_json(orient="index"))
    jsonUpload = [json_upl[x] for x in json_upl]

    # удалить записи из чистой бд которые соответствуют filetr_date_arr(для заменты значений)
    SQL_QUERY = delete(db_clean).where(and_(extract('year', db_clean.columns['date']).in_(filetr_date_arr['years']),
                                            extract('month', db_clean.columns['date']).in_(
                                                filetr_date_arr['months'])
                                            )
                                       )

    registry.get_session().execute(SQL_QUERY)
    SQL_QUERY = insert(db_clean).returning(db_clean.columns['id']).values(jsonUpload)
    response = registry.get_session().execute(SQL_QUERY).fetchall()

    return jsonify({'production': [x[0] for x in response]}), 201


"""
curl --location --request DELETE 'http://localhost:5000/api/margin/production/8' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer ...'
Входной параметр <int:offset_replace> смещение по месяцам(к примеру 3 обозначает что под замену пойдет данные которые начниаются с -3 месяцев от текущего момента)
На выходе {"production":deleted} , где id это возврат из бд id о подтверждений записи.
"""
@app.route('/api/margin/production/<int:offset_replace>', methods=['DELETE'])
@accept('application/json')
@jwt_required()
def delete_task(offset_replace):
    db_clean = registry.dict_registry['margin_input_instock_balance']
    filetr_date_arr = get_date_arrs_for_filter(offset_replace)
    # удалить записи из чистой бд которые соответствуют filetr_date_arr(для заменты значений)
    SQL_QUERY = delete(db_clean).where(and_(extract('year', db_clean.columns['date']).in_(filetr_date_arr['years']),
                                            extract('month', db_clean.columns['date']).in_(
                                                filetr_date_arr['months'])
                                            )
                                       )

    registry.get_session().execute(SQL_QUERY)

    return jsonify({'production':'deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
