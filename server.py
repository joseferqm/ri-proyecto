"""
$ export FLASK_APP=server.py
$ flask run
"""
import os
from flask import Flask
from flask import request
from flask import send_from_directory
from flask_cors import CORS

from ri_system.system import System

app = Flask(__name__)
cors = CORS(app)

# Directorio de archivos locales para las paginas en cache
app.config['LOCAL_FILES_CONFIG'] = '{}/RI_Coleccion/Coleccion'.format(os.getcwd())

ri_system = System(False, True)
ri_system.prepare_collection()


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/executeQuery', methods=['GET'])
def data_cluster():
    query_string = request.args.get('query_string', '')
    # print('Query string -> {}'.format(query_string))
    document_entries = ri_system.execute_query(query_string)
    return document_entries


@app.route('/RI_Coleccion/Coleccion/<path:filename>')
def send_js(filename):
    return send_from_directory(app.config['LOCAL_FILES_CONFIG'], filename)


if __name__ == "__main__":
    app.run()
