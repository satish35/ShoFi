from flask import request, make_response, jsonify, json
from werkzeug.datastructures import ImmutableMultiDict
import requests

def follow(uid, pid):
    try:
        json_data={
            "uid": uid,
            "pid": pid
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
    
def post_profile(request, username, uid):
    try:
        data=request.form.to_dict(flat=True)
        json_data={
            'username': username,
            'uid': uid,
            'bio': data['bio'],
            'whatsapp': data['whatsapp'],
            'email': data['email'],
            'twitter': data['twitter']
        }
        res=requests.post(
            'http://127.0.0.1:8081/profile',
            json= json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def get_profile(username):
    try:
        res=requests.get(
            'http://127.0.0.1:8081/profile?username={}'.format(username)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def get_notify(uid):
    try:
        res=requests.get(
            'http://127.0.0.1:8081/notify?uid={}'.format(uid)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def post_notify(uid):
    try:
        json_data={
            'uid': uid
        }
        res=requests.post(
            'http://127.0.0.1:8081/notify',
            json= json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def count(uid):
    try:
        res=requests.get(
            'http://127.0.0.1:8081/count?uid={}'.format(uid)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def avatar(username):
    try:
        res= requests.get(
            'http://127.0.0.1:8080/avatar/{}'.format(username)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def support_money(pid, amount, username):
    try:
        json_data={
            'pid': pid,
            'amount': amount,
            'username': username
        }
        res1= requests.post(
            'http://127.0.0.1:8080/support',
            json= json_data
        )
        return res1.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)