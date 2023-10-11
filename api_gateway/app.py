from flask import Flask, request, make_response, jsonify, redirect, url_for, abort, render_template, flash
from register import register_user
from authorize import authorize
from post_video import post_video
from follow import follow
from flask_pymongo import PyMongo

app=Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/aiflix"

public_key='pk_test_51NZ7EpSFQBSKFhiZHFBI7nhLYOlB2SnXXv3y4WQUgvSTy7lImrZoAgSHVqiSOrXAXakpxkvoweJzJOp26sQ5qw8o00bUCLIyvm'

mongo=PyMongo(app)

@app.route('/home')
def home():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    res3=follow.count(res['user'])
    if res['status'] == 'success':
        arg=request.args.to_dict(flat=True)
        if bool(arg):
            hot=1
        else:
            hot=0
        resp=post_video.get_video(res['user'], hot)
        res4=post_video.top_news()
        if resp['status'] == 'success':
            result.append(res)
            return render_template('/home.html', data=resp['data'], data2=result, count=res3['count'], top_news=res4['articles'])
        else:
            abort(500)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        res=authorize.login(request)
        if res['status'] == 'success':
            resp=make_response(redirect(url_for('popular')))
            resp.set_cookie('token', res['token'])
            return resp
        elif res['status'] and res['message'] == 'wrong credientials':
            flash(res['message'])
            return redirect(request.url)
        else:
            abort(401)
    else:
        return render_template('/login.html')
    
@app.route('/logout')
def logout():
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        resp=make_response(redirect(url_for('login')))
        resp.delete_cookie('token')
        return resp
    else:
        return redirect(url_for('login'))
    
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        auth= request.form.to_dict(flat=True)
        if ('' in auth.values()):
            flash('* marked fields are required')
            return redirect(request.url)
        else:
            res=register_user.register(request)
            if res['status'] == 'success':
                return redirect(url_for('login'))
            else:
                abort(406)
    else:
        return render_template('/register.html')
    
@app.route('/search_input', methods=['POST', 'GET'])
def input():
    res=authorize.validate(request.cookies.get('token'))
    if res['status']=='error':
        resp= jsonify(dict(redirect='login'))
        return resp
    else:
        if request.method=='POST':
            username=request.form.to_dict(flat=True)
            resp= jsonify(dict(redirect='search'))
            resp.set_cookie('username', username['username'])
            return resp
        else:
            pass
    
@app.route('/search')
def search_user():
    result=[]
    profile=[]
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        arg=request.args.to_dict(flat=True)
        if bool(arg):
            hot=1
        else:
            hot=0
        res1=follow.search(request.cookies.get('username'), hot, res['user'])
        res2=follow.get_profile(request.cookies.get('username'))
        res3=follow.count(res['user'])
        if res2['status']=='success':
            profile.append(res2['data'])
        if res1['status'] == 'error' or res1['status'] == 'fail':
            abort(500)
        else:
            result.append(res)
            return render_template('/search.html', user=res1['data'], data=res1['post_info'], data2=result, profile=profile, count=res3['count'])
    else:
        return redirect(url_for('login'))
    
@app.route('/follow', methods=['POST', 'GET'])
def fol():
    if request.method == 'POST':
        res=authorize.validate(request.cookies.get('token'))
        if res['status'] == 'success':
            data=request.form.to_dict(flat=True)
            print(data)
            resp=follow.follow(res['user'], data['button'])
            if resp['status'] == 'success':
                if data['from'] == 'popular':
                   flash(resp['message'])
                   res1= jsonify(dict(redirect='popular'))
                   return res1
                elif data['from'] == 'search': 
                    flash(resp['message'])
                    res2= jsonify(dict(redirect='search'))
                    return res2
                else:
                    flash(resp['message'])
                    res3= jsonify(dict(redirect='home'))
                    return res3
            else:
                abort(500)
        else:
            resp= jsonify(dict(redirect='login'))
            return resp
    else:
        pass
    
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                mongo.save_file(file.filename, file)
                res=post_video.post_video(file.filename, res['user'], request)
                if res['status'] == 'success':
                    flash(res['message'])
                    return redirect(request.url)
                else:
                    abort(500)
        else:
            res3=follow.count(res['user'])
            res2= post_video.wallet_update(res['username'], 0)
            result.append(res)
            return render_template('/upload.html', data2=result, count=res3['count'], wallet=res2['data'])
    else:
        return redirect(url_for('login'))
    

