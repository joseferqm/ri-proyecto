"""
$ export FLASK_APP=server.py
$ flask run
"""
from flask import Flask
from flask import request
from flask_cors import CORS

from ri_system.system import System

app = Flask(__name__)
cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

ri_system = System(True, True)
ri_system.prepare_collection()


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/executeQuery',  methods=['GET'])
def data_cluster():
    query_string = request.args.get('query_string', '')
    # print('Query string -> {}'.format(query_string))
    document_entries = ri_system.execute_query(query_string)
    return document_entries
