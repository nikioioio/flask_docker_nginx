#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()
"""
Функция принимает имя пользователя и должна искать пароль и сравнивать его с тем что пришло из req
username: параметр
"""


@auth.get_password
def get_password(username):
    if username == 'nikita':
        return 'kedrun'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


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
curl -u nikita:kedrun -i -H -X GET  http://localhost:5000/api/margin/production
"""


@app.route('/api/margin/production', methods=['GET'])
@auth.login_required
def get_tasks():
    return jsonify({'tasks': make_public_task(tasks)})


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H -X GET  http://localhost:5000/api/margin/production/2
"""


@app.route('/api/margin/production/<int:task_id>/', methods=['GET'])
@auth.login_required
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify({'task': make_public_task(task)})


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H "Content-Type: application/json" -X POST -d '....' http://localhost:5000/api/margin/production
"""


@app.route('/api/margin/production', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': make_public_task(task)}), 201


"""
Функция принимает...
Возвращает .....
curl -u nikita:kedrun -i -H "Content-Type: application/json" -X PUT -d '....' http://localhost:5000/api/margin/production/2
"""


@app.route('/api/margin/production/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
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
@auth.login_required
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
