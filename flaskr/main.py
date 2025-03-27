from datetime import datetime, timedelta
import os
import sqlite3
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import re
app = Flask(__name__, template_folder='Templates')

@app.route("/")
def hello_world():
    return render_template('index.html')
@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/services")
def services():
    return render_template('services.html')




@app.route("/booking-choice")
def booking_choice():
    return render_template('booking-choice.html')

@app.route("/booking-installation")
def booking_installation():
    return render_template('booking-installation.html')


@app.route("/booking-consultation")
def booking():
    return render_template('booking-consultation.html')

@app.route("/register")
def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            password_confirm = request.form['password-confirm']
            # have a input validation
            if not username or not email or not password or not password_confirm:
                return "All fields must be filled", 400
            
            
            # input length validation
            if len(username) > 200 or len(password) > 200 or len(email) > 200:
                return "Input exceeds character limit", 400
            if len(username) < 4 or len(password) < 10:
                return "Username and password must be at least 4 characters", 400
            
            
            
            # password match validation
            if password != password_confirm:
                return "Passwords do not match", 400
            
            # email validation
            if (
              not re.match("^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", email)
            ):
                return "Invalid characters in email ", 400
            
            # password validation
            if not re.match(
                r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_\-+=<>?.,]).{8,}$",
                password,
            ):
                return (
                "Password must contain at least 8 characters, including uppercase, lowercase, digits, and special characters.",
                400,
                )
            # generate password hash and input into database
            password_hash = generate_password_hash(password)
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()
            cursor.execute(
                "select * from users where username = ? or email = ?", (username, email)
            )
            # checks if user already exists
            exsiting_user = cursor.fetchone()
            if exsiting_user:
                return "Username or email already exists", 400
            
            
            try:
                cursor.execute(
                    "insert into users (username, email, password) values (?, ?, ?)",
                    (username, email, password_hash),
                )
                connection.commit()
            except sqlite3.IntegrityError:
                return "Username or email already is registered", 400
            finally:
                connection.close()
    
        return render_template('register.html')




@app.route("/login")
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if len(username) > 200 or len(password) > 200 or len(email) > 200:
            return "Input exceeds character limit", 400
        
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute(
            "SELECT username, password, email, admin FROM users WHERE username = ?",
            (username,),
        )
        user = cursor.fetchone()
        connection.close()
        if check_password_hash(user[1], password):
            session["username"] = username
            session["admin"] = False
            return redirect(url_for("profile"))
        else:
            return "Invalid username or password", 400

    return render_template("login.html")













if __name__ == '__main__':
    app.run(debug=True)
    