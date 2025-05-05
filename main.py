from flask import Flask, render_template, request, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authentication.user import User

app = Flask(__name__)

# Creating login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(name):
    return User(name)


# Index page
@app.route("/")
def index():
    if current_user.is_authenticated:
        pass

    return render_template("index.html", mode="night")


@app.route("/signup")
def signup():
    if current_user.is_authenticated:
        pass

    return render_template("signup.html", mode="night")


@app.route("/login")
def login():
    if current_user.is_authenticated:
        pass

    return render_template("login.html", mode="night")


if __name__ == "__main__":
    app.run()
