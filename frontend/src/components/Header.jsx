import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./header.css";

function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="app-header">
      <div className="container">
        <div className="header-left">
          <Link to="/" className="site-title">
            InstagramClone
          </Link>
        </div>

        <div className="header-right">
          {isAuthenticated ? (
            <div className="user-controls">
              <Link to="/" className="nav-link">
                🏠
              </Link>
              <Link to={`/profile/${user?.username}`} className="nav-link">
                👤
              </Link>
              <span className="username">Hello, {user?.username}!</span>
              <button onClick={logout} className="logout-button">
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="nav-link">
                Login
              </Link>
              <Link to="/signup" className="nav-link">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
