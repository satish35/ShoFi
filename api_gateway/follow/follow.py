from flask import request, make_response, jsonify, json
from werkzeug.datastructures import ImmutableMultiDict
import requests

def follow(uid, fid):
    try:
        json_data={
            "uid": uid,
            "fid": fid
        }
        res=requests.post(
            "http://127.0.0.1:8081/follow",
            json=json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def search(username, hot, uid):
    try:
        if hot == 1:
            res=requests.get(
                "http://127.0.0.1:8081/search/{}/{}?latest={}".format(username, uid, hot)
            )
        else:
            res=requests.get(
                "http://127.0.0.1:8081/search/{}/{}".format(username, uid)
            )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)