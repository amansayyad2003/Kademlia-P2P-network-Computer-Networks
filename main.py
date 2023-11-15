import random
import hashlib
def show_login_menu():
    usernme = input('Enter your username')
    pwd = input('Enter your password: ')
    return username, pwd
def show_signup_menu():
    usernme = input('Enter your username: ')
    fullnme = input('Enter your full name: ')
    pwd = input('Enter your password: ')
    return usernme, fullnme, pwd
import mysql.connector                                                                                                                                                                                         
conn = mysql.connector.connect(host='localhost', password='PetronesTower1.', user='root', database='MyDatabase')
cursor = conn.cursor()
print('connection established')
my_ipaddress = input('Enter your ip address: ')
port_no = random.randint(20000, 60000)
nodeid = hashlib.sha1(f'{my_ipaddress}:{port_no}'.encode()).digest()
username = None
passwd = None
fullname = None
while True:
    print('-----Menu----')
    print('1. Login')
    print('2. Sign up')
    print('3. exit')

    option = int(input('Enter your option: '))
    if option == 1:
        username, passwd = show_login_menu()
        query = 'SELECT exists(SELECT 1 from userInfo where username = %s and passwd = %s)'
        cursor.execute(query, (username, passwd))
        results = cursor.fetchone()
        if results[0]:
            print('Login successful')
            while True:
                a = 2
        else:
            print('Login failed')
    elif option == 2:
        username, fullname, passwd = show_signup_menu()
        query = "SELECT EXISTS(SELECT 1 FROM userInfo WHERE username = %s)"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        exists = result[0]
        if exists:
            print('Username already exists. Please try again.')
        else:
            query = 'INSERT INTO userInfo VALUES(%s, %s, %s)'
            cursor.execute(query, (username, fullname, passwd))
            conn.commit()
            print('Signup successful.')
