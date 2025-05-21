import React from "react";
import "./header.css"; // Assuming you have a CSS file for styling

function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="container">
        <div className="header-left">
          <h1>InstagramClone</h1> {/* Or a logo */}
        </div>
        <div className="header-right">
          {user ? (
            <div className="user-controls">
              {/* Placeholder for navigation icons (Home, Create, Profile, etc.) */}
              <span>Hello, {user.username}!</span> {/* Display username */}
              <button onClick={onLogout} className="logout-button">
                Logout
              </button>
            </div>
          ) : // Optional: Placeholder for login/signup links if not on auth page
          null}
        </div>
      </div>
    </header>
  );
}

export default Header;
