from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index_day.html")


if __name__ == "__main__":
    app.run()


'''
day: 1) #D4D4D4
     2) #B3B3B3
     3) #FFFFFF
     4) #2B2B2B
     
night: 1) #000000
       2) #D1D0D0
       3) #988686
       4) #5C4E4E
'''