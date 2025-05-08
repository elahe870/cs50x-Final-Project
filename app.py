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
    if not session.get("user_id"):
        return redirect("/login")
    return render_template("index.html")


@app.route("/logout")
def logout():
    #adapted from CS50's Finance
    "log user out"
    #forget any user_id
    session.clear()
    #redirect user to login form
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    #adapted from CS50's Finance
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    #adapted from my cs50x problem set Finance
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("No confirmation", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation not match", 400)
        # search for username
        user = request.form.get("username")
        exist = db.execute("SELECT * FROM users WHERE username = ?", user)
        if len(exist) == 1:
            return apology("Username is not valid! choose another username")

        # append database
        hashed = generate_password_hash(request.form.get("password"))

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hashed)
    elif request.method == "GET":
        return render_template("register.html")

    return render_template("login.html", message="Registration successful!")


@app.route("/forms_show", methods=["GET", "POST"])
@login_required
def forms_show():
    search_query = request.form.get("search") if request.method == "POST" else None

    if search_query:
        forms = db.execute(
            """SELECT forms.*, users.username AS created_by_name
               FROM forms JOIN users ON forms.created_by = users.id
               WHERE forms.name LIKE ? ORDER BY forms.id DESC""",
            f"%{search_query}%"
        )
    else:
        forms = db.execute(
            """SELECT forms.*, users.username AS created_by_name
               FROM forms JOIN users ON forms.created_by = users.id
               ORDER BY forms.id DESC"""
        )

    return render_template("forms_show.html", forms=forms)



@app.route("/forms_show/new", methods=["GET", "POST"])
@login_required
def new_form():
    if request.method == "POST":
        # Get form metadata
        name = request.form.get("name")
        description = request.form.get("description")
        user_id = session.get("user_id")  # Adjust if you use flask-login current_user.id

        if not name or not description:
            flash("Please provide both form name and description.", "warning")
            return render_template("form_new.html")

        # Insert new form and get its ID
        form_id = db.execute(
            "INSERT INTO forms (name, description, created_by) VALUES (?, ?, ?)",
            name, description, user_id
        )

        # Get fields data from form
        fields = request.form.getlist("field_label")
        field_types = request.form.getlist("field_type")
        field_options = request.form.getlist("field_options")
        field_required = request.form.getlist("field_required")

        # Insert each field into form_fields table
        for i in range(len(fields)):
            label = fields[i]
            ftype = field_types[i]
            options = field_options[i] if ftype in ["select", "radio", "checkbox"] else None
            required = 1 if str(i) in field_required else 0  # Store as integer boolean
            display_order = i + 1

            db.execute(
                "INSERT INTO form_fields (form_id, label, field_type, options, required, display_order) VALUES (?, ?, ?, ?, ?, ?)",
                form_id, label, ftype, options, required, display_order
            )

        flash("Form created successfully!", "success")
        return redirect(f"/forms_show/{form_id}/preview")

    # GET request - render the empty form creation page
    return render_template("form_new.html")


@app.route("/forms_show/<int:form_id>/preview")
@login_required
def preview_form(form_id):
    form = db.execute("SELECT * FROM forms WHERE id = ?", form_id)
    fields = db.execute("SELECT * FROM form_fields WHERE form_id = ? ORDER BY display_order", form_id)

    if not form:
        return apology("Form not found", 404)

    return render_template("form_preview.html", form=form[0], fields=fields)


@app.route("/forms_show/<int:form_id>/edit", methods=["GET", "POST"])
@login_required
def edit_form(form_id):
    if request.method == "POST":
        # Update form details
        name = request.form.get("name")
        description = request.form.get("description")
        db.execute("UPDATE forms SET name = ?, description = ? WHERE id = ?",
                   name, description, form_id)
        
        # First delete existing fields
        db.execute("DELETE FROM form_fields WHERE form_id = ?", form_id)
        
        # Then add updated fields (similar to new_form)
        fields = request.form.getlist("field_label")
        field_types = request.form.getlist("field_type")
        field_options = request.form.getlist("field_options")
        field_required = request.form.getlist("field_required")

        for i in range(len(fields)):
            field_label = fields[i]
            field_type = field_types[i]
            field_option = field_options[i] if field_type in ["select", "radio", "checkbox"] else None
            
            # Handle required checkbox logic
            required = 1 if str(i) in field_required else 0

            db.execute("""INSERT INTO form_fields 
                          (form_id, label, field_type, options, required, display_order) 
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       form_id, field_label, field_type, field_option, required, i+1)

        flash("Form updated successfully!")
        return redirect(f"/forms_show/{form_id}/preview")
    
    else:
        # GET request - load existing data
        form = db.execute("SELECT * FROM forms WHERE id = ?", form_id)[0]
        fields = db.execute("SELECT * FROM form_fields WHERE form_id = ? ORDER BY display_order", form_id)
        return render_template("form_edit.html", form=form, fields=fields)



@app.route("/forms_show/<int:form_id>/delete", methods=["POST"])
@login_required
def delete_form(form_id):
    # Optional: Verify the current user owns the form or has permission
    form = db.execute("SELECT * FROM forms WHERE id = ?", form_id)
    if not form:
        flash("Form not found.", "danger")
        return redirect("/forms_show")

    # Example permission check (adjust based on your auth system)
    if form[0]["created_by"] != session["user_id"]:
        flash("You do not have permission to delete this form.", "danger")
        return redirect("/forms_show")

    # Delete associated fields first (if your DB requires)
    db.execute("DELETE FROM form_fields WHERE form_id = ?", form_id)

    # Delete the form itself
    db.execute("DELETE FROM forms WHERE id = ?", form_id)

    flash("Form deleted successfully.", "success")
    return redirect("/forms_show")


    