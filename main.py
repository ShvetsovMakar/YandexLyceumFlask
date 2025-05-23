from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date

from authentication.user import User
from database.config import cur, db


class Post:
    def __init__(self, post_id, title, content, category, creation_date, author):
        self.id = post_id
        self.title = title
        self.content = content
        self.category = category
        self.creation_date = creation_date
        self.author = author


# Functions
def fetch_usernames():
    # Fetching usernames
    usernames = []
    cur.execute(f"SELECT username FROM users")
    for i in cur.fetchall():
        usernames.append(i[0])

    return usernames


def string_to_date(string):
    year, month, day = map(int, string.split('-'))
    return date(year, month, day)


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
        return redirect("/feed")

    return render_template("index.html", mode=mode)


@app.route("/sign_up", methods=['GET', 'POST'])
def signup():
    mode = "day"
    if current_user.is_authenticated:
        return redirect("/feed")

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        confirmation = request.form['confirmation']

        if password != confirmation:
            return redirect("/sign_up")  # password and confirmation do not match

        usernames = fetch_usernames()
        if username in usernames:
            return redirect("/sign_up")  # username already exists

        # Adding user to the database
        cur.execute(f'SELECT MAX(id) FROM users')
        try:
            user_id = cur.fetchone()[0] + 1
        except (Exception,):
            user_id = 1

        cur.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, username, password, '', '', '', '', 'day'))
        db.commit()

        return redirect("/")

    return render_template("sign_up.html", mode=mode)


@app.route("/login", methods=['GET', 'POST'])
def login():
    mode = "day"
    if current_user.is_authenticated:
        return redirect("/feed")

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        usernames = fetch_usernames()
        if username not in usernames:
            return redirect("/login")  # no such user

        cur.execute(f"SELECT password FROM users WHERE username = \"{username}\"")
        user_password = cur.fetchone()[0]

        if password != user_password:
            return redirect("/login")  # password is incorrect

        # Logging user in
        cur.execute(f"SELECT id FROM users WHERE username = \"{username}\"")
        user_id = cur.fetchone()[0]

        login_user(User(user_id))

        return redirect("/feed")

    return render_template("login.html", mode=mode)


@app.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
    mode = cur.fetchone()[0]

    if request.method == 'POST':
        title = request.form["title"]
        content = request.form["content"]
        category = request.form["category"]
        creation_date = str(datetime.now().date())
        author_id = current_user.id

        cur.execute(f'SELECT MAX(id) FROM posts')
        try:
            post_id = cur.fetchone()[0] + 1
        except (Exception,):
            post_id = 1

        cur.execute(f"INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)",
                    (post_id, title, content, category, creation_date, author_id))
        db.commit()

        return redirect("/feed")

    return render_template("create_post.html", mode=mode)


@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
    mode = cur.fetchone()[0]

    if request.method == 'POST':
        name = request.form["name"]
        surname = request.form["surname"]
        birth_date = request.form["birth_date"]
        about = request.form["about"]
        new_mode = request.form["mode"]

        cur.execute(f"UPDATE users SET name = \"{name}\", "
                                     f"surname = \"{surname}\","
                                     f"birth_date = \"{birth_date}\","
                                     f"about = \"{about}\","
                                     f"mode = \"{new_mode}\""
                    f"WHERE id = {current_user.id}")
        db.commit()

        return redirect("/feed")

    return render_template("edit_profile.html", mode=mode)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route("/feed", methods=['GET', 'POST'])
def feed():
    mode = 'day'
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    res = cur.execute("SELECT * FROM posts").fetchall()
    posts = []
    for i in range(len(res)):
        posts.append(
            Post(
                post_id=res[i][0],
                title=res[i][1],
                content=res[i][2],
                category=res[i][3],
                creation_date=string_to_date(res[i][4]),
                author=cur.execute(f"SELECT username FROM users WHERE id = ({res[i][5]})").fetchall()[0][0]
            )
        )
    return render_template(
        'feed.html',
        mode=mode,
        posts=posts
    )


@app.route("/user/<username>", methods=['GET', 'POST'])
def user_info(username):
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    usernames = fetch_usernames()
    if username not in usernames:
        return redirect("/invalid_user")

    cur.execute(f"SELECT name, surname, birth_date, about FROM users WHERE username = \"{username}\"")
    info = cur.fetchone()
    name = info[0]
    surname = info[1]
    birth_date = info[2]
    about = info[3]

    return render_template("user_info.html", mode=mode, username=username, name=name, surname=surname,
                           birth_date=birth_date, about=about)


@app.route("/invalid_user", methods=['GET', 'POST'])
def invalid_user():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    return render_template("invalid_user.html", mode=mode)


@app.errorhandler(401)
def unauthorized_callback(e):
    return render_template("login_required.html", mode="day")


@app.errorhandler(404)
def page_not_found(e):
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    return render_template("page_not_found.html", mode=mode)


if __name__ == "__main__":
    app.run()
