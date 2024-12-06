import tkinter
from tkinter import ttk


class app:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry("600x600")
        self.root.title("Password Manager")
        self.widgets()
        self.root.mainloop()

    def widgets(self):
        columns = ("url","username","password")
        tree = ttk.Treeview(self.root,columns=columns,show="headings")
        tree.heading('url', text='URL')
        tree.heading('username', text='Username')
        tree.heading('password', text='Password')

        contacts = []
        for n in range(1, 100):
            contacts.append((f'{n}', f'{n}', f'email{n}@example.com'))
        for contact in contacts:
            tree.insert('', tkinter.END, values=contact)
        tree.grid(row=0, column=0, sticky='nsew')

gui = app()

