from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy. this instance will be configured with the Flask app later. 

db= SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'# Explicity names the tabke in the database`
    
    #columns for the users' tablle
    id = db.Column(db.Integer, primary_key=True)# unique identifier for each user
    username = db.Column(db.String(50), unique=True, nullable=False)#user's chosen username
    password = db.Column(db.String(255), nullable=False)# user's password, hashed for security
    created_at = db.Column(db.DateTime, default=datetime.utcnow)#the time of when the user was created 

    # Relationships: Define how users relate to other models (posts, likes, comments)
    # 'backref' creates a virtual 'author' attribute on the Post, Like, and Comment models
    # 'lazy=True' means SQLAlchemy will load the related objects as needed


    posts = db.relationship('Post', backref='author', lazy=True) #relationship to the Post model, allowing access to a user's posts
    likes = db.relationship('Like', backref='user', lazy=True) #relationship to the Like model, allowing access to a user's likes
    comments = db.relationship('Comment', backref='author', lazy=True) #relationship to the Comment model, allowing access to a user's comments   

    def __repr__(self): #Optional: String representation for debugging
        return f'<User {self.username}>'
    
class Post(db.Model):
    __tablename__ = 'posts'  # Explicitly names the table in the database
    
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each post

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to the User model

    image_url = db.Column(db.String(255), nullable=False)  # URL of the image associated with the post

    caption = db.Column(db.Text)  # Optional caption for the post

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the post was created
    
    #relationships 

    #cascade='all, delete-orphan' ensures that if a post is deleted, all associated likes and comments are also deleted

    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')  # Relationship to the Like model

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')  # Relationship to the Comment model


    def __repr__(self):
        return f'<Post {self.id}>'
    
class Like(db.Model):
    __tablename__ = 'likes'  # Explicitly names the table in the database
    
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each like

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to the User model

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)  # Foreign key to the Post model

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the like was created


    # Table arguments: Define constraints that apply to the whole table
    # UniqueConstraint ensures a user can only like a specific post once.
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_like'),)

    def __repr__(self):
        return f'<Like user_id={self.user_id} post_id={self.post_id}>'
    
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # User who wrote the comment
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False) # Post that was commented on
    content = db.Column(db.Text, nullable=False) # The actual text of the comment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment {self.id} by user_id={self.user_id}>"