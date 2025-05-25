import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import Dashboard from './components/Dashboard/Dashboard';
import Login from './components/Auth/Login';
import ScanDomain from './components/ScanDomain/ScanDomain';
import Navbar from './components/UI/Navbar/Navbar';
import NotFound from './components/NotFound/NotFound';
import ToastProvider from './components/UI/Toast';
import BackgroundParticles from './components/UI/BackgroundParticles';
import Signup from './components/Auth/Signup';

const App: React.FC = () => (
  <AuthProvider>
    <ToastProvider />
    <Router>
      <div className='min-h-screen' style={{ position: 'relative' }}>
        <BackgroundParticles />
        <Navbar />
        <Routes>
          <Route path="" element={<Dashboard />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="scandomain" element={<ScanDomain />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </Router>
  </AuthProvider>
);

export default App;
