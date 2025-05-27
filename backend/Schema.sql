DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments; 

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, --store hashed passwords
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL, -- Foreign key to users
    image_url TEXT NOT NULL, -- URL of the image
    caption TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE likes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,--FOREIGN key to users 
    post_id INTEGER NOT NULL, --FOREIGN KEY to posts 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    --Ensure a user can only like a post once 
    UNIQUE (user_id,post_id),
    FOREIGN KEY (user_id) REFERENCES USERS(id)
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,--FOREIGN key to users 
    post_id INTEGER NOT NULL, --FOREIGN KEY to posts
    content TEXT NOT NULL, 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
    FOREIGN KEY (post_id) REFERENCES posts(id)
);