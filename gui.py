import tkinter
from tkinter import ttk
from main import DPManager

class app:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry("600x600")
        self.root.title("Password Manager")
        self.root.config(bg="#3e4142")
        self.widgets()
        self.root.mainloop()

    def widgets(self):
        columns = ("url","username","password")

        search_frame = tkinter.Frame(self.root,bg="#2C3136")
        search_frame.pack(side=tkinter.TOP,fill=tkinter.X)

        search_button = tkinter.Button(search_frame,text="Search",font=36,bg="green",borderwidth=-1,fg="white")
        search_button.pack(side=tkinter.RIGHT)
        searchbar_text = tkinter.StringVar()
        searchbar = tkinter.Entry(search_frame,bg="#2C3136",font=36,fg="white",borderwidth=-1,textvariable=searchbar_text,width=564) #width 564 because im too retarded to find a fix for this
        searchbar.pack(side=tkinter.LEFT,fill=tkinter.X)


        treeview_frame = tkinter.Frame(self.root)
        treeview_frame.pack(fill=tkinter.X, side=tkinter.TOP)
        tree = ttk.Treeview(treeview_frame, columns=columns, show="headings")
        scrollbar_treeview = ttk.Scrollbar(treeview_frame,orient="vertical",command=tree.yview)
        tree.config(yscrollcommand=scrollbar_treeview.set)
        tree.heading('url', text='URL')
        tree.heading('username', text='Username')
        tree.heading('password', text='Password')
        scrollbar_treeview.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        tree.pack(fill=tkinter.X, side=tkinter.TOP)

        contacts = []
        for n in range(1, 100):
            contacts.append((f'{n}', f'{n}', f'email{n}@example.com'))
        for contact in contacts:
            tree.insert('', tkinter.END, values=contact)



gui = app()

