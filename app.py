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




if __name__ == '__main__':
        app.secret_key = 'secret@'
        app.run(debug=True)