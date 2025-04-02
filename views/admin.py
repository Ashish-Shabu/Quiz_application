# views/admin.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
import json
import csv
import winsound
from datetime import datetime
from glob import glob
from models.auth import AuthManager

class AdminView:
    def __init__(self, app):
        self.app = app
        self.auth = AuthManager()
        self.admin_attempts = 0
    
    def admin_portal(self):
        """Handle admin portal access"""
        self.app.clear_frame()
        
        # Add a label
        admin_label = tk.Label(self.app.main_frame, text="Admin Portal", font=("Arial", 20, "bold"))
        admin_label.pack(pady=20)
        
        # Check if admin password file exists
        if not os.path.isfile('assets/psd.bin') or os.path.getsize('assets/psd.bin') == 0:
            self.create_admin_password()
        else:
            self.admin_login()
    
    def create_admin_password(self):
        """Create the admin password"""
        self.app.clear_frame()
        
        # Add a label
        title_label = tk.Label(self.app.main_frame, text="Admin Profile Creation", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        instructions = "Use 6 or more characters with a mix of letters, numbers & symbols"
        instruction_label = tk.Label(self.app.main_frame, text=instructions, font=("Arial", 12))
        instruction_label.pack(pady=10)
        
        # Password entry fields
        password_frame = tk.Frame(self.app.main_frame)
        password_frame.pack(pady=10)
        
        password_label = tk.Label(password_frame, text="Create password:", font=("Arial", 12))
        password_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.password_entry = tk.Entry(password_frame, show="*", width=30)
        self.password_entry.grid(row=0, column=1, padx=10, pady=5)
        
        confirm_label = tk.Label(password_frame, text="Confirm password:", font=("Arial", 12))
        confirm_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.confirm_entry = tk.Entry(password_frame, show="*", width=30)
        self.confirm_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Recovery key
        recovery_label = tk.Label(password_frame, text="Recovery key:", font=("Arial", 12))
        recovery_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.recovery_entry = tk.Entry(password_frame, width=30)
        self.recovery_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Order entry
        order_label = tk.Label(password_frame, 
                             text="For more protection enter an order from the interval [4,32]:", 
                             font=("Arial", 12))
        order_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.order_entry = tk.Entry(password_frame, width=30)
        self.order_entry.grid(row=3, column=1, padx=10, pady=5)
        self.order_entry.insert(0, "9")  # Default value
        
        # Submit button
        submit_btn = tk.Button(self.app.main_frame, text="Create Password", font=("Arial", 12),
                              command=self.save_admin_password)
        submit_btn.pack(pady=20)
        
        # Status message
        self.status_label = tk.Label(self.app.main_frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)
    
    def save_admin_password(self):
        """Save the admin password"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        hint = self.recovery_entry.get()
        
        try:
            k = int(self.order_entry.get())
        except ValueError:
            self.status_label.config(text="Invalid order! Please enter a number.", fg="red")
            winsound.Beep(440, 500)
            return
        
        if password != confirm:
            self.status_label.config(text="Passwords don't match. Try again.", fg="red")
            return
        
        if not self.auth.psdvalid(password):
            self.status_label.config(text="Invalid Password! Must be 6+ characters with letters, numbers & symbols.", fg="red")
            return
        
        if k <= 0:
            self.status_label.config(text="Invalid order! Using default value 9.", fg="red")
            winsound.Beep(440, 500)
            k = 9
        
        # Save the password
        if self.auth.save_password(password, hint, k):
            messagebox.showinfo("Success", "Password entered successfully!")
            self.admin_login()
    
    def admin_login(self):
        """Admin login screen"""
        self.app.clear_frame()
        
        # Add a label
        login_label = tk.Label(self.app.main_frame, text="Admin Login", font=("Arial", 18, "bold"))
        login_label.pack(pady=20)
        
        # Password entry
        password_frame = tk.Frame(self.app.main_frame)
        password_frame.pack(pady=10)
        
        password_label = tk.Label(password_frame, text="Enter admin password:", font=("Arial", 12))
        password_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.admin_password_entry = tk.Entry(password_frame, show="*", width=30)
        self.admin_password_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Login button
        login_btn = tk.Button(self.app.main_frame, text="Login", font=("Arial", 12),
                             command=self.verify_admin_login)
        login_btn.pack(pady=20)
        
        # Status message
        self.login_status_label = tk.Label(self.app.main_frame, text="", font=("Arial", 12))
        self.login_status_label.pack(pady=10)
        
        # Back button
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.app.show_welcome_screen)
        back_btn.pack(side=tk.BOTTOM, pady=20)
        
        # Track login attempts
        self.admin_attempts = 0
    
    def verify_admin_login(self):
        """Verify admin login credentials"""
        password = self.admin_password_entry.get()
        admin_pass, hint = self.auth.pcheck()
        
        if password == admin_pass:
            winsound.PlaySound("assets/07.wav", winsound.SND_FILENAME)
            self.show_admin_dashboard()
        else:
            self.admin_attempts += 1
            remaining = 5 - self.admin_attempts
            
            if remaining <= 0:
                self.login_status_label.config(text="No attempts left!", fg="red")
                # Show recovery option
                recover = messagebox.askyesno("Recovery", "Forgot your password?")
                if recover:
                    self.show_admin_recovery(hint)
            else:
                self.login_status_label.config(text=f"Wrong password! Attempts remaining: {remaining}", fg="red")
                winsound.PlaySound("assets/06.wav", winsound.SND_FILENAME)
    
    def show_admin_recovery(self, hint):
        """Show admin password recovery screen"""
        recovery_key = simpledialog.askstring("Recovery", "Enter your recovery key:")
        if recovery_key == hint:
            messagebox.showinfo("Success", "Recovery key verified. Create a new password.")
            self.create_admin_password()
        else:
            messagebox.showerror("Error", "Incorrect recovery key!")
    
    def show_admin_dashboard(self):
        """Show the admin dashboard"""
        self.app.clear_frame()
        
        # Add a label
        dashboard_label = tk.Label(self.app.main_frame, text="Admin Dashboard", font=("Arial", 20, "bold"))
        dashboard_label.pack(pady=10)
        
        # Create a frame for buttons
        button_frame = tk.Frame(self.app.main_frame)
        button_frame.pack(padx=20, pady=20)
        
        # Create buttons
        options = [
            ("Player Details", self.show_player_details),
            ("Reports", self.show_reports),
            ("View Feedbacks", self.view_feedbacks),
            ("Quiz Questions", self.manage_quiz_questions),
            ("See Admin Password", self.show_admin_password),
            ("Change Admin Password", self.change_admin_password),
            ("Help", lambda: self.show_help(1)),
            ("About Us", self.show_about)
        ]
        
        for i, (text, command) in enumerate(options):
            btn = tk.Button(button_frame, text=text, font=("Arial", 12), width=20, command=command)
            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, padx=10, pady=10)
        
        # Logout button
        logout_btn = tk.Button(self.app.main_frame, text="Logout", font=("Arial", 12),
                              command=self.app.show_welcome_screen)
        logout_btn.pack(side=tk.BOTTOM, pady=20)
    
    def show_player_details(self):
        """Show player details"""
        self.app.clear_frame()
        
        # Add a title
        title_label = tk.Label(self.app.main_frame, text="Player Details", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Check if there are registered players
        if not os.path.isfile('assets/details.csv') or os.path.getsize('assets/details.csv') == 0:
            msg_label = tk.Label(self.app.main_frame, text="No one has registered yet", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            # Create option frame
            option_frame = tk.Frame(self.app.main_frame)
            option_frame.pack(pady=10)
            
            # Create buttons
            search_name_btn = tk.Button(option_frame, text="Search by Name", font=("Arial", 12),
                                        command=lambda: self.search_player(1, 1))
            search_name_btn.grid(row=0, column=0, padx=10, pady=5)
            
            search_id_btn = tk.Button(option_frame, text="Search by User ID", font=("Arial", 12),
                                     command=lambda: self.search_player(1, 2))
            search_id_btn.grid(row=0, column=1, padx=10, pady=5)
            
            list_all_btn = tk.Button(option_frame, text="List All Players", font=("Arial", 12),
                                    command=lambda: self.list_players(1))
            list_all_btn.grid(row=0, column=2, padx=10, pady=5)
            
            # Create a frame for results
            self.results_frame = tk.Frame(self.app.main_frame)
            self.results_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Back button
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_admin_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def search_player(self, type_idx, search_type):
        """Search for a player by name or ID"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Create search frame
        search_frame = tk.Frame(self.results_frame)
        search_frame.pack(pady=10)
        
        search_label = tk.Label(search_frame, 
                              text=f"Enter the {'Name' if search_type == 1 else 'User ID'} to search:", 
                              font=("Arial", 12))
        search_label.grid(row=0, column=0, padx=10, pady=5)
        
        search_entry = tk.Entry(search_frame, width=30)
        search_entry.grid(row=0, column=1, padx=10, pady=5)
        
        search_btn = tk.Button(search_frame, text="Search", font=("Arial", 12),
                              command=lambda: self.execute_search(type_idx, search_type, search_entry.get()))
        search_btn.grid(row=0, column=2, padx=10, pady=5)
    
    def execute_search(self, type_idx, search_type, search_term):
        """Execute the player search"""
        # Clear previous results but keep the search frame
        for widget in self.results_frame.winfo_children()[1:]:
            widget.destroy()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        
        # Create a text widget to display results
        result_text = tk.Text(self.results_frame, wrap=tk.WORD, height=15, width=70)
        result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        found = False
        
        if type_idx == 1:  # Player details
            with open('assets/details.csv', 'r') as filein:
                reader = csv.reader(filein)
                for row in reader:
                    if len(row) < 7:  # Skip header or incomplete rows
                        continue
                    uid, name, email, age, dob, school, pno = row
                    if row[1 if search_type == 1 else 0] == search_term:
                        found = True
                        result_text.insert(tk.END, f"User ID: {uid}\n")
                        result_text.insert(tk.END, f"Player Name: {name}\n")
                        result_text.insert(tk.END, f"Email: {email}\n")
                        result_text.insert(tk.END, f"Age: {age}\n")
                        result_text.insert(tk.END, f"DOB: {dob}\n")
                        result_text.insert(tk.END, f"School: {school}\n")
                        result_text.insert(tk.END, f"Phone Number: {pno}\n")
                        result_text.insert(tk.END, "-" * 50 + "\n")
        else:  # Game results
            with open('assets/results.csv', 'r') as filein:
                reader = csv.reader(filein)
                for row in reader:
                    if len(row) < 6:  # Skip header or incomplete rows
                        continue
                    uid, name, c, ic, score, p = row[:6]
                    if row[1 if search_type == 1 else 0] == search_term:
                        found = True
                        result_text.insert(tk.END, f"User ID: {uid}\n")
                        result_text.insert(tk.END, f"Player Name: {name}\n")
                        result_text.insert(tk.END, f"No of correct answers: {c}\n")
                        result_text.insert(tk.END, f"No of incorrect answers: {ic}\n")
                        result_text.insert(tk.END, f"Total Score: {score}\n")
                        result_text.insert(tk.END, f"Percentage: {p}\n")
                        result_text.insert(tk.END, "-" * 50 + "\n")
        
        result_text.config(state=tk.DISABLED)
        
        if not found:
            messagebox.showinfo("Result", "No matching records found.")
    
    def list_players(self, type_idx):
        """List all players or results"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Create a frame for the treeview
        tree_frame = tk.Frame(self.results_frame)
        tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        if type_idx == 1:  # Player details
            columns = ("User ID", "Player Name", "Email ID", "Player Age", "Date Of Birth", "School Name", "Phone Number")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            with open('assets/details.csv', 'r') as filein:
                reader = csv.reader(filein)
                next(reader)
                for row in reader:
                    if len(row) >= 7:
                        tree.insert("", tk.END, values=row)
        else:  # Game results
            columns = ("User ID", "Player Name", "No of Questions", "Correct", "Incorrect", "Total Score", "Percentage")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            with open('assets/results.csv', 'r') as filein:
                reader = csv.reader(filein)
                next(reader)
                for row in reader:
                    if len(row) >= 7:
                        tree.insert("", tk.END, values=row)
    
    def show_reports(self):
        """Show game reports"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Game Reports", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        if not os.path.isfile('assets/results.csv') or os.path.getsize('assets/results.csv') == 0:
            msg_label = tk.Label(self.app.main_frame, text="No one has played this game yet", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            option_frame = tk.Frame(self.app.main_frame)
            option_frame.pack(pady=10)
            
            search_name_btn = tk.Button(option_frame, text="Search by Name", font=("Arial", 12),
                                       command=lambda: self.search_player(2, 1))
            search_name_btn.grid(row=0, column=0, padx=10, pady=5)
            
            search_id_btn = tk.Button(option_frame, text="Search by User ID", font=("Arial", 12),
                                     command=lambda: self.search_player(2, 2))
            search_id_btn.grid(row=0, column=1, padx=10, pady=5)
            
            list_all_btn = tk.Button(option_frame, text="List All Results", font=("Arial", 12),
                                    command=lambda: self.list_players(2))
            list_all_btn.grid(row=0, column=2, padx=10, pady=5)
            
            self.results_frame = tk.Frame(self.app.main_frame)
            self.results_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_admin_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def view_feedbacks(self):
        """View user feedbacks"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="User Feedbacks", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        if not os.path.isfile('assets/feedbacks.csv') or os.path.getsize('assets/feedbacks.csv') == 0:
            msg_label = tk.Label(self.app.main_frame, text="No feedbacks yet", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            feedback_text = tk.Text(self.app.main_frame, wrap=tk.WORD, height=20, width=70)
            feedback_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(self.app.main_frame, orient=tk.VERTICAL, command=feedback_text.yview)
            feedback_text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            with open('assets/feedbacks.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    feedback_text.insert(tk.END, f"* {row}\n")
            feedback_text.config(state=tk.DISABLED)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_admin_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def manage_quiz_questions(self):
        """Manage quiz questions"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Quiz Questions Management", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        subjects = [r[7:-5] for r in glob("assets/*.json")]
        
        option_frame = tk.Frame(self.app.main_frame)
        option_frame.pack(pady=10)
        
        add_btn = tk.Button(option_frame, text="Add New Questions", font=("Arial", 12),
                           command=lambda: self.show_add_questions(subjects))
        add_btn.grid(row=0, column=0, padx=10, pady=5)
        
        update_btn = tk.Button(option_frame, text="Update Questions", font=("Arial", 12),
                              command=lambda: self.show_update_questions(subjects))
        update_btn.grid(row=0, column=1, padx=10, pady=5)
        
        view_btn = tk.Button(option_frame, text="View Questions", font=("Arial", 12),
                            command=lambda: self.show_view_questions(subjects))
        view_btn.grid(row=0, column=2, padx=10, pady=5)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_admin_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def show_add_questions(self, subjects):
        """Show add questions screen"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Add New Questions", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        subject_frame = tk.Frame(self.app.main_frame)
        subject_frame.pack(pady=10)
        
        subject_label = tk.Label(subject_frame, text="Select or Enter New Subject:", font=("Arial", 12))
        subject_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.subject_var = tk.StringVar()
        
        if subjects:
            subject_dropdown = ttk.Combobox(subject_frame, textvariable=self.subject_var, values=subjects, width=30)
            subject_dropdown.grid(row=0, column=1, padx=10, pady=5)
        else:
            subject_entry = tk.Entry(subject_frame, textvariable=self.subject_var, width=30)
            subject_entry.grid(row=0, column=1, padx=10, pady=5)
        
        question_frame = tk.Frame(self.app.main_frame)
        question_frame.pack(pady=10, padx=20, fill=tk.X)
        
        question_label = tk.Label(question_frame, text="Question:", font=("Arial", 12))
        question_label.pack(anchor=tk.W)
        
        self.question_text = tk.Text(question_frame, height=3, width=60)
        self.question_text.pack(fill=tk.X, pady=5)
        
        options_frame = tk.Frame(self.app.main_frame)
        options_frame.pack(pady=10, padx=20, fill=tk.X)
        
        options_label = tk.Label(options_frame, text="Options (with A, B, C, D initials):", font=("Arial", 12))
        options_label.pack(anchor=tk.W)
        
        self.option_entries = []
        for i in range(4):
            option_label = tk.Label(options_frame, text=f"Option {chr(65+i)}:", font=("Arial", 12))
            option_label.pack(anchor=tk.W)
            
            option_entry = tk.Entry(options_frame, width=60)
            option_entry.pack(fill=tk.X, pady=2)
            option_entry.insert(0, f"{chr(65+i)}. ")
            self.option_entries.append(option_entry)
        
        answer_frame = tk.Frame(self.app.main_frame)
        answer_frame.pack(pady=10, padx=20, fill=tk.X)
        
        answer_label = tk.Label(answer_frame, text="Correct Answer:", font=("Arial", 12))
        answer_label.pack(side=tk.LEFT, padx=5)
        
        self.answer_var = tk.StringVar(value="")
        answers = ["A", "B", "C", "D"]
        for ans in answers:
            rb = tk.Radiobutton(answer_frame, text=ans, variable=self.answer_var, value=ans, font=("Arial", 12))
            rb.pack(side=tk.LEFT, padx=10)
        
        add_btn = tk.Button(self.app.main_frame, text="Add Question", font=("Arial", 12),
                           command=self.add_question)
        add_btn.pack(pady=10)
        
        self.add_status_label = tk.Label(self.app.main_frame, text="", font=("Arial", 12))
        self.add_status_label.pack(pady=5)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.manage_quiz_questions)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def add_question(self):
        """Add a new question to the subject"""
        subject = self.subject_var.get().strip()
        question = self.question_text.get("1.0", tk.END).strip()
        options = [entry.get().strip() for entry in self.option_entries]
        answer = self.answer_var.get()
        
        if not subject or not question or not all(options):
            self.add_status_label.config(text="All fields are required!", fg="red")
            return
        
        filename = f"assets/{subject}.json"
        
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                questions = json.load(f)
        else:
            questions = []
        
        new_question = {
            "question": question,
            "options": options,
            "answer": answer
        }
        
        questions.append(new_question)
        
        with open(filename, 'w') as f:
            json.dump(questions, f, indent=4)
        
        self.question_text.delete("1.0", tk.END)
        for entry in self.option_entries:
            opt_letter = entry.get()[:3]
            entry.delete(0, tk.END)
            entry.insert(0, opt_letter)
        
        self.add_status_label.config(text=f"Question added to {subject} successfully!", fg="green")
        winsound.PlaySound("assets/03.wav", winsound.SND_FILENAME)
    
    def show_update_questions(self, subjects):
        """Show update questions screen"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="Update Questions", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        if not subjects:
            msg_label = tk.Label(self.app.main_frame, text="No subjects available", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            subject_frame = tk.Frame(self.app.main_frame)
            subject_frame.pack(pady=10)
            
            subject_label = tk.Label(subject_frame, text="Select Subject:", font=("Arial", 12))
            subject_label.grid(row=0, column=0, padx=10, pady=5)
            
            self.update_subject_var = tk.StringVar()
            subject_dropdown = ttk.Combobox(subject_frame, textvariable=self.update_subject_var, values=subjects, width=30)
            subject_dropdown.grid(row=0, column=1, padx=10, pady=5)
            
            load_btn = tk.Button(subject_frame, text="Load Questions", font=("Arial", 12),
                                command=self.load_questions_for_update)
            load_btn.grid(row=0, column=2, padx=10, pady=5)
            
            self.questions_frame = tk.Frame(self.app.main_frame)
            self.questions_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.manage_quiz_questions)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def load_questions_for_update(self):
        """Load questions for the selected subject"""
        subject = self.update_subject_var.get()
        
        if not subject:
            messagebox.showwarning("Warning", "Please select a subject.")
            return
        
        for widget in self.questions_frame.winfo_children():
            widget.destroy()
        
        filename = f"assets/{subject}.json"
        
        with open(filename, 'r') as f:
            questions = json.load(f)
        
        if not questions:
            msg_label = tk.Label(self.questions_frame, text="No questions available for this subject", font=("Arial", 14))
            msg_label.pack(pady=20)
            return
        
        canvas = tk.Canvas(self.questions_frame)
        scrollbar = ttk.Scrollbar(self.questions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, q in enumerate(questions):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=5)
            
            question_text = q["question"]
            if len(question_text) > 50:
                question_text = question_text[:50] + "..."
            
            q_label = tk.Label(frame, text=f"Q{i+1}: {question_text}", font=("Arial", 12))
            q_label.pack(side="left", padx=5)
            
            edit_btn = tk.Button(frame, text="Edit", font=("Arial", 10),
                               command=partial(self.edit_question, subject, i))
            edit_btn.pack(side="right", padx=5)
            
            delete_btn = tk.Button(frame, text="Delete", font=("Arial", 10),
                                 command=partial(self.delete_question, subject, i))
            delete_btn.pack(side="right", padx=5)
    
    def edit_question(self, subject, question_index):
        """Edit a specific question"""
        filename = f"assets/{subject}.json"
        
        with open(filename, 'r') as f:
            questions = json.load(f)
        
        q = questions[question_index]
        
        edit_window = tk.Toplevel(self.app.root)
        edit_window.title(f"Edit Question {question_index+1}")
        edit_window.geometry("600x500")
        
        question_frame = tk.Frame(edit_window)
        question_frame.pack(pady=10, padx=20, fill=tk.X)
        
        question_label = tk.Label(question_frame, text="Question:", font=("Arial", 12))
        question_label.pack(anchor=tk.W)
        
        question_text = tk.Text(question_frame, height=3, width=60)
        question_text.pack(fill=tk.X, pady=5)
        question_text.insert("1.0", q["question"])
        
        options_frame = tk.Frame(edit_window)
        options_frame.pack(pady=10, padx=20, fill=tk.X)
        
        options_label = tk.Label(options_frame, text="Options:", font=("Arial", 12))
        options_label.pack(anchor=tk.W)
        
        option_entries = []
        for i, option in enumerate(q["options"]):
            option_label = tk.Label(options_frame, text=f"Option {chr(65+i)}:", font=("Arial", 12))
            option_label.pack(anchor=tk.W)
            
            option_entry = tk.Entry(options_frame, width=60)
            option_entry.pack(fill=tk.X, pady=2)
            option_entry.insert(0, option)
            option_entries.append(option_entry)
        
        answer_frame = tk.Frame(edit_window)
        answer_frame.pack(pady=10, padx=20, fill=tk.X)
        
        answer_label = tk.Label(answer_frame, text="Correct Answer:", font=("Arial", 12))
        answer_label.pack(side=tk.LEFT, padx=5)
        
        answer_var = tk.StringVar(value=q["answer"])
        answers = ["A", "B", "C", "D"]
        for ans in answers:
            rb = tk.Radiobutton(answer_frame, text=ans, variable=answer_var, value=ans, font=("Arial", 12))
            rb.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(edit_window, text="Save Changes", font=("Arial", 12),
                            command=lambda: self.save_edited_question(
                                subject, question_index, question_text.get("1.0", tk.END).strip(),
                                [entry.get().strip() for entry in option_entries], answer_var.get(), edit_window
                            ))
        save_btn.pack(pady=10)
    
    def save_edited_question(self, subject, question_index, question, options, answer, window):
        """Save the edited question"""
        filename = f"assets/{subject}.json"
        
        with open(filename, 'r') as f:
            questions = json.load(f)
        
        questions[question_index] = {
            "question": question,
            "options": options,
            "answer": answer
        }
        
        with open(filename, 'w') as f:
            json.dump(questions, f, indent=4)
        
        messagebox.showinfo("Success", "Question updated successfully!")
        window.destroy()
        self.load_questions_for_update()
    
    def delete_question(self, subject, question_index):
        """Delete a specific question"""
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this question?"):
            return
        
        filename = f"assets/{subject}.json"
        
        with open(filename, 'r') as f:
            questions = json.load(f)
        
        del questions[question_index]
        
        with open(filename, 'w') as f:
            json.dump(questions, f, indent=4)
        
        messagebox.showinfo("Success", "Question deleted successfully!")
        self.load_questions_for_update()
    
    def show_view_questions(self, subjects):
        """Show view questions screen"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="View Questions", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        if not subjects:
            msg_label = tk.Label(self.app.main_frame, text="No subjects available", font=("Arial", 14))
            msg_label.pack(pady=20)
        else:
            subject_frame = tk.Frame(self.app.main_frame)
            subject_frame.pack(pady=10)
            
            subject_label = tk.Label(subject_frame, text="Select Subject:", font=("Arial", 12))
            subject_label.grid(row=0, column=0, padx=10, pady=5)
            
            self.view_subject_var = tk.StringVar()
            subject_dropdown = ttk.Combobox(subject_frame, textvariable=self.view_subject_var, values=subjects, width=30)
            subject_dropdown.grid(row=0, column=1, padx=10, pady=5)
            
            load_btn = tk.Button(subject_frame, text="View Questions", font=("Arial", 12),
                                command=self.view_subject_questions)
            load_btn.grid(row=0, column=2, padx=10, pady=5)
            
            self.view_questions_frame = tk.Frame(self.app.main_frame)
            self.view_questions_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.manage_quiz_questions)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def view_subject_questions(self):
        """View questions for the selected subject"""
        subject = self.view_subject_var.get()
        
        if not subject:
            messagebox.showwarning("Warning", "Please select a subject.")
            return
        
        for widget in self.view_questions_frame.winfo_children():
            widget.destroy()
        
        filename = f"assets/{subject}.json"
        
        with open(filename, 'r') as f:
            questions = json.load(f)
        
        if not questions:
            msg_label = tk.Label(self.view_questions_frame, text="No questions available for this subject", font=("Arial", 14))
            msg_label.pack(pady=20)
            return
        
        questions_text = tk.Text(self.view_questions_frame, wrap=tk.WORD, height=20, width=70)
        questions_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.view_questions_frame, orient=tk.VERTICAL, command=questions_text.yview)
        questions_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for i, q in enumerate(questions):
            questions_text.insert(tk.END, f"Question {i+1}: {q['question']}\n\n")
            for option in q["options"]:
                questions_text.insert(tk.END, f"{option}\n")
            questions_text.insert(tk.END, f"\nCorrect Answer: {q['answer']}\n")
            questions_text.insert(tk.END, "-" * 50 + "\n\n")
        
        questions_text.config(state=tk.DISABLED)
    
    def show_admin_password(self):
        """Show the admin password"""
        admin_pass, _ = self.auth.pcheck()
        messagebox.showinfo("Admin Password", f"Current Admin Password: {admin_pass}")
    
    def change_admin_password(self):
        """Change the admin password"""
        self.create_admin_password()
    
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
                            command=self.show_admin_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)
    
    def show_about(self):
        """Show about us information"""
        self.app.clear_frame()
        
        title_label = tk.Label(self.app.main_frame, text="About Us", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        about_text = tk.Text(self.app.main_frame, wrap=tk.WORD, height=20, width=70)
        about_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        about_content = """
Quiz Game Application

This Quiz Game is designed for educational purposes, helping students test their knowledge across various subjects.

Features:
- Multiple subjects and question types
- Administrative controls for question management
- Player tracking and performance reporting
- User feedback collection

Developed as a Python project using Tkinter for the graphical user interface.

Version: 1.0
"""
        
        about_text.insert(tk.END, about_content)
        about_text.config(state=tk.DISABLED)
        
        back_btn = tk.Button(self.app.main_frame, text="Back", font=("Arial", 12),
                            command=self.show_admin_dashboard)
        back_btn.pack(side=tk.BOTTOM, pady=10)