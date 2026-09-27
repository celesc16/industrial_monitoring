import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router";

import { AuthProvider } from "./auth/AuthContext";
import { ToastProvider } from "./components/Toast/ToastContext";
import App from "./App";

import "bootstrap-icons/font/bootstrap-icons.css";
import "./styles/tokens.css";
import "./styles/primitives.css";
import "./styles/theme.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>
);