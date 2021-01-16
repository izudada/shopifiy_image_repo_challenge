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

app.config['IMAGE_UPLOADS'] = '/home/tony-medici/Projects/shopify_backend_challenge/static/images/uploads'
app.config['ALLOWED_IMAGE_EXTENSION'] = ['PNG', 'JPG', 'JPEG', 'GIF', 'SVG']
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


# init MYSQL
mysql = MySQL(app)


# Function to check the validity of image being uoloaded
def allowed_imaged(filename):
    ext = filename.rsplit(".", 1)[1]

    if not "." in filename:
        return False
    elif ext.upper() in app.config['ALLOWED_IMAGE_EXTENSION']:
        return True
    else:
        return False


#   Index/landing page route
@app.route('/')
def index():
    user_id = 0
    if 'logged_in' in session: 
        user_id = session['id']

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM images ")
    images = cur.fetchall()

    cur.close()
    
    return render_template('index.html', user_id=user_id, images=images)


#`Signup route`
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Get Signup Template Form Fields with request.form
    if request.method == 'POST':
        form = request.form
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
                return redirect(url_for('signup', form = form))
        else:
            cur.execute("INSERT users (full_name, username, email, password, create_date, create_time) VALUES(%s, %s, %s, %s, Now(), Now())", (fullname , username, email, password))

        # Commit To Database
        mysql.connection.commit()

        # CLose Connection
        cur.close()
            
        flash('You are successfully registered', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Check If User is Logged In and would be added to all routes where user authentication is needed
def is_logged_in(f):
        @wraps(f)
        def wrap(*args, **kwargs):                   
                if 'logged_in' in session:
                        return f(*args, **kwargs)
                else:
                        flash('Unauthorized, Please login', 'danger')
                        return redirect(url_for('index'))
        return wrap


#   Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        #   Create Mysql cursor
        cur = mysql.connection.cursor()
        #   Get user detail with mail
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        #   If user record exists in Database
        if result > 0:
            data = cur.fetchone()
            retrived_password = data['password']

            Cart = {}

            #   Compare both passwords for authentication
            if sha256_crypt.verify(password, retrived_password):
                # Passed
                session['logged_in'] = True
                session["Shoppingcart"] = Cart
                session['id'] = data['id']

                # Commit To DB
                mysql.connection.commit()

                flash('You are now logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid password'
                return render_template("login.html", error = error)
        else:
            error = 'Username not Found'
            return render_template("login.html", error = error)

    return render_template('login.html')


#   Logout  Route
@app.route('/logout')
def logout():
        session.clear()
        flash('You have succesfully logged out', 'success')
        return redirect(url_for('index'))


@app.route('/user/image_upload')
@is_logged_in
def upload():
    user_id = session['id']
    return render_template('add_new_image.html', user_id=user_id)


#   Image upload route   
@app.route('/user/<int:user_id>/upload_image', methods=['POST'])
@is_logged_in
def imageUpload(user_id):
    if request.method == 'POST':    #   When request to this route is a POST request
        
        #   Getting form variables
        user_id = session['id']
        title = request.form['title']
        category = request.form['category'].lower()
        description = request.form['description']

        #   Check if image(s) in form
        if request.files:
            #   Getting Image variables
            images = request.files.getlist('images')

            #   Open database connection
            cur = mysql.connection.cursor()

            #   Loop image list to get each filename, send to database and save to folder
            for image in images:

                #   Get image filenames from images list  and ensure it is secure with secure_filename
                filename = secure_filename(image.filename)

                #   Check if filename is empty
                if filename == "":
                    flash("Filename is not supported ")
                    return redirect(url_for('index'))
                elif not allowed_imaged(filename):  #   Calling allowed_image function
                    flash("Image extension is not allowed")
                    return redirect(url_for('index'))

                #   Send each filename and form data to database as separate rows thus why in a loop
                cur.execute("INSERT images (user_id, filename, 	title, 	category, description, create_time, create_date) VALUES(%s, %s, %s, %s, %s, Now(), Now())", (user_id , filename, title, category, description))

                #   Save all images to folder
                image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))

            # Commit To Database
            mysql.connection.commit()

            # CLose Connection
            cur.close()
        
        else:
            flash("Image upload unssuccessful", "danger")
            return redirect(url_for('index'))
        
        #   Success feedback to user after successful upload
        flash("Image upload successful", "success")
        return redirect(url_for('index'))
    
    return render_template('index.html')


#   Delete image route
@app.route('/user/<int:user_id>/<int:image_id>/delete_image', methods=['POST'])
@is_logged_in
def deleteImage(user_id, image_id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        #   Select flename from Database
        get = cur.execute("SELECT filename, user_id FROM images WHERE id = %s", [image_id])
        filename = cur.fetchone()
        image = filename['filename']

        #   Check to see if user ia authorised to delete image. Only the user who uploaded can delete. User_id is a foreign key in images table
        if filename['user_id'] == session['id']:

            #   Delete image data from Database
            cur.execute("DELETE FROM images WHERE id = %s", [image_id])

            #   Delete image from folder
            os.remove(f"static/images/uploads/{image}")

            # Commit To Database
            mysql.connection.commit()

            cur.close()

            flash("Image successfully deleted", "success")
            return redirect(url_for('index'))
        else:
            flash("You are not authorised to delete this image", "danger")
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))


#   Route for user profile
@app.route('/user/<int:user_id>/profile')
@is_logged_in
def userProfile(user_id):
    pass


#   Route for searching image
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        title = "%" + request.form['search'] + "%"  #   COllect search string from search box on navbar

        cur = mysql.connection.cursor()

        #   Query Database
        result = cur.execute("SELECT * FROM images WHERE title LIKE %s ORDER BY id DESC", [title]) 
        search = cur.fetchall()

        cur.close()

        if result > 0:
            return render_template('search.html', search=search)
        else:
            flash("Opps! There is no image with such title", "danger")
            return render_template('search.html')
    
    return render_template('search.html')



#   Route for viewing image by category = photo
@app.route('/view_category/photos')
def photo():
    category = "photo"
    cur = mysql.connection.cursor()

    #   Query Database
    result = cur.execute("SELECT filename FROM images WHERE category = %s ORDER BY id DESC", [category]) 
    search = cur.fetchall()

    cur.close()

    if result > 0:
        return render_template('search.html', search=search)
    else:
        flash("No image under this category yet", "danger")
        return render_template('view_category.html')


if __name__ == '__main__':
        app.secret_key = 'secret@'
        app.run(debug=True)