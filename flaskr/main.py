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

# page link structure


# @app.route("/")
# def _page():
#     return render_template('.html')

# database creation
def database_creation():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username VARCHAR NOT NULL,
        FirstName VARCHAR,
        LastName VARCHAR,
        Email VARCHAR NOT NULL,
        Password VARCHAR(20) NOT NULL,
        PaymentDetails INTEGER,
        AddressId INTEGER,
        admin BOOLEAN DEFAULT 0,
        FOREIGN KEY (PaymentDetails) REFERENCES PaymentDetails(PaymentId),
        FOREIGN KEY (AddressId) REFERENCES AllowedAddresses(AddressId)
    )
    """)

    # Create PaymentDetails table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PaymentDetails (
        PaymentId INTEGER PRIMARY KEY,
        CardNumber INTEGER NOT NULL,
        ExpiryDate INTEGER NOT NULL
    )
    """)

    # Create ConsultationBookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ConsultationBookings (
        ConsultationBookId INTEGER PRIMARY KEY,
        UserId INTEGER NOT NULL,
        Time INTEGER NOT NULL,
        Date INTEGER NOT NULL,
        StaffId INTEGER NOT NULL,
        IsBooked BOOLEAN NOT NULL,
        FOREIGN KEY (UserId) REFERENCES users(id),
        FOREIGN KEY (StaffId) REFERENCES Staff(StaffId)
    )
    """)

    # Create InstallationBookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS InstallationBookings (
        InstaBookId INTEGER PRIMARY KEY,
        UserId INTEGER NOT NULL,
        Time INTEGER NOT NULL,
        Date INTEGER NOT NULL,
        StaffId INTEGER NOT NULL,
        IsBooked BOOLEAN NOT NULL,
        FOREIGN KEY (UserId) REFERENCES users(id),
        FOREIGN KEY (StaffId) REFERENCES Staff(StaffId)
    )
    """)


    # Create InfoCards table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS InfoCards (
        InfoID INTEGER PRIMARY KEY,
        Title VARCHAR,
        SubHeading VARCHAR,
        Body VARCHAR
    )
    """)

    # Create Staff table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Staff (
        StaffId INTEGER PRIMARY KEY,
        FirstName VARCHAR NOT NULL,
        LastName VARCHAR NOT NULL,
        role VARCHAR NOT NULL,
        IsAdmin BOOLEAN NOT NULL,
        IsBooked BOOLEAN NOT NULL
    )
    """)

    # Create AllowedAddresses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AllowedAddresses (
        AddressId INTEGER PRIMARY KEY,
        AdressNum INTEGER,
        AdressName VARCHAR
    )
    """)

    connection.commit()
    connection.close()


# non funtinality page routes (pages that do not require backend functionality)
@app.route("/")
def index_page():
    return render_template('index.html')
@app.route("/about")
def about_page():
    return render_template('about.html')


@app.route("/infomation-page")
def information_page():
    return render_template('information-page.html')

@app.route("/projects-page")
def projects_page():
    return render_template('projects-page.html')

# funtinality page routes(pages that have backend functionality)

@app.route("/booking-choice")
def booking_choice_page():
    return render_template('booking-choice.html')

@app.route("/booking-installation")
def booking_installation_page():
    return render_template('booking-installation.html')


@app.route("/booking-consultation")
def booking_page():
    return render_template('booking-consultation.html')



@app.route("/register" , methods=["GET", "POST"])
def register_page():
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



@app.route("/calculations-choice")
def calculations_choice_page():
    return render_template('calulations-choice.html')

@app.route("/calculations-carbon")
def calculations_carbon_page():
    return render_template('calculations-carbon.html')


@app.route("/calculations-energy")
def calculations_energy_page():
    return render_template('calculations-energy.html')


@app.route("/login" , methods=["GET", "POST"])
def login_page():
    
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
    