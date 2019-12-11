import flask

import flask_login


foo_page = flask.Blueprint('foo_page',__name__, template_folder='templates')

@foo_page.route('/foo')
@flask_login.login_required
def show():
    return 'This is foo. Logged in as: ' + flask_login.current_user.id
