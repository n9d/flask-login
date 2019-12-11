import flask
import flask_login

import json, crypt

import random,string

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


login_page = flask.Blueprint('login_page',__name__, template_folder='templates')


'''
users_bak = {
    'aaa': {'password': 'foo'},
    'bbb': {'password': 'bar'},
    'zzz': {'password': 'zzz', 'admin':True},
}

users_crypt = {
    'aaa': {'password': '0EvD19Hw5TsNg'},
    'bbb': {'password': 'PZeK/WrNFGnbs'},
    'zzz': {'password': '2UJ9Mk7Lp9eiI', 'admin':True},
}
'''

# 後でs3にする
def load_users():
    user_json = json.load(open("./users.json",'r'))
    return user_json

def save_users():
    open("./users.json",'w').write(json.dumps(users, ensure_ascii=False, indent=2))
    return

users = load_users()


login_manager = flask_login.LoginManager()

# blueprint読み込み時に一度だけ評価して init_appを実行する
@login_page.record_once
def on_load(state):
    login_manager.init_app(state.app)


class User(flask_login.UserMixin):
    pass


# 暗号化ロジックをいじるときはここ
def verificate_password(password, crypt_password):
    return crypt.crypt(password, crypt_password)==crypt_password

def crypt_password(password):
    return crypt.crypt(password)


@login_manager.user_loader
def user_loader(userid):
    if userid not in users:
        return
    user = User()
    user.id = userid
    user.admin = True if 'admin' in users[userid] else False
    return user

@login_manager.request_loader
def request_loader(request):
    userid = request.form.get('userid')
    if userid not in users:
        return
    user = User()
    user.id = userid
    user.is_authenticated = verificate_password(request.form['password'],users[userid]['password'])
    return user

@login_page.route('/login', methods=['GET','POST'])
def login():
    if flask.request.method == 'GET':
        #flask_login.logout_user() # login画面出力時にはlogoutする
        return flask.render_template('login.html')

    userid = flask.request.form['userid']
    if userid in users and verificate_password(flask.request.form['password'],users[userid]['password']):
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

    if password1==password2 and verificate_password(flask.request.form['password'],users[userid]['password']):
        users[userid]['password']=crypt_password(password1)
        save_users()
        return flask.redirect('/')
    return flask.redirect('/changepassword')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect('/login')


@login_page.route('/manage_list')
@flask_login.login_required
def manage_list():
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    userlist=map(lambda n:(
        n,
        True if 'admin' in users[n] else False
    ),users)
    userlist=list(userlist)
    return flask.render_template('managelist.html',userlist=userlist)

@login_page.route('/manage_delete/<userid>', methods=['GET'])
@flask_login.login_required
def manage_delete(userid):
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    del users[userid]
    return flask.redirect(flask.url_for('login_page.manage_list'))

@login_page.route('/manage_add', methods=['GET','POST'])
@flask_login.login_required
def manage_add():
    if not flask_login.current_user.admin :
        return flask.redirect('/')
    if flask.request.method == 'GET':
        return flask.render_template('manageadd.html', password=randomString(10))
    userid=flask.request.form['userid']
    password=crypt_password(flask.request.form['password'])
    admin=flask.request.form['admin']
    users[userid]={'password': password, 'admin': admin}
    save_users()
    return flask.redirect(flask.url_for('login_page.manage_list'))

@login_page.route('/whoami')
@flask_login.login_required
def whoami():
    return "I'm %s"%(flask_login.current_user.id)
