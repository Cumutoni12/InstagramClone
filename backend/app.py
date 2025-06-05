from flask import Flask, jsonify, request
from flask_cors import CORS # For handling Cross-Origin Resource Sharing
import os # For accessing environment variables
from datetime import datetime, timedelta # For setting token expiration
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
import jwt # For generating and verifying JSON Web Tokens (JWT)
from functools import wraps # For creating decorators
from flask_migrate import Migrate # For database migrations
from models import db, User, Post, Like, Comment # Your database models
from dotenv import load_dotenv # For loading .env file

load_dotenv() # Load environment variables from .env file at the start

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes, allowing requests from your frontend

# Configure Secret Key for JWT and session management
# It reads from the .env file, with a fallback for safety (though .env is preferred)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-me-in-env')

# Database Configuration using f-string to build the connection URI
# This string tells SQLAlchemy how to connect to your SQL Server database.
# It uses pyodbc as the driver.

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_server = os.getenv("DB_SERVER")
db_name = os.getenv("DB_NAME")

# IMPORTANT: Ensure 'ODBC Driver 17 for SQL Server' exactly matches the name
# of the ODBC driver installed on your system. Spaces in the driver name
# should be replaced with '+' characters in the connection string.
# If you have a different driver (e.g., 'SQL Server Native Client 11.0'),
# update the driver name accordingly.

app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'

# Disable SQLAlchemy event system if not needed, to save resources

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask app
db.init_app(app)
# Initialize Flask-Migrate for handling database schema migrations

migrate = Migrate(app, db)


# --- JWT Authentication Decorator ---
# This decorator can be used to protect routes that require a valid token.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT is typically sent in the Authorization header as "Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Get token part after "Bearer "
                token = auth_header.split(' ')[1]
            except IndexError:
                # Malformed header, token remains None
                return jsonify({'message': 'Bearer token malformed!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401 # Unauthorized

        try:
            # Decode the token using the app's SECRET_KEY
            # This will raise an exception if the token is invalid or expired
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Fetch the user from the database based on the 'user_id' in the token payload
            current_user = User.query.get(data['user_id'])

            if not current_user:
                return jsonify({'message': 'User from token not found!'}), 401 # Unauthorized

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401 # Unauthorized
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401 # Unauthorized
        except Exception as e:
            print(f"Token verification error: {e}")
            return jsonify({'message': 'An error occurred during token verification!'}), 500

        # Pass the authenticated user object to the decorated route function
        return f(current_user, *args, **kwargs)
    return decorated


# --- API Endpoints ---

# == User Authentication ==
@app.route('/signup', methods=['POST'])
def signup():
    """Registers a new user."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400 # Bad Request

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409 # Conflict

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()

        # Generate a token for the new user upon successful signup
        token_payload = {
            'user_id': new_user.id,
            'username': new_user.username,
            'exp': datetime.utcnow() + timedelta(days=1) # Token expires in 1 day
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'message': 'User created successfully', 'username': username, 'token': token}), 201 # Created
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        print(f"Error during signup: {e}")
        return jsonify({'message': 'An error occurred during signup'}), 500 # Internal Server Error


@app.route('/login', methods=['POST'])
def login():
    """Logs in an existing user."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()

    # Check if user exists and password hash matches
    if user and check_password_hash(user.password, password):
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(days=1) # Token expires in 1 day
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'Login successful', 'username': user.username, 'token': token}), 200 # OK
    
    return jsonify({'message': 'Invalid credentials'}), 401 # Unauthorized


# == Posts ==
@app.route('/posts', methods=['GET'])
def get_posts():
    """Retrieves all posts, ordered by creation date."""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    posts_list = []

    for post in posts:
        posts_list.append({
            'id': post.id,
            'userId': post.user_id,
            'imageUrl': post.image_url,
            'caption': post.caption,
            'createdAt': post.created_at.isoformat(), # Use ISO format for dates
            'authorUsername': post.author.username, # Accessing username via backref
            'likesCount': len(post.likes), # Efficiently get count of likes
            'commentsCount': len(post.comments) # Efficiently get count of comments
        })
    return jsonify(posts_list)


