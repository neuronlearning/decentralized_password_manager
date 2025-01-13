from Crypto.Cipher import AES
import random
import hashlib
import sqlite3
import os
import datetime
import string

class DPManager:

    def __init__(self,db_name=""):
        if db_name:
            self.db_name = db_name
        self.db_encryption_key = None
        self.temp_db = None

    def set_db_name(self,db_name):
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
        try:
            decrypted = cipher.decrypt_and_verify(ciphertext=text[15:-16],received_mac_tag=text[-16:])
        except ValueError:
            raise ValueError("Wrong password")
        else:
            return decrypted

    def set_encryption_key(self,password = ""):
        if password:
            self.db_encryption_key = password.encode()

    def create_database(self,):
        database = sqlite3.connect(f"{self.db_name}")
        cursor = database.cursor()
        try:
            cursor.execute("CREATE TABLE credentials (id int,url varchar(512), username varchar(655), password MEDIUMTEXT, date_created varchar(64), date_updated varchar(64))")
            database.commit()
            self.encrypt_database(self.db_encryption_key)
            return 1
        except sqlite3.OperationalError:
            pass


    def load_database(self):

        if not os.path.isfile(f"{self.db_name}"):
            raise FileNotFoundError("Database file cannot be found")

        with open(f"{self.db_name}","rb") as file:
            database = self.decrypt(file.read(),self.db_encryption_key)

        with open(f"temp_db_file_{self.db_name}.temp", "wb") as file:
            file.write(database)
            file.close()

        database_d = sqlite3.connect(f"temp_db_file_{self.db_name}.temp")
        database_m = sqlite3.connect(":memory:")
        database_d.backup(database_m)
        self.temp_db = database_m
        database_d.close()
        self.delete_temp_file()

    def delete_temp_file(self):
        os.remove(f"temp_db_file_{self.db_name}.temp")

    def write_to_database(self):
        temp_new = sqlite3.connect(f"temp_db_file_{self.db_name}.temp") # Creates a temporary file where the database from memory is going to be stored

        self.temp_db.backup(temp_new) # stores the database in memory into the file

        temp_new.close() # closes the temp database

        with open(f"{self.db_name}", "wb") as file:
            with open(f"temp_db_file_{self.db_name}.temp","rb") as file2:
                file.write(self.encrypt(file2.read(),self.db_encryption_key)) # reads the temp database file (current database in the memory) and encrypts it and overwrites the original database
                file2.close()
        self.temp_db.close()
        self.delete_temp_file()


    def encrypt_database(self,key:bytes):
        with open(f"{self.db_name}","rb") as file:
            unencrypted = file.read()
        encrypted_database = self.encrypt(unencrypted,key)
        with open(f"{self.db_name}","wb") as file:
            file.write(encrypted_database)

    def list_all_credentials(self):
        database = self.temp_db
        cursor = database.cursor()

        cursor.execute(f'SELECT id,url,username,password FROM credentials')

        credentials = cursor.fetchall()

         #for item in credentials:
          #  print(f"ID: {item[0]}\nURL: {item[1]}\nUsername: {item[2]}\nPassword: {item[3]}\n{"-" * 30}")
        return credentials


    def search_through_credentials(self,query:str):
        database = self.temp_db
        cursor = database.cursor()

        cursor.execute(f'SELECT id,url,username,password FROM credentials WHERE credentials.url LIKE "%{query}%" OR credentials.username LIKE "%{query}%" OR credentials.password LIKE "%{query}%"')

        credentials = cursor.fetchall()

        #for item in credentials:
         #   print(f"ID: {item[0]}\nURL: {item[1]}\nUsername: {item[2]}\nPassword: {item[3]}\n{"-" * 30}")
        return credentials


    def check_if_credentials_exist(self, url: str, username: str, password: str):
        database = self.temp_db
        cursor = database.cursor()

        if cursor.execute(f'SELECT id,url,username,password '
                          f'FROM credentials '
                          f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"'):
            existing_data = cursor.fetchall()
            if len(existing_data) > 0:
                return existing_data
            return None

    def update_credentials_by_name_and_password(self,url:str,username:str,password:str,new_username:str,new_password:str):
        database = self.temp_db
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
        self.write_to_database() #thanks python for not allowing me to use wrapper for this
        self.load_database()

    def update_credentials_by_id(self,id:int,new_username:str,new_password:str):
        database = self.temp_db
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
        self.write_to_database() #thanks python for not allowing me to use wrapper for this
        self.load_database()

    def add_credentials(self,url:str,username:str,password:str):
        database = self.temp_db
        cursor = database.cursor()
        current_date = datetime.datetime.now()
        if url and username and password:
            cursor.execute(f'INSERT INTO credentials VALUES ((select count(*) from credentials)+1,"{url}","{username}","{password}","{current_date}","{current_date}")')
            database.commit()
            self.write_to_database() #thanks python for not allowing me to use wrapper for this
            self.load_database()

    def remove_credentials_by_id(self,id:int):
        database = self.temp_db
        cursor = database.cursor()

        cursor.execute(f"DELETE FROM credentials WHERE credentials.id = {id}")
        database.commit()
        self.write_to_database() #thanks python for not allowing me to use wrapper for this
        self.load_database()

'''
database = DPManager("default_user","test")
database.load_database()
print(database.search_through_credentials("goo"))
'''