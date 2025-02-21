import os
import pickle
from typing import List, Any
from datetime import datetime


class PickleHandler:

    def __init__(self, base_directory: str = "data"):
        self.base_directory = base_directory
        os.makedirs(self.base_directory, exist_ok=True)     # Create the directory if it doesn't exist

    def save_party(self, data: Any, filename: str) -> bool:
        if not filename.endswith('.pkl'):
            filename += '.pkl'
        filepath = os.path.join(self.base_directory, filename)
        try:
            with open(filepath, 'wb') as file:
                pickle.dump(data, file)
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False

    def load_party(self, filename: str):
        if not filename.endswith('.pkl'):
            filename += '.pkl'
        filepath = os.path.join(self.base_directory, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} not found")
        try:
            with open(filepath, 'rb') as file:
                return pickle.load(file)
        except pickle.UnpicklingError as e:
            raise pickle.UnpicklingError(f"Error loading pickle file: {str(e)}")

    def list_files(self):       # generates a dictionary of the format {"fileName": "Feb 3, 2025, 1:19 AM",...}
        try:
            files = [f for f in os.listdir(self.base_directory)
                     if f.endswith('.pkl')]
            file_dict = {}
            for file in files:
                full_path = os.path.join(self.base_directory, file)
                mod_time = os.path.getmtime(full_path)
                timestamp = datetime.fromtimestamp(mod_time).strftime("%b %d, %Y\n%I:%M %p").replace(" 0", " ")
                file_dict[file[:-4]] = timestamp
            return dict(sorted(file_dict.items()))
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []

    def delete_party(self, filename: str):
        if not filename.endswith('.pkl'):
            filename += '.pkl'
        filepath = os.path.join(self.base_directory, filename)
        if not os.path.exists(filepath):
            print(f"File {filename} does not exist")
            return False
        try:
            os.remove(filepath)
            print(f"Successfully deleted {filename}")
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    # then it becomes a question of, where do these save/load buttons live?
