from datetime import datetime, timedelta
import os
import sqlite3
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
import re
import google.generativeai as genai
app = Flask(__name__, template_folder='Templates')
app.secret_key = "hello"
# os.urandom(24)   Set a unique and secret key for session management

# page link structure


# @app.route("/")
# def _page():
#     return render_template('.html')

# database creation

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
    Password VARCHAR NOT NULL,
    PaymentDetails INTEGER,
    AddressId INTEGER,
    admin BOOLEAN DEFAULT 0,
    FOREIGN KEY (PaymentDetails) REFERENCES PaymentDetails(PaymentId),
    FOREIGN KEY (AddressId) REFERENCES AllowedAddresses(AddressId)
)
""")

# Create Bookings table

cursor.execute("""
CREATE TABLE IF NOT EXISTS Bookings (
    booking_id INTEGER PRIMARY KEY,
    is_active BOOLEAN DEFAULT 1,
    is_confirmed BOOLEAN DEFAULT 0,
    is_cancelled BOOLEAN DEFAULT 0,
    is_completed BOOLEAN DEFAULT 0,
    is_paid BOOLEAN DEFAULT 0,
    is_installation BOOLEAN DEFAULT 0,
    installation_choice VARCHAR,
    installation_number INTEGER,
    installation_details TEXT,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    postcode VARCHAR NOT NULL,
    message TEXT,
    date DATE NOT NULL,
    time TIME NOT NULL
)
""")





# time out system - this will log the user out after 30 minutes of inactivity
@app.before_request
def manage_session():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    if "username" in session:
        # Check if session has expired
        last_activity = session.get("last_activity")
        if last_activity:
            current_time = datetime.now()
            time_difference = current_time - last_activity.replace(tzinfo=None)
            if time_difference.total_seconds() > 1800:  # the timer for when logut happen, it checks the time difference between the currant time and the last action the user has done
                session.clear()
                return redirect(url_for("login"))

    # Update the last activity timestamp for the session
    session["last_activity"] = datetime.now()

# defines what happens when the user is logged in and what is authernticated and   admin
@app.context_processor
def inject_user():
    return {
        "authenticated": "username" in session,
        "admin": session.get("admin", False),
    }











# non funtinality page routes (pages that do not require backend functionality)
@app.route("/")
def index_page():
    username = session.get("username")
    return render_template('index.html')



@app.route("/about")
def about_page():
    return render_template('about.html')


@app.route("/infomation-page-pricing")
def information_page():
    return render_template('information-pricing.html')

@app.route("/information-page-article")
def information_page_article():
    return render_template('information-article.html')


@app.route("/projects-page")
def projects_page():
    return render_template('projects-page.html')

@app.route("/contact", methods=["GET", "POST"])
def contact_page():

    
    if request.method == "POST":
        is_error = request.form.get("is_error")
        email = request.form.get("email")
        what_error = request.form.get("error_choice")
        error_message = request.form.get("error-message")
        feedback_message = request.form.get("feedback-message")
        is_contacted = request.form.get("is-contacted")
        

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        try:
            # Insert the contact
            cursor.execute("""
                INSERT INTO contact ( is_error, error_message,  feedback_message, email, what_error, is_contacted
                ) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, ( is_error, error_message,  feedback_message, email, what_error, is_contacted))
            connection.commit()
            return redirect("/contact-confirm")
        except sqlite3.Error as e:
            return f"contact failed: {e}", 500
        finally:
            connection.close()

    return render_template("contact.html")

@app.route("/contact-confirm")
def contact_confirm_page():
    return render_template('contact-confirm.html')

@app.route("/faq")
def faq_page():
    return render_template('faq.html')

@app.route("/terms")
def terms_page():
    return render_template('terms.html')

@app.route("/privacy")
def privacy_page():
    return render_template('privacy-policy.html')
@app.route("/terms-and-conditions")
def terms_and_conditions_page():
    return render_template('terms-and-conditions.html')



