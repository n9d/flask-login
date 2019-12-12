import flask_login

import json, crypt

# 暗号化ロジックをいじるときはここ
def crypt_password(password,c_password=''):
    if c_password=='':
        return crypt.crypt(password)
    else:
        return crypt.crypt(password,c_password)

class User(flask_login.UserMixin):

    # {uid1:{pass,admin},uid2:{pass,admin}...}の形式
    user_json = {}
    json_file = './users.json'
    # 後でs3にする
    @classmethod
    def load(cls):
        u = json.load(open(cls.json_file,'r'))
        cls.user_json=u
        return u

    @classmethod
    def save(cls):
        open(cls.json_file,'w').write(json.dumps(cls.user_json, ensure_ascii=False, indent=2))
        return

    # [{id,password,admin}]を返す
    @classmethod
    def list(cls):
        cls.load()
        r = []
        for key in cls.user_json:
            r.append({'id': key,
                      'password': cls.user_json[key]['password'],
                      'admin': True if 'admin' in  cls.user_json[key] else False})
        return r

    # idからUserを再構築する
    @classmethod
    def reload(cls,userid):
        #print("reload *****")
        cls.load()
        if userid in cls.user_json:
            admin = True if 'admin' in  cls.user_json[userid] else False
            password = cls.user_json[userid]['password']
            return {'status':True, 'user':User(userid, admin=admin, crypt_pass=password)}
        else:
            return {'status':False}


    # id,admin,password,correct を持つ
    def __init__(self, id, password='', admin=False, crypt_pass=False):
        User.load()
        self.json = User.user_json
        self.id = id
        if crypt_password:  # User.reload用 汚い
            print("reload2 !!!!")
            self.password=crypt_pass
            self.admin= True if 'admin' in  self.json[self.id] else False
            self.correct=True
        else:
            #print("create !!!!")
            self.password = crypt_password(password)
            self.admin=admin
            self.correct = True
            if self.id in self.json :
                self.correct = crypt_password(password,self.json[self.id]['password'])==self.json[self.id]['password']
                self.password = self.json[self.id]['password']
                self.admin = True if 'admin' in  self.json[self.id] else False
            else:
                self.add()
                User.save()


    def delete(self):
        del self.json[self.id]
        User.save()
        return True

    def change_password(self, oldpass, newpass1, newpass2):
        if crypt_password(oldpass,self.password)!=self.password :
            return False
        if newpass1!=newpass2:
            return False
        self.password=crypt_password(newpass1)
        self.add()
        return True

    def add(self):
        if self.admin:
            self.user_json[self.id]={'password':self.password, 'admin':self.admin}
        else:
            self.user_json[self.id]={'password':self.password}
        User.save()
        return True
