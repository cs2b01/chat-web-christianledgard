from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json
import datetime

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

@app.route('/authenticate', methods = ['POST'])
def authenticate():
    #1. Get data form request.
    username = request.form['username']
    password = request.form['password']

    """
    #2. Get users from database
    db_session = db.getSession(engine)
    users = db_session.query(entities.User)

    #3. Search the user in collection (not efficient) :(
    for user in users:
        if user.username == username and user.password == password:
            return render_template("success.html")
    return render_template("fail.html")
    """

    #2. Look in the database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User
                ).filter(entities.User.username == username
                ).filter(entities.User.password == password
                ).one()
        return render_template("success.html")
    except Exception:
        return  render_template("fail.html")




@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users', methods = ['POST'])
def post_users():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/users', methods = ['PUT'])
def update_users():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "User Deleted"\


@app.route('/chat', methods = ['GET'])
def get_chat():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []

    for message in dbResponse:
        data.append(message)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/chat', methods = ['POST'])
def post_chat():
    c =  json.loads(request.form['values'])
    message = entities.Message(
        content=c['content'],
        sent_on = datetime.datetime.now(),
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id']
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    return 'Sent Message'

@app.route('/chat', methods = ['PUT'])
def update_chat():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(message, key, c[key])
    session.add(message)
    session.commit()
    return 'Updated User'

@app.route('/chat', methods = ['DELETE'])
def delete_chat():
    id = request.form['key']
    session = db.getSession(engine)
    chats = session.query(entities.Message).filter(entities.Message.id == id)
    for chat in chats:
        session.delete(chat)
    session.commit()
    return "Chat Deleted"


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/create_test_users', methods = ['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"\

@app.route('/create_test_message', methods = ['GET'])
def create_test_messages():
    db_session = db.getSession(engine)
    message = entities.Message(content="Hello World", sent_on = datetime.datetime.now(), user_from_id=1, user_to_id=3)
    db_session.add(message)
    db_session.commit()
    return "Test message created!"



if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'), debug=True)
