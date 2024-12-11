import tkinter
from tkinter import ttk, messagebox,filedialog
from main import DPManager
import json
import threading
import os

class app:

    def __init__(self):
        self.settings()
        self.root = tkinter.Tk()
        self.root.geometry("800x600")
        self.root.title("Password Manager")
        self.root.config(bg="#3e4142")
        self.widgets()
        self.root.mainloop()


    def password_input(self):
        file = filedialog.askopenfilename(title="Choose your password text file")
        self.db_decryption_key = open(file,"r").read()
        return file

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
                try:
                    self.db_decryption_key = open(json_settings_["key_path"], "r").read()
                except FileNotFoundError:
                    json_settings_["key_path"] = self.password_input()

                self.database = DPManager(json_settings_["database_name"],self.db_decryption_key)
                self.database.load_database()

                with open("dpm_settings.json", "w") as file:
                        json.dump(json_settings_,file)
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Database not found. New one was created.")
            json_settings["key_path"] = self.password_input()
            with open("dpm_settings.json", "w") as file:
                json.dump(json_settings,file,indent=2)

            self.database = DPManager(json_settings["database_name"], self.db_decryption_key)
            self.database.create_database()
            self.database.load_database()

    def add_credentials_window(self):
        root = tkinter.Toplevel(self.root)
        root.geometry("300x100")
        root.resizable(False,False)
        root.title("Add credentials")

        url = tkinter.Entry(root,font=30)
        tkinter.Label(root,font=30,text="URL: ").grid(row=1,column=0)
        url.grid(row=1,column=1)

        username = tkinter.Entry(root,font=30)
        tkinter.Label(root, text="Username: ",font=30).grid(row=2, column=0)
        username.grid(row=2, column=1)

        password = tkinter.Entry(root,font=30,show="*")
        tkinter.Label(root,font=30, text="Password: ").grid(row=3, column=0)
        password.grid(row=3, column=1)

        button = tkinter.Button(root,text="OK",command=lambda: (self.database.add_credentials(url.get(),username.get(), password.get()),self.refresh_listview("refresh"),root.destroy()))
        button.grid(row=4,columnspan=3,column=0)

    def refresh_listview(self,function_db,additional = ""):
        self.database.load_database()
        if function_db == "refresh":
            credentials = self.database.list_all_credentials()
        elif function_db == "search":
            credentials = self.database.search_through_credentials(additional)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for credential in credentials:
            self.tree.insert('', tkinter.END, values=credential)

    def widgets(self):
        columns = ("id","url","username","password")

        search_frame = tkinter.Frame(self.root,bg="#2C3136")
        search_frame.pack(side=tkinter.TOP,fill=tkinter.X)
        searchbar_text = tkinter.StringVar()
        search_button = tkinter.Button(search_frame,text="Search",font=36,bg="green",borderwidth=-1,fg="white",command= lambda : self.refresh_listview("search",searchbar_text.get()))
        search_button.pack(side=tkinter.RIGHT)
        searchbar = tkinter.Entry(search_frame,bg="#2C3136",font=36,fg="white",borderwidth=-1,textvariable=searchbar_text,width=564) #width 564 because im too retarded to find a fix for this
        searchbar.pack(side=tkinter.LEFT,fill=tkinter.X)


        treeview_frame = tkinter.Frame(self.root)
        treeview_frame.pack(fill=tkinter.X, side=tkinter.TOP)
        self.tree = ttk.Treeview(treeview_frame, columns=columns, show="headings")
        scrollbar_treeview = ttk.Scrollbar(treeview_frame,orient="vertical",command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar_treeview.set)
        self.tree.heading('id', text="ID")
        self.tree.heading('url', text='URL')
        self.tree.heading('username', text='Username')
        self.tree.heading('password', text='Password')
        scrollbar_treeview.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tree.pack(fill=tkinter.X, side=tkinter.TOP)

        credentials = self.database.list_all_credentials()
        for credential in credentials:
            self.tree.insert('', tkinter.END, values=credential)

        buttons_frame = tkinter.Frame(self.root,bg="#2C3136",height=566)
        buttons_frame.pack(fill=tkinter.X, anchor="center",side=tkinter.TOP,pady=15)
        add_button = tkinter.Button(buttons_frame,text="Add",command=self.add_credentials_window)
        add_button.pack(side=tkinter.LEFT,expand=True)
        refresh_button = tkinter.Button(buttons_frame, text="Refresh", command=lambda: self.refresh_listview("refresh"))
        refresh_button.pack(side=tkinter.LEFT,expand=True)

gui = app()


