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
            options = field_options[i] if ftype in ["dropdown", "radio", "checkbox", "select"] else None
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
            field_option = field_options[i] if field_type in ["select", "radio", "checkbox", "dropdown"] else None
            
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
    # Verify the current user owns the form or has permission
    form = db.execute("SELECT * FROM forms WHERE id = ?", form_id)
    if not form:
        flash("Form not found.", "danger")
        return redirect("/forms_show")

    if form[0]["created_by"] != session["user_id"]:
        flash("You do not have permission to delete this form.", "danger")
        return redirect("/forms_show")

    # Count related inspections
    inspections = db.execute("SELECT COUNT(*) AS count FROM inspections WHERE form_id = ?", form_id)[0]["count"]

    # Count related inspection fields via inspections
    fields_count = db.execute("""
        SELECT COUNT(*) AS count
        FROM inspection_fields
        JOIN inspections ON inspection_fields.inspection_id = inspections.id
        WHERE inspections.form_id = ?
    """, form_id)[0]["count"]

    if inspections > 0 or fields_count > 0:
        return apology("Cannot delete form: it has related inspections or fields.")
    else:
        # Delete associated fields first (if your DB requires)
        db.execute("DELETE FROM form_fields WHERE form_id = ?", form_id)

        # Delete the form itself
        db.execute("DELETE FROM forms WHERE id = ?", form_id)

        flash("Form deleted successfully.", "success")
    return redirect("/forms_show")


@app.route("/inspection_show", methods=["GET", "POST"])
@login_required
def inspection_show():
    user_id = session["user_id"]
    forms = db.execute("SELECT * FROM forms")

    selected_form_id = None
    inspections = []

    if request.method == "POST":
        selected_form_id = request.form.get("form_id")

        if selected_form_id:
            inspections_raw = db.execute("""
                SELECT * FROM inspections
                WHERE inspector_id = ? AND form_id = ?
                ORDER BY submitted_at DESC
            """, user_id, selected_form_id)

            # برای هر inspection، سه فیلد اول را بر اساس display_order واکشی کن
            for inspection in inspections_raw:
                fields = db.execute("""
                    SELECT ff.label, ifs.value
                    FROM inspection_fields AS ifs
                    JOIN form_fields AS ff ON ifs.field_id = ff.id
                    WHERE ifs.inspection_id = ?
                    ORDER BY ff.display_order
                    LIMIT 3
                """, inspection["id"])

                inspection["fields"] = fields
                inspections.append(inspection)

    return render_template("inspection_show.html", forms=forms, inspections=inspections, selected_form_id=selected_form_id)


from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename
from flask import current_app

