from flask import Flask, jsonify, request,g
from flask_cors import CORS
import sqlite3
import os
import jwt
from datetime import datetime,timedelta
from functools import wraps #need this for decorators
from werkzeug.security import generate_password_hash, check_password_hash

def token_required(f):
    @wraps(f) # Preserves original function's metadata
    def decorated(*args, **kwargs):
        token = None
        # JWT is typically sent in the Authorization header as "Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1] # Get token part after "Bearer "
            except IndexError:
                pass # Malformed header, token remains None

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401 # Unauthorized

        try:
            # Decode the token
            # This will raise an exception if the token is invalid or expired
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Get the user from the database based on token payload
            db = get_db()
            c = db.cursor()
            c.execute("SELECT id, username FROM users WHERE id = ?", (data['user_id'],))
            current_user = c.fetchone()

            if not current_user:
                return jsonify({'message': 'User not found!'}), 401 # Unauthorized, user from token not found

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401 # Unauthorized
        except jwt.InvalidTokenError:
             return jsonify({'message': 'Token is invalid!'}), 401 # Unauthorized
        except Exception as e:
             print(f"Token verification error: {e}")
             return jsonify({'message': 'An error occurred during token verification!'}), 500

        # Pass the authenticated user to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated


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

          # Generate JWT Token
        token_payload = {
                    'user_id': user_id,
                    'username': username,
                    'exp': datetime.utcnow() + timedelta(days=1) # Token expires in 1 day
                }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
                    'message': 'User created successfully',
                    'username': username,
                    'token': token # Return the token
                }), 201
    
    except sqlite3.IntegrityError: # Handle unique constraint error
         return jsonify({'message': 'Username already exists'}), 409
        
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
        # Generate JWT Token
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(days=1) # Token expires in 1 day
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'message': 'Login successful',
            'username': user['username'],
            'token': token # Return the token
        }), 200
        
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/')

def index():
    return "instagram clone Backend"

#add signup,login,and basic posts routes here in the next steps 

@app.route('/posts', methods=['GET'])
def get_posts():
    db = get_db()
    c = db.cursor()

    # Select posts, joining with users to get author's username
    # Order by creation date descending (newest first)
    c.execute("""
        SELECT
            p.id, p.user_id, p.image_url, p.caption, p.created_at,
            u.username AS author_username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    posts = c.fetchall() # Get all rows

    # Convert rows to a list of dictionaries
    posts_list = []
    for post in posts:
         posts_list.append({
             'id': post['id'],
             'userId': post['user_id'],
             'imageUrl': post['image_url'],
             'caption': post['caption'],
             'createdAt': post['created_at'],
             'authorUsername': post['author_username'],
             'likesCount': 0, # Placeholder for now
             'commentsCount': 0 # Placeholder for now
         })

    return jsonify(posts_list)

if __name__ =='__main__':
    
    #initialize db if it does not exisit 

    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)



