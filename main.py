#paras
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime


local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

# sno,name,phone_num,msg,date,email


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(13), unique=False, nullable=False)
    msg = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
    email = db.Column(db.String(80), unique=True, nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(25), unique=False, nullable=False)
    content = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
@app.route("/")
def home():
    return render_template('index.html', params=params)


@app.route("/about")
def about():
    return render_template('about.html', params=params, post=post)


@app.route("/post/<string:post_slug>", method=['GET'])
def post_route( post_slug ):
    post = Posts.query.filter_by(slug=post_slug).first()
    
    return render_template('post.html', params=params) 

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        #Add entry to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone,
                         msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone
                          )

    return render_template('contact.html', params=params)


app.run(debug=True)
