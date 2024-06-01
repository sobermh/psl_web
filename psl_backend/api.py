import json
import os
import socket
import inspect
import requests
import typing as t
from flask import Response, request, abort


def get_response(result):
    if request.method == 'GET':
        return result
    else:
        try:
            flag, message, data = result
            code = 200 if flag else 500
            msg = {
                'code': code,
                'message': message,
                'data': data
            }
            return json.dumps(msg)
        except ValueError:
            if isinstance(result, requests.Response):
                return  Response(result.content, status=result.status_code, headers=result.headers.items())
            msg = {
                'code': 401,
                'message': "invalid result",
                'data': None
            }
            return json.dumps(msg)


def get_request_args(func, method):
    def parse_args(params, filter):
        args, kwargs = {}, {}
        for k, v in params.items():
            if k in filter:
                args[k] = v
            else:
                kwargs[k] = v
        return args, kwargs

    signature = inspect.signature(func)
    parameters = signature.parameters

    if method.lower() == 'get':
        args, kwargs = parse_args(request.args, parameters)
    elif method.lower() == 'put':
        args, kwargs = parse_args(request.files, parameters)
        args2, kwargs2 = parse_args(request.form, parameters)
        args.update(args2)
        kwargs.update(kwargs2)
    else:
        args, kwargs = parse_args(request.json, parameters)
    return args, kwargs


def api_public(func):
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            return 'ok'
        try:
            v1, v2 = get_request_args(func, request.method)
            return get_response(func(**v1, **v2))
        except Exception as e:
            return abort(422)
    return wrapper


def port_used(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def download_url(url, path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
    return True
