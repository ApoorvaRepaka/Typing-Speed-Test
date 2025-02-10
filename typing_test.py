import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import mysql.connector
from leaderboard import Leaderboard

class TypingTest:
    def __init__(self, root, sentence, username, cursor, connection):
        self.root = root
        self.root.title("Typing Test")
        self.sentence = sentence
        self.correct_sentence = self.sentence.strip()
        self.username = username
        self.cursor = cursor
        self.connection = connection
        
        self.frame = tk.Frame(self.root, bg="black")
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.sentence_label = tk.Label(self.frame, text=self.sentence, bg="black", fg="white")
        self.sentence_label.grid(row=0, column=0, padx=5, pady=5)

        self.input_entry = tk.Entry(self.frame, width=40, font=("Helvetica", 12))
        self.input_entry.grid(row=1, column=0, padx=5, pady=10)
        self.input_entry.bind("<KeyRelease>", self.check_typing)

        self.feedback_label = tk.Label(self.frame, text="", bg="black", fg="white")
        self.feedback_label.grid(row=2, column=0, padx=5, pady=5)

        self.leaderboard_button = tk.Button(self.frame, text="Leaderboard", command=self.display_leaderboard)
        self.leaderboard_button.grid(row=3, column=0, padx=5, pady=5)

        self.start_time = time.time()
        self.word_count = 0
        self.update_wpm()

    def check_typing(self, event):
        typed_text = self.input_entry.get().strip()
        correct_chars = sum(1 for a, b in zip(typed_text, self.correct_sentence) if a == b)
        total_chars = len(self.correct_sentence)
        if typed_text == self.correct_sentence:
            elapsed_time = time.time() - self.start_time
            self.feedback_label.config(text=f"Time: {elapsed_time:.2f} sec, Accuracy: {correct_chars/total_chars:.2%}")
            self.input_entry.config(state="disabled")
            self.update_sentence_count()
            self.save_typing_test_result(elapsed_time, correct_chars, total_chars)
        else:
            accuracy = correct_chars / total_chars
            self.feedback_label.config(text=f"Accuracy: {accuracy:.2%}, Correct: {correct_chars}, Total: {total_chars}")
        self.word_count = len(typed_text.split())

    def update_wpm(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            wpm = (self.word_count / elapsed_time) * 60
            self.feedback_label.config(text=f"WPM: {round(wpm)}")
        self.root.after(1000, self.update_wpm)

    def update_sentence_count(self):
        query = "UPDATE users SET sentence_count = sentence_count + 1 WHERE username = %s"
        try:
            self.cursor.execute(query, (self.username,))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error updating sentence count: {err}")

    def save_typing_test_result(self, elapsed_time, correct_chars, total_chars):
        query = "INSERT INTO test_results (username, sentence, elapsed_time, correct_chars, total_chars) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (self.username, self.sentence, elapsed_time, correct_chars, total_chars))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error saving typing test result: {err}")

    def display_leaderboard(self):
        Leaderboard(self.root, self.cursor)
