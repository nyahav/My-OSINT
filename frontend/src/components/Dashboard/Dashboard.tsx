
import useAuth from "../../context/useAuth";
import { useNavigate } from "react-router-dom";
import DashboardGrid from "./DashboardGrid";




const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-app-bg text-app-text flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-2xl bg-white bg-opacity-5 backdrop-blur-md border border-white/10 rounded-2xl shadow-lg p-10 space-y-6">
        {/* Conditional Rendering based on user login status */}
        {user ? (
          // User is logged in: Show welcome message
          <h1 className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-app-primary to-app-accent">
            Welcome, {user.first_name || user.username}!
          </h1>
        ) : (
          // User is NOT logged in: Show login/sign-up options
          <div className="text-center space-y-4">
            <h2 className="text-xl font-semibold text-app-danger">You are not logged in.</h2>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => navigate("/login")}
                className="px-4 py-2 bg-app-primary text-white rounded-lg hover:bg-opacity-80 transition-all font-semibold shadow-md"
              >
                Login
              </button>
              <button
                onClick={() => navigate("/signup")}
                className="px-4 py-2 bg-app-accent text-black font-medium rounded-lg hover:bg-opacity-90 transition-all font-semibold shadow-md"
              >
                Sign Up
              </button>
            </div>
          </div>
        )}

        {/* DashboardGrid is always visible, regardless of login status */}
        <DashboardGrid />

       
        <div className="flex justify-center">
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-app-danger text-white rounded-lg hover:bg-opacity-80 transition-all font-semibold shadow-md"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
