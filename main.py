# main.py
import os
import tkinter as tk
from views.admin import AdminView
from views.player import PlayerView

class QuizAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        # Set up the main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize views
        self.admin_view = AdminView(self)
        self.player_view = PlayerView(self)
        
        # Show welcome screen
        self.show_welcome_screen()

    def clear_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Display the welcome screen"""
        self.clear_frame()
        
        # Add a label
        welcome_label = tk.Label(self.main_frame, text="Welcome to Quiz Game", font=("Arial", 24, "bold"))
        welcome_label.pack(pady=30)
        
        # Add buttons for Admin and Player
        admin_btn = tk.Button(self.main_frame, text="Admin", font=("Arial", 14),
                             width=20, command=self.admin_view.admin_portal)
        admin_btn.pack(pady=10)
        
        player_btn = tk.Button(self.main_frame, text="Player", font=("Arial", 14),
                              width=20, command=self.player_view.player_portal)
        player_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizAppGUI(root)
    root.mainloop()