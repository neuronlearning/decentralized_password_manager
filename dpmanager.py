from Crypto.Cipher import AES
import random
import hashlib
import sqlite3
import os
import datetime

class DPManager:

    def __init__(self):
        self.__db_encryption_key = None
        self.__temp_db = None

    def __set_db_path(self,db_name):
        if db_name == "":
            raise Exception("The database name is empty")
        else:
            self.__db_name = db_name

    def __get_db_path(self):
        return self.__db_name

    db_name = property(__get_db_path,__set_db_path)

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

    def set_encryption_key(self,password):
        if password:
            self.__db_encryption_key = password.encode()

    def create_database(self):
        database = sqlite3.connect(self.db_name)
        cursor = database.cursor()
        try:
            cursor.execute("CREATE TABLE credentials (id INTEGER PRIMARY KEY AUTOINCREMENT,url varchar(512), username varchar(655), password MEDIUMTEXT, date_created varchar(64), date_updated varchar(64))")
            database.commit()
            self.encrypt_database(self.__db_encryption_key)
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(e)


    def load_database(self):
        if not os.path.isfile(self.db_name):
            raise FileNotFoundError("Database file cannot be found")

        with open(f"{self.db_name}","rb") as file:
            database = self.decrypt(file.read(), self.__db_encryption_key)

        with open(f"temp_db_file_{self.db_name}.temp", "wb") as file:
            file.write(database)
            file.close()

        database_d = sqlite3.connect(f"temp_db_file_{self.db_name}.temp")
        database_m = sqlite3.connect(":memory:")
        database_d.backup(database_m)
        self.__temp_db = database_m
        database_d.close()
        self.delete_temp_file()

    def delete_temp_file(self):
        os.remove(f"temp_db_file_{self.db_name}.temp")

    def write_to_database(self):
        temp_new = sqlite3.connect(f"temp_db_file_{self.db_name}.temp") # Creates a temporary file where the database from memory is going to be stored

        self.__temp_db.backup(temp_new) # stores the database in memory into the file

        temp_new.close() # closes the temp database

        with open(f"{self.db_name}", "wb") as file:
            with open(f"temp_db_file_{self.db_name}.temp","rb") as file2:
                file.write(self.encrypt(file2.read(), self.__db_encryption_key)) # reads the temp database file (current database in the memory) and encrypts it and overwrites the original database
                file2.close()
        self.__temp_db.close()
        self.delete_temp_file()


    def encrypt_database(self,key:bytes):
        with open(f"{self.db_name}","rb") as file:
            unencrypted = file.read()
        encrypted_database = self.encrypt(unencrypted,key)
        with open(f"{self.db_name}","wb") as file:
            file.write(encrypted_database)

    def list_all_credentials(self):
        database = self.__temp_db
        cursor = database.cursor()

        cursor.execute(f'SELECT id,url,username,password FROM credentials')

        credentials = cursor.fetchall()

        return credentials


    def search_through_credentials(self,query:str):
        database = self.__temp_db
        cursor = database.cursor()

        cursor.execute(f'SELECT id,url,username,password FROM credentials WHERE credentials.url LIKE "%{query}%" OR credentials.username LIKE "%{query}%" OR credentials.password LIKE "%{query}%"')

        credentials = cursor.fetchall()


        return credentials


    def check_if_credentials_exist(self, url: str, username: str, password: str):
        database = self.__temp_db
        cursor = database.cursor()

        if cursor.execute(f'SELECT id,url,username,password '
                          f'FROM credentials '
                          f'WHERE credentials.url = "{url}" AND credentials.username = "{username}" AND credentials.password = "{password}"'):
            existing_data = cursor.fetchall()
            if len(existing_data) > 0:
                return existing_data
            return None

    def update_credentials_by_name_and_password(self,url:str,username:str,password:str,new_username:str,new_password:str):
        database = self.__temp_db
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
        database = self.__temp_db
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
        database = self.__temp_db
        cursor = database.cursor()
        current_date = datetime.datetime.now()
        if url and username and password:
            cursor.execute(f'INSERT INTO credentials(url,username,password,date_created,date_updated) VALUES ("{url}","{username}","{password}","{current_date}","{current_date}")')
            database.commit()
            self.write_to_database() #thanks python for not allowing me to use wrapper for this
            self.load_database()

    def remove_credentials_by_id(self,id:int):
        database = self.__temp_db
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