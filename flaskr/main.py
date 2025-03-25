from flask import Flask
from flask import render_template
app = Flask(__name__, template_folder='Templates')

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/booking")
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
    