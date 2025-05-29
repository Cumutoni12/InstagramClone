import { useState, useEffect } from "react";
import { API_URL } from "../constants";
import { useAuth } from "../context/AuthContext";
import "./CommentsModal.css"; // Create this CSS file

// Basic Comment Item component (Optional, could be inline)
function CommentItem({ comment }) {
  const formatDate = (timestamp) => {
    const dateObj = new Date(timestamp + "Z");
    return dateObj.toLocaleDateString("en-US"); // Simple date format
  };
  return (
    <div className="comment-item">
      <span className="comment-author">{comment.authorUsername}</span>
      <span className="comment-content">{comment.content}</span>
      <span className="comment-timestamp">{formatDate(comment.createdAt)}</span>
    </div>
  );
}

function CommentsModal({ postId, onClose, onCommentAdded }) {
  // Receive postId and onClose handler
  const [comments, setComments] = useState([]);
  const [loadingComments, setLoadingComments] = useState(true);
  const [commentContent, setCommentContent] = useState("");
  const [addingComment, setAddingComment] = useState(false);
  const [error, setError] = useState(null);
  const { user, isAuthenticated } = useAuth(); // Need user/token to add comments

  // Fetch comments when the modal opens (postId changes)
  useEffect(() => {
    const fetchComments = async () => {
      try {
        setLoadingComments(true);
        setError(null);
        // Decide if GET /comments is protected or public
        // const response = isAuthenticated ? await fetchAuthenticated(`/posts/${postId}/comments`) : await fetch(`${API_URL}/posts/${postId}/comments`);
        const response = await fetch(`${API_URL}/posts/${postId}/comments`); // Assuming public GET for comments

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setComments(data);
      } catch (err) {
        console.error(`Error fetching comments for post ${postId}:`, err);
        setError("Failed to load comments.");
      } finally {
        setLoadingComments(false);
      }
    };

    if (postId !== null) {
      // Only fetch if a post ID is provided
      fetchComments();
    } else {
      setComments([]); // Clear comments if no post is selected
    }
  }, [postId, isAuthenticated]); // Re-fetch if postId or auth state changes

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentContent.trim()) {
      setError("Comment cannot be empty.");
      return;
    }
    if (!isAuthenticated || !user?.token) {
      setError("You must be logged in to comment.");
      return;
    }
    if (addingComment) return;

    try {
      setAddingComment(true);
      setError(null);

      const response = await fetch(`${API_URL}/posts/${postId}/comments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`, // Send the JWT token
        },
        body: JSON.stringify({ content: commentContent }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to add comment.");
      }

      // Success! Add the new comment to the list and update parent count
      setComments([...comments, data.comment]);
      setCommentContent(""); // Clear the form
      if (onCommentAdded) {
        onCommentAdded(postId, data.commentsCount); // Notify parent with post ID and new total count
      }
    } catch (err) {
      console.error(`Error adding comment to post ${postId}:`, err);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setAddingComment(false);
    }
  };

  // If postId is null, don't render the modal
  if (postId === null) {
    return null;
  }

  return (
    // Simple modal structure - could use a dedicated modal library
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>
          &times;
        </button>
        <h3>Comments</h3>
        {error && <div className="error-message">{error}</div>}

        <div className="comments-list">
          {loadingComments ? (
            <div>Loading comments...</div>
          ) : comments.length === 0 ? (
            <div>No comments yet.</div>
          ) : (
            comments.map((comment) => (
              <CommentItem key={comment.id} comment={comment} />
            ))
          )}
        </div>

        {isAuthenticated && ( // Only show form if authenticated
          <form onSubmit={handleAddComment} className="add-comment-form">
            <input
              type="text"
              placeholder="Add a comment..."
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              disabled={addingComment}
            />
            <button type="submit" disabled={addingComment}>
              Post
            </button>
          </form>
        )}
        {!isAuthenticated && (
          <div className="comment-auth-prompt">Log in to comment.</div>
        )}
      </div>
    </div>
  );
}

export default CommentsModal;
