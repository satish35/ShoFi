from flask import Flask,request,make_response,jsonify
from flask_pymongo import PyMongo
import jwt, datetime
import uuid
import bcrypt

app=Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/aiflix"

mongo=PyMongo(app)

def encode(uid, username):
    try:
        payload={
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=0, minutes=10),
            "user": uid,
            "username": username
        }
        token=jwt.encode(
            payload,
            '210702100903',
            algorithm='HS256'
            )
        return token, None
    except Exception as err:
        return None, str(err)
    
def decode(token):
    try:
        res=jwt.decode(
            token,
            '210702100903',
            algorithms='HS256'
            )
        return res, None
    except jwt.ExpiredSignatureError:
        return  None , 'Expired token, please log in again'
    except jwt.InvalidTokenError:
        return  None , 'Invalid token. Please log in again.'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method=='POST':
        try:
            data=request.get_json()
            bytes=data['password'].encode('utf-8')
            salt=bcrypt.gensalt()
            hashed_password= bcrypt.hashpw(bytes, salt)
            mongo.db.user.insert_one({
                "uid": uuid.uuid4().hex,
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "wallet": 0,
                "email": data['email'],
                "avatar": data['avatar'],
                "username": data['username'],
                "password": hashed_password
            }) 
            return make_response(jsonify({
                'status': 'success',
                'message': 'user successfully registered'
            }))
        except Exception as err:
            message=str(err)
            return make_response(jsonify({
                'status': 'error',
                'message': message
            }))
    else:
        pass

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        try:
            data=request.get_json()
            res=mongo.db.user.find_one({
                "username": data['username']
            })
            if res is None:
                print('hi')
                return make_response(jsonify({
                        'status': 'error',
                        'message': 'unauthorized'
                    }))
            else:
                bytes=data['password'].encode('utf-8')
                if(bcrypt.checkpw(bytes, res['password'])):
                    uid= res['uid']
                    token,e=encode(uid, data['username'])
                    if e is None:
                        return make_response(jsonify({
                            'status': 'success',
                            'message': 'login successfully',
                            'token': token
                        }))
                    else:
                        raise Exception(e)
                else:
                    return make_response(jsonify({
                        'status': 'error',
                        'message': 'wrong credientials'
                    }))
        except Exception as err:
            message=str(err)
            return make_response(jsonify({
                'status': 'error',
                'message': message
            }))
        
@app.route('/validate', methods=['POST', 'GET'])
def validate():
    data=request.get_json()
    try:
        if request.method== 'POST':
            res,e=decode(data['token'])
            if e is None:
                return make_response(jsonify({
                    'status': 'success',
                    'message': 'user successfully authenticated',
                    'user': res['user'],
                    'username': res['username']
                }))
            else:
                return make_response(jsonify({
                    'status': 'error',
                    'message': e
                }))
        else:
            pass
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': str(err)
        }))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)