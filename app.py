### Import relevant modules ####
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set unique key to protect user data
app.secret_key = os.getenv("SECRET_KEY")

db_password = os.getenv("DB_PASSWORD")

# CHECK: are we testing?
if os.environ.get('FLASK_ENV') == 'TESTING':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    # Connect postgres database to Flask
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{db_password}@127.0.0.1/habittracker"

# Initiate SQLAlchemy to communicate with database
db = SQLAlchemy(app)


### Create 'Activity Logs' class / table to hold all instances of User's habits
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date)


### Create Habit class / table -- creates and stores habits in database ###
class Habit(db.Model):
    ### Set up database columns / attributes ###
    id = db.Column(db.Integer, primary_key=True)                                           # Create unique ID for each habit
    name = db.Column(db.String(100), nullable=False)                                       # Give each habit a name
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)              # Connect each habit to a user through user_id
    last_done = db.Column(db.Date, nullable=True)                                          # Track when each habit was last completed
    streak = db.Column(db.Integer, default=0, nullable=False)                              # Track streak for each habit
    date_created = db.Column(db.Date(), nullable=False)

    # Create relationship between ActivityLog and Habit table
    logs = db.relationship('ActivityLog', backref='habit', lazy='dynamic', cascade='all, delete-orphan')



### Create "Bridge Table" that connects to User table -- track connections between Users ###
followers = db.Table('followers',                                                               # Name table-- followers
                     ### Create 2 IDs -- One for follower, following ####
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),            # ID of person DOING the following
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))             # ID of the person BEING followed
                     )


### Create User class / table -- creates and stores Users in database ###
class User(db.Model):
    ### Set up table columns / attributes ###
    id = db.Column(db.Integer, primary_key=True)                                                # Give each User a unique ID
    username = db.Column(db.String(150), unique=True, nullable=False)                           # Store unique username for each User
    password = db.Column(db.String(255), nullable=False)                                        # Store password for each User
    habits = db.relationship("Habit", backref="owner")                                    # Find habits for each User

    ### Create relationship between User and followers table ###
    followed = db.relationship(
        "User",                                                                 # Connection is from User table
        secondary=followers,                                                          #     to followers table
        primaryjoin=(id == followers.c.follower_id),                                  # Match my ID to the follower column
        secondaryjoin=(id == followers.c.followed_id),                                # Match the followed column to their ID
        backref=db.backref('followers', lazy='dynamic'),                              # Create shortcut so my friends can see me in THEIR follower list
        lazy='dynamic')


### Create /register webpage functionality ###
@app.route("/register", methods=["GET", "POST"])
def register():
    # Check if data is being received from webpage
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Make sure username is valid
        if len(username) < 1 or not username.isalnum():
            flash("Username must consist only of letters and numbers")
            return redirect(url_for("register"))

        # Make sure password is valid length
        if len(password) < 8 or len(password) > 64:
            flash("Password must be between 8 and 64 characters long")
            return redirect(url_for("register"))

        # Make sure password is not only whitespace
        if password.isspace():
            flash("Password cannot be all whitespace")
            return redirect(url_for("register"))

        # Make sure username is not too long
        if len(username) > 30:
            flash("Username must be less than 30 characters")
            return redirect(url_for("register"))

        # Check if username is already taken
        existing_user = User.query.filter(func.lower(User.username) == username.lower()).first()
        if existing_user is not None:
            flash("An account with that username already exists")
            return redirect(url_for("register"))

        # Encrypt password
        password = generate_password_hash(password)

        # Create User object using user input
        user = User(username = username, password = password)
        db.session.add(user)                                                        # Add User object to database
        db.session.commit()                                                         # Save changes permanently to database
        session["user_id"] = user.id                                                # Create valid credentials for user
        return redirect(url_for("home"))                                            # Redirect user to Home page

    return render_template("register.html")


