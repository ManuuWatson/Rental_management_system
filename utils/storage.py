import json
import os

DATA_DIR = "data"
USER_FILE = os.path.join(DATA_DIR, "users.json")
TRANSACTION_FILE = os.path.join(DATA_DIR, "transactions.json")

# Ensure that the data directory and files exist
def ensure_file_exists(file_path, default_data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump(default_data, file)

# Save user information (role, name, contact, address, password)
def save_user(role, name, contact, address, password):
    ensure_file_exists(USER_FILE, {"landlord": [], "tenant": []})
    with open(USER_FILE, "r") as file:
        users = json.load(file)

    if any(user["name"] == name for user in users[role]):
        return False  # User already exists

    users[role].append({"name": name, "contact": contact, "address": address, "password": password})
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)
    return True

# Save transaction details
def save_transaction(tenant_name, apartment_id, amount, status):
    ensure_file_exists(TRANSACTION_FILE, [])
    with open(TRANSACTION_FILE, "r") as file:
        transactions = json.load(file)

    transactions.append({
        "tenant_name": tenant_name,
        "apartment_id": apartment_id,
        "amount": amount,
        "status": status
    })
    with open(TRANSACTION_FILE, "w") as file:
        json.dump(transactions, file, indent=4)
    return True

# Update user details (name, field, new_value)
def update_user(name, field, new_value):
    ensure_file_exists(USER_FILE, {"landlord": [], "tenant": []})
    with open(USER_FILE, "r") as file:
        users = json.load(file)

    updated = False
    for role in ["landlord", "tenant"]:
        for user in users[role]:
            if user["name"] == name:
                user[field] = new_value
                updated = True

    if updated:
        with open(USER_FILE, "w") as file:
            json.dump(users, file, indent=4)
    return updated

# Update payment status for transactions
def update_payment_status(tenant_name, apartment_id, status):
    ensure_file_exists(TRANSACTION_FILE, [])
    with open(TRANSACTION_FILE, "r") as file:
        transactions = json.load(file)

    updated = False
    for transaction in transactions:
        if transaction["tenant_name"] == tenant_name and transaction["apartment_id"] == apartment_id:
            transaction["status"] = status
            updated = True

    if updated:
        with open(TRANSACTION_FILE, "w") as file:
            json.dump(transactions, file, indent=4)
    return updated

# Authenticate user by checking username and password
def authenticate_user(username, password):
    ensure_file_exists(USER_FILE, {"landlord": [], "tenant": []})
    with open(USER_FILE, "r") as file:
        users = json.load(file)

    for role in ["landlord", "tenant"]:
        for user in users[role]:
            if user["name"] == username and user["password"] == password:
                return True  # Authentication successful
    return False  # Invalid username or password


import json

# Function to save user data to user.json
def save_user(role, name, contact, address, password):
    try:
        with open("data/users.json", "r") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []  # If file doesn't exist or is empty, create an empty list
    
    # Check if user already exists
    for user in users:
        if user["name"] == name:
            return False  # User already exists
    
    # Create a new user dictionary
    new_user = {
        "role": role,
        "name": name,
        "contact": contact,
        "address": address,
        "password": password  # In a real app, you should hash the password for security
    }
    
    # Add the new user to the list
    users.append(new_user)
    
    # Save the updated user list to user.json
    with open("data/users.json", "w") as file:
        json.dump(users, file, indent=4)
    
    return True

# Function to check if a user already exists in user.json
def check_user_exists(name):
    try:
        with open("data/users.json", "r") as file:
            users = json.load(file)
            for user in users:
                if user["name"] == name:
                    return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False  # If the file doesn't exist or is empty, return False
    
    return False
