# Note: some of the code in here is taken from the distribution code from Week 9 Finance
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are automatically reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///chatter.db")


@app.route("/")
@login_required
def index():
    """Show the home page"""

    # Get the user's username
    users = db.execute("SELECT username FROM users WHERE id = :user_id", user_id=session["user_id"])

    # Get posts from people the user follows
    posts = db.execute(
        "SELECT title, datetime, posts.id AS post_id, user_id, username FROM posts INNER JOIN users ON posts.user_id = users.id WHERE posts.user_id IN (SELECT followee_id FROM follows WHERE follower_id = :follower_id) ORDER BY datetime DESC LIMIT 50", follower_id=session["user_id"])

    return render_template("index.html", posts=posts, users=users)


@app.route("/addcomment", methods=["POST"])
@login_required
def add_comment():
    """Add a comment to an existing post"""

    # Ensure the user typed something into the comment box
    if not request.form.get("comment"):
        return apology("can not have a blank comment", 403)

    # Assign form information to variables
    post_id = request.form.get("post_id")
    user_id = session["user_id"]
    contents = request.form.get("comment")

    # Insert the comment into the database
    db.execute("INSERT INTO comments (post_id, user_id, contents) VALUES (:post_id, :user_id, :contents)",
               post_id=post_id, user_id=user_id, contents=contents)

    return redirect("/post/" + post_id)


@app.route("/discover/people")
@login_required
def discover_people():
    """Show the user a list of people followed by their followees"""

    # Set page title
    page_title = "Followees of Followees"

    # Get the followees of the user's followees
    follows = db.execute(
        "SELECT DISTINCT followee_id AS user_id, username FROM follows INNER JOIN users ON follows.followee_id = users.id WHERE follower_id IN (SELECT followee_id FROM follows WHERE follower_id = :follower_id)", follower_id=session["user_id"])

    if len(follows) == 0:
        zero = True
    else:
        zero = False

    return render_template("peoplelist.html", follows=follows, page_title=page_title, zero=zero)


@app.route("/discover/posts")
@login_required
def discover_posts():
    """Show the user recent posts by other users"""

    # Get the 50 newest posts in the database
    posts = db.execute(
        "SELECT title, datetime, posts.id AS post_id, user_id, username FROM posts INNER JOIN users ON posts.user_id = users.id ORDER BY datetime DESC LIMIT 50")

    return render_template("postlist.html", posts=posts)