### Create /login webpage and functionality ###
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if data is being received from webpage
    if request.method == "POST":
        username = request.form["username"].strip()                                        # Store user input as username
        password = request.form["password"]                                       #      and password
        user = User.query.filter(func.lower(User.username) == username.lower()).first()                    # Find first instance of username in User table, store User object in variable

        # Check if user exists and password is valid
        if user is not None and check_password_hash(user.password, password):
            session["user_id"] = user.id                                               # Create valid credentials from user
            return redirect(url_for("home"))                                           # Redirect user to home page

        # Tell user if credentials they entered were invalid
        flash("Invalid Username or Password")
    return render_template("login.html")


### Create / webpage (home) and functionality ###
@app.route("/", methods=["GET", "POST"])
def home():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("register"))                        # redirect user to register page (change this to login in future?)

    # Check if logged-in user exists in database
    if db.session.get(User, session['user_id']) is None:
        session.pop("user_id", None)                                 # Clear invalid ID from browser
        return redirect(url_for("register"))                         # Send user to register page (change this to login in future?)

    # Save current user to pass to html
    current_user = db.session.get(User, session['user_id'])

    # Allow user to create new habit
    if request.method == "POST":
        habit = request.form["new_habit"]                                                           # Fetch user input
        new_habit = Habit(name= habit, user_id=session["user_id"], date_created=date.today())      # Create new Habit object
        db.session.add(new_habit)                                                                    # Add new habit object to database
        db.session.commit()                                                                         # Save changes permanently to database
        return redirect(url_for("home"))                                                            # Redirect user to home page

    # Find users habits in database
    habits = Habit.query.filter_by(user_id=session["user_id"]).order_by(Habit.id).all()

    # Display users habits
    return render_template("home.html", habits = habits, today= date.today(), user= current_user)


### Create option for users to delete habits ###
@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_habit(id):
    habit = db.session.get(Habit, id)                             # Find habit by ID in database

    # Check if habit exists and if user owns habit
    if habit and 'user_id' in session and habit.user_id == session["user_id"]:
        db.session.delete(habit)                            # Remove habit from database
        db.session.commit()                                 # Make database change official
    return redirect(url_for("home"))                        # Refresh home page (habit will no long appear)


### Create option for users to mark habit as complete ###
@app.route("/done/<int:id>", methods=["POST"])
def mark_done(id):
    habit = db.session.get(Habit, id)                                             #Find habit by ID in database

    # Check if habit exists and if user owns habit
    if habit and 'user_id' in session and habit.user_id == session["user_id"]:
        yesterday = date.today() - timedelta(days=1)                        # Define yesterday for streak logic

        # If this is users first time logging habit
        if habit.last_done is None:
            habit.streak = 1                                                # Set habit streak to 1
        # If habit was logged yesterday
        elif habit.last_done == yesterday:
            habit.streak += 1                                               # Increment streak by 1
        # If habit was already logged today
        elif date.today() - habit.last_done == timedelta(days=0):           # Leave streak as is
            pass
        # if it has been > 1 day since user logged habit
        else:
            habit.streak = 1                                                # Set streak to 1

        # Add habit to ActivityLog table
        habit_log = ActivityLog(habit_id=habit.id, date=date.today())
        db.session.add(habit_log)

        habit.last_done = date.today()                                      # Set today as day habit was last completed in database
        db.session.commit()                                                 # Make change to database official
    return redirect(url_for("home"))                                        # Refresh home page (habit will show status and streak)


# Create /stats route for habit analytics
@app.route("/stats/<int:id>", methods=["GET", "POST"])
def stats(id):
    habit = db.session.get(Habit, id)

    # Create dictionary to hold daily stats --> (0- mon, 1- tues, 3- wed, etc.) 
    stats_by_day = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

    # Make sure habit exists and user session is valid
    if habit and 'user_id' in session and habit.user_id == session['user_id']:
        # Get total count of users logs for habit
        count = habit.logs.count()

        # Calculate days passed
        delta = (date.today() - habit.date_created)
        days_since_start = delta.days + 1
        # Calculate completion rate
        completion_rate = round((count / days_since_start) * 100)

        # Fill dictionary with all logged habits
        for log in ActivityLog.query.filter_by(habit_id= habit.id).all():
            day = log.date
            weekday = day.weekday()
            stats_by_day[weekday] += 1

    # Send user back to home page if user query is not valid
    else:
        return redirect(url_for('home'))

    return render_template('stats.html', habit= habit.name, count= count, completion_rate= completion_rate, daily_stats= stats_by_day)



