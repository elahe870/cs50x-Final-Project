import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

import datetime

# Configure application
app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///GMP.db")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get the current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Get the user's ID from the session
    user_id = session["user_id"]

    # Query the database for 
    #stocks = db.execute("SELECT * FROM stocks WHERE user_id = ?", user_id)

    # Render the index.html template with the stocks data and current date
    return render_template("index.html")


@app.route("/logout")
def logout():
    "log user out"
    #forget any user_id
    session.clear()
    #redirect user to login form
    return redirect("/login")
