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
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("users.db")
cursor = connection.cursor()

hashed_password = generate_password_hash("123456789")
cursor.execute(
    "INSERT INTO users (username, email, password, admin) VALUES ('admin', 'admin@gmail.com', ?, TRUE)",
    (hashed_password,),
)
connection.commit()
connection.close()
