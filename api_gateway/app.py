from flask import Flask, request, make_response, jsonify, redirect, url_for, abort, render_template, flash
from register import register_user
from authorize import authorize
from post_video import post_video
from follow import follow
from flask_pymongo import PyMongo

app=Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/aiflix"

mongo=PyMongo(app)

@app.route('/home')
def home():
    result=[]
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        arg=request.args.to_dict(flat=True)
        if bool(arg):
            hot=1
        else:
            hot=0
        resp=post_video.get_video(res['user'], hot)
        if resp['status'] == 'success':
            result.append(res)
            return render_template('/home.html', data=resp['data'], data2=result)
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
        return redirect(url_for('ulogin'))
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
    res=authorize.validate(request.cookies.get('token'))
    if res['status'] == 'success':
        arg=request.args.to_dict(flat=True)
        if bool(arg):
            hot=1
        else:
            hot=0
        res1=follow.search(request.cookies.get('username'), hot, res['user'])
        if res1['status'] == 'error' or res1['status'] == 'fail':
            abort(500)
        else:
            result.append(res)
            return render_template('/search.html', user=res1['data'], data=res1['post_info'], data2=result)
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
            return redirect(url_for('login'))
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
            result.append(res)
            return render_template('/upload.html', data2=result)
    else:
        return redirect(url_for('login'))
    

@app.route('/vote', methods=['POST', 'GET'])
def vote():
    if request.method == 'POST':
        res=authorize.validate(request.cookies.get('token'))
        if res['status'] == 'success':
            data=request.form.to_dict(flat=True)
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
            return redirect(url_for('login'))
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
        if resp['status'] == 'success':
            result.append(res)
            return render_template('/popular.html', data=resp['data'], data2=result)
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
            resp1=post_video.video(data['pid'])
            resp=post_video.get_comment(data['pid'])
            if resp['status'] == 'no data':
                result.append(res)
                return render_template('/comment.html', data=resp1['data'], data2=result)
            elif resp['status'] == 'error':
                abort(500)
            else:
                result.append(res)
                return render_template('/comment.html', comment=resp['data'], data=resp1['data'], data2=result, count=resp['count'])
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

if __name__ == '__main__':
    app.run()