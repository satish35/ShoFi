from flask import request, make_response, jsonify, json
import requests
from werkzeug.datastructures import ImmutableMultiDict

def login(request):
    try:
        data=request.form.to_dict(flat=True)
        json_data={
            'username': data['username'],
            'password': data['password']
        }
        res=requests.post(
            'http://127.0.0.1:80/login',
            json=json_data
        )
        data=res.json()
        return data
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))
    
def validate(token):
    try:
        json_data={
            'token': token
        }
        res=requests.post(
            'http://127.0.0.1:80/validate',
            json=json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))