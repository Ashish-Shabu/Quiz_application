# views/player.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import csv
import winsound
from datetime import datetime
from glob import glob
from functools import partial
from models.player import PlayerManager
from models.question import QuestionManager

class PlayerView:
    def __init__(self, app):
        self.app = app
        self.player_manager = PlayerManager()
        self.question_manager = QuestionManager()
        self.current_player = None
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.selected_subject = ""
    
    def player_portal(self):
        """Handle player portal access"""
        self.app.clear_frame()
        
        player_label = tk.Label(self.app.main_frame, text="Player Portal", font=("Arial", 20, "bold"))
        player_label.pack(pady=20)
        
        register_btn = tk.Button(self.app.main_frame, text="Register", font=("Arial", 14),
                                width=20, command=self.player_register)
        register_btn.pack(pady=10)
        
        login_btn = tk.Button(self.app.main_frame, text="Login", font=("Arial", 14),
                             width=20, command=self.player_login)
        login_btn.pack(pady=10)
        
        help_btn = tk.Button(self.app.main_frame, text="Help", font=("Arial", 14),
                            width=20, command=lambda: self.show_help(2))
        help_btn.pack(pady=10)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.app.show_welcome_screen)
        back_btn.pack(side=tk.BOTTOM, pady=20)
    
    def player_register(self):
        """Show player registration form"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Player Registration", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        form_frame = tk.Frame(self.app.main_frame)
        form_frame.pack(pady=10)
        
        fields = [
            ("Name:", "name"),
            ("Email:", "email"),
            ("Age:", "age"),
            ("Date of Birth (DD/MM/YYYY):", "dob"),
            ("School/College:", "school"),
            ("Phone Number:", "phone")
        ]
        
        self.player_entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 12))
            label.grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            self.player_entries[field_name] = entry
        
        register_btn = tk.Button(self.app.main_frame, text="Register", font=("Arial", 12),
                                command=self.register_player)
        register_btn.pack(pady=10)
        
        self.register_status_label = tk.Label(self.app.main_frame, text="", font=("Arial", 12))
        self.register_status_label.pack(pady=5)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.player_portal)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def register_player(self):
        """Register a new player"""
        player_data = [
            self.player_entries["name"].get().strip(),
            self.player_entries["email"].get().strip(),
            self.player_entries["age"].get().strip(),
            self.player_entries["dob"].get().strip(),
            self.player_entries["school"].get().strip(),
            self.player_entries["phone"].get().strip()
        ]
        
        if not all(player_data):
            self.register_status_label.config(text="All fields are required!", fg="red")
            return
        
        uid = self.player_manager.register_player(player_data)
        
        if uid:
            messagebox.showinfo("Success", 
                              f"Registration Successful!\nYour User ID is: {uid}\nPlease note down your User ID for login.")
            for entry in self.player_entries.values():
                entry.delete(0, tk.END)
            self.player_portal()
    
    def player_login(self):
        """Show player login screen"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Player Login", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        login_frame = tk.Frame(self.app.main_frame)
        login_frame.pack(pady=20)
        
        uid_label = tk.Label(login_frame, text="Enter User ID:", font=("Arial", 12))
        uid_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.player_uid_entry = tk.Entry(login_frame, width=30)
        self.player_uid_entry.grid(row=0, column=1, padx=10, pady=5)
        
        login_btn = tk.Button(self.app.main_frame, text="Login", font=("Arial", 12),
                             command=self.verify_player_login)
        login_btn.pack(pady=10)
        
        self.login_status_label = tk.Label(self.app.main_frame, text="", font=("Arial", 12))
        self.login_status_label.pack(pady=5)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.player_portal)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def verify_player_login(self):
        """Verify player login"""
        uid = self.player_uid_entry.get().strip()
        
        if not uid:
            self.login_status_label.config(text="Please enter a User ID", fg="red")
            return
        
        player = self.player_manager.verify_player(uid)
        
        if player:
            self.current_player = player
            self.show_player_dashboard()
        else:
            self.login_status_label.config(text="Invalid User ID", fg="red")
    
    def show_player_dashboard(self):
        """Show player dashboard"""
        self.app.clear_frame()
        
        welcome_label = tk.Label(self.app.main_frame, 
                               text=f"Welcome, {self.current_player['name']}!", 
                               font=("Arial", 20, "bold"))
        welcome_label.pack(pady=10)
        
        button_frame = tk.Frame(self.app.main_frame)
        button_frame.pack(padx=20, pady=20)
        
        options = [
            ("Play Game", self.play_game),
            ("View Scores", self.view_scores),
            ("Submit Feedback", self.submit_feedback),
            ("Help", lambda: self.show_help(2))
        ]
        
        for i, (text, command) in enumerate(options):
            btn = tk.Button(button_frame, text=text, font=("Arial", 12), width=20, command=command)
            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, padx=10, pady=10)
        
        logout_btn = tk.Button(self.app.main_frame, text="Logout", font=("Arial", 12),
                              command=self.player_portal)
        logout_btn.pack(side=tk.BOTTOM, pady=20)
    
    def play_game(self):
        """Show game selection screen"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Select a Subject", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        subjects = self.question_manager.get_subjects()
        
        if not subjects:
            msg_label = tk.Label(self.app.main_frame, text="No quiz subjects available", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            subject_frame = tk.Frame(self.app.main_frame)
            subject_frame.pack(pady=10, fill=tk.BOTH, expand=True)
            
            subject_listbox = tk.Listbox(subject_frame, font=("Arial", 12), height=10)
            subject_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
            
            scrollbar = ttk.Scrollbar(subject_frame, orient=tk.VERTICAL, command=subject_listbox.yview)
            subject_listbox.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            for subject in subjects:
                subject_listbox.insert(tk.END, subject)
            
            start_btn = tk.Button(self.app.main_frame, text="Start Quiz", font=("Arial", 12),
                                 command=lambda: self.start_quiz(subject_listbox))
            start_btn.pack(pady=10)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_player_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def start_quiz(self, subject_listbox):
        """Start a quiz on the selected subject"""
        selected_indices = subject_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a subject")
            return
        
        selected_subject = subject_listbox.get(selected_indices[0])
        self.questions = self.question_manager.get_questions(selected_subject)
        
        if not self.questions:
            messagebox.showwarning("Warning", "No questions available for this subject")
            return
        
        self.current_question = 0
        self.score = 0
        self.selected_subject = selected_subject
        
        self.show_quiz_question()
    
    def show_quiz_question(self):
        """Show a quiz question"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, 
                             text=f"Quiz: {self.selected_subject}", 
                             font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        progress_label = tk.Label(self.app.main_frame, 
                                text=f"Question {self.current_question+1} of {len(self.questions)}", 
                                font=("Arial", 12))
        progress_label.pack(pady=5)
        
        q = self.questions[self.current_question]
        
        question_frame = tk.Frame(self.app.main_frame)
        question_frame.pack(pady=10, padx=20, fill=tk.X)
        
        question_label = tk.Label(question_frame, 
                                text=q["question"], 
                                font=("Arial", 14), 
                                wraplength=500, 
                                justify=tk.LEFT)
        question_label.pack(anchor=tk.W)
        
        options_frame = tk.Frame(self.app.main_frame)
        options_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.answer_var = tk.StringVar(value="")
        
        for i, option in enumerate(q["options"]):
            option_text = f"{chr(65+i)}. {option}"
            rb = tk.Radiobutton(options_frame, 
                               text=option_text, 
                               variable=self.answer_var, 
                               value=chr(65+i), 
                               font=("Arial", 12), 
                               wraplength=500, 
                               justify=tk.LEFT)
            rb.pack(anchor=tk.W, pady=5)
        
        button_frame = tk.Frame(self.app.main_frame)
        button_frame.pack(pady=20)
        
        submit_btn = tk.Button(button_frame, text="Submit Answer", font=("Arial", 12),
                              command=self.submit_answer)
        submit_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = tk.Button(button_frame, text="Quit Quiz", font=("Arial", 12),
                            command=self.confirm_quit_quiz)
        quit_btn.pack(side=tk.LEFT, padx=10)
    
    def submit_answer(self):
        """Submit the answer for the current question"""
        selected_answer = self.answer_var.get()
        
        if not selected_answer:
            messagebox.showwarning("Warning", "Please select an answer")
            return
        
        correct_answer = self.questions[self.current_question]["answer"]
        
        if selected_answer == correct_answer:
            self.score += 1
            winsound.PlaySound("assets/01.wav", winsound.SND_FILENAME)
        else:
            winsound.PlaySound("assets/02.wav", winsound.SND_FILENAME)
        
        self.current_question += 1
        
        if self.current_question >= len(self.questions):
            self.finish_quiz()
        else:
            self.show_quiz_question()
    
    def confirm_quit_quiz(self):
        """Confirm quitting the quiz"""
        if messagebox.askyesno("Confirm", "Are you sure you want to quit the quiz? Your progress will be lost."):
            self.play_game()
    
    def finish_quiz(self):
        """Finish the quiz and show results"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Quiz Completed!", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        score_label = tk.Label(self.app.main_frame, 
                             text=f"Your Score: {self.score}/{len(self.questions)}", 
                             font=("Arial", 16))
        score_label.pack(pady=10)
        
        percentage = (self.score / len(self.questions)) * 100
        percentage_label = tk.Label(self.app.main_frame, 
                                  text=f"Percentage: {percentage:.2f}%", 
                                  font=("Arial", 16))
        percentage_label.pack(pady=10)
        
        self.save_quiz_result(percentage)
        
        dashboard_btn = tk.Button(self.app.main_frame, text="Back to Dashboard", font=("Arial", 12),
                                 command=self.show_player_dashboard)
        dashboard_btn.pack(pady=20)
    
    def save_quiz_result(self, percentage):
        """Save the quiz result"""
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        if not os.path.isfile('assets/results.csv'):
            with open('assets/results.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["User ID", "Name", "Subject", "Score", "Total", "Percentage", "Date", "Time"])
        
        with open('assets/results.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.current_player["uid"],
                self.current_player["name"],
                self.selected_subject,
                self.score,
                len(self.questions),
                f"{percentage:.2f}%",
                date_str,
                time_str
            ])
    
    def view_scores(self):
        """View player's scores"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Your Scores", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        if not os.path.isfile('assets/results.csv'):
            msg_label = tk.Label(self.app.main_frame, text="No quiz results available", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            results_frame = tk.Frame(self.app.main_frame)
            results_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            columns = ("subject", "score", "total", "percentage", "date", "time")
            tree = ttk.Treeview(results_frame, columns=columns, show="headings")
            
            tree.heading("subject", text="Subject")
            tree.heading("score", text="Score")
            tree.heading("total", text="Total")
            tree.heading("percentage", text="Percentage")
            tree.heading("date", text="Date")
            tree.heading("time", text="Time")
            
            tree.column("subject", width=150)
            tree.column("score", width=80)
            tree.column("total", width=80)
            tree.column("percentage", width=100)
            tree.column("date", width=100)
            tree.column("time", width=100)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            with open('assets/results.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)
                
                results_found = False
                
                for row in reader:
                    if len(row) > 0 and row[0] == self.current_player["uid"]:
                        tree.insert("", tk.END, values=(row[2], row[3], row[4], row[5], row[6], row[7]))
                        results_found = True
                
                if not results_found:
                    msg_label = tk.Label(self.app.main_frame, 
                                        text="No quiz results available for your account", 
                                        font=("Arial", 14))
                    msg_label.pack(pady=20)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_player_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def submit_feedback(self):
        """Show feedback submission form"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Submit Feedback", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        form_frame = tk.Frame(self.app.main_frame)
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        
        rating_label = tk.Label(form_frame, text="Rating (1-5):", font=("Arial", 12))
        rating_label.pack(anchor=tk.W, pady=5)
        
        self.rating_var = tk.StringVar()
        rating_frame = tk.Frame(form_frame)
        rating_frame.pack(fill=tk.X, pady=5)
        
        for i in range(1, 6):
            rb = tk.Radiobutton(rating_frame, text=str(i), variable=self.rating_var, value=str(i), font=("Arial", 12))
            rb.pack(side=tk.LEFT, padx=10)
        
        comments_label = tk.Label(form_frame, text="Comments:", font=("Arial", 12))
        comments_label.pack(anchor=tk.W, pady=5)
        
        self.comments_text = tk.Text(form_frame, height=5, width=50)
        self.comments_text.pack(fill=tk.X, pady=5)
        
        suggestions_label = tk.Label(form_frame, text="Suggestions for Improvement:", font=("Arial", 12))
        suggestions_label.pack(anchor=tk.W, pady=5)
        
        self.suggestions_text = tk.Text(form_frame, height=5, width=50)
        self.suggestions_text.pack(fill=tk.X, pady=5)
        
        submit_btn = tk.Button(self.app.main_frame, text="Submit Feedback", font=("Arial", 12),
                              command=self.save_feedback)
        submit_btn.pack(pady=10)
        
        self.feedback_status_label = tk.Label(self.app.main_frame, text="", font=("Arial", 12))
        self.feedback_status_label.pack(pady=5)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_player_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def save_feedback(self):
        """Save player feedback"""
        rating = self.rating_var.get()
        comments = self.comments_text.get("1.0", tk.END).strip()
        suggestions = self.suggestions_text.get("1.0", tk.END).strip()
        
        if not rating:
            self.feedback_status_label.config(text="Please provide a rating", fg="red")
            return
        
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        if not os.path.isfile('assets/feedbacks.csv'):
            with open('assets/feedbacks.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["User ID", "Name", "Rating", "Comments", "Suggestions", "Date", "Time"])
        
        with open('assets/feedbacks.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.current_player["uid"],
                self.current_player["name"],
                rating,
                comments,
                suggestions,
                date_str,
                time_str
            ])
        
        self.feedback_status_label.config(text="Feedback submitted successfully!", fg="green")
        self.rating_var.set("")
        self.comments_text.delete("1.0", tk.END)
        self.suggestions_text.delete("1.0", tk.END)
    
    def show_help(self, user_type):
        """Show help information"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Help", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        help_text = tk.Text(self.app.main_frame, wrap=tk.WORD, height=20, width=70)
        help_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.app.main_frame, orient=tk.VERTICAL, command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if user_type == 1:  # Admin
            help_content = """
Admin Help:

1. Player Details: View registered player information, search by name or ID.
2. Reports: Access game results and reports, search by player name or ID.
3. View Feedbacks: Read user feedbacks.
4. Quiz Questions: Add, update, or view quiz questions by subject.
5. See Admin Password: View the current admin password.
6. Change Admin Password: Change the admin password and recovery key.
7. About Us: View information about the quiz game.

For password recovery, use the recovery key you set up during password creation.
"""
        else:  # Player
            help_content = """
Player Help:

1. Register: Create a player profile with your details.
2. Login: Access the game with your user ID.
3. Play Game: Select a subject and answer quiz questions.
4. View Score: Check your scores after completing a quiz.
5. Feedback: Share your thoughts about the game.

Game Rules:
- Each correct answer earns 1 point.
- There's no negative marking for incorrect answers.
- Try to answer all questions within the time limit.
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_player_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)