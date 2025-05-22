import { useState } from "react";
import { API_URL } from "../constants";
import { useAuth } from "../context/AuthContext"; // Import useAuth
import "./AuthForm.css";

function AuthForm({ type }) {
  // Remove onSubmit prop, use context instead
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth(); // Get login function from context

  const handleSubmit = async (e) => {
    // Make function async
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password");
      return;
    }

    try {
      setLoading(true);
      setError(null); // Clear previous errors

      const url = type === "signup" ? `${API_URL}/signup` : `${API_URL}/login`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle API errors (e.g., username taken, invalid credentials)
        throw new Error(data.message || "Authentication failed");
      }

      // Assuming success, call login from context
      // The backend currently only returns username, but we'll add token later
      login({ username: data.username, token: data.token }); // Pass username and token (when backend sends it)
      // No need to clear form here, redirect/state change will handle it
    } catch (err) {
      console.error("Authentication error:", err);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      {/* ... rest of the component remains the same ... */}
      <h2>{type === "signup" ? "Sign Up" : "Log In"}</h2>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="auth-form">
        {/* ... form fields ... */}
        <div className="form-group">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
            autoComplete="username"
          />
        </div>

        <div className="form-group">
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            autoComplete={
              type === "signup" ? "new-password" : "current-password"
            }
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading
            ? type === "signup"
              ? "Signing Up..."
              : "Logging In..."
            : type === "signup"
            ? "Sign Up"
            : "Log In"}
        </button>
      </form>
    </div>
  );
}

export default AuthForm;
