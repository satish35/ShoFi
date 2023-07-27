from flask import Flask, request, make_response, jsonify
from flask_pymongo import PyMongo, ObjectId
import datetime, random
import uuid
from operator import attrgetter

app=Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/aiflix"

mongo=PyMongo(app)

@app.route('/post', methods=['POST', 'GET'])
def post():
    if request.method == 'POST':
        try:
            data= request.get_json()
            post_id= uuid.uuid4().hex
            res=mongo.db.post.insert_one({
                'post_id': post_id,
                'uid': data['uid'],
                'video': data['filename'],
                'description': data['description'],
                'voters_id': [],
                'uploaded_on': datetime.datetime.now(None),
                'net_vote': 0
            })
            res2=mongo.db.user_post.find_one({
                "uid": data['uid']
            })
            if res2 is None:
                mongo.db.user_post.insert_one({
                    'uid': data['uid'],
                    'post_id': [post_id]
                })
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'video uploaded successfully'
                }))
            else:
                query_find={"uid": data['uid']}
                query_update={ "$push": {
                    "post_id": post_id
                }}
                mongo.db.user_post.update_one(query_find, query_update)
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'video uploaded successfully'
                }))
        except Exception as err:
            return make_response(jsonify({
                'status': 'error',
                'message': str(err)
            }))
    else:
        pass

@app.route('/video/<pid>')
def video(pid):
    try:
        result=[]
        res=mongo.db.post.find_one({
            "post_id": pid
        })
        res1=mongo.db.user.find_one({
            "uid": res['uid']
        })
        res.pop('_id')
        tx_info=res['uploaded_on'].tzinfo
        difference=datetime.datetime.now(tx_info)-res['uploaded_on']
        days=divmod(difference.total_seconds(), 3600)
        res['hours']=int(days[0])
        res['username']=res1['username']
        result.append(res)
        return make_response(jsonify({
            'status': 'success',
            'data': result
        }),200)
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)
                
@app.route('/feed/<uid>')
def feed(uid):
    try:
        arg=request.args.to_dict(flat=True)
        result=[]
        res=mongo.db.following.find_one({
            'uid': uid
        })
        if res is not None:
            followers=res['following']
            for id in followers:
                res1=mongo.db.user_post.aggregate([
                    {
                        "$match":{
                            "uid": id
                        }
                    },
                    {
                        "$lookup":{
                            "from": "user",
                            "localField": "uid",
                            "foreignField": "uid",
                            "as": "user_info"
                        }
                    },
                    { "$unwind": "$user_info"},
                    {
                        "$lookup":{
                            "from": "post",
                            "localField": "post_id",
                            "foreignField": "post_id",
                            "as": "post_info"
                        }
                    },
                    { "$unwind": "$post_info"},
                    {
                        "$project":{
                            "_id": 0,
                            "uid": 1,
                            "username": "$user_info.username",
                            "post_id": "$post_info.post_id",
                            "video": "$post_info.video",
                            "uploaded_on": "$post_info.uploaded_on",
                            "net_vote": "$post_info.net_vote",
                            "description": "$post_info.description"
                        }
                    },
                    {
                        "$limit": 3
                    }
                ])
            for data in res1:
                tx_info=data['uploaded_on'].tzinfo
                difference=datetime.datetime.now(tx_info)-data['uploaded_on']
                days=divmod(difference.total_seconds(), 3600)
                data['hours']=int(days[0])
                result.append(data)
            if bool(arg) and arg['latest'] == '1':
                result.sort(key=lambda x: x['uploaded_on'],  reverse=True)
            else:
                result.sort(key=lambda x: x['net_vote'],  reverse=True)
            return make_response(jsonify({
                'status': 'success',
                'data': result
            }))
        else:
            return make_response(jsonify({
                'status': 'no follwers'
            }))
    except Exception as err:
         return make_response(jsonify({
              'status': 'error',
              'message': str(err)
         }))
    
@app.route('/popular_feed/<uid>')
def top_feed(uid):
    try:
        arg=request.args.to_dict(flat=True)
        result=[]
        res1=mongo.db.following.find_one({
            "uid": uid
        })
        if bool(arg) and arg['latest'] == '1':
            res=mongo.db.post.find().sort("uploaded_on", -1).limit(15)
        else:
            res=mongo.db.post.find().sort("net_vote", -1).limit(15)
        for data in res:
            user=mongo.db.user.find_one({
                "uid": data['uid']
            })
            data.update({'username': user['username']})
            data.pop('_id')
            if res1 is None:
                data.update({'follow_status': 'follow'})
            elif data['uid'] in res1['following']:
                data.update({'follow_status': 'following'})
            else:
                data.update({'follow_status': 'follow'})
            tx_info=data['uploaded_on'].tzinfo
            difference=datetime.datetime.now(tx_info)-data['uploaded_on']
            days=divmod(difference.total_seconds(), 3600)
            data['hours']=int(days[0])
            result.append(data)
        return make_response(jsonify({
            'status': 'success',
            'data': result
        }))
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': str(err)
        }))

