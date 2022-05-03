import sqlite3
from hashlib import md5

class DB():
    code = '''Return Code:
            [0][0] : Full Name
            [0][1] : Email
            [0][2] : Password
        '''
    conn = sqlite3.connect('account.db', check_same_thread=False)
    cursor = conn.cursor()
    def create(fullName, Email, Pswd):
        Password = md5(Pswd.encode()).hexdigest()
        DB.cursor.execute(f"INSERT INTO Account VALUES('{fullName}', '{Email}', '{Password}')")
        DB.conn.commit()
        return f"Sucessfull added user {fullName}"
    def read(Email):
        values = DB.cursor.execute(f"SELECT * FROM Account WHERE Email = '{Email}'").fetchall()
        if len(values) == 0:
            return "User not found"
        else:
            return values
        

if __name__ == '__main__':
    help = '''To write data in table:
        DB.create(fullName, Email, Password)
To Read data from table:
        DB.read(Email)
        '''
    print(help)
    dat = DB.read('sachinshrivastv152207@gmail.com')
    print(dat)
    print(len(dat))
    if len(dat) == 0:
        print('db empty')
    else:
        print(dat)
