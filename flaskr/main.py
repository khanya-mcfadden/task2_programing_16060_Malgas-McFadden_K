from flask import Flask
from flask import render_template
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




@app.route("booking-choice")
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
    return render_template('register.html')

@app.route("/login")
def login():
    return render_template('login.html')
if __name__ == '__main__':
    app.run(debug=True)
    