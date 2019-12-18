import flask
import flask_login
import random,string

from user_model import Users

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

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(userid):
    if not Users().exist(userid):
        return
    user = User()
    user.id = userid
    user.admin = Users().isAdmin(userid)
    return user

@login_manager.request_loader
def request_loader(request):
    userid = request.form.get('userid')
    if not Users().exist(userid):
        return
    user = User()
    user.id = userid
    user.is_authenticated = Users().verifiy(userid,request.form['password'])
    return user

@login_page.route('/login', methods=['GET','POST'])
def login():
    if flask.request.method == 'GET':
        #flask_login.logout_user() # login画面出力時にはlogoutする
        return flask.render_template('login.html')
    userid = flask.request.form['userid']
    if Users().exist(userid) and Users().verify(userid,flask.request.form['password']):
        user = User()
        user.id = userid
        flask_login.login_user(user)
        return flask.redirect('/')
    return flask.redirect('/login')

@login_page.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect('/login')

@login_page.route('/changepassword', methods=['GET','POST'])
@flask_login.login_required
def change_password():
    if flask.request.method == 'GET':
        return flask.render_template('changepassword.html')
    userid = flask_login.current_user.id
    password=flask.request.form['password']
    password1=flask.request.form['password1']
    password2=flask.request.form['password2']
    if password1==password2 and Users().verify(userid,password):
        Users().change_password(userid,password1)
        return flask.redirect('/')
    return flask.redirect('/change_password')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect('/login')

@login_page.route('/manage_list')
@flask_login.login_required
def manage_list():
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    return flask.render_template('manage_list.html',userlist=Users().list())

@login_page.route('/manage_delete/<userid>', methods=['GET'])
@flask_login.login_required
def manage_delete(userid):
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    Users().delete(userid)
    return flask.redirect(flask.url_for('login_page.manage_list'))

@login_page.route('/manage_add', methods=['GET','POST'])
@flask_login.login_required
def manage_add():
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    if flask.request.method == 'GET':
        return flask.render_template('manage_add.html', password=randomString(10))
    Users().add(flask.request.form['userid'],
                flask.request.form['password'],
                'admin' in flask.request.form)
    return flask.redirect(flask.url_for('login_page.manage_list'))
