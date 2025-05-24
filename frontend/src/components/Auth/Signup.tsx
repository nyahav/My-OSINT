import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import  useAuth  from "../../context/useAuth";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch("/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
    if (res.ok) {
      const user = await res.json();
      login(user);
      navigate("/dashboard");
    } else {
      alert("Signup failed");
    }
  };

 return (
  <div className="min-h-screen bg-app-bg text-app-text flex items-center justify-center p-6">
    <form
      onSubmit={handleSubmit}
      className="bg-white bg-opacity-5 backdrop-blur-md border border-white/10 rounded-2xl p-10 shadow-md w-full max-w-md space-y-6"
    >
      <h2 className="text-2xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-app-primary to-app-accent">
        Sign Up
      </h2>

      <div className="space-y-4">
        <input
          className="w-full px-4 py-2 rounded-lg bg-app-bg border border-white/20 focus:ring-2 focus:ring-app-accent placeholder:text-app-secondary text-app-text transition-all"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
        <input
          className="w-full px-4 py-2 rounded-lg bg-app-bg border border-white/20 focus:ring-2 focus:ring-app-accent placeholder:text-app-secondary text-app-text transition-all"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          type="email"
          required
        />
        <input
          className="w-full px-4 py-2 rounded-lg bg-app-bg border border-white/20 focus:ring-2 focus:ring-app-accent placeholder:text-app-secondary text-app-text transition-all"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-app-primary text-white font-semibold rounded-lg hover:bg-opacity-90 transition-all shadow-sm"
      >
        Sign Up
      </button>
    </form>
  </div>
);
};

export default Signup;