import { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom"; // Import router components
import Header from "./components/Header";
import Footer from "./components/Footer";
import AuthForm from "./components/AuthForm";
import PostFeed from "./components/PostFeed";
import CommentsModal from "./components/CommentsModal";
import SimpleProfilePage from "./components/SimpleProfilePage"; // We'll create this
import { AuthProvider, useAuth } from "./context/AuthContext";

import "./App.css";
import "./components/Header.css";
import "./components/Footer.css";
import "./components/AuthForm.css";
import "./components/PostFeed.css";
import "./components/CreatePostForm.css";
import "./components/CommentsModal.css";
import { API_URL } from "./constants"; // Import API URL constant
function AppRoutes() {
  const { isAuthenticated, user, loading: authLoading } = useAuth();
  const [selectedPostIdForComments, setSelectedPostIdForComments] =
    useState(null);

  // Function to open comments modal for a specific post
  const handleViewComments = (postId) => {
    setSelectedPostIdForComments(postId);
  };

  // Function to close comments modal
  const handleCloseComments = () => {
    setSelectedPostIdForComments(null);
  };

  // This function needs to update the state in PostFeed - prop drilling or context needed
  // For simplicity *in this plan*, let's manage posts state in App.js or a shared context
  // Let's refactor App to hold posts state and pass it down
  const [posts, setPosts] = useState([]); // Move posts state up here

  // Function to fetch posts (now in AppRoutes)
  const fetchPosts = async () => {
    // ... (same fetch logic as in PostFeed before) ...
    try {
      const response = await fetch(`${API_URL}/posts`);
      if (!response.ok)
        throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      setPosts(data); // Update state in AppRoutes
    } catch (err) {
      console.error("Failed to fetch posts:", err);
      // Handle error state if needed at App level
    }
  };

  useEffect(() => {
    // Fetch posts when component mounts or auth state changes?
    // Let's fetch on mount for the feed
    fetchPosts();
  }, []); // Fetch only once on mount

  // Function to handle new post created (passed to CreatePostForm)
  const handlePostCreated = (newPost) => {
    setPosts([newPost, ...posts]); // Add new post to the top
  };

  // Function to update post likes/comments counts after action
  const handlePostUpdate = (updatedPostId, updates) => {
    setPosts((currentPosts) =>
      currentPosts.map((post) =>
        post.id === updatedPostId ? { ...post, ...updates } : post
      )
    );
  };

  if (authLoading) {
    return <div className="loading-screen">Loading app...</div>;
  }

  return (
    <div className="app-container">
      <Header />{" "}
      {/* Header doesn't need user/logout props anymore if using context directly */}
      <main className="app-main container">
        <Routes>
          {/* Redirect /login and /signup to home if authenticated */}
          <Route
            path="/login"
            element={
              isAuthenticated ? <Navigate to="/" /> : <AuthForm type="login" />
            }
          />
          <Route
            path="/signup"
            element={
              isAuthenticated ? <Navigate to="/" /> : <AuthForm type="signup" />
            }
          />

          {/* Protected Route: Home/Feed */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <PostFeed
                  posts={posts} // Pass posts from App state
                  setPosts={setPosts} // Pass setter to allow updates
                  onPostCreated={handlePostCreated} // Pass handlers down
                  onViewComments={handleViewComments}
                  onPostUpdate={handlePostUpdate} // Pass handler for likes/comments count updates
                />
              ) : (
                <Navigate to="/login" replace /> // Redirect to login if not authenticated
              )
            }
          />

          {/* Protected Route: Simple Profile */}
          <Route
            path="/profile/:username" // Dynamic route for username
            element={
              isAuthenticated ? (
                <SimpleProfilePage
                  currentUser={user}
                  posts={posts.filter(
                    (p) => p.authorUsername === user?.username
                  )}
                /> // Pass current user and their posts
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          {/* Add a generic redirect for unmatched routes */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <Footer />
      {/* Render Comments Modal outside of Routes so it can appear over any page */}
      <CommentsModal
        postId={selectedPostIdForComments}
        onClose={handleCloseComments}
        onCommentAdded={handlePostUpdate} // Update feed count using the same handler
      />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        {" "}
        {/* Wrap your entire app content with Router */}
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
