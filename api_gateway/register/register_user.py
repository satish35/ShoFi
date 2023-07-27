from flask import request, make_response, jsonify
import requests,json
from werkzeug.datastructures import ImmutableMultiDict

def register(request):
    try:
        data=request.form.to_dict(flat=True)
        json_data={
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'username': data['username'],
            'password': data['password']
        }
        res=requests.post(
            'http://127.0.0.1:80/register',
            json=json_data
        )
        data=res.json()
        return data
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))