import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Header.css";

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
                <span role="img" aria-label="Home">
                  🏠
                </span>
              </Link>
              <Link to="/create" className="nav-link">
                <span role="img" aria-label="Create post">
                  ➕
                </span>
              </Link>
              <Link to={`/profile/${user?.username}`} className="nav-link">
                <span role="img" aria-label="Profile">
                  👤
                </span>
              </Link>
              <span className="header-username">{user?.username}</span>
              <button onClick={logout} className="logout-button">
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="nav-link">
                Log in
              </Link>
              <Link to="/signup" className="nav-link">
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
