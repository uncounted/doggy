from flask import Flask, render_template, request, jsonify, url_for, make_response
import jwt
import datetime
import hashlib
import certifi
from pymongo import MongoClient
from werkzeug.utils import secure_filename, redirect

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

ca = certifi.where()
# 비번: sparta 추가 필요
client = MongoClient('mongodb+srv://test:sparta@cluster0.7eo9i.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
# client = MongoClient('mongodb+srv://hoholoudly:heyhey11@cluster0.qqm1l.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbdoggy

# 로그인 여부 체크(로그인이 필요한 모든 페이지에서 실행 필요)
def checklogin():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload['id']})
        return user_info['user_id']
    except jwt.ExpiredSignatureError:
        return "logout"
    except jwt.exceptions.DecodeError:
        return 'logout'

@app.route('/')
def home():
    # board = db.board.find({}, {'_id':False})
    # for post in board:
    #     print(post['comment'])
    boards = db.board.find({}, {'_id': False})

    result = checklogin()
    if result == 'logout':
        return render_template("index.html", msg="logout", board=boards)
    else:
        return render_template("index.html", userid=result, board=boards)

@app.route('/login')
def login():
    result = checklogin()
    if result == 'logout':
        return render_template('login.html', msg='logout')
    else:
        return render_template('login.html', msg='login')

@app.route('/join')
def join():
    result = checklogin()
    if result == 'logout':
        return render_template('join.html', msg='logout')
    else:
        return render_template('join.html', msg='login')

# @app.route('/logout')
# def logout():
#     return render_template('index.html', msg='logout')

@app.route('/searching/<keyword>')
def search(keyword):
    boards = db.board.find({'dog_name':keyword}, {'_id':False})

    result = checklogin()
    if result == 'logout':
        return render_template("searching.html", msg="logout", board=boards)
    else:
        return render_template("searching.html", userid=result, board=boards)

@app.route('/api/join', methods=['POST'])
def api_join():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    dname_receive = request.form['dname_give']
    dage_receive = request.form['dage_give']
    dbirth_receive = request.form['dbirth_give']
    dog_id = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    if request.form['dgender_give'] =='암컷':
        dgender_receive = 'F'
    else:
        dgender_receive = 'M'
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'user_id': id_receive, 'pwd': pw_hash, 'user_name': name_receive, 'dog_id':dog_id, 'reg_date':datetime.datetime.today()})
    db.dog.insert_one({'user_id':id_receive, 'dog_id':dog_id, 'dog_name':dname_receive, 'dog_age':dage_receive, 'dog_gender':dgender_receive, 'dog_birthday':dbirth_receive})

    return jsonify({'result': 'success'})

@app.route('/api/join/dup', methods=['POST'])
def api_join_dup():
    id_receive = request.form['id_give']
    result = db.user.find_one({'id': id_receive})

    if result:
        return jsonify({'msg':'중복된 아이디가 있습니다'})
    else:
        return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST'])
def api_login():
    # 로그인
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'user_id': id_receive, 'pwd': pw_hash})

    if result is not None:
        payload = {
         'id': id_receive,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=8087, debug=True)