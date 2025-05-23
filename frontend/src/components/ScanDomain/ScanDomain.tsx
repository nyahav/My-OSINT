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
    <div className="min-h-screen bg-app-bg text-app-text flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-white bg-opacity-5 backdrop-blur-md border border-white/10 rounded-2xl shadow-lg p-8 space-y-6">
        <h1 className="text-3xl font-bold text-app-primary text-center">
          OSINT Domain Scanner
        </h1>

        <p className="text-app-secondary text-center text-sm">
          Enter a domain to perform Open Source Intelligence gathering using
          industry-standard tools like{" "}
          <span className="text-app-accent font-semibold">theHarvester</span> and{" "}
          <span className="text-app-accent font-semibold">Amass</span>. The results
          will include emails, subdomains, hosts, and public metadata.
        </p>

        <form onSubmit={handleScan} className="space-y-4">
          <input
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.com"
            className="w-full px-4 py-2 rounded-lg border border-app-secondary bg-white bg-opacity-10 placeholder-app-secondary text-app-text focus:outline-none focus:ring-2 focus:ring-app-primary"
          />

          <button
            type="submit"
            className="w-full py-2 bg-app-primary hover:bg-opacity-80 text-white font-semibold rounded-lg transition-all duration-200 shadow hover:shadow-lg"
          >
            Scan
          </button>
        </form>

        {/* This could later show results */}
        {/* <div className="text-sm text-app-accent mt-4">
          Results will be displayed here...
        </div> */}
      </div>
    </div>
  );
};

export default ScanDomain;