
# A very simple Flask Hello World app for you to get started with...

from flask import render_template
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/byprog')
def byprog():
    return render_template("byprog.html",
                           title='Initiatives by Program')
