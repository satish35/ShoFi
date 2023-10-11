from flask import request, make_response, jsonify, json
from werkzeug.datastructures import ImmutableMultiDict
import requests
from datetime import timedelta
from requests_cache import CachedSession
from newscatcherapi import NewsCatcherApiClient

session= CachedSession(
    cache_name='top_in_chart',
    expire_after=timedelta(seconds=60)
)

session2= CachedSession(
    cache_name='top_news',
    expire_after=timedelta(days=2)
)


def post_video(filename, username, request):
    try:
        data=request.form.to_dict(flat=True)
        json_data={
            'filename': filename,
            'uid': username,
            'description': data['description'],
            'public_key': data['public_key']
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
    
def video(pid, uid):
    try:
        res=requests.get(
            'http://127.0.0.1:8080/video/{}/{}'.format(pid, uid)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))
    
def top():
    try:
        res=session.get('http://127.0.0.1:8080/top')
        data1=res.json()
        return data1
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def top_news():
    try:
        # url = 'https://v3-api.newscatcherapi.com/api/search?'
        # params = {'q': 'Top short films teaser news', 'lang': 'en', 'countries': 'US', 'page_size': 10}
        # headers = {'x-api-token': 'NWdBDXmN6U8-rDGUSQfZIGcZy64mn38a7I7xTaTcX4E'}
        # response = session2.get(url, params=params, headers=headers)
        newscatcherapi= NewsCatcherApiClient(x_api_key='NWdBDXmN6U8-rDGUSQfZIGcZy64mn38a7I7xTaTcX4E')
        res= newscatcherapi.get_search(q='Top short films teaser news',lang='en',countries='US',page_size=10)
        return res
        pass
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
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
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def wallet_update(username, post):
    try:
        if post == 0:
            res= requests.get(
                'http://127.0.0.1:8080/wallet_init?username={}'.format(username)
            )
        else:
            json_data={
                "username": username
            }
            res= requests.post(
                'http://127.0.0.1:8080/wallet_init',
                json= json_data
            )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    
def get_key(pid):
    try:
        res= requests.get(
            'http://127.0.0.1:8080/get_key?pid={}'.format(pid)
        )
        return res.json()
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
    