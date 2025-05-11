from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

from authentication.user import User
from database.config import cur, db


# Модель данных поста (в реальном приложении это будет из БД)
class Post:
    def __init__(self, id, title, content, category, creation_date, author_id):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.creation_date = creation_date
        self.author_id = author_id

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

        cur.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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

        return redirect("/feed")

    return render_template("login.html", mode=mode)

@app.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    mode = "day"
    if current_user.is_authenticated:
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
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    if request.method == 'POST':
        first_name = request.form["first_name"]
        second_name = request.form["last_name"]
        birth_date = request.form["birth_date"]
        about = request.form["about"]
        new_mode = request.form["mode"]

        cur.execute(f"UPDATE users SET name = \"{first_name}\", "
                                     f"surname = \"{second_name}\","
                                     f"birth_date = \"{birth_date}\","
                                     f"about = \"{about}\","
                                     f"mode = \"{new_mode}\""
                    f"WHERE id = {current_user.id}")
        db.commit()

        return redirect("/feed")

    return render_template("edit_profile.html", mode=mode)


@app.route("/feed", methods=['GET', 'POST'])
def feed():
    mode = "day"
    if current_user.is_authenticated:
        cur.execute(f"SELECT mode FROM users WHERE id = {current_user.id}")
        mode = cur.fetchone()[0]

    return render_template("feed.html", mode=mode)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")



@app.route('/posts')
def view_posts():
    res = cur.execute("""Select * from posts""").fetchall()
    print(len(res))
    posts = []
    for i in range(len(res)):
        posts.append(Post(
            id = res[i][0],
            title = res[i][1],
            content = res[i][2],
            category = res[i][3],
            creation_date = datetime.now(),
            author_id = cur.execute(f"Select username from users Where id = ({res[i][5]})").fetchall()[0][0]

        ))
        print(cur.execute(f"Select username from users Where id = ({res[i][5]})").fetchall()[0][0])


    return render_template(
        'posts_list.html',
        mode="day",
        posts=posts
    )
if __name__ == "__main__":
    app.run()
