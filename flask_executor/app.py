from flask import Flask,request
import json
import pandas as pd


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello lssbdfvsd!'

@app.route('/get_val',methods = ['POST'])
def post_r():
    a = request.files['test']
    df = pd.read_excel(a,sheet_name='Sheet1')
    print(df)
    return json.dumps({'status':200})
    # return request.args


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
