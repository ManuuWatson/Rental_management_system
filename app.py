import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for sessions and flash messages

# Paths for data files
USERS_FILE_PATH = os.path.join("data", "users.json")
APARTMENTS_FILE_PATH = os.path.join("data", "apartments.json")

# Utility to read/write JSON files
def read_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)
    with open(file_path, "r") as f:
        return json.load(f)

def write_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Function to register a new user
def register_user(role, name, contact, address, password):
    try:
        users = read_json(USERS_FILE_PATH)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    # Generate a sequential user ID
    user_id = len(users) + 1

    # Create user data
    user_data = {
        "id": user_id,
        "role": role,
        "name": name,
        "contact": contact,
        "address": address,
        "password": password,
        "apartments": [],
        "tenants": []
    }

    users.append(user_data)

    try:
        write_json(USERS_FILE_PATH, users)
        return True
    except IOError:
        return False

# Home route
@app.route("/")
def home():
    return render_template("base.html")

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        password = request.form['password']

        # Load current users from the JSON file
        users = read_json(USERS_FILE_PATH)

        # Check if the name already exists
        for user in users:
            if user['name'] == name:
                flash('A user with this name already exists. Please choose a different one.')
                return redirect(url_for('register'))

        # Register the new user
        new_user = {
            'id': len(users) + 1,  # Assign a new ID
            'name': name,
            'password': password,  # Note: Store a hashed password in production
            'role': role,
            'contact': contact,
            'address': address,
            'total_apartments': 0 if role == 'landlord' else None,
            'total_tenants': 0 if role == 'landlord' else None,
            'rent_collected': 0.0 if role == 'landlord' else None,
            'pending_payments': 0.0 if role == 'landlord' else None,
            'apartments': [] if role == 'landlord' else None,
            'tenants': [] if role == 'landlord' else None
        }

        users.append(new_user)
        write_json(USERS_FILE_PATH, users)

        # Set session for the new user
        session['user_id'] = new_user['id']
        session['role'] = role

        # Redirect landlords to their dashboard
        if role == 'landlord':
            flash(f'Registration successful! Welcome, {name}.')
            return redirect(url_for('landlord_dashboard'))

        # Redirect other roles to the login page
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Get 'username' from the form
        password = request.form.get('password')  # Get 'password' from the form

        if not username or not password:  # Check if the fields are empty
            flash('Username and password are required.')
            return redirect(url_for('login'))

        # Load users data from the USERS_FILE_PATH (users.json)
        users = read_json(USERS_FILE_PATH)

        # Find the user with the matching username and password
        user = next((u for u in users if u['name'] == username and u['password'] == password), None)

        if user:
            session['user_id'] = user['id']  # Store user ID in the session
            session['role'] = user['role']  # Store user role in the session

            if user['role'] == 'landlord':
                return redirect(url_for('landlord_dashboard'))  # Redirect to the landlord dashboard
            elif user['role'] == 'tenant':
                return redirect(url_for('tenant_dashboard'))  # Redirect to the tenant dashboard
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html')


# Landlord dashboard
@app.route("/landlord/dashboard")
def landlord_dashboard():
    if "user_id" in session and session.get("role") == "landlord":
        user_id = session.get("user_id")
        
        # Fetch apartments for the landlord
        apartments = read_json(APARTMENTS_FILE_PATH)
        landlord_apartments = [apt for apt in apartments if apt["landlord_id"] == user_id]

        # Fetch landlord data from users.json
        users = read_json(USERS_FILE_PATH)
        landlord = next((user for user in users if user["id"] == user_id), None)

        if not landlord:
            return "Landlord not found", 404

        # Fetch tenants associated with the landlord (if any)
        tenants = landlord.get("tenants", [])

        # Prepare dashboard data
        data = {
            "landlord": landlord,  # Pass the landlord object
            "total_apartments": len(landlord_apartments),
            "total_tenants": len(tenants),
            "rent_collected": sum(tenant.get("rent_paid", 0) for tenant in tenants),
            "pending_payments": sum(tenant.get("rent_due", 0) for tenant in tenants),
            "apartments": landlord_apartments,
            "tenants": tenants
        }

        return render_template("landlord_dashboard.html", data=data)

    return "Unauthorized Access", 403


# Tenant dashboard
@app.route("/tenant/dashboard")
def tenant_dashboard():
    if "user_id" in session and session.get("role") == "tenant":
        user_id = session.get("user_id")
        
        # Fetch user details and apartments available for the tenant
        users = read_json(USERS_FILE_PATH)
        tenant = next((user for user in users if user["id"] == user_id), None)
        available_apartments = read_json(APARTMENTS_FILE_PATH)
        
        # Prepare dashboard data
        data = {
            "name": tenant["name"],
            "apartments": available_apartments
        }

        return render_template("tenant_dashboard.html", data=data)

    return "Unauthorized Access", 403

# Add apartment route

@app.route('/add_apartment', methods=['POST'])
def add_apartment():
    apartment_name = request.form['apartment_name']
    units = int(request.form['units'])
    vacancies = int(request.form['vacancies'])
    location = request.form['location']

    # Load existing apartments from JSON file
    with open('apartments.json', 'r') as f:
        apartments = json.load(f)

    # Get the next available ID
    new_id = max(apartment['id'] for apartment in apartments) + 1 if apartments else 1

    # Create new apartment entry
    new_apartment = {
        'id': new_id,
        'landlord_id': session['landlord_id'],  # Assuming you're using session to track the landlord's ID
        'landlord_name': session['landlord_name'],
        'name': apartment_name,
        'units': units,
        'vacancies': vacancies,
        'location': location  # Adding the location here
    }

    # Add new apartment to the list and save to the file
    apartments.append(new_apartment)
    with open('apartments.json', 'w') as f:
        json.dump(apartments, f, indent=4)

    return redirect(url_for('landlord_dashboard'))



# Transaction report route
@app.route("/reports/transactions")
def transaction_report():
    data = [
        {"tenant_name": "John Doe", "amount": 1200, "status": "Paid"},
        {"tenant_name": "Jane Smith", "amount": 800, "status": "Pending"},
    ]
    return render_template("transaction_report.html", data=data)

# Overview report route
@app.route("/reports/overview")
def overview_report():
    data = {
        "total_tenants": 10,
        "total_apartments": 5,
        "total_payments": 3400,
    }
    return render_template("overview_report.html", data=data)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
