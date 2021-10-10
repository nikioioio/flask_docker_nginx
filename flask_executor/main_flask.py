from flask import Flask,request
import json
import pandas as pd


app = Flask(__name__)
app.config.from_pyfile('../settings.py')



@app.route('/')
def hello_world():
    return 'Hello ld!'

@app.route('/get_val',methods = ['POST'])
def post_r():
    print(request.headers)
    a = request.files['test']
    # доп параметры request
    # b = request.form
    df = pd.read_excel(a,sheet_name='Sheet1')
    print(df)
    return json.dumps({'status':200})
    # return request.args

# Функция  разрешающая запросы с js другого ресурса (комментировать когда запросы с postman
@app.after_request
def after_request(response):
    white_origin= ['http://127.0.0.1:8000','http://127.0.0.1:5000']
    try:
        if request.headers['Origin'] in white_origin:
            response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
            response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    except KeyError:
        pass
    return response




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
