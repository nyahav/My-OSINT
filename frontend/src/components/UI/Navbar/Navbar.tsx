import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => (
  <nav style={{
    background: '#222',
    color: '#fff',
    padding: '1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  }}>
    <div>
      <Link to="/dashboard" style={{ color: '#fff', marginRight: '1rem', textDecoration: 'none' }}>Dashboard</Link>
      <Link to="/scandomain" style={{ color: '#fff', marginRight: '1rem', textDecoration: 'none' }}>Scan Domain</Link>
    </div>
    <div>
      <Link to="/" style={{ color: '#fff', textDecoration: 'none' }}>Logout</Link>
    </div>
  </nav>
);

export default Navbar;