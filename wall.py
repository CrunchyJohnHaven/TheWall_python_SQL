from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'wall')
import re
import time
import md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app.secret_key = "NinjaStealth"
@app.route('/')
def index():
    if 'login' not in session:
        session['login'] = False
    if 'user' not in session:
        session['user'] = ''
    if session['login']:
        flash("Welcome" + ' ' + session['welcome'], "category1")
        query = "SELECT messages.message, messages.id, users.first_name, users.last_name, DATE_FORMAT(messages.created_at, '%e, %b, %Y') FROM messages JOIN users ON messages.user_id = users.id ORDER BY messages.updated_at desc"
        query2 = "SELECT users.first_name, DATE_FORMAT(comments.created_at, '%e, %b, %Y'), users.last_name, messages.id, comments.comment FROM comments JOIN messages ON messages.id = comments.message_id JOIN users ON users.id = comments.user_id"
        messages = mysql.query_db(query)
        comments = mysql.query_db(query2) 
        return render_template('wall.html', messages=messages, comments=comments, login=session['login'], user=session['user'])
    else:
        return render_template('wall_login.html', login=session['login'], user=session['user'])


@app.route('/login', methods=['POST'])
def login():
    if not session['login']:
        print "login not true at login:", session['login']
        password = md5.new(request.form['password']).hexdigest()
        users = "SELECT * FROM users"
        for i in mysql.query_db(users):
            if i['email'] == request.form['email'] and i['password'] == password:
                session['welcome'] = i['first_name']
                print "login found true"
                session['login'] = True
                print "session['login'] is now:", session['login']
                flash('logged in', 'valid')
                return redirect('/')
    if session['login']:
        print "login true at login"
        return redirect('/')
    if not session['login']:
        print "redirect false at login"
        flash("Login email or password invalid, try again or register below:", "invalid")
        return redirect('/')

@app.route('/logout', methods=['POST'])
def logout():
    session['login'] = False
    return redirect('/')

@app.route('/wall_register', methods=['POST'])
def wall_register():
    session['login'] = True
    print "register1"
    message = ""
    print "message:", message
    if  len(request.form['first_name']) < 2:
        print "register2"
        message = message + "Invalid first name" 
        session['login'] = False
    if len(request.form['last_name']) < 2:
        print "register3"
        message = message + " " + "Invalid first name"
        session['login'] = False
    if not EMAIL_REGEX.match(request.form['email']):
        print "register4"
        message = message + " " + "Invalid Email"
        session['login'] = False
    if not session['login']:
        flash(message, 'invalid')
        return redirect('/')
    else:
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest()
        }
        print "register data:", data
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        mysql.query_db(query, data)
        password = md5.new(request.form['password']).hexdigest()
        data = {
            'specific_password': password
        }
        print "user reg data:", data
        print "register8"
        select_query = "SELECT id FROM users WHERE password = :specific_password LIMIT 1"
        print "select_query at reg:", select_query
        user = mysql.query_db(select_query, data)
        print "user:", user
        session['user'] = user
        print "session['user] at reg (id)", session['user']
        flash('login successful', 'valid')
        return redirect('/')

@app.route('/wall', methods=['POST'])
def wall():
    message = request.form['message']
    user_id = session['user'][0]['id']
    data = {'message': message, 'user_id': user_id}
    # assign message and id to data
    query = 'INSERT INTO messages (message, user_id,created_at, updated_at) VALUES (:message, :user_id,NOW(), NOW())'
    mysql.query_db(query, data)
    return redirect('/')
@app.route('/comment', methods=['POST'])
def comments():
    comment = request.form['comment']
    print "comment at comment:", comment
    user_id = session['user'][0]['id']
    message_id = request.form['action']
    print "user_id at comment:", user_id
    print "message_id at comment", message_id
    data = {'comment': comment, 'user_id' : user_id, 'message_id' : message_id}
    # assign message and id to data
    query = 'INSERT INTO comments (comment, message_id, user_id, created_at, updated_at) VALUES (:comment, :message_id, :user_id, NOW(), NOW())'
    mysql.query_db(query, data)
    return redirect('/')
app.run(debug=True)

# John 
# Bradley
# JohnHavenBradley
# havenbradley@yahoo.com
# delwin170

    # query = "SELECT users.first_name, messages.message, messages.id FROM users JOIN messages ON users.id = messages.users_id ORDER BY messages.id DESC"
    # messages = mysql.query_db(query)
    # query2 = "SELECT users.first_name, messages.id, comments.comment FROM comments JOIN messages ON messages.id = comments.messages_id JOIN users ON users.id = comments.users_id"

    # comments = mysql.query_db(query2)