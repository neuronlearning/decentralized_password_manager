from Crypto.Cipher import AES
import random
import hashlib
import sqlite3
import os
import datetime
import string

def encrypt(text:bytes,password:bytes):
    password = hashlib.sha256(password).digest()
    print(password)
    nonce = random.randbytes(15)
    cipher = AES.new(key=password,mode=AES.MODE_GCM,nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(text)
    return nonce+ciphertext+tag

def decrypt(text:bytes,password:bytes):
    cipher = AES.new(key=password,mode=AES.MODE_GCM,nonce=text[:15])
    decrypted = cipher.decrypt_and_verify(ciphertext=text[15:-16],received_mac_tag=text[-16:])
    return decrypted

def generate_database_key(length = 16):
    alphabet = list(string.ascii_letters + string.digits + string.punctuation)
    for i in range(10):
        random.shuffle(alphabet)

    return "".join(alphabet[:length])

def create_database(db_name:str):
    database = sqlite3.connect(f"{db_name}_db.db")
    cursor = database.cursor()
    try:
        cursor.execute("CREATE TABLE credentials (id int,url varchar(512), username varchar(655), password MEDIUMTEXT, date_created varchar(64), date_updated varchar(64))")
        database.commit()
        return 1
    except sqlite3.OperationalError:
        raise sqlite3.OperationalError("Database already exists")


def load_database(db_name:str):
    if not os.path.isfile(f"{db_name}_db.db"):
        return None
    database = sqlite3.connect(f"{db_name}_db.db")
    return database

def encrypt_database(db_name:str,key:bytes):
    with open(f"{db_name}_db.db","rb") as file:
        unencrypted = file.read()
    encrypted_database = encrypt(unencrypted,key)
    with open(f"{db_name}_db_encrypted.db","wb") as file:
        file.write(encrypted_database)

def decrypt_database(db_name:str,key:bytes):
    with open(f"{db_name}_db_encrypted.db","rb") as file:
        encrypted = file.read()
    decrypted_database = decrypt(encrypted,key)
    with open(f"{db_name}_db_decrypted_temp.db","wb") as file:
        file.write(decrypted_database)


def list_all_credentials(db_name: str):
    database = load_database(db_name)
    cursor = database.cursor()

    cursor.execute(f'SELECT url,username,password FROM credentials ')

    credentials = cursor.fetchall()

    for item in credentials:
        print(f"URL: {item[0]}\nUsername: {item[1]}\nPassword: {item[2]}\n{"-" * 30}")

def search_through_credentials(db_name:str,query:str):
    database = load_database(db_name)
    cursor = database.cursor()

    cursor.execute(f'SELECT url,username,password FROM credentials WHERE credentials.url LIKE "%{query}%" OR credentials.username LIKE "%{query}%" OR credentials.password LIKE "%{query}%"')

    credentials = cursor.fetchall()

    for item in credentials:
        print(f"URL: {item[0]}\nUsername: {item[1]}\nPassword: {item[2]}\n{"-" * 30}")


def check_if_credentials_exist(db_name: str, url: str, username: str, password: str):
    database = load_database(db_name)
    cursor = database.cursor()

    if cursor.execute(f'SELECT url,username,password '
                      f'FROM credentials '
                      f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"'):
        existing_data = cursor.fetchall()
        if len(existing_data) > 0:
            return existing_data
        return None

def update_credentials(url:str,username:str,password:str,database_object,new_username:str,new_password:str):
    cursor = database_object.cursor()
    current_date = datetime.datetime.now()
    if new_password and new_username:
        cursor.execute(
            f'UPDATE credentials SET username = "{new_username}", password = "{new_password}", date_updated = "{current_date}" '
            f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"')
    elif new_password:
        cursor.execute(f'UPDATE credentials SET password = "{new_password}",date_updated = "{current_date}" '
                       f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"')
    elif new_username:
        cursor.execute(f'UPDATE credentials SET username = "{new_username}",date_updated = "{current_date}" '
                       f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"')
    database_object.commit()


def add_credentials(db_name:str,url:str,username:str,password:str):
    database = load_database(db_name)
    cursor = database.cursor()
    current_date = datetime.datetime.now()

    if_exist = check_if_credentials_exist(db_name,url,username,password)
    if if_exist:
        for item in if_exist:
            print(f"URL: {item[0]}\nUsername: {item[1]}\nPassword: {item[2]}\n{"-" * 30}")
        option = input("Do you want to update the password or username? (y/n)")
        if option.lower() == "y":
            new_username = input("Enter new username (leave blank for no changes): ")
            new_password = input("Enter new password (leave blank for no changes): ")
            update_credentials(url,username,password,database,new_username,new_password)
    else:
        cursor.execute(f'INSERT INTO credentials VALUES ("{url}","{username}","{password}","{current_date}","{current_date}")')
    database.commit()


#add_credentials("dada","kokot.com","hajzel","heslo123")
