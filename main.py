from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
from datetime import datetime
from werkzeug import secure_filename
from flask_mail import Mail
import json
import os
import base64
import math
with open('config.json', 'r') as c:
    params = json.load(c)

app = Flask(__name__)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = params['params']['data-base']
app.secret_key = params['params']['secret-key']
app.config['UPLOAD_FOLDER'] = params['params']['file-location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['params']['email-username'],
    MAIL_PASSWORD=params['params']['email-password']
)

mail = Mail(app)


class blogpost(db.Model):

    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(15), nullable=False)
    like = db.Column(db.Integer, nullable=True)

    date = db.Column(db.String(12), nullable=True)


class popular(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(150), nullable=False)

    slug = db.Column(db.String(15), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class review1(db.Model):

    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(15), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class contact(db.Model):

    srno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(400), nullable=False)
    subject = db.Column(db.String(205), nullable=False)
    date = db.Column(db.String(12), nullable=True)


# function section
@app.route('/')
def home():
    posts = blogpost.query.filter_by().all()
    # popularposts = popular.query.filter_by().all()
    
    last = math.ceil(len(posts)/3)
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[(page-1)*3:(page-1)*3+3]
    if page == 1:
        prev1 = "#"
        next1 = "/?page="+str(page+1)

    elif page == last:
        next1 = "#"
        prev1 = "/?page="+str(page-1)
    else:
        next1 = "/?page="+str(page+1)
        prev1 = "/?page="+str(page-1)

    return render_template('index.html', posts=posts, next=next1, prev=prev1)


@app.route('/contact', methods=['GET', 'POST'])
def contact1():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        entry = contact(username=username, email=email,
                        subject=subject, message=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + username,
                          sender=email,
                          recipients=["fighter7415963@gmail.com"],
                          body="subject:" + subject + "\n" + "message:" + message
                          )

    return render_template('contact.html')


@app.route('/about')
def about():
    reviews = review1.query.order_by(func.rand()).all()
    return render_template('about.html', reviews=reviews)


@app.route('/post/<string:srno>', methods=['GET'])
def post_viewer(srno):
    posts = blogpost.query.filter_by(srno=srno).first()

    return render_template('post.html', post=posts)


@app.route('/review/<string:srno>', methods=['GET'])
def review_viewer(srno):

    reviews = review1.query.filter_by(srno=srno).first()
    return render_template('review_viewer.html', reviews=reviews)


@app.route('/submit', methods=['POST', 'GET'])
def feedback_form():

    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    entry = review1(name=name, email=email, subject=subject,
                    message=message, date=datetime.now())
    db.session.add(entry)
    db.session.commit()
    return redirect('about')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    content = blogpost.query.all()
    if 'user' in session and session['user'] == "naman":
        return render_template('dashboard.html', content=content)

    if request.method == "POST":
        user_name = request.form.get('username')
        user_password = request.form.get('pass')

        if user_name == params['params']['login-username'] and user_password == params['params']['login-password']:

            session['user'] = "naman"
            return render_template('dashboard.html', content=content)
        else:
            return render_template('login.html')

    else:
        return render_template('login.html')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():

    session['user'] = False
    return redirect('dashboard')


@app.route('/upload', methods=['GET', 'POST'])
def new_post_viewer():
    # last=blogpost.query.filter_by().all()
    # last_post=last[-1]
    return render_template('newpost.html')


@app.route('/upload_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        srno = request.form.get('srno')
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        new_file = request.files['file']

        new_file.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(new_file.filename)))
        os.rename(
            f'E:\\website\\static\\images\\{new_file.filename}', f'E:\\website\\static\\images\\{srno}.jpg')
        entry = blogpost(srno=srno, title=title, content=content,
                         slug=slug,like=0, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('dashboard'))


@app.route('/edit_viewer/<string:srno>', methods=['GET', 'POST'])
def edit_viewer(srno):
    post = blogpost.query.filter_by(srno=srno).first()
    return render_template('edit.html', srno=post.srno, title=post.title, slug=post.slug, content=post.content)


@app.route('/edit/<string:srno1>', methods=['GET', 'POST'])
def edit(srno1):
    if request.method == 'POST':
        post = blogpost.query.filter_by(srno=srno1).first()
        srno = request.form.get('srno')
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        post.srno = srno
        post.title = title
        post.slug = slug
        post.content = content

        new_file = request.files['file']
        if new_file.filename != "":
            os.remove(f'E:\website\static\images\\{srno1}.jpg')
            new_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(new_file.filename)))
            os.rename(
                f'E:\website\static\images\\{new_file.filename}', f'E:\website\static\images\\{srno}.jpg')
        elif new_file.filename == "":

            pass

        db.session.commit()
        return redirect(url_for('dashboard'))

    else:
        return redirect(url_for('dashboard'))


@app.route('/delete/<string:srno>', methods=['GET', 'POST'])
def delete_post(srno):
    if request.method == 'POST':
        data = blogpost.query.filter_by(srno=srno).first()
        db.session.delete(data)
        db.session.commit()
        if os.path.isfile(f'E:\website\static\images\{srno}.jpg'):
            os.remove(f'E:\website\static\images\{srno}.jpg')
        return redirect(url_for('dashboard'))

    else:
        return redirect(url_for('dashboard'))


@app.route('/likebutton/<string:srno>', methods=['GET', 'POST'])
def like(srno):

    posts = blogpost.query.filter_by(srno=srno).first()
    likes = posts.like
    new_like = likes+1
    posts.like = new_like

    db.session.commit()

    return redirect(url_for('post_viewer', srno=srno))


# end of function section
app.run(debug=True)

#  , host='0.0.0.0'
