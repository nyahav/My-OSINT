import axiosInstance from '../api/axiosInstance';

export const login = async (username: string, password: string) => {
  const response = await axiosInstance.get('/login', {
    auth: { username, password },
  });
  return response.data;
};

const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const fetchUserDetails = async (token: string) => {
  console.log("Fetching user details with token:", token);
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
     const text = await res.text();
    console.error("Failed to fetch user details:", text);
    throw new Error("Failed to fetch user");
  }

  return res.json();
};