@app.route('/vote', methods=['POST', 'GET'])
def vote():
    if request.method == 'POST':
        res=authorize.validate(request.cookies.get('token'))
        if res['status'] == 'success':
            data=request.form.to_dict(flat=True)
            print(request.url)
            resp=post_video.vote(request, res['user'])
            if resp['status'] == 'success':  
                flash(resp['message'])
                return jsonify(dict(redirect=data['from']))
            elif resp['status'] == 'done':
                flash(resp['message'])
                return jsonify(dict(redirect=data['from']))
            else:
                abort(500)
        else:
            resp= jsonify(dict(redirect='login'))
            return resp
    else:
        pass

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

@app.route('/popular')
def popular():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        arg=request.args.to_dict(flat=True)
        if bool(arg):
            hot=1
        else:
            hot=0
        resp=post_video.get_top_video(res['user'], hot)
        resp1=post_video.top()
        res3=follow.count(res['user'])
        res4=post_video.top_news()
        # print(res4)
        if resp['status'] == 'success':
            result.append(res)
            return render_template('/popular.html', data=resp['data'], data2=result, public_key=public_key, top=resp1['data'], top_news=res4['articles'] , count=res3['count'])
            # return render_template('/popular.html', data=resp['data'], data2=result, public_key=public_key, top=resp1['data'], count=res3['count'])
        else:
            abort(500)
    else:
        return redirect(url_for('login'))
    
@app.route('/suggest')
def suggest():
    result=[]
    resp=mongo.db.user.find({}, {'username': 1, '_id': 0})
    for data in resp:
        result.append(data['username'])
    return make_response(jsonify({
        'data': result
    }))

@app.route('/comment', methods=['POST', 'GET'])
def comment():
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        if request.method == 'POST':
            data=request.args.to_dict(flat=True)
            form_data=request.form.to_dict(flat=True)
            resp=post_video.post_comment(data['pid'], res['username'], res['user'], form_data['comment'])
            flash(resp['message'])
            return redirect(request.url)
        else:
            result=[]
            data=request.args.to_dict(flat=True)
            resp1=post_video.video(data['pid'], res['user'])
            resp=post_video.get_comment(data['pid'])
            res3=follow.count(res['user'])
            if resp['status'] == 'no data':
                result.append(res)
                return render_template('/comment.html', data=resp1['data'], data2=result)
            elif resp['status'] == 'error':
                abort(500)
            else:
                result.append(res)
                return render_template('/comment.html', comment=resp['data'], data=resp1['data'], data2=result, count=resp['count'], count1=res3['count'])
    else:
        return redirect(url_for('login'))
    
@app.route('/reply_comment/<pid>', methods=['POST', 'GET'])
def reply_comment(pid):
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        if request.method == 'POST':
            data=request.args.to_dict(flat=True)
            comment=request.form.to_dict(flat=True)
            resp=post_video.reply_comment(data['cid'], res['user'], res['username'], comment['reply_comment'])
            if resp['status'] == 'error':
                abort(500)
            else:
                flash(resp['message'])
                return redirect('/comment?pid={}'.format(pid))
        else:
            pass
    else:
        return redirect(url_for('login'))
    
@app.route('/profile', methods=['POST','GET'])
def profile():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    res3=follow.count(res['user'])
    if res['status'] == 'success':
        if request.method == 'POST':
            resp=follow.post_profile(request, res['username'], res['user'])
            flash(resp['message'])
            return redirect(request.url)
        else:
            result.append(res)
            return render_template('/profile.html', data2=result, count=res3['count'])
    else:
        return redirect(url_for('login'))
    
@app.route('/notify')
def notify():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        res2=follow.get_notify(res['user'])
        res1=follow.post_notify(res['user'])
        result.append(res)
        return render_template('/notification.html', notify=res2['data'], data2=result)
    else:
        return redirect(url_for('login'))
    
@app.route('/wallet_init')
def wallet_init():
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        resp= post_video.wallet_update(res['username'], 1)
        if res['status'] == 'success':
            resp= jsonify(dict(redirect='wallet'))
            return resp
        else:
            abort(500)
    else:
        resp= jsonify(dict(redirect='login'))
        return resp
    
@app.route('/wallet')
# include status connected check using public key from user
def wallet():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        res1=follow.avatar(res['username'])
        res2= post_video.wallet_update(res['username'], 0)
        result.append(res)
        if res2['data']['wallet'] == 0:
            return render_template('/walletinit.html', data2=result)
        else:
            return render_template('/wallet.html', avatar=res1['data'], data2=result)
    else:
        return redirect(url_for('login'))
    
@app.route('/key')
def key():
    try:
        data = request.args.to_dict(flat=True)
        res= post_video.get_key(data['pid'])
        return res
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))

@app.route('/support_money')
def support():
    try:
        data = request.args.to_dict(flat=True)
        res= follow.support_money(data['pid'], data['amount'], data['username'])
        return res
    except Exception as err:
        return make_response(jsonify({
            'status': 'error',
            'message': 'something went wrong'
        }))

if __name__ == '__main__':
    app.run()