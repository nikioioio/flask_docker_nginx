#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_accept import accept
from flask_executor import app
import pandas as pd
from .models_db import registry
from sqlalchemy import select, and_, insert, func, extract
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import datetime



jwt = JWTManager(app)

@app.route("/api/margin/production/login", methods=['POST'])
@accept('application/json')
def login():
    # password = '2203'
    # hashAndSalt = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    username = request.json.get("username")
    password = request.json.get("password")
    db = registry.dict_registry['users']
    SQL_QUERY = select(db.columns['username'],db.columns['password']).where(db.columns['username'] == username)
    username_pass_from_db = registry.engine.execute(SQL_QUERY).fetchall()
    username_from_db = username_pass_from_db[0][0]
    password_from_db = username_pass_from_db[0][1]
    valid = bcrypt.checkpw(password.encode('utf8'), str.encode(password_from_db))
    if username!=username_from_db or valid==False:
        return jsonify({"production": "Bad username or password"}), 401
    access_token = create_access_token(username)
    return jsonify(access_token=access_token)


"""
Функция принимает имя пользователя и должна искать пароль и сравнивать его с тем что пришло из req
username: параметр
"""
@jwt.expired_token_loader
def my_expired_token_callback():
    return jsonify({'production': 'The token has expired'}), 401


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'production': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'production': 'Not found'}), 404)


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


def make_public_task(task):
    d = dict((x['id'], x) for x in task)
    return d


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
    columns = ['id', 'date', 'value']
    db = registry.dict_registry['data']
    SQL_QUERY = select(db)
    jsonUpload = registry.prepareJson(SQL_QUERY=SQL_QUERY, columnsDf=columns, colsPivot=['date'], indexPivot=['id'],
                         valuesPivot=['value'])

    return jsonify({'production': jsonUpload})


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H -X GET  http://localhost:5000/api/margin/production/2
"""


@app.route('/api/margin/production/<int:year>/', methods=['GET'])
@accept('application/json')
@jwt_required()
def get_task(year):
    columns = ['id', 'date', 'value']
    db = registry.dict_registry['data']
    SQL_QUERY = select(db).where(extract('year', db.columns['date']) == year)
    jsonUpload = registry.prepareJson(SQL_QUERY=SQL_QUERY, columnsDf=columns, colsPivot=['date'], indexPivot=['id'],
                                      valuesPivot=['value'])


    return jsonify({'production': jsonUpload}), 200


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H "Content-Type: application/json" -X POST -d '....' http://localhost:5000/api/margin/production
"""


@app.route('/api/margin/production', methods=['POST'])
@accept('application/json')
@jwt_required()
def create_task():
    if not request.json:
        abort(400)

    db = registry.dict_registry['data']
    json_body = [request.json[x] for x in request.json]
    SQL_QUERY = insert(db).returning(db.columns['id']).values(json_body)
    response = registry.engine.execute(SQL_QUERY).fetchall()

    return jsonify({'added_id': [x[0] for x in response]}), 201


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H "Content-Type: application/json" -X PUT -d '....' http://localhost:5000/api/margin/production/2
"""


@app.route('/api/margin/production/<int:task_id>', methods=['PUT'])
@accept('application/json')
@jwt_required()
def update_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and not isinstance(request.json['title'], str):
        abort(400)
    if 'description' in request.json and not isinstance(request.json['description'], str):
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': make_public_task(task[0])})


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H "Content-Type: application/json" -X DELETE  http://localhost:5000/api/margin/production/2
"""


@app.route('/api/margin/production/<int:task_id>', methods=['DELETE'])
@accept('application/json')
@jwt_required()
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
