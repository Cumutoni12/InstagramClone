import { useState } from "react";
import { API_URL } from "../constants";
import { useAuth } from "../context/AuthContext";
import "./CreatePostForm.css"; // Create this CSS file

function CreatePostForm({ onPostCreated }) {
  // onPostCreated prop to notify parent (e.g., PostFeed)
  const [imageUrl, setImageUrl] = useState("");
  const [caption, setCaption] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth(); // Get user (and token) from context

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!imageUrl.trim()) {
      setError("Image URL is required.");
      return;
    }

    if (!user || !user.token) {
      setError("You must be logged in to create a post.");
      return; // Should ideally not happen if form is only shown when authenticated
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/posts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`, // Send the JWT token
        },
        body: JSON.stringify({
          imageUrl,
          caption,
          // userId and authorUsername are handled by the backend using the token
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle backend validation or auth errors
        throw new Error(data.message || "Failed to create post.");
      }

      // Success! Clear form and notify parent
      setImageUrl("");
      setCaption("");
      if (onPostCreated) {
        onPostCreated(data); // Pass the newly created post data
      }
    } catch (err) {
      console.error("Error creating post:", err);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post-container">
      <h3>Create New Post</h3>
      {error && <div className="error-message">{error}</div>}{" "}
      {/* Reuse error style */}
      <form onSubmit={handleSubmit} className="create-post-form">
        <div className="form-group">
          <label htmlFor="imageUrl">Image URL:</label>
          <input
            type="text"
            id="imageUrl"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            placeholder="Paste image URL here"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="caption">Caption (Optional):</label>
          <textarea
            id="caption"
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            placeholder="Write a caption..."
            disabled={loading}
            rows="3"
          ></textarea>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Posting..." : "Share Post"}
        </button>
      </form>
    </div>
  );
}

export default CreatePostForm;
