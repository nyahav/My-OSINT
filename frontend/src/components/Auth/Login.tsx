import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../../context/useAuth";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); 
  const [isLoading, setIsLoading] = useState(false); 
  const { login } = useAuth();
  const navigate = useNavigate();

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); 
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (res.ok) {
        const user = await res.json();
        login(user);
        navigate("/dashboard");
      } else {
        
        const errorData = await res.json().catch(() => ({}));
        const errorMessage = errorData.message || "Login failed. Please check your credentials.";
        setError(errorMessage);
      }
    } catch (err) {
      
      setError("Network error. Please check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
  <div className="min-h-screen bg-app-bg text-app-text flex items-center justify-center p-6">
    <form
      onSubmit={handleSubmit}
      className="bg-white bg-opacity-5 backdrop-blur-md border border-white/10 rounded-2xl p-10 shadow-md w-full max-w-md space-y-6"
    >
      <h1 className="text-2xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-app-primary to-app-accent">
        Login
      </h1>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-app-secondary mb-1">
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
            className="w-full px-4 py-2 rounded-lg bg-app-bg border border-white/20 focus:ring-2 focus:ring-app-accent placeholder:text-app-secondary text-app-text transition-all"
            placeholder="Enter your username"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-app-secondary mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
            className="w-full px-4 py-2 rounded-lg bg-app-bg border border-white/20 focus:ring-2 focus:ring-app-accent placeholder:text-app-secondary text-app-text transition-all"
            placeholder="Enter your password"
          />
        </div>

        {error && (
          <p className="text-app-danger text-sm text-center font-medium">
            {error}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-4 py-2 bg-app-primary text-white font-semibold rounded-lg hover:bg-opacity-90 transition-all shadow-sm disabled:opacity-50"
      >
        {isLoading ? "Logging in..." : "Login"}
      </button>
    </form>
  </div>
);
};

export default Login;