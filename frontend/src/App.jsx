import { useState } from "react";
import Header from "./components/header";
import Footer from "./components/Footer";
import AuthForm from "./components/AuthForm";
import "./App.css";
import "./components/header.css";
import "./components/Footer.css";
import "./components/AuthForm.css";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showSignUp, setShowSignUp] = useState(false);

  const handleAuthSubmit = (formData) => {
    console.log("Form submitted", formData);
    if (!formData.error) {
      console.log("Simulating successful auth");
      setIsAuthenticated(true);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <main className="app-main container">
        {isAuthenticated ? (
          <div>
            <h2>Welcome! You are logged in.</h2>
            <button onClick={() => setIsAuthenticated(false)}>Logout</button>
          </div>
        ) : (
          <div className="auth-page-content">
            {showSignUp ? (
              <AuthForm type="signup" onSubmit={handleAuthSubmit} />
            ) : (
              <AuthForm type="login" onSubmit={handleAuthSubmit} />
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
