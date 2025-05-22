import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import Dashboard from './components/Dashboard/Dashboard';
import Login from './components/Login/Login';
import ScanDomain from './components/ScanDomain/ScanDomain';
import Navbar from './components/Navbar/Navbar';
import NotFound from './components/NotFound/NotFound';
import ToastProvider from './components/UI/Toast';
import BackgroundParticles from './components/UI/BackgroundParticles';

const App: React.FC = () => (
  <AuthProvider>
    <ToastProvider />
    <BackgroundParticles/>
    <Router>
       <Navbar />
      <Routes>
        <Route path="" element={<Login />} />
        <Route path="dashboard" element={<Dashboard />} />
         <Route path="scandomain" element={<ScanDomain />} />
         <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  </AuthProvider>
);

export default App;
