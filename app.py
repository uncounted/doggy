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
    boards = db.board.find({}, {'_id': False})
    ranking = db.board.find().sort("likes_cnt", -1).limit(3)

    result = checklogin()
    if result == 'logout':
        return render_template("index.html", msg="logout", board=boards, ranking=ranking)
    else:
        return render_template("index.html", userid=result, board=boards, ranking=ranking)

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

@app.route('/searching/<keyword>')
def search(keyword):

    boards = list(db.board.find({'dog_name':keyword}, {'_id':False}))
    if not boards:
        boards = 'empty'

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


@app.route('/update')
def view_update():
    user_id = checklogin()

    postings = list(db.dog.find({'user_id': user_id}, {'_id': False}))
    my_dog=postings[0]['dog_name']

    if user_id == 'logout':
        return jsonify({'msg': '로그 아웃 되었습니다. '})
    else:
        return render_template("update.html", my_dog=my_dog)

@app.route('/modify/<key>')
def view_modify(key):
    user_id = checklogin()
    postings = list(db.board.find({'post_id': int(key)}, {'_id': False}))
    # print(postings[0]["comment"])

    if user_id == 'logout':
        return jsonify({'msg': '로그 아웃 되었습니다. '})
    else:
        return render_template("modify.html", postings=postings)



@app.route('/api/post/update', methods=['POST'])
def post_update():
    user_id = checklogin()
    doggyname_receive = request.form["doggyname_give"]
    postingdoggy_receive = request.form["postingdoggy_give"]

    file = request.files["file_give"]
    extension = file.filename.split('.')[-1]
    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    reg_date = today.strftime('%Y-%m-%d')
    post_id = today.strftime('%Y%m%d%H%M%S')

    filename = f'file-{mytime}'
    save_to = f'static/{filename}.{extension}'

    file.save(save_to)

    doc = {
        'img1': f'{filename}.{extension}',
        'comment': postingdoggy_receive,
        'dog_name': doggyname_receive,
        'user_id': user_id,
        'likes_cnt': 0,
        'post_id': int(post_id),
        'reg_date': reg_date,
        'mod_date': "",
    }

    if user_id == 'logout':
        return jsonify({'msg': '로그 아웃 되었습니다. '})
    else:
        db.board.insert_one(doc)
        return jsonify({'msg': '저장완료'})


@app.route('/api/post/delete', methods=['POST'])
def post_delete():
    post_id_receive = int(request.form["post_id_give"])
    print(post_id_receive)
    db.board.delete_one({'post_id': post_id_receive})
    return jsonify({'result': 'success', 'msg': '게시물이 삭제되었습니다'})


@app.route('/api/post/modify', methods=['POST'])
def post_modify():

    post_id_receive = request.form["post_id_give"]
    posting_doggy_receive = request.form["posting_doggy_give"]

    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    modi_date = today.strftime('%Y-%m-%d')

    try:
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]
        filename = f'file-{mytime}'
        save_to = f'static/{filename}.{extension}'
        file.save(save_to)
        print(post_id_receive)
        db.board.update_one({'post_id': int(post_id_receive)},
                            {'$set': {'comment': posting_doggy_receive}})
        db.board.update_one({'post_id': int(post_id_receive)},
                            {'$set': {'img1': f'{filename}.{extension}'}})
        db.board.update_one({'post_id': int(post_id_receive)},
                            {'$set': {'mod_date': modi_date}})
    except IOError:
        print("파일 이즈 논")
        db.board.update_one({'comment': posting_doggy_receive}, {'$set': {'post_id': int(post_id_receive)}})
        db.board.update_one({'mod_date': modi_date}, {'$set': {'post_id': int(post_id_receive)}})

    return jsonify({'result': 'success', 'msg': '게시물이 수정되었습니다'})

# 좋아요 업데이트
@app.route('/api/likes/update', methods=['POST'])
def update_like():
    user_info = request.form["user_id_give"]
    post_id_receive = int(request.form["post_id_give"])

    doc = {
        "post_id": post_id_receive,
        "user_id": user_info
    }


    db.likes.find({})
    likes_list = list(db.likes.find({'post_id': post_id_receive}, {'_id': False}))
    global action

    if not likes_list:                                                                          #like 테이블이 완전히 비어있다면
        action = 'like'
    else:                                                                                       #like 테이블에 데이터가 있다면
        for i in likes_list:                                                                    #좋아요를 눌렀는지 안눌렀는지를 판별
            if post_id_receive == i['post_id'] and user_info == i['user_id']:
                action = 'unlike'
                break
            else:
                action = 'like'

    if action == 'unlike':                                                                      #눌렀는지 다시 눌러서 취소했는지
        db.likes.delete_one(doc)
    else:
        db.likes.insert_one(doc)

    print(action)
    count = db.likes.count_documents({"post_id": post_id_receive})
    db.board.update_one({"post_id": post_id_receive}, {"$set": {"likes_cnt": count}})

    return render_template("index.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=8086, debug=True)