@app.route('/posts', methods=['POST'])
@token_required # Protect this endpoint - only authenticated users can create posts
def create_post(current_user): # The decorator passes the authenticated user object here
    """Creates a new post for the authenticated user."""
    data = request.json
    image_url = data.get('imageUrl')
    caption = data.get('caption', '') # Caption is optional, default to empty string

    if not image_url or not image_url.strip():
        return jsonify({'message': 'Image URL is required'}), 400

    try:
        new_post = Post(
            user_id=current_user.id, # Associate post with the logged-in user
            image_url=image_url,
            caption=caption
        )
        db.session.add(new_post)
        db.session.commit()

        # Return the created post data, including counts which will be 0
        return jsonify({
            'id': new_post.id,
            'userId': new_post.user_id,
            'imageUrl': new_post.image_url,
            'caption': new_post.caption,
            'createdAt': new_post.created_at.isoformat(),
            'authorUsername': current_user.username, # Use current_user directly
            'likesCount': 0,
            'commentsCount': 0
        }), 201 # Created
    except Exception as e:
        db.session.rollback()
        print(f"Error creating post: {e}")
        return jsonify({'message': 'An error occurred while creating the post'}), 500


# == Likes ==
@app.route('/posts/<int:post_id>/like', methods=['POST'])
@token_required # Protect this endpoint
def like_post(current_user, post_id):
    """Allows an authenticated user to like a post."""
    post = Post.query.get_or_404(post_id) # Get post or return 404 if not found

    # Check if the user has already liked this post
    if Like.query.filter_by(user_id=current_user.id, post_id=post_id).first():
        return jsonify({'message': 'Post already liked by this user'}), 409 # Conflict

    try:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()

        return jsonify({
            'message': 'Post liked successfully',
            'likesCount': len(post.likes) # Return updated like count for the post
        }), 200 # OK
    except Exception as e:
        db.session.rollback()
        print(f"Error liking post: {e}")
        return jsonify({'message': 'An error occurred while liking the post'}), 500


@app.route('/posts/<int:post_id>/unlike', methods=['DELETE'])
@token_required # Protect this endpoint
def unlike_post(current_user, post_id):
    """Allows an authenticated user to unlike a post."""
    post = Post.query.get_or_404(post_id) # Ensure post exists
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if not like:
        return jsonify({'message': 'Post not liked by this user or like not found'}), 404 # Not Found (or 409 Conflict)

    try:
        db.session.delete(like)
        db.session.commit()

        return jsonify({
            'message': 'Post unliked successfully',
            'likesCount': len(post.likes) # Return updated like count
        }), 200 # OK
    except Exception as e:
        db.session.rollback()
        print(f"Error unliking post: {e}")
        return jsonify({'message': 'An error occurred while unliking the post'}), 500


# == Comments ==
@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """Retrieves all comments for a specific post."""
    post = Post.query.get_or_404(post_id) # Ensure post exists
    
    # Order comments by creation date (e.g., oldest first, or .desc() for newest first)
    comments_ordered = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    
    comments_list = [{
        'id': comment.id,
        'userId': comment.user_id,
        'postId': comment.post_id,
        'content': comment.content,
        'createdAt': comment.created_at.isoformat(),
        'authorUsername': comment.author.username # Access username via backref
    } for comment in comments_ordered]

    return jsonify(comments_list)


@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required # Protect this endpoint
def add_comment(current_user, post_id):
    """Adds a comment to a specific post by an authenticated user."""
    data = request.json
    content = data.get('content')

    if not content or not content.strip():
        return jsonify({'message': 'Comment content is required'}), 400

    post = Post.query.get_or_404(post_id) # Ensure post exists

    try:
        new_comment = Comment(
            user_id=current_user.id,
            post_id=post_id,
            content=content
        )
        db.session.add(new_comment)
        db.session.commit()

        # Return the newly created comment and the updated count

        return jsonify({
            'message': 'Comment added successfully',
            'comment': {
                'id': new_comment.id,
                'userId': new_comment.user_id,
                'postId': new_comment.post_id,
                'content': new_comment.content,
                'createdAt': new_comment.created_at.isoformat(),
                'authorUsername': new_comment.author.username # Access username via backref on Comment
            },
            'commentsCount': len(post.comments) # Updated comment count for the post
        }), 201 # Created
    except Exception as e:
        db.session.rollback()
        print(f"Error adding comment: {e}")
        return jsonify({'message': 'An error occurred while adding the comment'}), 500


# == Health Check / Index ==

@app.route('/')
def index():
    """A simple health check or welcome message for the API."""
    return jsonify({'message': 'Instagram Clone Backend is running!'})


# --- Main execution ---

if __name__ == '__main__':
    
    # The 'debug=True' mode is useful for development as it provides detailed error pages
    # and automatically reloads the server when code changes.
    # Do not use debug=True in a production environment.

    app.run(debug=True)