import json, crypt

class Users:
    def __init__(self):
        self.json = json.load(open("./users.json",'r'))

    def save(self):
        open("./users.json",'w').write(json.dumps(self.json, ensure_ascii=False, indent=2))
        return

    def list(self):
        return list(map(lambda n:(n,True if 'admin' in self.json[n] else False),self.json))

    def exist(self,id):
        return id in self.json

    def isAdmin(self,id):
        if not self.exist(id):
            return False
        return True if 'admin' in self.json[id] else False

    def delete(self,id):
        if not self.exist(id):
            return False
        del self.json[id]
        self.save()
        return True

    # 暗号形式を変えるときは以下の３メソッドを修正する
    def add(self,id,password,admin=False):
        self.json[id]={'password':crypt.crypt(password)}
        if admin:
            self.json[id]['admin']=True
        self.save()
        return True

    def change_password(self,id,password):
        if not self.exist(id):
            return False
        self.json[id]['password']=crypt.crypt(password)
        self.save()
        return True

    def verify(self,id,password):
        if not self.exist(id):
            return False
        crypt_password=self.json[id]['password']
        return crypt.crypt(password, crypt_password)==crypt_password

if __name__ == '__main__':
    print("存否チェック")
    print(Users().exist('zzz'))
    print(Users().exist('zza'))
    print('管理者チェック')
    print(Users().isAdmin('zzz'))
    print(Users().isAdmin('zza'))
    print(Users().isAdmin('aaa'))
    print('パスワード取得')
    print(Users().getPassword('zzz'))
    print(Users().list())
    print('追加チェック')
    print(Users().add('ccc','c'))
    print(Users().list())
    print('パスワードチェック')
    print(Users().verify('ccc','c'))
    print(Users().verify('ccc','d'))
    print('削除チェック')
    print(Users().delete('ccc'))
    print(Users().list())
