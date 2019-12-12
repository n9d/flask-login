import flask
import flask_login

#import json, crypt
import random,string

from user_model import User

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

login_page = flask.Blueprint('login_page',__name__, template_folder='templates')
login_manager = flask_login.LoginManager()

# blueprint読み込み時に一度だけ評価して init_appを実行する
@login_page.record_once
def on_load(state):
    login_manager.init_app(state.app)

@login_manager.user_loader
def user_loader(userid):
    print("**** exec loader ***")
    ret=User.reload(userid)
    if ret['status']:
        print(ret['user'].id)
        print(ret['user'].admin)
        return ret['user']
    else:
        return None

'''
# apiキーとかでログインするときにはここ
@login_manager.request_loader
def request_loader(request):
    return None
'''

@login_page.route('/login', methods=['GET','POST'])
def login():
    if flask.request.method == 'GET':
        #flask_login.logout_user() # login画面出力時にはlogoutする
        return flask.render_template('login.html')
    user = User(flask.request.form['userid'],flask.request.form['password'])
    if user.correct:
        flask_login.login_user(user)
        return flask.redirect('/')
    return flask.redirect('/login')

@login_page.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect('/login')

@login_page.route('/change_password', methods=['GET','POST'])
@flask_login.login_required
def change_password():
    if flask.request.method == 'GET':
        return flask.render_template('change_password.html')

    if flask_login.current_user.change_password(flask.request.form['password'],flask.request.form['password1'],flask.request.form['password2']):
        return flask.redirect('/')
    return flask.redirect('/change_password')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect('/login')

@login_page.route('/manage_list')
@flask_login.login_required
def manage_list():
    print("******* manage list ********")
    if not flask_login.current_user.admin :
        print("******* manage list ********")
        return flask.redirect('/')
    userlist=map(lambda n:(
        n['id'],
        n['admin']
    ),User.list())
    return flask.render_template('manage_list.html',userlist=list(userlist))

@login_page.route('/manage_delete/<userid>', methods=['GET'])
@flask_login.login_required
def manage_delete(userid):
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    User(userid).delete()
    return flask.redirect(flask.url_for('login_page.manage_list'))

@login_page.route('/manage_add', methods=['GET','POST'])
@flask_login.login_required
def manage_add():
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    if flask.request.method == 'GET':
        return flask.render_template('manage_add.html', password=randomString(10))

    User(flask.request.form['userid'],
         flask.request.form['password'],
         True if 'admin' in flask.request.form else False
    )
    return flask.redirect(flask.url_for('login_page.manage_list'))
