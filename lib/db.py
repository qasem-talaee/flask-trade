import sqlite3
import hashlib
import datetime

class DB:
    
    def __add_admin(self):
        if self.__get_admin():
            name = 'Admin'
            email = 'admin@gmail.com'
            password = hashlib.sha256('admin'.encode()).hexdigest()
            status = 'admin'
            date = datetime.datetime.now()
            data = (name, email, password, '0', '0', status, date, '0')
            db_string = "INSERT INTO user(name,email,pass,access_id,secret_key,status,expired,baned) VALUES (?,?,?,?,?,?,?,?);"
            curser = self.conn.cursor()
            curser.execute(db_string, data)
            self.conn.commit()
            curser.close()
    
    def create_table(self):
        #users table
        self.conn.execute('''
                          CREATE TABLE IF NOT EXISTS user
                          (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name CHAR(100) NOT NULL,
                            email CHAR(1000) NOT NULL,
                            pass CHAR(300) NOT NULL,
                            access_id CHAR(1000),
                            secret_key CHAR(1000),
                            status CHAR(10) NOT NULL,
                            expired TIMESTAMP,
                            baned CHAR(10) NOT NULL
                          );
                          ''')
    
    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA KEY='Qasem@15273438'")
        self.create_table()
        self.__add_admin()
    
    def __get_admin(self):
        cursor = self.conn.execute("SELECT * FROM user WHERE status='admin';")
        i = 0
        for _ in cursor:
            i += 1
        if i == 0:
            return True
        else:
            return False
        
    def get_login(self, email, password):
        password = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.execute("SELECT * FROM user WHERE email=%(email)s AND pass=%(password)s;", {'email': email, 'password': password})
        i = 0
        for _ in cursor:
            i += 1
        if i == 0:
            return False
        else:
            return True
        
    def get_account(self, email):
        cursor = self.conn.execute("SELECT * FROM user WHERE email='{email}';".format(email=email))
        out = {}
        for row in cursor:
            out['id'] = row[0]
            out['name'] = row[1]
            out['email'] = row[2]
            out['pass'] = row[3]
            out['access_id'] = row[4]
            out['secret_key'] = row[5]
        return out
    
    def update_account(self, id, name, email, access_id, secret_key):
        self.cursor.execute("UPDATE user SET name='{name}',email='{email}',access_id='{access_id}',secret_key='{secret_key}' WHERE id={id};".format(name=name, email=email, access_id=access_id, secret_key=secret_key, id=int(id)))
        self.conn.commit()
        
    def update_account_pass(self, id, name, email, access_id, secret_key, password):
        self.cursor.execute("UPDATE user SET name='{name}',email='{email}',access_id='{access_id}',secret_key='{secret_key}',pass='{password}' WHERE id={id};".format(name=name, email=email, access_id=access_id, secret_key=secret_key, password=password, id=int(id)))
        self.conn.commit()
        
    def get_user_admin(self, email):
        cursor = self.conn.execute("SELECT * FROM user WHERE status='admin' and email='{email}';".format(email=email))
        i = 0
        for _ in cursor:
            i += 1
        if i == 0:
            return False
        else:
            return True
        
    def add_new_user(self, name, email, password, status, baned):
        date = datetime.datetime.now()
        password = hashlib.sha256(password.encode()).hexdigest()
        data = (name, email, password, '0', '0', status, date, baned)
        db_string = "INSERT INTO user(name,email,pass,access_id,secret_key,status,expired,baned) VALUES (?,?,?,?,?,?,?,?);"
        curser = self.conn.cursor()
        curser.execute(db_string, data)
        self.conn.commit()
        curser.close()
        
    def get_user(self, email):
        cursor = self.conn.execute("SELECT * FROM user WHERE email <> '{email}';".format(email=email))
        out = []
        for row in cursor:
            user = []
            user.append(row[0])
            user.append(row[1])
            user.append(row[2])
            user.append(row[6])
            user.append(row[7])
            user.append(row[8])
            out.append(user)
        return out
    
    def change_status(self, id, status):
        if status == 'admin':
            self.cursor.execute("UPDATE user SET status='user' WHERE id={id};".format(id=int(id)))
            self.conn.commit()
        if status == 'user':
            self.cursor.execute("UPDATE user SET status='admin' WHERE id={id};".format(id=int(id)))
            self.conn.commit()
    
    def change_baned(self, id, status):
        if status == '0':
            self.cursor.execute("UPDATE user SET baned='1' WHERE id={id};".format(id=int(id)))
            self.conn.commit()
        if status == '1':
            self.cursor.execute("UPDATE user SET baned='0' WHERE id={id};".format(id=int(id)))
            self.conn.commit()
            
    def delete_user(self, id):
        self.cursor.execute("DELETE FROM user WHERE id={id};".format(id=int(id)))
        self.conn.commit()
        
    def get_secret(self, email):
        if email != '':
            cursor = self.conn.execute("SELECT * FROM user WHERE email='{email}';".format(email=email))
            out = []
            for row in cursor:
                out.append(row[4])
                out.append(row[5])
            return out
        
    def get_ban(self, email):
        cursor = self.conn.execute("SELECT * FROM user WHERE baned='1' and email='{email}';".format(email=email))
        i = 0
        for _ in cursor:
            i += 1
        if i == 0:
            return False
        else:
            return True