# models/player.py
import os
import csv
import random
import string
from datetime import datetime

class PlayerManager:
    def __init__(self):
        # Initialize the assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
    
    def generate_uid(self):
        """Generate a unique 6-character user ID"""
        uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        # Check if the ID already exists
        if os.path.isfile('assets/details.csv'):
            with open('assets/details.csv', 'r') as f:
                reader = csv.reader(f)
                existing_ids = [row[0] for row in reader if len(row) > 0]
            
            # Regenerate if ID exists
            while uid in existing_ids:
                uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        return uid
    
    def register_player(self, player_data):
        """
        Register a new player
        Args:
            player_data: List containing [name, email, age, dob, school, phone]
        Returns:
            str: Generated user ID if successful, None otherwise
        """
        try:
            uid = self.generate_uid()
            
            # Create file with headers if it doesn't exist
            if not os.path.isfile('assets/details.csv'):
                with open('assets/details.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["User ID", "Name", "Email", "Age", "DOB", "School", "Phone"])
            
            # Append new player data
            with open('assets/details.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([uid] + player_data)
            
            return uid
        except Exception as e:
            print(f"Error registering player: {e}")
            return None
    
    def verify_player(self, uid):
        """
        Verify player login credentials
        Args:
            uid: User ID to verify
        Returns:
            dict: Player info if found, None otherwise
        """
        try:
            if not os.path.isfile('assets/details.csv'):
                return None
            
            with open('assets/details.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) > 0 and row[0] == uid:
                        return {
                            "uid": row[0],
                            "name": row[1],
                            "email": row[2],
                            "age": row[3],
                            "dob": row[4],
                            "school": row[5],
                            "phone": row[6]
                        }
            return None
        except Exception as e:
            print(f"Error verifying player: {e}")
            return None
    
    def save_quiz_result(self, player_id, player_name, subject, score, total_questions):
        """
        Save quiz results to file
        Args:
            player_id: User ID
            player_name: Player's name
            subject: Quiz subject
            score: Number of correct answers
            total_questions: Total questions in quiz
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            percentage = (score / total_questions) * 100
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            time_str = now.strftime("%H:%M:%S")
            
            # Create file with headers if it doesn't exist
            if not os.path.isfile('assets/results.csv'):
                with open('assets/results.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "User ID", "Name", "Subject", 
                        "Score", "Total", "Percentage", 
                        "Date", "Time"
                    ])
            
            # Append new result
            with open('assets/results.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    player_id,
                    player_name,
                    subject,
                    score,
                    total_questions,
                    f"{percentage:.2f}%",
                    date_str,
                    time_str
                ])
            
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            return False
    
    def get_player_results(self, player_id):
        """
        Get all quiz results for a player
        Args:
            player_id: User ID to look up
        Returns:
            list: List of result dictionaries, empty list if none found
        """
        try:
            if not os.path.isfile('assets/results.csv'):
                return []
            
            results = []
            with open('assets/results.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 8 and row[0] == player_id:
                        results.append({
                            "subject": row[2],
                            "score": int(row[3]),
                            "total": int(row[4]),
                            "percentage": row[5],
                            "date": row[6],
                            "time": row[7]
                        })
            return results
        except Exception as e:
            print(f"Error getting player results: {e}")
            return []
    
    def save_feedback(self, player_id, player_name, rating, comments, suggestions):
        """
        Save player feedback
        Args:
            player_id: User ID
            player_name: Player's name
            rating: Rating (1-5)
            comments: Feedback comments
            suggestions: Improvement suggestions
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            time_str = now.strftime("%H:%M:%S")
            
            # Create file with headers if it doesn't exist
            if not os.path.isfile('assets/feedbacks.csv'):
                with open('assets/feedbacks.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "User ID", "Name", "Rating", 
                        "Comments", "Suggestions", 
                        "Date", "Time"
                    ])
            
            # Append new feedback
            with open('assets/feedbacks.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    player_id,
                    player_name,
                    rating,
                    comments,
                    suggestions,
                    date_str,
                    time_str
                ])
            
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_all_players(self):
        """
        Get all registered players
        Returns:
            list: List of player dictionaries, empty list if none found
        """
        try:
            if not os.path.isfile('assets/details.csv'):
                return []
            
            players = []
            with open('assets/details.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 7:
                        players.append({
                            "uid": row[0],
                            "name": row[1],
                            "email": row[2],
                            "age": row[3],
                            "dob": row[4],
                            "school": row[5],
                            "phone": row[6]
                        })
            return players
        except Exception as e:
            print(f"Error getting all players: {e}")
            return []
    
    def get_player_by_name(self, name):
        """
        Get player by name (case-insensitive partial match)
        Args:
            name: Name to search for
        Returns:
            list: Matching players
        """
        try:
            if not os.path.isfile('assets/details.csv'):
                return []
            
            matches = []
            with open('assets/details.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if len(row) >= 2 and name.lower() in row[1].lower():
                        matches.append({
                            "uid": row[0],
                            "name": row[1],
                            "email": row[2],
                            "age": row[3],
                            "dob": row[4],
                            "school": row[5],
                            "phone": row[6]
                        })
            return matches
        except Exception as e:
            print(f"Error searching players by name: {e}")
            return []