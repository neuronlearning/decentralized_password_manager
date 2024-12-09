import tkinter
from tkinter import ttk, messagebox,filedialog
from main import DPManager
import json
import threading
import os

class app:

    def __init__(self):
        self.password_input()
        self.root = tkinter.Tk()
        self.root.geometry("800x600")
        self.root.title("Password Manager")
        self.root.config(bg="#3e4142")
        self.settings()
        self.widgets()
        self.root.mainloop()


    def password_input(self):
        file = filedialog.askopenfilename(title="Choose your password text file")
        self.db_decryption_key = open(file,"r").read()

    def settings(self):
        json_settings = { # more are on the way tm
            "database": "default_user.db",
            "database_name": "default_user",
            "key_path": "default_key_path"
        }
        try:
            with open("dpm_settings.json","r") as file:
                json_settings_ = json.load(file)
            if os.path.isfile(json_settings_["database"]):
                self.database = DPManager(json_settings_["database_name"],self.db_decryption_key)
                self.database.load_database()
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Database not found. New one was created.")
            with open("dpm_settings.json", "w") as file:
                json.dump(json_settings,file,indent=2)
            self.database = DPManager(json_settings["database_name"], self.db_decryption_key)
            self.database.create_database()

    def widgets(self):
        columns = ("id","url","username","password")

        search_frame = tkinter.Frame(self.root,bg="#2C3136")
        search_frame.pack(side=tkinter.TOP,fill=tkinter.X)
        searchbar_text = tkinter.StringVar()
        search_button = tkinter.Button(search_frame,text="Search",font=36,bg="green",borderwidth=-1,fg="white")
        search_button.pack(side=tkinter.RIGHT)
        searchbar = tkinter.Entry(search_frame,bg="#2C3136",font=36,fg="white",borderwidth=-1,textvariable=searchbar_text,width=564) #width 564 because im too retarded to find a fix for this
        searchbar.pack(side=tkinter.LEFT,fill=tkinter.X)


        treeview_frame = tkinter.Frame(self.root)
        treeview_frame.pack(fill=tkinter.X, side=tkinter.TOP)
        tree = ttk.Treeview(treeview_frame, columns=columns, show="headings")
        scrollbar_treeview = ttk.Scrollbar(treeview_frame,orient="vertical",command=tree.yview)
        tree.config(yscrollcommand=scrollbar_treeview.set)
        tree.heading('id', text="ID")
        tree.heading('url', text='URL')
        tree.heading('username', text='Username')
        tree.heading('password', text='Password')
        scrollbar_treeview.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        tree.pack(fill=tkinter.X, side=tkinter.TOP)

        credentials = self.database.list_all_credentials()
        for contact in credentials:
            tree.insert('', tkinter.END, values=contact)



gui = app()


