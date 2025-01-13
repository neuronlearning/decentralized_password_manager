import tkinter
from tkinter import ttk, messagebox,filedialog
from dpmanager import DPManager
import json
import threading
import os

class app:

    def __init__(self):
        self.root = tkinter.Tk()
        self.settings()
        self.root.geometry("800x600")
        self.root.title("Password Manager")
        self.root.config(bg="#3e4142")
        self.root.mainloop()


    def password_check(self,window_object,password,exists,database_name = ""):
        if exists:
            self.database.set_encryption_key(password)
            try:
                self.database.load_database()
                self.widgets()
                window_object.destroy()
            except ValueError:
                messagebox.showerror("Error", "Wrong password")
        else:
            try:
                self.database.set_db_name(database_name),
                self.database.set_encryption_key(password),
                self.database.create_database(),
                self.database.load_database(),
                open("dpm_settings.json", "w").write(json.dumps({
                    "database": f"{database_name}.db",
                    "database_name": f"{database_name}"
                })),
                self.widgets()
                window_object.destroy()
            except ValueError:
                messagebox.showerror("Error", "Wrong password")


    def password_input(self,exists):
        #file = filedialog.askopenfilename(title="Choose your password text file")
        #self.db_decryption_key = open(file,"r").read()
        #return file
        pass_w = tkinter.Toplevel(self.root)
        pass_w.geometry("300x100")
        pass_w.resizable(False, False)
        pass_w.title("Enter password")
        password_label = tkinter.Label(pass_w,text="Password:",font=30)
        password_label.grid(row=0,column=0)
        password_input = tkinter.Entry(pass_w,font=30,show="*")
        password_input.grid(row=0,columnspan=2,column=1)
        if exists:
            ok_button = tkinter.Button(pass_w,text="Enter",font=20,command=lambda : self.password_check(pass_w,password_input.get(),True))
            ok_button.grid(row=1,columnspan=2,column=1,pady=5)
        else:
            database_label = tkinter.Label(pass_w, text="Database name:", font=30)
            database_label.grid(row=1, column=0)
            database_input = tkinter.Entry(pass_w, font=30)
            database_input.grid(row=1, columnspan=2, column=1)
            ok_button = tkinter.Button(pass_w, text="Enter", font=20, command=lambda: self.password_check(pass_w,password_input.get(),False,database_input.get()))
            ok_button.grid(row=2, columnspan=2, column=1, pady=5)


    def settings(self):
        json_settings = {  # more are on the way tm
            "database": "default_user.db",
            "database_name": "default_user"
        }
        try:
            with open("dpm_settings.json", "r") as file:
                setting = file.read()
                setting = json.loads(setting)
                self.database = DPManager(setting["database"])
                self.password_input(exists=True)

        except FileNotFoundError:
            not_found = messagebox.askyesno("Warning", "The database file was not found. Do you have an already existing one?")
            if not_found:
                database_path = filedialog.askopenfilename(title="Choose database file")

                with open(database_path, "rb") as file:
                    dat = file.read()
                    with open(os.path.basename(database_path), "wb") as file2:
                        file2.write(dat)
                    open("dpm_settings.json", "w").write(json.dumps({
                        "database" : os.path.basename(database_path),
                        "database_name": os.path.basename(database_path)[:-3]
                    })),

                self.database = DPManager(os.path.basename(database_path))
                self.password_input(exists=True)
            else:
                self.database = DPManager()
                self.password_input(exists=False)


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

        button = tkinter.Button(root,text="OK",command=lambda: (self.refresh_listview("add",[url.get(),username.get(),password.get()]),root.destroy()))
        button.grid(row=4,columnspan=3,column=0)

    def change_credentials_window(self):
        root = tkinter.Toplevel(self.root)
        root.geometry("300x100")
        root.resizable(False, False)
        root.title("Update credentials")

        username = tkinter.Entry(root, font=30)
        tkinter.Label(root, text="Username: ", font=30).grid(row=2, column=0)
        username.grid(row=2, column=1)

        password = tkinter.Entry(root, font=30, show="*")
        tkinter.Label(root, font=30, text="Password: ").grid(row=3, column=0)
        password.grid(row=3, column=1)

        button = tkinter.Button(root, text="OK", command=lambda: (self.refresh_listview("change", [self.tree.item(self.tree.focus())["values"][0],username.get(), password.get()]), root.destroy()))
        button.grid(row=4, columnspan=3, column=0)

    def refresh_listview(self,function_db,additional = []):
        if function_db == "refresh":
            credentials = self.database.list_all_credentials()
        elif function_db == "search":
            credentials = self.database.search_through_credentials(additional)
        elif function_db == "delete":
            try:
                self.database.remove_credentials_by_id(additional[0])
                credentials = self.database.list_all_credentials()
            except IndexError:
                messagebox.showwarning("Warning", "You must first select the credential before removing it.")
                credentials = self.database.list_all_credentials()
        elif function_db == "add":
            self.database.add_credentials(additional[0],additional[1],additional[2])
            credentials = self.database.list_all_credentials()
        elif function_db == "change":
            self.database.update_credentials_by_id(additional[0],additional[1],additional[2])
            credentials = self.database.list_all_credentials()

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
        delete_button = tkinter.Button(buttons_frame, text="Delete", command=lambda: self.refresh_listview("delete",self.tree.item(self.tree.focus())["values"]))
        delete_button.pack(side=tkinter.LEFT, expand=True)
        change_button = tkinter.Button(buttons_frame, text="Change", command=self.change_credentials_window)
        change_button.pack(side=tkinter.LEFT, expand=True)

gui = app()


