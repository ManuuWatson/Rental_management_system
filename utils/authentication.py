# utils/authentication.py
import json

def authenticate_user(username, password):
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        return False  # Return False if the file doesn't exist

    # Check if any user matches the provided username and password
    for user in users:
        if user["name"] == username and user["password"] == password:
            return True  # Return True if credentials match
    return False  # Return False if no match found
