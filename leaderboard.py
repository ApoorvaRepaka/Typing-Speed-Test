import tkinter as tk
from tkinter import ttk

class Leaderboard:
    def __init__(self, root, cursor):
        self.root = root
        self.cursor = cursor
        self.page = 0
        self.page_size = 10

        self.frame = tk.Frame(self.root, bg="black")
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.search_label = tk.Label(self.frame, text="Search:", bg="black", fg="white")
        self.search_label.grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(self.frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_button = tk.Button(self.frame, text="Search", command=self.search)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.columns = ("ID", "Username", "Sentence Count")
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show="headings")
        self.tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        for col in self.columns:
            self.tree.heading(col, text=col)

        self.prev_button = tk.Button(self.frame, text="Previous", command=self.prev_page)
        self.prev_button.grid(row=2, column=0, padx=5, pady=5)
        self.next_button = tk.Button(self.frame, text="Next", command=self.next_page)
        self.next_button.grid(row=2, column=2, padx=5, pady=5)

        self.load_leaderboard()

    def load_leaderboard(self, search_term=""):
        query = "SELECT id, username, sentence_count FROM users"
        if search_term:
            query += " WHERE username LIKE %s"
            self.cursor.execute(query, (f"%{search_term}%",))
        else:
            query += " ORDER BY sentence_count DESC LIMIT %s OFFSET %s"
            self.cursor.execute(query, (self.page_size, self.page * self.page_size))

        leaderboard = self.cursor.fetchall()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, (user_id, username, sentence_count) in enumerate(leaderboard, start=1):
            self.tree.insert("", "end", values=(user_id, username, sentence_count))

    def search(self):
        search_term = self.search_entry.get()
        self.page = 0
        self.load_leaderboard(search_term)

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_leaderboard()

    def next_page(self):
        self.page += 1
        self.load_leaderboard()
