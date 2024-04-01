import tkinter as tk
from tkinter import *


class ListBox:
    def __init__(self, master, title, items, multiple=False):
        self.master = master
        self.master.title(title)
        self.master.resizable(True, True)
        self.master.config(width=1000)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.attributes('-topmost', True)
        self.left_frame = Frame(master)
        self.right_frame = Frame(master)
        self.items = items
        self.selected_items = []
        self.multiple = multiple
        # create the listboxes
        self.listbox1 = Listbox(self.left_frame, selectmode=(EXTENDED if multiple else SINGLE))
        self.listbox2 = Listbox(self.right_frame, selectmode=EXTENDED)
        self.scrollbar1 = Scrollbar(self.left_frame, orient=VERTICAL)
        self.scrollbar2 = Scrollbar(self.right_frame, orient=VERTICAL)
        self.scrollbar1.config(command=self.listbox1.yview)
        self.scrollbar2.config(command=self.listbox2.yview)
        # add items to listbox1
        for item in self.items:
            self.listbox1.insert(END, item)
        # create the filter entry 2 and add a trace on its value
        self.filter_entry2 = Entry(self.right_frame)
        self.filter_entry_var2 = tk.StringVar()
        self.filter_entry2.config(textvariable=self.filter_entry_var2)
        self.filter_entry_var2.trace("w", self.filter_listbox2)
        # create the filter entry 1 and add a trace on its value
        self.filter_entry1 = Entry(self.left_frame)
        self.filter_entry_var1 = StringVar()
        self.filter_entry1.config(textvariable=self.filter_entry_var1)
        self.filter_entry_var1.trace("w", self.filter_listbox1)
        # select items that meet the filter by default
        self.filter_listbox1()
        self.filter_listbox2()
        # create the buttons
        self.add_button = Button(self.left_frame, text="Add >>", command=self.add_items, pady=14)
        self.remove_button = Button(self.right_frame, text="<< Remove", command=self.remove_items)
        self.clear_button = Button(self.right_frame, text="Clear", command=self.clear_items)
        # grid layout
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.listbox1.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
        self.listbox2.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
        self.scrollbar1.grid(row=0, column=1, padx=5, pady=3, sticky="ns")
        self.scrollbar2.grid(row=0, column=1, padx=5, pady=3, sticky="ns")
        self.filter_entry1.grid(row=1, column=0, padx=10, pady=10, sticky="we")
        self.filter_entry2.grid(row=1, column=0, padx=10, pady=10, sticky="we")
        self.add_button.grid(row=2, column=0, padx=5, pady=3, sticky="nsew")
        self.remove_button.grid(row=2, column=0, padx=5, pady=3, sticky="nsew")
        self.clear_button.grid(row=3, column=0, padx=5)
        self.master.bind('<Return>', self.add_items)

    def filter_listbox1(self, *args):
        # get the filter text
        filter_text = self.filter_entry_var1.get().lower()

        # clear the selection in listbox1
        self.listbox1.selection_clear(0, tk.END)

        # Clear the listbox
        self.listbox1.delete(0, tk.END)

        # select items that meet the filter and are not in listbox 2
        filtered_items = [item for item in self.items if (filter_text.lower() in item.lower()) and
                          (item.lower() not in list(self.listbox2.get(0, END)))]

        # add items to listbox1
        for item in filtered_items:
            self.listbox1.insert(tk.END, item)

        # select items that are not in listbox2 and that meet the filter
        for index in range(self.listbox1.size()):
            item = self.listbox1.get(index).lower()
            if filter_text in item:
                self.listbox1.selection_set(index)

    def filter_listbox2(self, *args):
        # get the filter text
        filter_text = self.filter_entry_var2.get().lower()

        # clear the selection in listbox1
        self.listbox2.selection_clear(0, tk.END)

        # select items that meet the filter
        for index in range(self.listbox2.size()):
            item = self.listbox2.get(index).lower()
            if filter_text in item:
                self.listbox2.selection_set(index)

    def add_items(self, event=None):
        # first determine if multiple=false if an item is already selected
        if not self.multiple:
            if len(self.selected_items) > 0:
                return
            elif len(self.listbox1.curselection()) > 1:
                return
        # get the selected items from listbox1
        selected = self.listbox1.curselection()
        # add selected items to listbox2
        listbox2_content = list(self.listbox2.get(0, END))
        items = [self.listbox1.get(i) for i in selected]
        listbox2_content.extend(items)
        listbox2_content = sorted(listbox2_content)
        self.listbox2.delete(0, END)
        for i in listbox2_content:
            self.listbox2.insert(tk.END, i)
        for i in reversed(selected):
            self.listbox1.delete(i)
        self.selected_items = self.listbox2.get(0, END)

    def remove_items(self):
        # get the selected items from listbox2
        selected = self.listbox2.curselection()
        # add selected items to listbox2
        listbox1_content = list(self.listbox1.get(0, END))
        items = [self.listbox2.get(i) for i in selected]
        listbox1_content.extend(items)
        listbox1_content = sorted(listbox1_content)
        self.listbox1.delete(0, END)
        for i in listbox1_content:
            self.listbox1.insert(tk.END, i)
        for i in reversed(selected):
            self.listbox2.delete(i)
        self.selected_items = self.listbox2.get(0, END)

    def clear_items(self):
        # get all items from listbox2
        items = list(self.listbox2.get(0, END))
        # add items to listbox1
        listbox1_content = list(self.listbox1.get(0, END))
        listbox1_content.extend(items)
        listbox1_content = sorted(listbox1_content)
        self.listbox1.delete(0, END)
        for i in listbox1_content:
            self.listbox1.insert(tk.END, i)
        for i in reversed(range(len(items))):
            self.listbox2.delete(i)
        self.selected_items = self.listbox2.get(0, END)

    def on_closing(self):
        # Register a callback function for the wm_delete_window protocol.
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def on_window_close(self):
        self.master.quit()
        self.master.destroy()


def select_from_listbox(title='Listbox', items=[], multiple=False):
    root = tk.Tk()
    app = ListBox(root, title, items, multiple)
    root.mainloop()
    selected_items = app.selected_items
    # The selected items will be stored in the 'selected_items' attribute of the ListBoxExample instance.
    if multiple:
        return list(selected_items)
    else:
        return selected_items[0]


if __name__ == "__main__":
    items = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi"]
    print(select_from_listbox(title="What is your fruit?", items=items, multiple=True))
    print(select_from_listbox(title="What is your fruit?", items=items))
    print(select_from_listbox(title="What is your fruit?", items=items))