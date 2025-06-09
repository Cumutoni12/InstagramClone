import unittest
import json
import os
import tempfile
import sqlite3
from datetime import datetime, timedelta,timezone # Needed for JWT testing
import jwt
from werkzeug.security import generate_password_hash # Only needed for creating a user directly in test setup

# Import the app and db initialization functions from your main app file
# Adjust import path as necessary
from app import app, init_db, get_db, DATABASE # Assuming you have these in app.py

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Use an in-memory database for testing
        app.config['DATABASE'] = ':memory:' # Use in-memory SQLite
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key' # Use a test secret key
        self.client = app.test_client()

        # Initialize the database schema (in-memory)
        with app.app_context():
            init_db() # Use your existing init_db which reads schema.sql

    def tearDown(self):
         # Clean up the in-memory database (optional for :memory:)
         pass # With ':memory:', the db is reset for each test

    def create_test_user(self, username="testuser", password="testpassword"):
        """Helper function to create a user directly in the test DB."""
        with app.app_context():
            db = get_db()
            hashed_password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hashed_password))
            db.commit()
            # Fetch the created user to return ID and username
            user = db.execute("SELECT id, username FROM users WHERE username = ?", (username,)).fetchone()
            return dict(user) # Return as dictionary

    def create_test_post(self, user_id, image_url="http://example.com/image.jpg", caption="Test caption"):
        """Helper function to create a post."""
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO posts (user_id, image_url, caption) VALUES (?, ?, ?)",
                       (user_id, image_url, caption))
            db.commit()
            # Fetch the created post to return its ID
            post = db.execute("SELECT id FROM posts WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchone()
            return dict(post)

    def get_auth_token(self, username="testuser", password="testpassword"):
         """Helper to get a JWT token for a user."""
         # Ensure user exists first
         with app.app_context():
             user = get_db().execute("SELECT id, username FROM users WHERE username = ?", (username,)).fetchone()
         
         if not user:
              user = self.create_test_user(username, password)

         token_payload = {
             'user_id': user['id'],
             'username': user['username'],
             'exp': datetime.now(timezone.utc) + timedelta(days=1)
         }
         token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
         return token


    # --- Tests Start Here ---

    def test_signup_success(self):
        response = self.client.post('/signup', json={'username': 'newuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User created successfully')
        self.assertIn('token', data) # Should return token
        self.assertEqual(data['username'], 'newuser')

    def test_signup_user_exists(self):
        self.create_test_user("existinguser") # Create user first
        response = self.client.post('/signup', json={'username': 'existinguser', 'password': 'password456'})
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Username already exists')

    def test_login_success(self):
        self.create_test_user("loginuser", "correctpassword")
        response = self.client.post('/login', json={'username': 'loginuser', 'password': 'correctpassword'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('token', data)

    def test_login_invalid_credentials(self):
        self.create_test_user("user", "pass")
        response = self.client.post('/login', json={'username': 'user', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid credentials')

    def test_get_posts_empty(self):
        response = self.client.get('/posts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0) # Should be empty initially

    def test_create_post_success(self):
        user = self.create_test_user()
        token = self.get_auth_token(user['username'])
        response = self.client.post('/posts',
            json={'imageUrl': 'http://example.com/new.jpg', 'caption': 'My new post'},
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['imageUrl'], 'http://example.com/new.jpg')
        self.assertEqual(data['caption'], 'My new post')
        self.assertEqual(data['authorUsername'], user['username']) # Check author
        self.assertIn('id', data) # Check if ID is returned

    def test_create_post_unauthenticated(self):
         response = self.client.post('/posts',
             json={'imageUrl': 'http://example.com/new.jpg', 'caption': 'My new post'}
             # Missing Authorization header
         )
         self.assertEqual(response.status_code, 401)
         data = json.loads(response.data)
         self.assertEqual(data['message'], 'Token is missing!')

    def test_like_post_success(self):
        user = self.create_test_user("liker1")
        post_user = self.create_test_user("poster")
        post = self.create_test_post(post_user['id'])
        token = self.get_auth_token(user['username'])

        response = self.client.post(f'/posts/{post["id"]}/like',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Post liked successfully')
        self.assertEqual(data['likesCount'], 1)

        # Check if like is in DB
        with app.app_context():
            db = get_db()
            like_entry = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", (user['id'], post['id'])).fetchone()
            self.assertIsNotNone(like_entry)

    def test_like_nonexistent_post(self):
        user = self.create_test_user("liker2")
        token = self.get_auth_token(user['username'])
        response = self.client.post('/posts/9999/like', headers={'Authorization': f'Bearer {token}'})
        self.assertIn(response.status_code, [404, 400])

    def test_like_post_twice(self):
        user = self.create_test_user("liker3")
        post_user = self.create_test_user("poster2")
        post = self.create_test_post(post_user['id'])
        token = self.get_auth_token(user['username'])
        # First like
        response1 = self.client.post(f'/posts/{post["id"]}/like', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response1.status_code, 200)
        # Second like
        response2 = self.client.post(f'/posts/{post["id"]}/like', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response2.status_code, 400)
        data = json.loads(response2.data)
        self.assertIn('already liked', data['message'])

    def test_unlike_post(self):
        user = self.create_test_user("liker4")
        post_user = self.create_test_user("poster3")
        post = self.create_test_post(post_user['id'])
        token = self.get_auth_token(user['username'])
        # Like first
        self.client.post(f'/posts/{post["id"]}/like', headers={'Authorization': f'Bearer {token}'})
        # Now unlike
        response = self.client.delete(f'/posts/{post["id"]}/unlike', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Post unliked successfully')

    def test_unlike_nonexistent_post(self):
        user = self.create_test_user("liker5")
        token = self.get_auth_token(user['username'])
        response = self.client.delete('/posts/9999/unlike', headers={'Authorization': f'Bearer {token}'})
        self.assertIn(response.status_code, [404, 400])

    def test_unlike_post_not_liked(self):
        user = self.create_test_user("liker6")
        post_user = self.create_test_user("poster4")
        post = self.create_test_post(post_user['id'])
        token = self.get_auth_token(user['username'])
        response = self.client.delete(f'/posts/{post["id"]}/unlike', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('not liked', data['message'])

    def test_add_comment(self):
        user = self.create_test_user("commenter1")
        post_user = self.create_test_user("poster5")
        post = self.create_test_post(post_user['id'])
        token = self.get_auth_token(user['username'])
        response = self.client.post(f'/posts/{post["id"]}/comments',
            json={'content': 'Nice post!'},
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Comment added successfully')
        self.assertEqual(data['comment']['content'], 'Nice post!')
        self.assertEqual(data['comment']['authorUsername'], user['username'])

    def test_get_comments_for_post(self):
        user = self.create_test_user("commenter2")
        post_user = self.create_test_user("poster6")
        post = self.create_test_post(post_user['id'])
        token = self.get_auth_token(user['username'])
        # Add a comment
        self.client.post(f'/posts/{post["id"]}/comments',
            json={'content': 'First comment!'},
            headers={'Authorization': f'Bearer {token}'}
        )
        # Get comments
        response = self.client.get(f'/posts/{post["id"]}/comments')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['content'], 'First comment!')
        self.assertEqual(data[0]['authorUsername'], user['username'])


if __name__ == '__main__':
    unittest.main()