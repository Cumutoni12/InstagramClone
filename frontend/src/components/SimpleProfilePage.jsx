import { useState } from "react";
import "./SimpleProfilePage.css";

function SimpleProfilePage({ currentUser, posts }) {
  const [isLoading, setIsLoading] = useState(false);

  if (!currentUser) {
    return (
      <div className="profile-container">Please log in to view profiles.</div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-picture">
          <img
            src={
              currentUser.profilePicture || "https://via.placeholder.com/150"
            }
            alt={`${currentUser.username}'s profile`}
            onError={(e) => {
              e.target.src = "https://via.placeholder.com/150";
            }}
          />
        </div>

        <div className="profile-info">
          <div className="profile-info-header">
            <h2 className="username">{currentUser.username}</h2>
            <button className="edit-profile-button">Edit Profile</button>
          </div>

          <div className="profile-stats">
            <div className="stat-item">
              <span className="stat-number">{posts.length}</span> posts
            </div>
            <div className="stat-item">
              <span className="stat-number">0</span> followers
            </div>
            <div className="stat-item">
              <span className="stat-number">0</span> following
            </div>
          </div>

          <div className="profile-bio">
            <div className="full-name">
              {currentUser.fullName || currentUser.username}
            </div>
            <p>{currentUser.bio || "No bio yet."}</p>
          </div>
        </div>
      </div>

      <div className="posts-grid">
        {posts.map((post) => (
          <div key={post.id} className="post-thumbnail">
            <img src={post.imageUrl} alt={post.caption || "Post image"} />
            <div className="post-overlay">
              <div className="post-stats">❤️ {post.likes || 0}</div>
              <div className="post-stats">💬 {post.comments?.length || 0}</div>
            </div>
          </div>
        ))}
      </div>

      {isLoading && <div className="loading-skeleton">Loading...</div>}

      {posts.length === 0 && !isLoading && (
        <div className="no-posts-message">No posts yet.</div>
      )}
    </div>
  );
}

export default SimpleProfilePage;