### Provide a search function, allowing users to search for friends ###
@app.route("/search", methods=["GET", "POST"])
def search():
    result = []                                                                             # Initialize result as an empty list

    # Is the website sending us data?
    if request.method == "POST":
        search_data = request.form["username"].lower()                                              # Store the users search data in a variable
        # Did the user input a valid search?
        if len(search_data) > 0:
            result = User.query.filter(func.lower(User.username).contains(search_data)).all()           # If so, return Users that match search
    return render_template("search.html", results=result)
    

### Allow users to follow others ###
@app.route("/follow/<username>", methods=["GET", "POST"])
def follow(username):
    friend_user = User.query.filter_by(username= username).first()          # Fetch friends user object from user input
    my_user = db.session.get(User, session['user_id'])                            # Fetch users id

    # Check if friends user exists
    if friend_user:
        # Make sure account does not belong to user
        if friend_user.id == session['user_id']:
            flash("That username is associated with your account")                  # Tell user they cannot follow themselves
            return redirect(url_for("home"))                                        # Redirect to home
        # Check is user already follows the account they are trying to follow
        if my_user.followed.filter_by(id=friend_user.id).first() is not None:
            flash("You already follow this user")                                   # Tell user they already follow the user they input
            return redirect(url_for("home"))                                        # Redirect to home
        # If user makes valid attempt to follow friend
        my_user.followed.append(friend_user)                        # Append friend to users followed list in database
        db.session.commit()                                         # Make database change official
        flash("User followed successfully")                         # Tell user the follow was successful
        return redirect(url_for("home"))                            # Redirect to home
    # If user is trying to follow an account that does not exist
    flash("The username you are trying to follow does not exist")   # Tell user friend doesnt exist
    return redirect(url_for("home"))                                # Redirect to home


### Allow user to unfollow other users ###
@app.route("/unfollow/<username>", methods=["GET", "POST"])
def unfollow(username):
    friend_user = User.query.filter_by(username= username).first()                  # Fetch friends User object from user input
    my_user = db.session.get(User, session["user_id"])                                    # Fetch users id

    # Check if friends User exists
    if friend_user:
        # Make sure account does not belong to user
        if friend_user.id == session["user_id"]:
            flash("That username is associated with your account")                  # Tell user they cannot unfollow themselves
            return redirect(url_for("home"))                                        # Redirect to home
        # Make sure user is already following friend
        if my_user.followed.filter_by(id=friend_user.id).first() is None:
            flash("You do not follow this user")                                    # Tell user they do not follow the user
            return redirect(url_for("home"))                                        # Redirect to home
        # If user makes valid attempt to unfollow friend
        my_user.followed.remove(friend_user)                                # Remove friend from users followed list in database
        db.session.commit()                                                 # Make database change official
        flash("User unfollowed successfully")                               # Tell user they have successfully unfollowed friend
        return redirect(url_for("home"))                                    # Redirect to home
    # If user is trying to unfollow account that does not exist
    flash("The user you are trying to unfollow does not exist")             # Tell user friend doesnt exist
    return redirect(url_for("home"))                                        # Redirect to home


### Create a dashboard that displays friends habits
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    friend_user = User.query.filter_by(username= username).first()
    my_user = db.session.get(User, session['user_id'])
    today = date.today()

    # Make sure friend exists in database
    if friend_user is None:
        flash("That user does not exist")
        return redirect(url_for('home'))

    # Check if friend is in users friends list
    if my_user.followed.filter_by(id=friend_user.id).first() is None:
        flash("Follow {0} to see their habits".format(friend_user.username))
        return redirect(url_for("home"))

    # Find friends habits in database
    habits = Habit.query.filter_by(user_id = friend_user.id).order_by(Habit.id).all()

    # Send habit list to html
    return render_template("friend.html", habits=habits, friend=friend_user, today=today)


### Create /logout page and functionality ###
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)                            # Remove user credentials (will require log in next time)
    return redirect(url_for("login"))                       # Redirect user to login page



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)