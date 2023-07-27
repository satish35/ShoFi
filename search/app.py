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
            if res is None:
                mongo.db.following.insert_one({
                    "uid": data['uid'],
                    "following": [data['fid']]
                })
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'followed successfully'
                }))
            else:
                if data['fid'] in res['following']:
                    return make_response(jsonify({
                        'status': 'success',
                        'message': 'you are already following'
                    }))
                else:
                    query_find={"uid": data['uid']}
                    query_update={ "$push": {
                        "following": data['fid']
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)