from flask import render_template, request, json, Response, Blueprint, redirect, url_for, session
from .extensions import mongo
from .tools import *
from datetime import datetime
import bcrypt

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/index")
@main.route("/home")
def index():
    return render_template("index.html")


def set_keys(collection, key):
    collection_list = collection.find({})
    
    for element in collection_list:
        if bcrypt.hashpw(key.encode('utf-8'), element['secret']):
            return element['public']
    return 0

@main.route('/handle_login', methods=['POST'])
def handle_login():
    users = mongo.db.users
    mh = mongo.db.mh
    personal = mongo.db.personal
    login_user = users.find_one({'username': request.form['username']})

    if login_user:
        decripted = bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password'])
        if decripted == login_user['password']:
            
            session['personal'] = set_keys(personal, request.form['password'])
            session['mh'] = set_keys(mh, request.form['password'])
            session['username'] = request.form['username']

            return redirect(url_for('main.data'))
    return redirect(url_for('main.register'))
    

@main.route("/data")
def data():
    gad_data = mongo.db.gad_data
    data = gad_data.find({'patient': session['mh']})
    labels = []
    scores = []
    for elem in list(data):
        print (str(elem['datetime'].strftime('%d/%m/%Y')))
        
        labels = labels + [elem['datetime'].strftime('%d/%m/%Y')]
        scores = scores + [elem['score']]
    
    print (labels)
    return render_template("data.html", labels = labels, scores = scores)

@main.route('/handle_privacy', methods=['POST'])
def handle_privacy():
    return redirect(url_for('main.data'))

@main.route("/gad")
def gad():
    return render_template("gad.html")

@main.route("/gad_results",  methods=['POST'])
def gad_results():
    score_respondes = mongo.db.gad_score
    gad_data = mongo.db.gad_data
    personal = mongo.db.personal
    score = (int(request.form['one']) + int(request.form['two']) + int(request.form['three']) + int(request.form['four']) + 
        int(request.form['five']) + int(request.form['six']) + int(request.form['seven']))
    now = datetime.now()
    if score < 5:
        severity = 'minimal'
    elif score < 10:
        severity = 'mild'
    elif score < 15:
        severity = 'moderate'
    else:
        severity = 'severe'
    
    print ("SESSION: " + session['mh'])

    response = score_respondes.find_one({'severity': severity})
    gad_data.insert({
        'patient': session['mh'],
        'datetime': now,
        'score': score
    })

    return render_template("results.html", score = score, response = response)





# AUTH
@main.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        personal = mongo.db.personal
        mh = mongo.db.mh
        existing_user = users.find_one({'username' : request.form['username']})
        mh_public = randomstr(8)
        personal_public = randomstr(8)

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            personal_data = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            app_data = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({
                'username':request.form['username'], 'password': hashpass
            })
            mh.insert({
                'secret':app_data,
                'public': mh_public,
                'diagnostics': 'anxiety'
            })
            personal.insert({
                'secret': personal_data,
                'public': personal_public,
                'name': 'anon',
                'therapist': 'Psich Claudia'
            })
            session['personal'] = personal_public
            session['mh'] = mh_public
            session['username'] =  request.form['username']
            return render_template("privacy.html")

        return 'That username already exists!'

    return render_template('register.html')