@app.route("/unfinished")
def unfinished_page():
    return render_template('unfinished.html')





# funtinality page routes(pages that have backend functionality)


# booking
@app.route("/booking", methods=["GET", "POST"])
def booking_choice_page():
    if "username" not in session:
        return redirect(url_for("login_page"))
    
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        is_installation = request.form.get("is_installation", "")
        installation_choice = request.form.get("installation_choice", "")
        installation_number = request.form.get("installation_number", 0)
        installation_details = request.form.get("installation_details", "")
        email = request.form.get("email")
        phone = request.form.get("phone")
        postcode = request.form.get("postcode")
        message = request.form.get("message")
        date = request.form.get("date")
        time = request.form.get("time")

        if not first_name or not last_name or not email or not phone or not postcode or not date or not time or not is_installation:
            return "Please fill out all fields", 400

        # Get the user_id of the logged-in user
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
        user = cursor.fetchone()
        if not user:
            return "User not found", 400
        user_id = user[0]

        try:
            # Insert the booking with the user_id
            cursor.execute(
                """
                INSERT INTO Bookings (
                    is_installation, installation_choice, installation_number, 
                    installation_details, first_name, last_name, email, phone, 
                    postcode, message, date, time, user_id
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    is_installation == "installation",  # Convert to boolean
                    installation_choice,
                    installation_number,
                    installation_details,
                    first_name,
                    last_name,
                    email,
                    phone,
                    postcode,
                    message,
                    date,
                    time,
                    user_id,
                ),
            )
            connection.commit()
            return redirect("/booking-confirm")
        except sqlite3.Error as e:
            return f"Booking failed: {e}", 500
        finally:
            connection.close()

    return render_template("booking.html")

@app.route("/booking-confirm")
def booking_confirm_page():
    return render_template('booking-confirm.html')







# calculations
@app.route("/calculations-choice")
def calculations_choice_page():
    return render_template('calculations-choice.html')


# carbon
@app.route("/calculations-carbon", methods=["GET", "POST"])
def calculations_carbon_page():
    if request.method == 'POST':
        try:
            # Collect inputs from the form
            home_size = float(request.form.get('home-size', 0))  # Home size in ft²
            heating_type = request.form.get('heating-type', 'Gas')  # Heating type
            
            num_appliances = int(request.form.get('appliances', 0))  # Number of appliances
            num_laptops = int(request.form.get('laptops', 0))  # Number of laptops
            num_desktops = int(request.form.get('desktops', 0))  # Number of desktops
            
            has_car = request.form.get('car', 'no') == 'yes'  # Do you have a car?
            car_travel_5_miles = int(request.form.get('travel-over-5', 0)) if has_car else 0
            car_travel_10_miles = int(request.form.get('travel-over-10', 0)) if has_car else 0
            
            uses_train = request.form.get('train', 'no') == 'yes'  # Do you travel by train?
            train_travel_count = int(request.form.get('train-frequency', 0)) if uses_train else 0
            train_long_journeys = request.form.get('train-duration', 'no') == 'yes'
            
            uses_bus = request.form.get('bus', 'no') == 'yes'  # Do you travel by bus?
            bus_travel_count = int(request.form.get('bus-frequency', 0)) if uses_bus else 0
            bus_long_journeys = request.form.get('bus-duration', 'no') == 'yes'
            
            # Corrected carbon emission factors (kg CO₂ per unit)
            heating_factors = {
                "Gas": 1.53,  # kg CO₂ per ft²
                "Oil": 2.2,
                "Wood": 0.8,
            }
            appliance_factor = 50  # kg per appliance
            laptop_factor = 30  # kg per laptop
            desktop_factor = 50  # kg per desktop

            car_5_miles_factor = 0.4  # kg per trip
            car_10_miles_factor = 0.8  # kg per trip
            train_short_factor = 0.1  # kg per trip
            train_long_factor = 0.3  # kg per trip
            bus_short_factor = 0.2  # kg per trip
            bus_long_factor = 0.5  # kg per trip

            # Calculate total carbon usage for a year
            total_carbon = 0
            # home
            home_carbon = home_size * heating_factors.get(heating_type, 1.0)
            appliance_carbon = num_appliances * appliance_factor
            # appliances
            laptop_carbon = num_laptops * laptop_factor
            desktop_carbon = num_desktops * desktop_factor
            # transport
            car_5_carbon = car_travel_5_miles * car_5_miles_factor 
            
            car_10_carbon = car_travel_10_miles * car_10_miles_factor 
            
            train_carbon = train_travel_count * (train_long_factor if train_long_journeys else train_short_factor) 
            
            bus_carbon = bus_travel_count * (bus_long_factor if bus_long_journeys else bus_short_factor) 

            # Convert total carbon usage to metric tons
            total_carbon =( home_carbon + appliance_carbon + laptop_carbon + desktop_carbon + car_5_carbon + car_10_carbon + train_carbon + bus_carbon) *12
            total_carbon = round(total_carbon / 1000, 2)  # Convert kg to tons and round to 2 decimal places
            total_carbon_use = total_carbon

            # Redirect to results page with calculated carbon usage
            return redirect(url_for('calculations_results_carbon_page', total_carbon_use=total_carbon_use))
        except (ValueError, KeyError):
            error_message = "Please fill in all the fields or ensure values are correct."
            return redirect(url_for('calculations_carbon_page', error=error_message))
    return render_template('calculations-carbon.html')

@app.route("/calculations-results-carbon")
def calculations_results_carbon_page():
    total_carbon_use = request.args.get('total_carbon_use', type=float)
    return render_template('calculations-results-carbon.html', total_carbon_use=total_carbon_use)

# energy
@app.route("/calculations-energy", methods=["GET", "POST"])
def calculations_energy_page():
    if request.method == 'POST':
        try:
            home_kwh = float(request.form['energy'])  # Avg hourly kWh use
            energy_rates = float(request.form['cost']) / 100  # Convert pence to pounds
            time_frame = float(request.form['time'])  # Months
            
            avg_days_month = 30  # Assumed average month length
            
            # Calculate total energy usage over the given months
            total_energy = home_kwh * 24 * avg_days_month * time_frame  
            
            # Calculate total cost (round to two digits )
            total_energy_cost = total_energy * energy_rates  

            if total_energy_cost < 0 or total_energy < 0:
                return "Invalid input", 400
            else:
                return redirect(url_for('calculations_results_energy_page', total_energy_cost=total_energy_cost, total_energy_use=total_energy))
        except (ValueError, KeyError):
            return "Invalid input data", 400
    return render_template('calculations-energy.html')

@app.route("/calculations-results-energy")
def calculations_results_energy_page():
    total_energy_use = request.args.get('total_energy_use', type=float)
    total_energy_cost = request.args.get('total_energy_cost', type=float)
    return render_template('calculations-results-energy.html', total_energy_cost=total_energy_cost, total_energy_use=total_energy_use)







# users data e.g login, logout and register
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate input lengths
        if len(username) > 200 or len(password) > 200 or len(email) > 200:
            return "Input exceeds character limit", 400

        # Check if the user exists in the database
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Fetch user by username and email only
        cursor.execute(
            "SELECT username, password, email, admin FROM users WHERE username = ? AND email = ?",
            (username, email),
        )
        user = cursor.fetchone()
        connection.close()

        print(f"Debug: User fetched from database: {user}")  # Debugging

        if user:
            # Use check_password_hash to verify the password
            if check_password_hash(user[1], password):  # user[1] is the hashed password
                session["username"] = username
                session["admin"] = user[3]  # user[3] is the admin status
                return redirect(url_for("profile"))

        return "Invalid username or password", 400

    return render_template("login.html")

@app.route("/register" , methods=["GET", "POST"])
def register_page():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            password_confirm = request.form['password-confirm']
            
            # Prevents usernames with variations of "admin" or "test"
            if re.search(r"(?i)(admin|test)", username):
                return "Username cannot contain 'admin' or 'test'", 400
            
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
  
@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login_page"))
    
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    
    # Get the user_id of the logged-in user
    cursor.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
    user = cursor.fetchone()
    if not user:
        return "User not found", 400
    user_id = user[0]

    # Fetch bookings for the logged-in user
    cursor.execute("""
        SELECT 
            date, 
            time, 
            is_installation, 
            installation_choice, 
            installation_number, 
            message 
        FROM Bookings
        WHERE user_id = ?
    """, (user_id,))
    bookings = [
        {
            "date": row[0],
            "time": row[1],
            "type": "Installation: " + row[3] if row[2] else "Consultation",
            "installation_amount": row[4] if row[2] else "N/A",
            "message": row[5]
        }
        for row in cursor.fetchall()
    ]
    connection.close()
    
    return render_template("profile.html", username=session["username"], bookings=bookings)
  
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# error handling and other
@app.errorhandler(404)
def page_not_found(_):
    app.logger.error(f"Page not found: {request.url}")
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(_):
    app.logger.error(f"Server error: {request.url}")
    return render_template("500.html"), 500


@app.route("/admin")
def admin_page():
    if "username" not in session:
        return redirect(url_for("login_page"))
    if not session.get("admin", False):
        return redirect(url_for("index_page"))
    return render_template("admin.html")

@app.route("/404")
def page_not_found():
    return render_template("404.html")

@app.route("/500")
def internal_server_error():
    return render_template("500.html")

@app.route("/ai-data", methods=["GET", "POST"])
def ai_data_page():

    genai.configure(api_key="AIzaSyDC8TaqSgpDw2Emfkd7-1njplpLgd5dRxI")

    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(
        history=[
            {"role": "user", "parts": "Hello"},
            {
                "role": "model",
                "parts": "Great to meet you. What would you like to know?",
            },
        ]
    )

    # ai-question = request.form["ai-question"]

    data = request.get_json()
    question = data.get("question")

    response = chat.send_message(question)
    response_text = response.text

    def is_relevant_response(response):
        eco_freindly_keywords = [
            "eco-friendly",
            "sustainable",
            "green energy",
            "environmentally friendly",
            "renewable energy",
            "carbon footprint",
            "energy-efficient",
            "recycling",
            "conservation",
            "solar energy",
            "wind energy",
            "heating",
            "insulation",
            "energy consumption",
            "energy-saving",
            "energy efficiency",
            "energy bills",
            "energy costs",
            "energy usage",
            "carbon emissions",
            "carbon offset",
            "carbon neutral",
            "carbon credits",
            "carbon reduction",
            "carbon capture",
            "carbon sequestration",
        ]
        return any(keyword in response.lower() for keyword in eco_freindly_keywords)

    # Filter the response
    if is_relevant_response(response_text):
        # Check if the question specifies a longer response
        if "detailed" in question.lower() or "long" in question.lower():
            return jsonify(
                {
                    "response1": response_text,
                }
            )
        else:
            # Return a few short sentences
            short_response = " ".join(response_text.split(".")[:5]) + "."
            return jsonify(
                {
                    "response1": short_response,
                    "note": "As I am an AI, I can be wrong and you should always check trusted and well-known sources.",
                }
            )
    else:
        return jsonify(
            {
                "response1": "I'm sorry, but your question doesn't seem to be related to eco-friendly or sustainable topics. Please try asking something relevant.",
                "note": "As I am an AI, I can be wrong and you should always check trusted and well-known sources.",
            }
        )
                    
            
if __name__ == '__main__':
    app.run(debug=True)
    