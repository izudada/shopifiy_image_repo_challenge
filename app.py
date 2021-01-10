import sys
import os
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory, make_response
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename

# sys.path.insert(0, os.path.dirname(__file__))
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'image_repo'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# app.config['IMAGE_UPLOADS'] = '/home/tony-medici/Projects/POS/static/images/logo'
# app.config['ALLOWED_IMAGE_EXTENSION'] = ['PNG', 'JPG', 'JPEG', 'GIF']
# app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


# init MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Get Signup Template Form Fields
    if request.method == 'POST':
        fullname =request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        encrpt = request.form['password']
        password = sha256_crypt.encrypt(str(encrpt)) # Encrypt user password

        # Create Cursor for Quesries o the database
        cur = mysql.connection.cursor()

        # Execute Query to check if user already exists else insert into databse
        result = cur.execute("SELECT email FROM users WHERE email=%s", [email])
        if result > 0:
                flash("Sorry, Account ALready Exits", "danger")
                return redirect(url_for('login'))
        else:
            cur.execute("INSERT users (full_name, username, email, password, create_date, create_time) VALUES(%s, %s, %s, %s, Now(), Now())", (fullname , username, email, password))

        # Commit To Database
        mysql.connection.commit()

        # CLose Connection
        cur.close()
            
        flash('You are successfully registered', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    pass


@app.route('/user/<int:user_id>/<int:image_id>/upload_image')
def imageUpload(user_id, image_id):
    pass


@app.route('/user/<int:user_id>/<int:image_id>/edit_image')
def editImage(user_id, image_id):
    pass


@app.route('/user/<int:user_id>/<int:image_id>/delete_image')
def deleteImage(user_id, image_id):
    pass

@app.route('/user/<int:user_id>/profile')
def userProfile(user_id):
    pass


@app.route('/search')
def search():
    pass



if __name__ == '__main__':
        app.secret_key = 'secret@'
        app.run(debug=True)