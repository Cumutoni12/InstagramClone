import { createContext, useState, useEffect, useContext } from "react";
import { API_URL } from "../constants"; // We'll create this next

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // Stores { username, token } (or just username for now)
  const [loading, setLoading] = useState(true); // To show loading while checking stored token

  useEffect(() => {
    // Check for stored user/token on initial load
    const storedUser = localStorage.getItem("instaCloneUser");
    const storedToken = localStorage.getItem("instaCloneToken"); // Will use token later

    if (storedUser && storedToken) {
      // For now, just set user based on username.
      // Later, we'll validate the token.
      setUser({ username: storedUser, token: storedToken });
    }

    setLoading(false); // Finished checking
  }, []); // Empty dependency array means this runs once on mount

  const login = ({ username, token }) => {
    // Accept token even if not used immediately
    setUser({ username, token });
    localStorage.setItem("instaCloneUser", username);
    localStorage.setItem("instaCloneToken", token); // Store token for later
    console.log(token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("instaCloneUser");
    localStorage.removeItem("instaCloneToken");
  };

  const isAuthenticated = !!user; // Simple check if user is not null

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
