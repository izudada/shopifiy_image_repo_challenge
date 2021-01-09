import sys
import os
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory, make_response
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename

# sys.path.insert(0, os.path.dirname(__file__))
app = Flask(__name__)

# init MYSQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    pass


@app.route('user/<int:user_id>/<int:image_id>/upload_image')
def imageUpload(user_id, image_id):
    pass


@app.route('user/<int:user_id>/<int:image_id>/edit_image')
def editImage(user_id, image_id):
    pass


@app.route('user/<int:user_id>/<int:image_id>/delete_image')
def editImage(user_id, image_id):
    pass

@app.route('/user/<int:user_id>/profile')
def userProfile(user_id):
    pass


@app.route('/search'):
def search():
    pass



if __name__ == '__main__':
        app.secret_key = 'secret@'
        app.run(debug=True)