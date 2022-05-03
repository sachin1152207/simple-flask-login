from flask import Flask, make_response, render_template, request, redirect, url_for
import random
from hashlib import md5, sha256
import sqlite3

class DB():
    code = '''Return Code:
            [0][0] : Full Name
            [0][1] : Email
            [0][2] : Password
            [0][3] : Session Object
        '''
    conn = sqlite3.connect('account.db', check_same_thread=False)
    cursor = conn.cursor()
    def create(fullName, Email, Password):
        '''CREATE TABLE "Account" (
            "fullName"	TEXT,
            "Email"	TEXT,
            "Password"	TEXT,
            "SessionObject"	TEXT
        );'''
        Password = md5(Password.encode()).hexdigest()
        UID = sha256(f"{fullName}-{Email}-{Password}".encode('utf-8')).hexdigest()
        PID = "1000" + str(random.randint(1111, 9999))
        Session_code = str(random.randint(1111, 9999))
        Session_Obj = f"{UID}-{PID}-{Email}-{Session_code}"
        checkAccount = DB.cursor.execute(f"SELECT * FROM Account WHERE Email = '{Email}'").fetchall()
        if len(checkAccount) == 0:
            DB.cursor.execute(f"INSERT INTO Account VALUES('{fullName}', '{Email}', '{Password}','{Session_Obj}')")
            DB.conn.commit()
            return 201
        elif checkAccount[0][1] == Email:
            return 302
    def read(Email):
        values = DB.cursor.execute(f"SELECT * FROM Account WHERE Email = '{Email}'").fetchall()
        if len(values) == 0:
            return "User not found"
        else:
            return values
    def get_session(Email):
        '''Return code
        [0] = UID
        [1] = PID
        [2] = Email
        [3] = Session Code      
        '''
        session_obj = DB.cursor.execute(f"SELECT SessionObject FROM Account WHERE Email = '{Email}'").fetchall()[0][0].split('-')
        return session_obj

def check_session():
    UID, PID, Session_code, email = request.cookies.get('UID'), request.cookies.get('PID'), request.cookies.get('Session_code'), request.cookies.get('email')
    if UID == None and PID == None and email == None and Session_code == None:
        return "not_logged"
    elif not email == None:
        session_check = DB.get_session(email)
        if UID == session_check[0] and PID == session_check[1] and email == session_check[2] and Session_code == session_check[3]:
            return "logged"
        else:
            request.cookies.pop('UID', None)
            request.cookies.pop('PID', None)
            request.cookies.pop('email', None)
            request.cookies.pop('Session_code', None)
            return "session_cleared"
    else:
        return "not_logged"


app = Flask(__name__)
app.secret_key = '3ca768693330469b8b43d4033e46c60c29c2a5d21b0994403d5da8485cc681c6'


@app.route('/')
def index():
    result = check_session()
    if result == "not_logged":
        return render_template('index.html')
    elif result == "logged":
        return render_template('home.html', user_info = DB.read(request.cookies.get('email')))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        UID, PID, Session_code, email = request.cookies.get('UID'), request.cookies.get('PID'), request.cookies.get('Session_code'), request.cookies.get('email')
        if UID == None and PID == None and email == None and Session_code == None:
            return render_template('login.html')
        elif not email == None:
            session_check = DB.get_session(email)
            if UID == session_check[0] and PID == session_check[1] and email == session_check[2] and Session_code == session_check[3]:
                return redirect(url_for('index'))
            else:
                request.cookies.pop('UID', None)
                request.cookies.pop('PID', None)
                request.cookies.pop('email', None)
                request.cookies.pop('Session_code', None)
                return render_template('login.html')
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        paswd = request.form.get('password')
        check_login = DB.read(email)
        if check_login == "User not found":
            return render_template('login.html', status="Account not registered.")
        else:
            if md5(paswd.encode()).hexdigest() == DB.read(email)[0][2]:
                cookies_set = DB.get_session(email)
                resp = make_response(redirect(url_for('index'))) #return user details
                resp.set_cookie('UID', cookies_set[0])
                resp.set_cookie('PID', cookies_set[1])
                resp.set_cookie('email', cookies_set[2])
                resp.set_cookie('Session_code', cookies_set[3])
                return resp
            else:
                return render_template('login.html', status="Wrong email and password.")
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == 'POST':
        resp = make_response(redirect(url_for('index')))
        resp.delete_cookie('UID')
        resp.delete_cookie('PID')
        resp.delete_cookie('email')
        resp.delete_cookie('Session_code')
        return resp

@app.route('/sing-up', methods=['GET', 'POST'])
def singup():
    if request.method == "GET":
        result = check_session()
        if result == "not_logged":
            return render_template('singup.html'), 200
        else:
            return redirect(url_for('index'))
    elif request.method == "POST":
        fullName = request.form.get('fullname')
        Email = request.form.get('email')
        Password = request.form.get('password')
        confirm = DB.create(fullName, Email, Password)
        if confirm == 201:
            return render_template('login.html', status = "Account created sucessfull.")
        elif confirm == 302:
            return render_template('singup.html', status = "Account already registered.")

if __name__ == '__main__':
    app.run(debug=True)