@app.route("/editprofile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Allow the user to edit their profile"""

    # User reached route via POST
    if request.method == "POST":
        about = request.form.get("about")
        picture = request.form.get("picture")

        # Update the database with the user's new profile information
        db.execute("UPDATE profiles SET about = :about, picture = :picture WHERE user_id = :user_id",
                   about=about, picture=picture, user_id=session["user_id"])

        return redirect("/profile/" + str(session["user_id"]))

    # User reached route via GET
    else:
        return render_template("editprofile.html")


@app.route("/follow", methods=["POST"])
@login_required
def follow():
    """Let user follow other people"""

    followee_id = request.form.get("user_id")

    # Make sure that the user isn't already following the followee
    follows = db.execute("SELECT * FROM follows WHERE follower_id = :follower_id AND followee_id = :followee_id",
                         follower_id=session["user_id"], followee_id=followee_id)

    if len(follows) == 1:
        return apology("you are already following this person", 400)

    # Add the follower and followee to the database
    db.execute("INSERT INTO follows (follower_id, followee_id) VALUES (:follower_id, :followee_id)",
               follower_id=session["user_id"], followee_id=followee_id)

    return redirect("/profile/" + followee_id)


@app.route("/followees")
@login_required
def followees():
    """Show the user a list of their followees"""

    # Set page title
    page_title = "My Followees"
    # Get the user's followees
    follows = db.execute(
        "SELECT followee_id AS user_id, username FROM follows INNER JOIN users ON follows.followee_id = users.id WHERE follower_id = :follower_id", follower_id=session["user_id"])

    if len(follows) == 0:
        zero = True
    else:
        zero = False

    return render_template("peoplelist.html", follows=follows, page_title=page_title, zero=zero)


@app.route("/followers")
@login_required
def followers():
    """Show the user a list of their followers"""

    # Set page title
    page_title = "My Followers"
    # Get the user's followers
    follows = db.execute(
        "SELECT follower_id AS user_id, username FROM follows INNER JOIN users ON follows.follower_id = users.id WHERE followee_id = :followee_id", followee_id=session["user_id"])

    if len(follows) == 0:
        zero = True
    else:
        zero = False

    return render_template("peoplelist.html", follows=follows, page_title=page_title, zero=zero)


# This implementation of login was taken from the distribution code of CS50 Finance
@app.route("/login", methods=["GET", "POST"])
def login():
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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pw_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# This implementation of logout was taken from the distribution code of CS50 Finance
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/newpost", methods=["GET", "POST"])
@login_required
def new_post():
    """Allow user to make a new post"""

    # User reached route via POST
    if request.method == "POST":
        # Ensure the post has a title
        if not request.form.get("title"):
            return apology("you must enter a title", 403)

        # Ensure the post has contents
        if not request.form.get("contents"):
            return apology("you must enter contents", 403)

        # Assign form information to variables
        user_id = session["user_id"]
        title = request.form.get("title")
        contents = request.form.get("contents")

        # Check if the user has already made a post with the same title
        rows = db.execute("SELECT title FROM posts WHERE user_id = :user_id AND title = :title", user_id=user_id, title=title)

        # If rows does not have a length of 0, then the user has made a post with the same title before
        if len(rows) != 0:
            return apology("you have already made a post with that title", 403)

        # Check if the user has already made a post with the same contents
        rows = db.execute("SELECT contents FROM posts WHERE user_id = :user_id AND contents = :contents",
                          user_id=user_id, contents=contents)

        # If rows does not have a length of 0, then the user has made a post with the same contents before
        if len(rows) != 0:
            return apology("you have already made a post with these contents", 403)

        # Add post into database
        db.execute("INSERT INTO posts (user_id, title, contents) VALUES (:user_id, :title, :contents)",
                   user_id=user_id, title=title, contents=contents)

        return redirect("/")

    # USer reached route via GET
    else:
        return render_template("newpost.html")


@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    """Show the user the contents of the post they clicked on as well as any comments on the post"""

    # Query database for the post
    posts = db.execute(
        "SELECT title, contents, datetime, posts.id AS post_id, user_id, username FROM posts INNER JOIN users ON posts.user_id = users.id WHERE posts.id = :post_id", post_id=post_id)

    # Make sure that there is only 1 post with that id
    if len(posts) != 1:
        return apology("something went wrong on our end", 400)

    # Query the database for any comments attached to the post
    comments = db.execute(
        "SELECT username, contents, datetime FROM comments INNER JOIN users ON comments.user_id = users.id WHERE post_id = :post_id ORDER BY datetime ASC", post_id=post_id)

    return render_template("post.html", posts=posts, comments=comments)


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    """Show the user the profile they clicked on"""

    # Query database for user's profile information
    profiles = db.execute(
        "SELECT about, picture, user_id, users.username AS username FROM profiles INNER JOIN users ON profiles.user_id = users.id WHERE user_id = :user_id", user_id=user_id)

    # Make sure that only 1 profile was returned
    if len(profiles) != 1:
        return apology("something went wrong on our end", 400)

    # Find out if the profile belongs to the user
    if profiles[0]["user_id"] == session["user_id"]:
        self_profile = True
        following = False

    else:
        self_profile = False

        # Find out if the profile belongs to someone the user follows
        follows = db.execute("SELECT * FROM follows WHERE follower_id = :follower_id AND followee_id = :followee_id",
                             follower_id=session["user_id"], followee_id=profiles[0]["user_id"])
        if len(follows) == 1:
            following = True
        elif len(follows) == 0:
            following = False
        else:
            return apology("something went wrong on our end", 400)

    # Query database for user's post history
    posts = db.execute(
        "SELECT title, datetime, posts.id AS post_id, user_id, username FROM posts INNER JOIN users ON posts.user_id = users.id WHERE user_id = :user_id ORDER BY datetime DESC", user_id=user_id)

    return render_template("profile.html", profiles=profiles, posts=posts, self_profile=self_profile, following=following)


# This implementation of register was taken from my implementation of register in CS50 Finance
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":
        # Check that username is not blank
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Check that password is not blank
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Assign form information to variables
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if username already exists or not
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # If rows does not have a length of 0, then the username is taken
        if len(rows) != 0:
            return apology("username is already taken", 403)

        # Check that passwords match
        if password != confirmation:
            return apology("passwords did not match", 403)

        # Hash the password
        pw_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, pw_hash) VALUES (:username, :pw_hash)", username=username, pw_hash=pw_hash)

        # Retrieve the user's newly generated id
        users = db.execute("SELECT id FROM users WHERE username = :username", username=username)

        # Create a profile for the user
        db.execute("INSERT INTO profiles (user_id) VALUES (:user_id)", user_id=users[0]["id"])

        return redirect("/")

    # User reached route via GET
    if request.method == "GET":
        return render_template("register.html")


@app.route("/search", methods=["POST"])
@login_required
def search():
    """Allow the user to search for posts and people"""

    # Make sure that the search bar is not empty
    if not request.form.get("keyword"):
        return apology("search criteria must not be empty", 403)

    keyword = request.form.get("keyword")

    # Add in the wildcard characters for the SQL queries
    like_keyword = "%" + keyword + "%"

    # Get all posts that match the keyword(s)
    posts = db.execute(
        "SELECT title, datetime, posts.id AS post_id, user_id, username FROM posts INNER JOIN users ON posts.user_id = users.id WHERE title LIKE ? OR contents LIKE ? ORDER BY datetime DESC", (like_keyword), (like_keyword))

    if len(posts) == 0:
        no_posts = True
    else:
        no_posts = False

    # Get all people that match the keyword(s)
    people = db.execute("SELECT id AS user_id, username FROM users WHERE username LIKE ?", (like_keyword))

    if len(people) == 0:
        no_people = True
    else:
        no_people = False

    return render_template("search.html", posts=posts, no_posts=no_posts, people=people, no_people=no_people)


@app.route("/unfollow", methods=["POST"])
@login_required
def unfollow():
    """Allow the user to unfollow anyone they already follow"""

    followee_id = request.form.get("user_id")

    # Make sure that the user is following the followee
    follows = db.execute("SELECT * FROM follows WHERE follower_id = :follower_id AND followee_id = :followee_id",
                         follower_id=session["user_id"], followee_id=followee_id)
    if len(follows) == 0:
        return apology("you weren't following this person to begin with", 400)

    # Remove the follower and followee from the database
    db.execute("DELETE FROM follows WHERE follower_id = :follower_id AND followee_id = :followee_id",
               follower_id=session["user_id"], followee_id=followee_id)

    return redirect("/profile/" + followee_id)