@app.route('/inspection_new', methods=['GET', 'POST'])
@login_required
def inspection_new():
    form_id = request.args.get('form_id')
    if not form_id:
        flash("Form ID missing.", "danger")
        return redirect("/inspection_show")

    if request.method == "GET":
        form = db.execute("SELECT * FROM forms WHERE id = ?", form_id)
        if not form:
            flash("Form not found.", "danger")
            return redirect("/inspection_show")

        fields = db.execute("""
            SELECT * FROM form_fields
            WHERE form_id = ?
            ORDER BY display_order ASC
        """, form_id)

        # Send inspection=None to prevent Jinja errors
        return render_template('inspection_new.html', form=form[0], fields=fields, inspection=None)

    # POST method: process the form
    user_id = session["user_id"]
    fields = db.execute("SELECT * FROM form_fields WHERE form_id = ?", form_id)

    errors = []
    valid_count = 0
    total_count = len(fields)

    for field in fields:
        field_name = f"field_{field['id']}"
        value = None

        if field['field_type'] == 'checkbox':
            values = request.form.getlist(field_name + "[]")
            value = ",".join(values) if values else None
            if field['required'] and not values:
                errors.append(f"{field['label']} is required.")
            elif values:
                valid_count += 1
        else:
            value = request.form.get(field_name)
            if field['required'] and (value is None or value.strip() == ""):
                errors.append(f"{field['label']} is required.")
            elif value and value.strip():
                valid_count += 1

            if field['field_type'] == 'date' and value:
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                    if date_obj > datetime.today().date():
                        errors.append(f"{field['label']} cannot be in the future.")
                except ValueError:
                    errors.append(f"{field['label']} is not a valid date.")
                    continue

    if errors:
        for error in errors:
            flash(error, "warning")
        form = db.execute("SELECT * FROM forms WHERE id = ?", form_id)
        if not form:
            flash("Form not found.", "danger")
            return redirect("/inspection_show")

        return render_template(
            'inspection_new.html',
            form=form[0],
            fields=fields,
            inspection=None  # Still no inspection in POST error case
        )

    score = round((valid_count / total_count) * 100, 2) if total_count > 0 else 0

    # Save inspection
    db.execute("""
        INSERT INTO inspections (form_id, inspector_id, location, notes, score)
        VALUES (?, ?, ?, ?, ?)
    """, form_id, user_id, request.form.get("location"), request.form.get("notes"), score)

    inspection_id = db.execute("SELECT last_insert_rowid() AS id")[0]["id"]

    for field in fields:
        field_id = field["id"]
        field_name = f"field_{field_id}"

        if field['field_type'] == 'checkbox':
            values = request.form.getlist(field_name + "[]")
            value_str = ",".join(values) if values else None
        else:
            value_str = request.form.get(field_name)

        db.execute("""
            INSERT INTO inspection_fields (inspection_id, field_id, value, comment)
            VALUES (?, ?, ?, NULL)
        """, inspection_id, field_id, value_str)

    # === Handle image uploads ===
    image_folder = os.path.join("static", "inspection_photos")
    os.makedirs(image_folder, exist_ok=True)

    # 1. Uploaded file
    photo_file = request.files.get("photo_upload")
    if photo_file and photo_file.filename:
        filename = secure_filename(photo_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        full_filename = f"{timestamp}_{filename}"
        path = os.path.join(image_folder, full_filename)
        photo_file.save(path)

        db.execute("""
            INSERT INTO inspection_images (inspection_id, filename)
            VALUES (?, ?)
        """, inspection_id, full_filename)

    # 2. Captured base64 image
    captured_data = request.form.get("captured_photo")
    if captured_data and captured_data.startswith("data:image/"):
        try:
            header, encoded = captured_data.split(",", 1)
            image_data = base64.b64decode(encoded)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            full_filename = f"{timestamp}_captured.png"
            path = os.path.join(image_folder, full_filename)

            with open(path, "wb") as f:
                f.write(image_data)

            db.execute("""
                INSERT INTO inspection_images (inspection_id, filename)
                VALUES (?, ?)
            """, inspection_id, full_filename)
        except Exception as e:
            flash("Failed to save captured photo.", "warning")

    flash(f"Inspection submitted successfully. Score: {score}%", "success")
    return redirect("/inspection_show")


@app.route("/inspection/<int:inspection_id>/delete", methods=["POST"])
@login_required
def inspection_delete(inspection_id):
    try:
        # Check if inspection exists
        inspection = db.execute("SELECT 1 FROM inspections WHERE id = ?", inspection_id)
        if not inspection:
            flash("Inspection not found.", "danger")
            return redirect("/inspection_show")

        # Delete related inspection_fields
        db.execute("DELETE FROM inspection_fields WHERE inspection_id = ?", inspection_id)
        # Delete related inspection_images
        db.execute("DELETE FROM inspection_images WHERE inspection_id = ?", inspection_id)
        # Finally, delete the inspection itself
        db.execute("DELETE FROM inspections WHERE id = ?", inspection_id)

        flash("Inspection and all related records deleted successfully.", "success")
        return redirect("/inspection_show")

    except Exception as e:
        flash(f"Error deleting inspection: {str(e)}", "danger")
        return redirect("/inspection_show")


@app.route("/inspection/<int:inspection_id>")
@login_required
def inspection_preview(inspection_id):
    # Get inspection main details
    inspection = db.execute("""
        SELECT i.*, f.name AS form_name, u.username AS inspector_name
        FROM inspections i
        JOIN forms f ON i.form_id = f.id
        JOIN users u ON i.inspector_id = u.id
        WHERE i.id = ?
    """, inspection_id)
    if not inspection:
        flash("Inspection not found.", "danger")
        return redirect("/inspection_show")

    inspection = inspection[0]

    # Get inspection field values
    fields = db.execute("""
        SELECT ff.label, ff.field_type, ifs.value
        FROM inspection_fields ifs
        JOIN form_fields ff ON ifs.field_id = ff.id
        WHERE ifs.inspection_id = ?
        ORDER BY ff.display_order ASC
    """, inspection_id)

    # Get attached images
    images = db.execute("""
        SELECT filename FROM inspection_images
        WHERE inspection_id = ?
    """, inspection_id)

    return render_template("inspection_preview.html", inspection=inspection, fields=fields, images=images)


from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, base64

@app.route("/inspection/<int:inspection_id>/edit", methods=["GET", "POST"])
@login_required
def inspection_edit(inspection_id):
    inspection = db.execute("SELECT * FROM inspections WHERE id = ? AND inspector_id = ?", inspection_id, session["user_id"])[0]
    form = db.execute("SELECT * FROM forms WHERE id = ?", inspection["form_id"])[0]
    fields = db.execute("SELECT * FROM form_fields WHERE form_id = ?", form["id"])

    # Add current values to each field
    for field in fields:
        value = db.execute("""
            SELECT value FROM inspection_fields
            WHERE inspection_id = ? AND field_id = ?
        """, inspection_id, field["id"])
        field["value"] = value[0]["value"] if value else ""

    # Get images
    images = db.execute("SELECT * FROM inspection_images WHERE inspection_id = ?", inspection_id)

    # DELETE IMAGE logic
    if request.method == "POST" and "delete_image_id" in request.form:
        image_id = request.form.get("delete_image_id")
        image = db.execute("SELECT filename FROM inspection_images WHERE id = ? AND inspection_id = ?", image_id, inspection_id)
        if image:
            filename = image[0]["filename"]
            filepath = os.path.join("static", "inspection_photos", filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            db.execute("DELETE FROM inspection_images WHERE id = ?", image_id)
            flash("Image deleted successfully.", "success")
        else:
            flash("Image not found or unauthorized.", "danger")
        return redirect(url_for("inspection_edit", inspection_id=inspection_id))

    # FORM SUBMISSION logic
    if request.method == "POST":
        # Save text, number, date, select, checkbox, radio values
        for field in fields:
            key = f"field_{field['id']}"
            value = request.form.getlist(key) if field["field_type"] == "checkbox" else request.form.get(key)
            value = ",".join(value) if isinstance(value, list) else value
            db.execute("""
                INSERT INTO inspection_fields (inspection_id, field_id, value)
                VALUES (?, ?, ?)
                ON CONFLICT(inspection_id, field_id)
                DO UPDATE SET value = excluded.value
            """, inspection_id, field["id"], value)

        # Save notes and location
        db.execute("UPDATE inspections SET notes = ?, location = ? WHERE id = ?", request.form.get("notes"), request.form.get("location"), inspection_id)

        # Handle uploaded photo
        if "photo_upload" in request.files:
            photo = request.files["photo_upload"]
            if photo and photo.filename != "":
                filename = secure_filename(photo.filename)
                photo_path = os.path.join("static", "inspection_photos", filename)
                photo.save(photo_path)
                db.execute("INSERT INTO inspection_images (inspection_id, filename) VALUES (?, ?)", inspection_id, filename)

        # Handle captured photo (base64)
        captured = request.form.get("captured_photo")
        if captured:
            import base64, uuid
            header, encoded = captured.split(",", 1)
            binary_data = base64.b64decode(encoded)
            filename = f"captured_{uuid.uuid4().hex}.png"
            with open(os.path.join("static", "inspection_photos", filename), "wb") as f:
                f.write(binary_data)
            db.execute("INSERT INTO inspection_images (inspection_id, filename) VALUES (?, ?)", inspection_id, filename)

        flash("Inspection updated successfully.", "success")
        return redirect(url_for("inspection_show", inspection_id=inspection_id))

    return render_template("inspection_edit.html", form=form, fields=fields, inspection=inspection, images=images)



from datetime import datetime

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    # 1. Total inspections by user
    total_inspections = db.execute(""" 
        SELECT COUNT(*) AS count FROM inspections WHERE inspector_id = ? 
    """, user_id)[0]["count"]
    
    # 2. Inspections this month
    current_month = datetime.now().strftime("%Y-%m")
    inspections_this_month = db.execute("""
        SELECT COUNT(*) AS count FROM inspections 
        WHERE strftime('%Y-%m', submitted_at) = ?
    """, (current_month,))[0]["count"]

    # 3. Inspections with deviations (score < 100)
    deviations = db.execute("""
        SELECT COUNT(*) AS count FROM inspections 
        WHERE inspector_id = ? AND score < 100
    """, user_id)[0]["count"]

    # 4. Recent 5 inspections
    recent_inspections = db.execute("""
        SELECT i.id, f.name AS form_name, i.submitted_at, i.location, i.score 
        FROM inspections i 
        JOIN forms f ON i.form_id = f.id 
        WHERE i.inspector_id = ? 
        ORDER BY i.submitted_at DESC 
        LIMIT 5
    """, user_id)

    # 5. Average score (optional)
    avg_score = db.execute("""
        SELECT ROUND(AVG(score), 2) AS avg FROM inspections WHERE inspector_id = ?
    """, user_id)[0]["avg"] or 0

    return render_template("dashboard.html",
                           total=total_inspections,
                           this_month=inspections_this_month,
                           deviations=deviations,
                           recent=recent_inspections,
                           avg_score=avg_score)