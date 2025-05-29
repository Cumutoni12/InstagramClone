import { useState, useEffect } from "react";
import { API_URL } from "../constants";
import { useAuth } from "../context/AuthContext"; // Needed for auth headers if fetchAuthenticated is used
import PostItem from "./PostItem";
import CreatePostForm from "./CreatePostForm"; // Import the form
import "./PostFeed.css";
import "./CreatePostForm.css"; // Import form styles

function PostFeed({ onViewComments, onCommentAdded, posts, setPosts }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // const { user } = useAuth(); // Use if you need auth headers for fetching feed (not for this endpoint currently)

  const fetchPosts = async () => {
    // Use plain fetch for the public /posts endpoint
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/posts`);

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setPosts(data);
      setError(null);
    } catch (error) {
      console.error("Error fetching posts:", error);
      setError("Failed to load posts. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, []); // Fetch once on mount

  // Function to handle new post creation
  const handlePostCreated = (newPost) => {
    // Add the new post to the top of the feed without refetching all
    setPosts([newPost, ...posts]);
    // Alternative: Re-fetch all posts: fetchPosts();
  };

  if (loading) return <div className="feed-message">Loading feed...</div>;
  if (error) return <div className="error-message">{error}</div>; // Re-use AuthForm error style

  return (
    <div className="post-feed">
      {/* Include the Create Post Form */}
      <CreatePostForm onPostCreated={handlePostCreated} />

      {posts.length === 0 ? (
        <div className="feed-message">No posts yet. Be the first to share!</div>
      ) : (
        posts.map((post) => (
          <PostItem key={post.id} post={post} onViewComments={onViewComments} />
        ))
      )}
    </div>
  );
}

export default PostFeed;
