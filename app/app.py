import flask
import flask_login

from foo import foo_page
from login import login_page

app = flask.Flask(__name__)
app.secret_key = 'aaa bbb'



app.register_blueprint(foo_page)
app.register_blueprint(login_page)


@app.route('/')
def hello_world():
    #raise
    return 'Hello, World!'
