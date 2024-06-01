from datetime import datetime
import importlib
import io
import os
import uuid
import json
from flask import Flask,request, send_file

from psl_backend.api import api_public, port_used
from psl_backend.db import connection

def hello():
    state = {
        'status': 'ok',
        'message': 'hello world'
    }
    return json.dumps(state)


def download_file():
    pass

def upload_file(**kwargs):
    file = request.files['file']
    filename = file.filename
    upload_dir = f'uploads/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}'

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)  # 如果路径不存在则创建
    filepath = f'{upload_dir}/{str(uuid.uuid4())}.{filename.split(".")[1]}'
    file.save(filepath)
    with connection.cursor() as cursor:
        sql = "INSERT INTO files (filename, filepath, upload_time) VALUES (%s, %s, %s)"
        cursor.execute(sql, (filename,filepath,datetime.now(),datetime.datetime.now()))
        connection.commit()
        return True,"上传成功",None


def plugin_execute(name, func, **kwargs):
    plugin_path = fr"./plugin"
    kwargs["filename"] = name
    file_path =os.path.join(plugin_path, name, "views.py")
    if not os.path.exists(file_path):
        return False, "plugin not found", None
    # name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, func, None)
    return func(**kwargs)

def run_flask_app():
    flask_host = "0.0.0.0"
    flask_port = 23333
    while port_used(flask_port):
        flask_port += 1

    app = Flask(__name__)
    app.add_url_rule('/', str(uuid.uuid4()), api_public(hello), methods=['OPTIONS', 'GET'])

    app.add_url_rule('/plugin/donwload', str(uuid.uuid4()), api_public(download_file), methods=['OPTIONS', 'POST'])
    app.add_url_rule('/api/upload', str(uuid.uuid4()), api_public(upload_file), methods=['OPTIONS', 'PUT'])

    app.add_url_rule('/plugin/execute', str(uuid.uuid4()), api_public(plugin_execute), methods=['OPTIONS', 'POST'])




    app.run(host=flask_host, port=flask_port)


run_flask_app()







