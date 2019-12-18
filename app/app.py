import flask
import flask_login

from foo import foo_page
from login import login_page

app = flask.Flask(__name__)
app.secret_key = 'aaa bbb'



app.register_blueprint(foo_page)
app.register_blueprint(login_page)


@app.route('/')
@flask_login.login_required
def show():
    #raise #コレをコメントインすることで強制停止してブラウザでロギング可能
    return flask.render_template('app.html', user=flask_login.current_user.id)
