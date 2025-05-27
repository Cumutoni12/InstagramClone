import { useState, useEffect } from 'react';
import { API_URL } from '../constants';
import PostItem from './PostItem';
import './PostFeed.css';

function PostFeed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/posts`); // Fetch from backend

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setPosts(data);
        setError(null);
      } catch (error) {
        console.error('Error fetching posts:', error);
        setError('Failed to load posts. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []); // Empty dependency array: fetch once on mount

  if (loading) return <div className="feed-message">Loading feed...</div>;
  if (error) return <div className="error-message">{error}</div>; // Re-use AuthForm error style

  return (
    <div className="post-feed">
      {posts.length === 0 ? (
        <div className="feed-message">No posts yet. Be the first to share!</div>
      ) : (
        posts.map(post => (
          <PostItem key={post.id} post={post} />
        ))
      )}
    </div>
  );
}

export default PostFeed;