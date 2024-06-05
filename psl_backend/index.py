from datetime import datetime
import importlib
import io
import os
from pathlib import Path
import uuid
import json
from flask import Flask,request, send_file

from psl_backend.api import api_public, port_used
from psl_backend.db import connection

BASE_PATH = Path(__file__).resolve().parent
MEDIA_PATH = os.path.join(BASE_PATH,"uploads")
ANNOTATION_PATH = os.path.join(MEDIA_PATH,'annotaiton')

def hello():
    state = {
        'status': 'ok',
        'message': 'hello world'
    }
    return json.dumps(state)


def download_file():
    path = os.path.normpath(os.path.join(BASE_PATH, request.args.get("filepath")))
    return send_file(path, as_attachment=True)

def upload_file(file,**kwargs):
    type = kwargs.get("type",None)
    uuid_str = str(uuid.uuid4()).replace('-', '_')
    time_str = f'{str(datetime.now().year)}_{str(datetime.now().month).zfill(2)}_{str(datetime.now().day).zfill(2)}_{uuid_str}' 
    filename =f'{time_str}_{type}.{file.filename.rsplit(".",1)[1]}'
    # upload_dir = os.path.normpath(os.path.join(ANNOTATION_PATH))
    if not os.path.exists(ANNOTATION_PATH):
        os.makedirs(ANNOTATION_PATH) 
    filepath = f'{ANNOTATION_PATH}/{filename}'
    file.save(filepath)
    relative_path = str(Path(filepath).relative_to(BASE_PATH))
    # with connection.cursor() as cursor:
    #     sql = "INSERT INTO files (filename, filepath, upload_time) VALUES (%s, %s, %s)"
    #     cursor.execute(sql, (filename,filepath,datetime.now(),datetime.datetime.now()))
    #     connection.commit()
    return True,"上传成功",{"path":relative_path}


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

    app.add_url_rule('/plugin/donwload', str(uuid.uuid4()), download_file, methods=['OPTIONS', 'GET'])

    app.add_url_rule('/api/upload', str(uuid.uuid4()), api_public(upload_file), methods=['OPTIONS', 'PUT'])

    app.add_url_rule('/plugin/execute', str(uuid.uuid4()), api_public(plugin_execute), methods=['OPTIONS', 'POST'])




    app.run(host=flask_host, port=flask_port)









