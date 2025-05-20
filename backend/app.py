from flask import Flask, jsonify, request,g
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app= Flask(__name__)
CORS(app) #allow requests from frontend 
app.config['SECRET_KEY'] = os.environ.get ("Secret-key ","your-super-secret-key-change-me") # replace with a strong key!

DATABASE= "insgram_clone.db"

def get_db():
    db=getattr(g, '_database', None)
    

    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row #access columns by name
    return db  

#this is a good practice to close the db connection after each request 
# from flask import g
@app.teardown_appcontext

def close_db(error):
    db=getattr(g,'-database',None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db=get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read ())
            db.commit()
    print("Database initialized.")

#---Routes---

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    db = get_db()
    c = db.cursor()

    try:
        # Check if username already exists
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return jsonify({'message': 'Username already exists'}), 409

        # Hash password and insert user
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hashed_password))
        db.commit()

        # Optionally fetch the newly created user's ID for the token
        user_id = c.lastrowid

        # Generate JWT token (optional for basic auth flow)
        # We will add JWT token generation and verification on Day 7

        return jsonify({'message': 'User created successfully', 'username': username}), 201 # Return username for simplicity initially

    except Exception as e:
         print(f"Error during signup: {e}")
         return jsonify({'message': 'An error occurred during signup'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    db = get_db()
    c = db.cursor()

    c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = c.fetchone() # Use fetchone() because username is unique

    if user and check_password_hash(user['password'], password):
        # Authentication successful
        # Generate JWT token (Day 7)
        # For now, just return success
         return jsonify({'message': 'Login successful', 'username': user['username']}), 200 # Return username

    else:
        return jsonify({'message': 'Invalid credentials'}), 401

    # We will add JWT token generation and verification on Day 7

@app.route('/')

def index():
    return "instagram clone Backend"

#add signup,login,and basic posts routes here in the next steps 

if __name__ =='__main__':
    #initialize db if it does not exisit 

    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)



