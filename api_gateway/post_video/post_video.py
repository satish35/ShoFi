from flask import request, make_response, jsonify, json
from werkzeug.datastructures import ImmutableMultiDict
import requests

def post_video(filename, username, request):
    try:
        data=request.form.to_dict(flat=True)
        json_data={
            'filename': filename,
            'uid': username,
            'description': data['description']
        }
        res=requests.post(
            'http://127.0.0.1:8080/post',
            json=json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': str(err)
        }))
    
def get_video(uid, hot):
    try:
        if hot == 1:
            res=requests.get(
                'http://127.0.0.1:8080/feed/{}?latest={}'.format(uid, hot)
            )
        else:
            res=requests.get(
                'http://127.0.0.1:8080/feed/{}'.format(uid)
            )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def video(pid):
    try:
        res=requests.get(
            'http://127.0.0.1:8080/video/{}'.format(pid)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))
    
def get_top_video(uid, hot):
    try:
        if hot == 1:
            res=requests.get(
                'http://127.0.0.1:8080/popular_feed/{}?latest={}'.format(uid, hot)
            )
        else:
            res=requests.get(
                'http://127.0.0.1:8080/popular_feed/{}'.format(uid)
            )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def vote(request, uid):
    try:
        data=request.form.to_dict(flat=True)
        json_data={
            "uid": uid,
            "post_id": data['button'],
            "vote": data['vote']
        }
        res=requests.post(
            "http://127.0.0.1:8080/vote",
            json=json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def get_comment(pid):
    try:
        res=requests.get(
            'http://127.0.0.1:8080/comment?pid={}'.format(pid)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def reply_comment(cid,uid, username, comment):
    try:
        json_data={
            'cid': cid,
            'uid': uid,
            'username': username,
            'comment': comment
        }
        res=requests.post(
            'http://127.0.0.1:8080/reply',
            json=json_data
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def post_comment(pid, username, uid, comment):
    try:
        json_data={
            "uid": uid,
            "pid": pid,
            "comment": comment,
            "username": username
        }
        res=requests.post(
            'http://127.0.0.1:8080/comment',
            json=json_data
        )
        print(res.json())
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)