from Crypto.Cipher import AES
import random
import hashlib
import sqlite3
import os
import datetime
import string

class DPManager:

    def __init__(self,db_name):
        self.db_name = db_name

    def encrypt(self,text:bytes,password:bytes):
        password = hashlib.sha256(password).digest()
        nonce = random.randbytes(15)
        cipher = AES.new(key=password,mode=AES.MODE_GCM,nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(text)
        return nonce+ciphertext+tag

    def decrypt(self,text:bytes,password:bytes):
        password = hashlib.sha256(password).digest()

        cipher = AES.new(key=password,mode=AES.MODE_GCM,nonce=text[:15])
        decrypted = cipher.decrypt_and_verify(ciphertext=text[15:-16],received_mac_tag=text[-16:])
        return decrypted

    def generate_database_key(self,length = 16):
        alphabet = list(string.ascii_letters + string.digits + string.punctuation)
        for i in range(10):
            random.shuffle(alphabet)

        password = "".join(alphabet[:length])
        open("database_key.txt","w").write(password)
        return password

    def create_database(self):
        database = sqlite3.connect(f"{self.db_name}_db.db")
        cursor = database.cursor()
        try:
            cursor.execute("CREATE TABLE credentials (id int,url varchar(512), username varchar(655), password MEDIUMTEXT, date_created varchar(64), date_updated varchar(64))")
            database.commit()
            return 1
        except sqlite3.OperationalError:
            pass


    def load_database(self):
        if not os.path.isfile(f"{self.db_name}_db.db"):
            return None
        database = sqlite3.connect(f"{self.db_name}_db.db")
        return database

    def encrypt_database(self,key:bytes):
        with open(f"{self.db_name}_db.db","rb") as file:
            unencrypted = file.read()
        encrypted_database = self.encrypt(unencrypted,key)
        with open(f"{self.db_name}_db_encrypted.db","wb") as file:
            file.write(encrypted_database)

    def decrypt_database(self,key:bytes):
        with open(f"{self.db_name}_db_encrypted.db","rb") as file:
            encrypted = file.read()
        decrypted_database = self.decrypt(encrypted,key)
        with open(f"{self.db_name}_db_decrypted_temp.db","wb") as file:
            file.write(decrypted_database)


    def list_all_credentials(self):
        database = self.load_database()
        cursor = database.cursor()

        cursor.execute(f'SELECT id,url,username,password FROM credentials ')

        credentials = cursor.fetchall()

        for item in credentials:
            print(f"ID: {item[0]}\nURL: {item[1]}\nUsername: {item[2]}\nPassword: {item[3]}\n{"-" * 30}")

    def search_through_credentials(self,query:str):
        database = self.load_database()
        cursor = database.cursor()

        cursor.execute(f'SELECT id,url,username,password FROM credentials WHERE credentials.url LIKE "%{query}%" OR credentials.username LIKE "%{query}%" OR credentials.password LIKE "%{query}%"')

        credentials = cursor.fetchall()

        for item in credentials:
            print(f"ID: {item[0]}\nURL: {item[1]}\nUsername: {item[2]}\nPassword: {item[3]}\n{"-" * 30}")


    def check_if_credentials_exist(self, url: str, username: str, password: str):
        database = self.load_database()
        cursor = database.cursor()

        if cursor.execute(f'SELECT id,url,username,password '
                          f'FROM credentials '
                          f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"'):
            existing_data = cursor.fetchall()
            if len(existing_data) > 0:
                return existing_data
            return None

    def update_credentials_by_name_and_password(self,url:str,username:str,password:str,new_username:str,new_password:str):
        database = self.load_database()
        cursor = database.cursor()
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
        database.commit()

    def update_credentials_by_id(self,id:int,new_username:str,new_password:str):
        database = self.load_database()
        cursor = database.cursor()
        current_date = datetime.datetime.now()
        if new_password and new_username:
            cursor.execute(
                f'UPDATE credentials SET username = "{new_username}", password = "{new_password}", date_updated = "{current_date}" '
                f'WHERE credentials.id = {id}')
        elif new_password:
            cursor.execute(f'UPDATE credentials SET password = "{new_password}",date_updated = "{current_date}" '
                           f'WHERE credentials.id = {id}')
        elif new_username:
            cursor.execute(f'UPDATE credentials SET username = "{new_username}",date_updated = "{current_date}" '
                           f'WHERE credentials.id = {id}')
        database.commit()


    def add_credentials(self,url:str,username:str,password:str):
        database = self.load_database()
        cursor = database.cursor()

        if_exist = self.check_if_credentials_exist(url,username,password)
        if if_exist:
            for item in if_exist:
                print(f"ID: {item[0]}\nURL: {item[1]}\nUsername: {item[2]}\nPassword: {item[3]}\n{"-" * 30}")
            option = input("Do you want to update the password or username? (y/n)")
            if option.lower() == "y":
                new_username = input("Enter new username (leave blank for no changes): ")
                new_password = input("Enter new password (leave blank for no changes): ")
                self.update_credentials_by_name_and_password(url,username,password,new_username,new_password)
        else:
            current_date = datetime.datetime.now()
            cursor.execute(f'INSERT INTO credentials VALUES ((select count(*) from credentials)+1,"{url}","{username}","{password}","{current_date}","{current_date}")')
        database.commit()



databa = DPManager("john")
databa.create_database()