@app.route('/vote', methods=['POST', 'GET'])
def vote():
    if request.method == 'POST':
        try:
            data=request.get_json()
            res=mongo.db.post.find_one({
                "post_id": data['post_id']
            })
            if data['uid'] in res['voters_id']:
                return make_response(jsonify({
                    'status': 'done',
                    'message': 'sorry you had voted once'
                }))
            else:
                if data['vote'] == 'plus':
                    query_find={"post_id": data['post_id']}
                    query_update={ 
                        "$push": {
                            "voters_id": data['uid']
                        },
                        "$set": {
                            "net_vote": res['net_vote']+1
                        }
                    }
                else:
                    query_find={"post_id": data['post_id']}
                    query_update={ 
                        "$push": {
                            "voters_id": data['uid']
                        },
                        "$set": {
                            "net_vote": res['net_vote']-1
                        }
                    }
                mongo.db.post.update_one(query_find, query_update)
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'voted successfully'
                }))
        except Exception as err:
            return make_response(jsonify({
                'status': 'error',
                'message': str(err)
            }))
    else:
        pass

@app.route('/comment', methods=['POST', 'GET'])
def comment():
    if request.method == 'POST':
        try:
            c_id=uuid.uuid4().hex
            data= request.get_json()
            res1=mongo.db.user_comment.insert_one({
                'uid': data['uid'],
                'comment_id': c_id,
                'username': data['username'],
                'comment': data['comment'],
                'commented_on': datetime.datetime.now(None),
                'replyed_by': []
            })
            res=mongo.db.comment.find_one({
                "post_id": data['pid']
            })
            if res is None:
                mongo.db.comment.insert_one({
                    "post_id": data['pid'],
                    "comment": [c_id]
                })
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'commented successfully'
                }),200)
            else:
                query_find={"post_id": data['pid']}
                query_update={ "$push": {
                    "comment": c_id
                }}
                mongo.db.comment.update_one(query_find, query_update)
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'commented successfully'
                }),200)
        except Exception as err:
            return make_response(jsonify({
                'status': 'error',
                'message': 'something went wrong'
            }))
    else:
        try:
            result=[]
            replyed_comments=[]
            data=request.args.to_dict(flat=True)
            res=mongo.db.comment.find_one({
                'post_id': data['pid']
            })
            if res is None:
                return make_response(jsonify({
                    'status': 'no data',
                    'message': 'no comments posted by the first to comment'
                }))
            else:
                res2=mongo.db.comment.aggregate([
                    {
                        "$match":{
                            "post_id": data['pid']
                        }
                    },
                    {
                        "$lookup":{
                            "from": "user_comment",
                            "localField": "comment",
                            "foreignField": "comment_id",
                            "as": "comment_info"
                        }
                    },
                    { "$unwind": "$comment_info" },
                    {
                        "$project":{
                            "_id": 0,
                            "comment_id": "$comment_info.comment_id",
                            "username": "$comment_info.username",
                            "comment": "$comment_info.comment",
                            "commented_on": "$comment_info.commented_on",
                            "replyed_by": "$comment_info.replyed_by"
                        }
                    }
                ])
                for data in res2:
                    tx_info=data['commented_on'].tzinfo
                    difference=datetime.datetime.now(tx_info)-data['commented_on']
                    days=divmod(difference.total_seconds(), 3600)
                    data['hours']=int(days[0])
                    if len(data['replyed_by']) == 0:
                        pass
                    else:
                        for comment in data['replyed_by']:
                            res3=mongo.db.user_comment.find_one({
                                "comment_id": comment
                            })
                            res3.pop('_id')
                            tx_info=res3['commented_on'].tzinfo
                            difference=datetime.datetime.now(tx_info)-res3['commented_on']
                            days=divmod(difference.total_seconds(), 3600)
                            res3['hours']=int(days[0])
                            replyed_comments.append(res3)
                        data['replyed_comments']=replyed_comments
                    result.append(data)
                return make_response(jsonify({
                    'status': 'success',
                    'data': result,
                    'count': len(result)
                }))
        except Exception as err:
            print(str(err))
            return make_response(jsonify({
                'status': 'error',
                'message': 'something went wrong'
            }))
        
@app.route('/reply', methods=['POST', 'GET'])
def reply():
    try:
        c_id=uuid.uuid4().hex
        data=request.get_json()
        res1=mongo.db.user_comment.insert_one({
            'uid': data['uid'],
            'comment_id': c_id,
            'username': data['username'],
            'comment': data['comment'],
            'commented_on': datetime.datetime.now(None),
            'replyed_by': []
        })
        res=mongo.db.user_comment.find_one({
            "comment_id": data['cid']
        })
        if res is None:
            return make_response(jsonify({
                'status': 'error',
                'message': 'no comment found'
            }))
        else:
            query_find={"comment_id": data['cid']}
            query_update={ "$push": {
                "replyed_by": c_id
            }}
            mongo.db.user_comment.update_one(query_find, query_update)
            return make_response(jsonify({
                'status': 'success',
                'message': 'replyed successfully'
            }),200)
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }),500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)