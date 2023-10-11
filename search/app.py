from flask import Flask, make_response, jsonify, request
from flask_pymongo import PyMongo
import datetime
  
app=Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/aiflix"

mongo=PyMongo(app)

@app.route('/search/<username>/<uid>')
def search(username, uid):
    try:
        result=[]
        post_info=[]
        arg=request.args.to_dict(flat=True)
        res=mongo.db.user.find_one({
            "username": username
        })
        if res is None:
            return make_response(jsonify({
                'status': 'fail',
                'message': 'user not found'
            }))
        else:
            res.pop('_id')
            res.pop('password')
            uidf= res['uid']
            if uid == res['uid']:
                res.update({'self': False})
            else:
                res.update({'self': True})
            res2=mongo.db.following.find_one({
                "uid": uid
            })
            if res2 is None:
                res.update({'follow_status': 'follow'})
            elif uidf in res2['following']:
                res.update({'follow_status': 'following'})
            else:
                res.update({'follow_status': 'follow'})
            result.append(res)
            if bool(arg) and arg['latest'] == 1:
                resp=mongo.db.post.find({
                    "uid": uidf
                }).sort("uploaded_on")
            else:
                resp=mongo.db.post.find({
                    "uid": uidf
                }).sort("net_vote", -1)
            for data in resp:
                    if res['self'] == False:
                        data.update({'self': False})
                    else:
                        data.update({'self': True})
                    data.pop('_id')
                    tx_info=data['uploaded_on'].tzinfo
                    difference=datetime.datetime.now(tx_info)-data['uploaded_on']
                    days=divmod(difference.total_seconds(), 3600)
                    data['hours']=int(days[0])
                    post_info.append(data)
        return make_response(jsonify({
            'status': 'success',
            'data': result,
            'post_info': post_info
        }),200)
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': str(err)
        }))

@app.route('/follow', methods=['POST', 'GET'])
def follow():
    if request.method == 'POST':
        try:
            data=request.get_json()
            res=mongo.db.following.find_one({
                "uid": data['uid']
            })
            res5= mongo.db.post.find_one({
                "post_id": data['pid']
            })
            if res is None:
                mongo.db.following.insert_one({
                    "uid": data['uid'],
                    "following": [res5['uid']]
                })
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'followed successfully'
                }))
            else:
                if res5['uid'] in res['following']:
                    return make_response(jsonify({
                        'status': 'success',
                        'message': 'you are already following'
                    }))
                else:
                    query_find={"uid": data['uid']}
                    query_update={ "$push": {
                        "following": res5['uid']
                    }}
                    mongo.db.following.update_one(query_find, query_update)
                    return make_response(jsonify({
                        'status': 'success',
                        'message': 'followed successfully'
                    }))
        except Exception as err:
            return make_response(jsonify({
                'status': 'error',
                'message': str(err)
            }))
    else:
        pass

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    try:
        if request.method == 'POST':
            data=request.get_json()
            mongo.db.profile.insert_one({
                'username': data['username'],
                'uid': data['uid'],
                'bio': data['bio'],
                'whatsapp': data['whatsapp'],
                'email': data['email'],
                'twitter': data['twitter']
            })
            return make_response(jsonify({
                'status': 'success',
                'message': 'profile updated successfully'
            }),200)
        else:
            data=request.args.to_dict(flat=True)
            res= mongo.db.profile.find_one({
                'username': data['username']
            })
            if res is None:
                return make_response(jsonify({
                    'status': 'not found',
                    'message': 'profile not updated'
                }))
            else:
                res.pop('_id')
                return make_response(jsonify({
                    'status': 'success',
                    'data': res
                }))
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': str(err)
        }),500)
    
@app.route('/notify', methods=['POST','GET'])
def notification():
    try:
        if request.method == 'POST':
            data=request.get_json()
            query_find={ "$and": [{"view": 0},{"r_id": data['uid']}] }
            query_update={ "$set": { "view": 1 } }
            mongo.db.notification.update_many(query_find, query_update)
            return make_response(jsonify({
                'status': 'success',
                'message': 'notification viewed'
            }))
        else:
            result=[]
            data=request.args.to_dict(flat=True)
            res=mongo.db.notification.aggregate([
                {
                    "$match":{
                        "r_id": data['uid']
                    }
                },
                { "$sort" : { "time" : -1 } }
            ])
            if res is None:
                return make_response(jsonify({
                    'status': 'no data found',
                    'message': 'no notification found'
                }))
            for data in res:
                data.pop('_id')
                tx_info=data['time'].tzinfo
                difference=datetime.datetime.now(tx_info)-data['time']
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
        }),500)
    
@app.route('/count')
def notify_count():
    try:
        count=0
        data=request.args.to_dict(flat=True)
        res=mongo.db.notification.aggregate([
            {
                "$match":{
                    "$and": [{"view": 0},{"r_id": data['uid']}]
                }
            }
        ])
        for data in res:
            count=count+1
        return make_response(jsonify({
            'status': 'success',
            'count': count
        }))
    except Exception as err:
        print(str(err))
        return make_response(jsonify({
            'status': 'error',
            'message': str(err)
        }),500)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)