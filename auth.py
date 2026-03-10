import json
import os

class AccountManager:
    FILE_PATH = "accounts.json"

    @staticmethod
    def save(username, data):
        """Saves or updates user data in the JSON file."""
        all_data = {}
        if os.path.exists(AccountManager.FILE_PATH):
            try:
                with open(AccountManager.FILE_PATH, 'r') as f:
                    all_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                all_data = {}
        
        all_data[username] = data
        with open(AccountManager.FILE_PATH, 'w') as f:
            json.dump(all_data, f, indent=4)

    @staticmethod
    def load(username):
        """Retrieves user data. Returns None if user not found."""
        if os.path.exists(AccountManager.FILE_PATH):
            try:
                with open(AccountManager.FILE_PATH, 'r') as f:
                    all_accounts = json.load(f)
                    return all_accounts.get(username)
            except (json.JSONDecodeError, IOError):
                return None
        return None