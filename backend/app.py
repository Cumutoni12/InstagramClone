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

    # Select posts, join users for author, LEFT JOIN likes and group to count likes
    c.execute("""
        SELECT
            p.id, p.user_id, p.image_url, p.caption, p.created_at,
            u.username AS author_username,
            COUNT(DISTINCT l.id) AS likes_count ,-- Count likes for each post
            COUNT(DISTINCT c.id) AS comments_count -- Count distinct comments for each post
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.post_id -- LEFT JOIN to include posts with 0 likes
        LEFT JOIN comments c ON p.id = c.post_id -- LEFT JOIN to include posts with 0 comments
        GROUP BY p.id -- Group by post to count likes for each
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
             'likesCount': post['likes_count'], # Use the count from the query
             'commentsCount': post['comments_count']
         })

    return jsonify(posts_list)

@app.route('/posts', methods=['POST'])

@token_required # protect tgus endpoint-only authenticated users can create posts
def create_post(current_user):
    data = request.json
    image_url = data.get('imageUrl') 
    caption = data.get('caption',) #caption is optional

    if not image_url or not image_url.strip():
        return jsonify({'message': 'Image URL is required'}), 400

    db = get_db()
    c = db.cursor()

    try:
        # Insert new post
        c.execute("INSERT INTO posts (user_id, image_url, caption) VALUES (?, ?, ?)",
                  (current_user['id'], image_url, caption))
        db.commit()

        # Optionally fetch the newly created post's ID
        post_id = c.lastrowid
        c.execute(""" select p.id,p.user_id, p.image_url, p.caption, p.created_at,u.username as author_username from posts p join users u on p.user_id = u.id where p.id = ?""",(post_id,))

    
        new_post = c.fetchone()

        if new_post:
            new_post_dict = {
                'id': new_post['id'],
                'userId': new_post['user_id'],
                'imageUrl': new_post['image_url'],
                'caption': new_post['caption'],
                'createdAt': new_post['created_at'],
                'authorUsername': new_post['author_username'],
                'likesCount': 0, # Placeholder for now
                'commentsCount': 0 # Placeholder for now
            }

            return jsonify(new_post_dict),201#retun the created post
        else:
            return jsonify({'message': 'Post created successfully', 'post': new_post}), 201 

    except Exception as e:
        print(f"Error creating post: {e}")
        return jsonify({'message': 'An error occurred while creating the post'}), 500

@app.route('/posts/<int:post_id>/like', methods=['POST'])
@token_required #protect this endpoint
def like_post(current_user, post_id):
    db = get_db()
    c = db.cursor()
    user_id = current_user['id']
    # Validate post_id

    try:
        c.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if c.fetchone() is None:
            return jsonify({'message': 'Post not found'}), 404
        
        # Check if the user has already liked this post
        c.execute("SELECT id FROM likes WHERE user_id = ? AND post_id = ?", (current_user['id'], post_id))
        if c.fetchone() is not None:
            return jsonify({'message': 'You have already liked this post'}), 400
        
        # Insert like 
        c.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
        db.commit() 
        c.execute("SELECT COUNT(id) as likes_count FROM likes WHERE post_id = ?", (post_id,))
        likes_count = c.fetchone()['likes_count']
        return jsonify({'message': 'Post liked successfully', 'likesCount': likes_count}), 200

    except Exception as e:
        print(f"Error liking/unliking post: {e}")
        return jsonify({'message': 'An error occurred while liking/unliking the post'}), 500

@app.route('/posts/<int:post_id>/unlike', methods=['DELETE'])
@token_required #protect this endpoint  
def unlike_post(current_user, post_id):
    db = get_db()
    c = db.cursor()
    user_id = current_user['id']

    try:
        # Check if the post exists
        c.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if c.fetchone() is None:
            return jsonify({'message': 'Post not found'}), 404
        
        # Check if the user has liked this post
        c.execute("SELECT id FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        like = c.fetchone()
        if like is None:
            return jsonify({'message': 'You have not liked this post'}), 400
        
        # Delete the like
        c.execute("DELETE FROM likes WHERE id = ?", (like['id'],))
        db.commit()

        # return updated likes count
        c.execute("SELECT COUNT(id) as likes_count FROM likes WHERE post_id = ?", (post_id,))
        likes_count = c.fetchone()['likes_count']
        
        return jsonify({'message': 'Post unliked successfully', 'likesCount': likes_count}), 200

    except Exception as e:
        print(f"Error unliking post: {e}")
        db.rollback()  # Rollback in case of error
        return jsonify({'message': 'An error occurred while unliking the post'}), 500
    
@app.route('/posts/<int:post_id>/comments', methods=['GET'])
# Optional: Make GET comments public or protected depending on requirements
# @token_required
def get_comments(post_id): # No user needed if public, add user if protected
    db = get_db()
    c = db.cursor()

    # Check if post exists
    c.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
    if c.fetchone() is None:
         return jsonify({'message': 'Post not found'}), 404

    # Select comments for this post, join users for author username
    c.execute("""
        SELECT
            c.id, c.user_id, c.post_id, c.content, c.created_at,
            u.username AS author_username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC -- Display comments chronologically
    """, (post_id,))
    comments = c.fetchall()

    comments_list = []
    for comment in comments:
        comments_list.append({
            'id': comment['id'],
            'userId': comment['user_id'],
            'postId': comment['post_id'],
            'content': comment['content'],
            'createdAt': comment['created_at'],
            'authorUsername': comment['author_username']
        })

    return jsonify(comments_list)

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required # Protect this endpoint
def add_comment(current_user, post_id): # Decorator passes user and post_id
    data = request.json
    content = data.get('content')

    if not content or not content.strip():
        return jsonify({'message': 'Comment content is required'}), 400

    db = get_db()
    c = db.cursor()
    user_id = current_user['id']

    try:
        # Check if post exists
        c.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if c.fetchone() is None:
            return jsonify({'message': 'Post not found'}), 404

        # Insert the comment
        c.execute("INSERT INTO comments (user_id, post_id, content) VALUES (?, ?, ?)",
                  (user_id, post_id, content))
        db.commit()

        # Optionally, fetch the created comment including its new ID and author username
        comment_id = c.lastrowid
        c.execute("""
            SELECT c.id, c.user_id, c.post_id, c.content, c.created_at, u.username AS author_username
            FROM comments c JOIN users u ON c.user_id = u.id WHERE c.id = ?
        """, (comment_id,))
        new_comment = c.fetchone()

        if new_comment:
             new_comment_dict = {
                 'id': new_comment['id'],
                 'userId': new_comment['user_id'],
                 'postId': new_comment['post_id'],
                 'content': new_comment['content'],
                 'createdAt': new_comment['created_at'],
                 'authorUsername': new_comment['author_username']
             }
             # Also get updated comment count for the post
             c.execute("SELECT COUNT(id) AS comments_count FROM comments WHERE post_id = ?", (post_id,))
             comments_count = c.fetchone()['comments_count']

             return jsonify({
                 'message': 'Comment added successfully',
                 'comment': new_comment_dict,
                 'commentsCount': comments_count # Include updated count
             }), 201
        else:
             return jsonify({'message': 'Comment added, but could not retrieve data'}), 201


    except Exception as e:
         print(f"Error adding comment: {e}")
         db.rollback()
         return jsonify({'message': 'An error occurred while adding the comment'}), 500

if __name__ =='__main__':

    #initialize db if it does not exisit    

    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)



