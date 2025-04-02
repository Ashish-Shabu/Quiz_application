# models/question.py
import os
import json
from glob import glob
import random
from typing import List, Dict, Optional

class QuestionManager:
    def __init__(self):
        # Initialize the assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
    
    def get_subjects(self) -> List[str]:
        """
        Get all available quiz subjects
        Returns:
            List of subject names (filenames without extension)
        """
        try:
            return [os.path.splitext(os.path.basename(f))[0] for f in glob("assets/*.json")]
        except Exception as e:
            print(f"Error getting subjects: {e}")
            return []
    
    def get_questions(self, subject: str) -> List[Dict]:
        """
        Get all questions for a subject
        Args:
            subject: Name of the subject
        Returns:
            List of question dictionaries or empty list if none found
        """
        try:
            filename = f"assets/{subject}.json"
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading questions for {subject}: {e}")
            return []
    
    def save_questions(self, subject: str, questions: List[Dict]) -> bool:
        """
        Save questions for a subject
        Args:
            subject: Name of the subject
            questions: List of question dictionaries
        Returns:
            True if successful, False otherwise
        """
        try:
            filename = f"assets/{subject}.json"
            with open(filename, 'w') as f:
                json.dump(questions, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving questions for {subject}: {e}")
            return False
    
    def add_question(self, subject: str, question_data: Dict) -> bool:
        """
        Add a new question to a subject
        Args:
            subject: Name of the subject
            question_data: Dictionary containing:
                - question: The question text
                - options: List of answer options
                - answer: Correct answer (A, B, C, or D)
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = self.get_questions(subject)
            questions.append(question_data)
            return self.save_questions(subject, questions)
        except Exception as e:
            print(f"Error adding question to {subject}: {e}")
            return False
    
    def update_question(self, subject: str, question_index: int, question_data: Dict) -> bool:
        """
        Update an existing question
        Args:
            subject: Name of the subject
            question_index: Index of question to update
            question_data: Updated question data
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = self.get_questions(subject)
            if 0 <= question_index < len(questions):
                questions[question_index] = question_data
                return self.save_questions(subject, questions)
            return False
        except Exception as e:
            print(f"Error updating question in {subject}: {e}")
            return False
    
    def delete_question(self, subject: str, question_index: int) -> bool:
        """
        Delete a question from a subject
        Args:
            subject: Name of the subject
            question_index: Index of question to delete
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = self.get_questions(subject)
            if 0 <= question_index < len(questions):
                del questions[question_index]
                return self.save_questions(subject, questions)
            return False
        except Exception as e:
            print(f"Error deleting question from {subject}: {e}")
            return False
    
    def get_random_questions(self, subject: str, count: int) -> List[Dict]:
        """
        Get random questions from a subject
        Args:
            subject: Name of the subject
            count: Number of questions to return
        Returns:
            List of randomly selected questions
        """
        try:
            questions = self.get_questions(subject)
            if count >= len(questions):
                return questions
            return random.sample(questions, count)
        except Exception as e:
            print(f"Error getting random questions from {subject}: {e}")
            return []
    
    def validate_question(self, question_data: Dict) -> bool:
        """
        Validate question data structure
        Args:
            question_data: Dictionary containing question data
        Returns:
            True if valid, False otherwise
        """
        required_keys = {"question", "options", "answer"}
        if not all(key in question_data for key in required_keys):
            return False
        
        if not isinstance(question_data["question"], str) or not question_data["question"].strip():
            return False
        
        if not isinstance(question_data["options"], list) or len(question_data["options"]) != 4:
            return False
        
        if question_data["answer"] not in ["A", "B", "C", "D"]:
            return False
        
        return True
    
    def get_question_count(self, subject: str) -> int:
        """
        Get number of questions for a subject
        Args:
            subject: Name of the subject
        Returns:
            Number of questions
        """
        try:
            return len(self.get_questions(subject))
        except Exception as e:
            print(f"Error getting question count for {subject}: {e}")
            return 0
    
    def subject_exists(self, subject: str) -> bool:
        """
        Check if a subject exists
        Args:
            subject: Name of the subject
        Returns:
            True if subject exists, False otherwise
        """
        return os.path.isfile(f"assets/{subject}.json")
    
    def delete_subject(self, subject: str) -> bool:
        """
        Delete a subject and all its questions
        Args:
            subject: Name of the subject to delete
        Returns:
            True if successful, False otherwise
        """
        try:
            filename = f"assets/{subject}.json"
            if os.path.isfile(filename):
                os.remove(filename)
                return True
            return False
        except Exception as e:
            print(f"Error deleting subject {subject}: {e}")
            return False
    
    def get_all_questions(self) -> Dict[str, List[Dict]]:
        """
        Get all questions from all subjects
        Returns:
            Dictionary with subject names as keys and question lists as values
        """
        try:
            subjects = self.get_subjects()
            return {subject: self.get_questions(subject) for subject in subjects}
        except Exception as e:
            print(f"Error getting all questions: {e}")
            return {}
    
    def search_questions(self, search_term: str) -> Dict[str, List[Dict]]:
        """
        Search questions across all subjects
        Args:
            search_term: Text to search for in questions
        Returns:
            Dictionary of matching questions grouped by subject
        """
        try:
            results = {}
            all_questions = self.get_all_questions()
            
            for subject, questions in all_questions.items():
                matches = [
                    q for q in questions 
                    if search_term.lower() in q["question"].lower() or 
                    any(search_term.lower() in opt.lower() for opt in q["options"])
                ]
                if matches:
                    results[subject] = matches
            
            return results
        except Exception as e:
            print(f"Error searching questions: {e}")
            return {}