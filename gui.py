import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import connect_to_database
from authentication import hash_password, check_password
from typing_test import TypingTest
import time
import random
import mysql

class TypingSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.geometry("800x600")
        self.center_window()
        
        self.background_image = Image.open("assets/bg.jpg")
        self.background_image = self.background_image.resize((800, 600), Image.NEAREST)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.loading_bar = ttk.Progressbar(root, mode="determinate", length=600)
        self.loading_bar.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        self.loading_animation()
    def center_window(self):
        self.root.update_idletasks()
        width = 800
        height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
    def loading_animation(self):
        for i in range(100):
            self.loading_bar["value"] = i
            self.root.update_idletasks()
            time.sleep(0.02)

        self.loading_bar.destroy()
        self.login_page = LoginPage(self.root)

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.connection, self.cursor = connect_to_database()

        self.frame = tk.Frame(self.root, bg="black")
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.username_label = tk.Label(self.frame, text="Username:", bg="black", fg="white")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.frame, text="Password:", bg="black", fg="white")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.signup_button = tk.Button(self.frame, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        self.reset_button = tk.Button(self.frame, text="Reset Password", command=self.reset_password)
        self.reset_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.logged_in = False

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        query = "SELECT * FROM users WHERE username = %s"
        self.cursor.execute(query, (username,))
        user = self.cursor.fetchone()
        if user and check_password(user[2], password):
            messagebox.showinfo("Login", "Login Successful")
            self.frame.destroy()
            self.show_start_and_logout_buttons(username)
            self.logged_in = True
        else:
            messagebox.showerror("Login", "Invalid username or password")

    def signup(self):
        SignupPage(self.root, self.connection, self.cursor)

    def reset_password(self):
        ResetPasswordPage(self.root, self.connection, self.cursor)

    def show_start_and_logout_buttons(self, username):
        start_button = tk.Button(self.root, text="Start", command=lambda: self.start_typing_test(username))
        start_button.pack()

        logout_button = tk.Button(self.root, text="Logout", command=self.logout)
        logout_button.pack()

    def start_typing_test(self, username):
        if self.logged_in:
            sentence = random.choice(open("sentences.txt").read().split("\n"))
            TypingTest(self.root, sentence, username, self.cursor, self.connection)
        else:
            messagebox.showerror("Error", "Please login to start the typing test.")
    
    def get_random_sentence(self):
        with open("sentences.txt", "r") as file:
            sentences = file.readlines()
        return random.choice(sentences).strip()
    def logout(self):
        for widget in self.root.winfo_children():
            if widget.winfo_y() > 0:
                widget.destroy()
        self.__init__(self.root)
class SignupPage:
    def __init__(self, root, connection, cursor):
        self.root = root
        self.root.title("Sign Up")
        self.connection = connection
        self.cursor = cursor

        self.frame = tk.Frame(self.root, bg="black")
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.username_label = tk.Label(self.frame, text="Username:", bg="black", fg="white")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.frame, text="Password:", bg="black", fg="white")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.confirm_password_label = tk.Label(self.frame, text="Confirm Password:", bg="black", fg="white")
        self.confirm_password_label.grid(row=2, column=0, padx=5, pady=5)
        self.confirm_password_entry = tk.Entry(self.frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        self.signup_button = tk.Button(self.frame, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if password != confirm_password:
            messagebox.showerror("Sign Up", "Passwords do not match")
            return

        hashed_password = hash_password(password)
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (username, hashed_password))
            self.connection.commit()
            messagebox.showinfo("Sign Up", "Account created successfully")
            self.frame.destroy()
            LoginPage(self.root)
        except mysql.connector.Error as err:
            messagebox.showerror("Sign Up", f"Error: {err}")

class ResetPasswordPage:
    def __init__(self, root, connection, cursor):
        self.root = root
        self.root.title("Reset Password")
        self.connection = connection
        self.cursor = cursor

        self.frame = tk.Frame(self.root, bg="black")
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.username_label = tk.Label(self.frame, text="Username:", bg="black", fg="white")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.new_password_label = tk.Label(self.frame, text="New Password:", bg="black", fg="white")
        self.new_password_label.grid(row=1, column=0, padx=5, pady=5)
        self.new_password_entry = tk.Entry(self.frame, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.confirm_password_label = tk.Label(self.frame, text="Confirm Password:", bg="black", fg="white")
        self.confirm_password_label.grid(row=2, column=0, padx=5, pady=5)
        self.confirm_password_entry = tk.Entry(self.frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        self.reset_button = tk.Button(self.frame, text="Reset Password", command=self.reset_password)
        self.reset_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def reset_password(self):
        username = self.username_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if new_password != confirm_password:
            messagebox.showerror("Reset Password", "Passwords do not match")
            return

        reset_password(username, new_password, self.cursor, self.connection)
        messagebox.showinfo("Reset Password", "Password reset successfully")
        self.frame.destroy()
        LoginPage(self.root)