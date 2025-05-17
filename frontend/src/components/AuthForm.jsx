import { useState } from "react";
import "./AuthForm.css";

function AuthForm({ type, onSubmit, error, loading }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      onSubmit({ error: "Please fill out all fields" });
      return;
    }
    onSubmit({ username, password });
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>{type === "Log" ? "Sign Up" : "Sign up "}</h2>
      {error && <div className="error-message">{error}</div>}
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
            type === "Log in " ? "new-password" : "current-password"
          }
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Loading..." : type === "signup" ? "Sign Up" : "Login"}
      </button>
    </form>
  );
}

export default AuthForm;
