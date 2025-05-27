import { useState } from "react";
import Header from "./components/header";
import Footer from "./components/Footer";
import AuthForm from "./components/AuthForm";
import "./App.css";
import "./components/header.css";
import "./components/Footer.css";
import "./components/AuthForm.css";
import { useAuth } from "./context/AuthContext.jsx";
import PostFeed from "./components/PostFeed"; // Import PostFeed
import "./components/PostFeed.css"; // Import PostFeed styles
import "./components/PostItem.css"; // Import PostItem styles (can import here or in PostFeed)

function App() {
  const { isAuthenticated, user, loading: authLoading, logout } = useAuth();
  const [showSignUp, setShowSignUp] = useState(false);

  if (authLoading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="app-container">
      <Header user={user} onLogout={logout} />
      <main className="app-main container">
        {isAuthenticated ? (
          <PostFeed /> /* Render the PostFeed */
        ) : (
          // ... auth forms ...
          <div className="auth-page-content">
            {showSignUp ? (
              <AuthForm type="signup" />
            ) : (
              <AuthForm type="login" />
            )}
            <div className="auth-switch">
              {showSignUp ? (
                <p>
                  Have an account?{" "}
                  <button
                    className="switch-button"
                    onClick={() => setShowSignUp(false)}
                  >
                    Log In
                  </button>
                </p>
              ) : (
                <p>
                  Don't have an account?{" "}
                  <button
                    className="switch-button"
                    onClick={() => setShowSignUp(true)}
                  >
                    Sign Up
                  </button>
                </p>
              )}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;
