import { useState } from "react";
import Header from "./components/header";
import Footer from "./components/Footer";
import AuthForm from "./components/AuthForm";
import "./App.css";
import "./components/header.css";
import "./components/Footer.css";
import "./components/AuthForm.css";
import { useAuth } from "./context/AuthContext.jsx";

function App() {
  const { isAuthenticated, user, loading: authLoading, logout } = useAuth(); // Get state and functions from context
  const [showSignUp, setShowSignUp] = useState(false); // Still needed for toggling forms

  // If auth is still loading (checking local storage), show a loading state
  if (authLoading) {
    return <div className="loading-screen">Loading...</div>; // Add basic loading screen style
  }

  return (
    <div className="app-container">
      <Header user={user} onLogout={logout} />{" "}
      {/* Pass user and logout to Header */}
      <main className="app-main container">
        {isAuthenticated ? (
          <div>
            {/* Placeholder for authenticated content (Feed/Profile) */}
            <h2>Welcome, {user?.username}!</h2> {/* Display username */}
            <p>You are logged in.</p>
            {/* Feed and other components will go here */}
          </div>
        ) : (
          <div className="auth-page-content">
            {showSignUp ? (
              <AuthForm type="signup" /> // No onSubmit needed here anymore
            ) : (
              <AuthForm type="login" /> // No onSubmit needed here anymore
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
