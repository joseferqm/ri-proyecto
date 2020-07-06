"""
$ export FLASK_APP=server.py
$ flask run
"""
import os
from flask import Flask
from flask import request
from flask import send_from_directory
from flask_cors import CORS

from sri.ri_system.system import System

app = Flask(__name__)
cors = CORS(app)

# Directorio de archivos locales para la devolver paginas en cache
# Si el sistema opera en modo de motor de búsqueda, el directorio principal es RI_Coleccion
# y los archivos de la colección se encuentran en el subdirectorio Coleccion
app.config['LOCAL_FILES_CONFIG'] = '{}/RI_Coleccion/Coleccion'.format(os.getcwd())

ri_system = System(False, True)
ri_system.prepare_collection()


# Request para obtener los resultados de una consulta
@app.route('/executeQuery', methods=['GET'])
def execute_query():
    query_string = request.args.get('query_string', '')
    # print('Query string -> {}'.format(query_string))
    document_entries = ri_system.execute_query(query_string)
    return document_entries


# Request para obtener una pagina html estática (versión en caché de los resultados)
@app.route('/RI_Coleccion/Coleccion/<path:filename>')
def send_html(filename):
    return send_from_directory(app.config['LOCAL_FILES_CONFIG'], filename)


if __name__ == "__main__":
    app.run()
