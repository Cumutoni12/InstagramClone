import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css"; // Your global CSS
import { AuthProvider } from "./context/AuthContext.jsx"; // Import AuthProvider

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      {" "}
      {/* Wrap App with AuthProvider */}
      <App />
    </AuthProvider>
  </React.StrictMode>
);
