import React, { useState } from 'react';
import useAuth from '../../context/useAuth';
import toast from 'react-hot-toast';
import { Link, Navigate } from 'react-router-dom';

const ScanDomain: React.FC = () => {
  const [domain, setDomain] = useState('');
  //const { user, logout } = useAuth();

 
//   if (!user) {
//     return <p>Loading...</p>;
//   }
  const handleScan = async () => {
    if (!domain) {
      toast.error('Please enter a domain');
      return;
    }
    try {
      // Send domain to backend to start scan
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain }),
      });
      if (!res.ok) throw new Error('Failed to start scan');
      const { scan_id } = await res.json();
      toast.success('Scan started!');
      // Navigate to results page
      <Link to={`/scan-results/${scan_id}`} />
    } catch (err) {
      toast.error('Failed to start scan');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '2rem auto', textAlign: 'center' }}>
      <h1>Scan Domain</h1>
      <h3>Enter a domain to scan for OSINT information</h3>
      <input
        type="text"
        value={domain}
        onChange={e => setDomain(e.target.value)}
        placeholder="example.com"
        style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
      />
      <br />
      <button onClick={handleScan}>Scan</button>
    </div>
  );
};

export default ScanDomain;