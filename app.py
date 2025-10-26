from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
import re
from cs50 import SQL

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///hy.db")


# Deals with cache
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

matches_done = True
game_done = False
valid_class_years = [2025, 2026, 2027, 2028]


@app.route("/")
def index():

    if session.get("user_id") is None:
        return render_template("index.html")
    else:
        return redirect("/hub")


@app.route("/hub", methods=["GET", "POST"])
@login_required
def hub():
    
    user_progress = get_user_progress(session["user_id"])

    # Render the hub.html template with the user's progress
    return render_template("hub.html", user_progress=user_progress)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide an email address", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE email = ?", request.form.get("email")
        )

        if len(rows) == 0:
            flash(
                "We don't recognize the email that you provided, please register",
                "warning",
            )
            return redirect("/register")

        # If email exists, check if the password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Incorrect password", "danger")
            return apology("Incorrect password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        class_year = request.form.get("class_year")
        gender = request.form.get("gender")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check all fields are filled
        if not (
            fname
            and lname
            and email
            and phone
            and class_year
            and gender
            and password
            and confirmation
        ):
            return apology("All fields need to be filled")

        # Check if passwords match
        if password != confirmation:
            return apology("Passwords don't match")

        # Check that the email is valid
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return apology("Invalid email address")

        # Check email domain
        if not (email.endswith("@college.harvard.edu") or email.endswith("@yale.edu")):
            return apology("Email must be a Harvard or Yale email address")

        # Check first and last names format
        if not all(re.match(r"^[A-Za-z\s-]+$", name) for name in [fname, lname]):
            return apology("Names must only include letters, spaces, and dashes")

        # Check class year
        if not (class_year.isdigit() and int(class_year) in valid_class_years):
            return apology("Class year must be between 2025 and 2028")

        # Check gender
        if gender not in ["male", "female"]:
            return apology("Gender must be Male or Female")

        if email.endswith("@college.harvard.edu"):
            school = "Harvard"
        elif email.endswith("@yale.edu"):
            school = "Yale"

        try:
            db.execute(
                "INSERT INTO users (fname, lname, email, phone, class_year, school, gender, hash, same_gender, same_class, party, bed_hour, alcohol, progress) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                fname,
                lname,
                email,
                phone,
                class_year,
                school,
                gender,
                generate_password_hash(password),
                None,
                None,
                None,
                None,
                None,
                1,
            )

        except ValueError:
            return apology("This email is already registered")

        # Update the current session to make sure that the user remains logged in
        rows = db.execute("SELECT id FROM users WHERE email = ?", email)
        session["user_id"] = rows[0]["id"]

        flash("Registered!")
        return redirect("/hub")

    else:
        return render_template("register.html")


@app.route("/hdiw", methods=["GET"])
def hdiw():

    return render_template("hdiw.html")


@app.route("/about", methods=["GET"])
def about():

    return render_template("about.html")


@app.route("/form", methods=["GET", "POST"])
@login_required
def form():

    user_progress = get_user_progress(session["user_id"])


    if request.method == "POST":
        # Retrieve and convert form data
        same_gender = request.form.get("same_gender")
        same_class = request.form.get("same_class")
        party = request.form.get("party")
        bed_hour = request.form.get("bed_hour")
        alcohol = request.form.get("alcohol")

        # Convert to integers and handle missing values
        try:
            same_gender = int(same_gender) if same_gender is not None else None
            same_class = int(same_class) if same_class is not None else None
            party = int(party) if party is not None else None
            bed_hour = int(bed_hour) if bed_hour is not None else None
            alcohol = int(alcohol) if alcohol is not None else None
        except ValueError:
            return apology("Invalid form inputs")

        # Check all fields are filled
        if any(v is None for v in [same_gender, same_class, party, bed_hour, alcohol]):
            return apology("All fields need to be filled")

        # Validate 'same_gender' field
        if same_gender not in [0, 1]:
            return apology("Invalid input for same gender preference")

        # Validate 'same_class' field
        if same_class not in [0, 1]:
            return apology("Invalid input for same class preference")

        # Validate 'party' field
        if party not in [0, 1, 2, 3, 4, 5]:
            return apology("Invalid input for party preference")

        # Validate 'bed_hour' field
        if bed_hour not in [8, 10, 12, 14, 16]:
            return apology("Invalid input for bedtime preference")

        # Validate 'alcohol' field
        if alcohol not in [0, 1, 2]:
            return apology("Invalid input for alcohol preference")

        #  SQL statement
        db.execute(
            "UPDATE users SET same_gender = ?, same_class = ?, party = ?, bed_hour = ?, alcohol = ?, progress = ? WHERE id = ?",
            same_gender,
            same_class,
            party,
            bed_hour,
            alcohol,
            2,
            session["user_id"],
        )

        flash("Form submitted!")

        return redirect("/")

    else:
        # Render the form template for GET request
        return render_template("form.html", user_progress=user_progress, matches_done=matches_done)




@app.route("/match")
@login_required
def match():
    # Retrieve the current user's ID from the session
    user_id = session["user_id"]

    # TO DO: Query the 'matches' table to find the match for the current user
    # TO DO: If the user_id is in the table, set match to match_id
    # TO DO: If the user_id is not in the table, set match to -1
    match_data = db.execute(
        "SELECT * FROM matches WHERE user_id = :user_id", user_id=user_id
    )
    
    if match_data:
        match_id = match_data[0]['match_id']
        if match_id and match_id != -1:
            # User has been matched
            match = db.execute(
                "SELECT * FROM users WHERE id = :match_id", match_id=match_id
            )
        else:
            # User has not been matched
            match = -1
    else:
        # If the user_id is not in the table, set match to -1
        match = -1
    
    if match == -1:
        return render_template("match.html", match=-1, matches_done=matches_done)
    
    return render_template("match.html", match=match[0], matches_done=matches_done)




@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user_id = session["user_id"]

    if request.method == "POST":
        # Extract data from form submission
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        class_year = int(request.form.get("class_year"))
        gender = request.form.get("gender")
        same_gender = request.form.get("same_gender")
        same_class = request.form.get("same_class")
        party = request.form.get("party")
        bed_hour = request.form.get("bed_hour")
        alcohol = request.form.get("alcohol")

        if not fname:
            return apology("First name is required")

        if not lname:
            return apology("Last name is required")

        # Phone number validation can vary based on the format you expect
        if not phone:
            return apology("Phone number is required")

        if class_year not in valid_class_years:
            return apology("Invalid class year")

        # Validate gender
        if gender not in ["male", "female"]:
            return apology("Invalid gender selection")

        # Existing validations
        if (
            same_gender is None
            or same_class is None
            or party is None
            or bed_hour is None
            or alcohol is None
        ):
            return apology("All fields need to be filled")
        
        same_gender = int(same_gender)
        same_class = int(same_class)
        party = int(party)
        bed_hour = int(bed_hour)
        alcohol = int(alcohol)

        if same_gender not in [0, 1]:
            return apology("Invalid input for same gender preference")

        if same_class not in [0, 1]:
            return apology("Invalid input for same class preference")

        if party not in [0, 1, 2, 3, 4, 5]:
            return apology("Invalid input for party preference")

        if bed_hour not in [8, 10, 12, 14, 16]:
            return apology("Invalid input for bedtime preference")

        if alcohol not in [0, 1, 2]:
            return apology("Invalid input for alcohol preference")

        # Update profile information
        db.execute(
            "UPDATE users SET fname = ?, lname = ?, email = ?, phone = ?, class_year = ?, gender = ?, same_gender = ?, same_class = ?, party = ?, bed_hour = ?, alcohol = ? WHERE id = ?",
            fname,
            lname,
            email,
            phone,
            class_year,
            gender,
            same_gender,
            same_class,
            party,
            bed_hour,
            alcohol,
            user_id,
        )

        flash("Profile updated!")
        return redirect("/")

    else:
        # Handling the GET request to display user information
        user_info = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)

        if not user_info:
            # Handle the case when no user data is returned
            return apology("User not found")

        # Convert numeric values to descriptive words
        user_data = user_info[0]

        return render_template("account.html", user=user_data)



@app.route("/changep", methods=["GET", "POST"])
@login_required
def changep():
    if request.method == "POST":
        # Get the user's inputs
        oldP = request.form.get("oldP")
        newP = request.form.get("newP")
        confP = request.form.get("confP")

        # Check the user's inputs
        if not oldP or not newP or not confP:
            return apology("All fields must be filled")

        hash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0
        ]["hash"]



        if not check_password_hash(hash, oldP):
            return apology("Incorrect current password")

        elif newP != confP:
            return apology("New passwords don't match")

        # Update the password
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            generate_password_hash(newP),
            session["user_id"],
        )

        flash("Password successfully changed!")
        return redirect("/profile")

    # Handles the get method
    else:
        return render_template("changep.html")
    
    
def get_user_progress(user_id):
   user_progress_result = db.execute(
       "SELECT progress FROM users WHERE id = ?", user_id
   )
   user_progress = user_progress_result[0]["progress"] if user_progress_result else 0
   if user_progress == 2 and matches_done:
       user_progress = 3
   if user_progress == 3 and game_done:
       user_progress = 4
   return user_progress