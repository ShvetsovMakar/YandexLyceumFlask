from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from authentication.user import User
from database.config import cur, db

# Functions
def fetch_usernames():
    # Fetching usernames
    usernames = []
    cur.execute(f"SELECT username FROM users")
    for i in cur.fetchall():
        usernames.append(i[0].lower())

    return usernames


app = Flask(__name__)
app.secret_key = "V&6zapM5k@0B8qn"

# Creating login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(name):
    return User(name)


# Index page
@app.route("/")
def index():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    return render_template("index.html", mode=mode)


@app.route("/sign_up", methods=['GET', 'POST'])
def signup():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']

        if password != confirmation:
            return redirect("/sign_up")  # password and confirmation do not match

        usernames = fetch_usernames()
        if username.lower() in usernames:
            return redirect("/sign_up")  # username already exists

        # Adding user to the database
        cur.execute(f'SELECT MAX(id) FROM users')
        user_id = cur.fetchone()[0] + 1

        cur.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, username, password, '', '', '', '', 'day'))
        db.commit()

        return redirect("/")

    return render_template("sign_up.html", mode=mode)


@app.route("/login", methods=['GET', 'POST'])
def login():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usernames = fetch_usernames()
        if username.lower() not in usernames:
            return redirect("/login")  # no such user

        cur.execute(f"SELECT password FROM users WHERE username = \"{username}\"")
        user_password = cur.fetchone()[0]

        if password != user_password:
            return redirect("/login")  # password is incorrect

        # Logging user in
        cur.execute(f"SELECT id FROM users WHERE username = \"{username}\"")
        user_id = cur.fetchone()[0]

        login_user(User(user_id))

        return redirect("/")

    return render_template("login.html", mode=mode)

@app.route("/add_post")
def add_post():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    return render_template("add_post.html", mode=mode)

@app.route("/profile_form")
def profile_form():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    return render_template("profile_form.html", mode=mode)

if __name__ == "__main__":
    app.run()
