import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { API_URL } from "../constants";
import "./PostItem.css";

// Optional: Basic icon placeholders (replace with actual SVG/font icons later)
const HeartIcon = ({ filled }) => (
  <span style={{ color: filled ? "red" : "black" }}>
    {filled ? "❤️" : "🤍"}
  </span>
);

function PostItem({ post, onViewComments }) {
  const { user, isAuthenticated } = useAuth(); // Need user to check if current user liked it
  const [isLiked, setIsLiked] = useState(false);
  const [currentLikesCount, setCurrentLikesCount] = useState(post.likesCount);
  const [loading, setLoading] = useState(false); // For like/unlike action

  // Check if the current user has liked this post when the component mounts or post changes
  useEffect(() => {
    // We would ideally fetch THIS user's like status for this post from the backend
    // For simplicity *in this plan*, we'll just assume the user hasn't liked it initially
    // or add a check to the main feed fetch later.
    // Stretch goal: Add a `/posts/:id/is_liked` endpoint or include this info in `/posts` feed.
    // For now, let's simulate based on user and localStorage (not ideal for accuracy)
    const likedPosts = JSON.parse(
      localStorage.getItem("instaCloneLikedPosts") || "{}"
    );
    if (
      user &&
      likedPosts[user.username] &&
      likedPosts[user.username][post.id]
    ) {
      setIsLiked(true);
    } else {
      setIsLiked(false);
    }

    setCurrentLikesCount(post.likesCount); // Update count if post prop changes
  }, [post, user]); // Re-run if post or user changes

  const handleLikeToggle = async () => {
    if (!isAuthenticated) {
      // Prompt user to login
      alert("You must be logged in to like posts.");
      return;
    }
    if (loading) return; // Prevent double clicking

    setLoading(true);
    const endpoint = isLiked
      ? `/posts/${post.id}/unlike`
      : `/posts/${post.id}/like`;
    const method = isLiked ? "DELETE" : "POST";

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: method,
        headers: {
          Authorization: `Bearer ${user.token}`, // Send the JWT token
        },
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle backend errors
        throw new Error(
          data.message || `Failed to ${isLiked ? "unlike" : "like"} post.`
        );
      }

      // Success! Update state and local storage
      setIsLiked(!isLiked);
      setCurrentLikesCount(data.likesCount); // Update count from backend response

      // Simple local storage tracking (Optional, can be removed if backend fully tracks)
      const likedPosts = JSON.parse(
        localStorage.getItem("instaCloneLikedPosts") || "{}"
      );
      likedPosts[user.username] = likedPosts[user.username] || {};
      if (!isLiked) {
        // If we just liked
        likedPosts[user.username][post.id] = true;
      } else {
        // If we just unliked
        delete likedPosts[user.username][post.id];
      }
      localStorage.setItem("instaCloneLikedPosts", JSON.stringify(likedPosts));
    } catch (err) {
      console.error(`Error toggling like for post ${post.id}:`, err);
      alert(
        `Failed to ${isLiked ? "unlike" : "like"} post: ` +
          (err.message || "An error occurred.")
      );
    } finally {
      setLoading(false);
    }
  };

  // Basic date formatting
  const formatDate = (timestamp) => {
    // const Date = new Date(timestamp);
    // Adjust parsing for potential string formats from backend
    const dateObj = new Date(timestamp + "Z"); // Assume UTC if not specified
    if (isNaN(dateObj.getTime())) {
      // Fallback if parsing fails
      try {
        const [year, month, day, time] = timestamp.split(/[- :]/);
        const dt = new Date(
          Date.UTC(
            year,
            month - 1,
            day,
            time.split(":")[0],
            time.split(":")[1],
            time.split(":")[2]
          )
        );
        return dt.toLocaleDateString("en-US", {
          month: "long",
          day: "numeric",
          year: "numeric",
        });
      } catch (e) {
        console.error("Failed to parse date:", timestamp, e);
        return timestamp; // Return original if all else fails
      }
    }
    return dateObj.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="post-item">
      <div className="post-header">
        <span className="post-author">{post.authorUsername}</span>
      </div>
      <div className="post-image">
        <img src={post.imageUrl} alt={post.caption} />
      </div>
      <div className="post-actions">
        <button
          className="action-button like-button"
          onClick={handleLikeToggle}
          disabled={loading}
        >
          <HeartIcon filled={isLiked} /> {/* Show heart icon */}
        </button>
        {/* Comment and Share icons/buttons will go here */}
        <button
          className="action-button"
          onClick={() => onViewComments(post.id)}
        >
          💬
        </button>
        {/* Placeholder Comment icon */}
        <button className="action-button">➡️</button>{" "}
        {/* Placeholder Share icon */}
        {/* Placeholder Share icon */}
      </div>
      <div className="post-likes">
        <span>{currentLikesCount} likes</span> {/* Use state for count */}
      </div>
      <div className="post-caption">
        <span className="post-author">{post.authorUsername}</span>{" "}
        {post.caption}
      </div>
      {/* Comments preview section (Day 10) */}
      <div
        className="post-comments-preview"
        onClick={() => onViewComments(post.id)}
      >
        {/* Make the preview clickable */}
        <span>
          {post.commentsCount > 0 && <span>{post.commentsCount} comments</span>}
        </span>
      </div>
      <div className="post-timestamp">{formatDate(post.createdAt)}</div>
    </div>
  );
}

export default PostItem;
