import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';


const ScanDomain: React.FC = () => {
  const [domain, setDomain] = useState('');
  const navigate = useNavigate();

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!domain) {
      toast.error('Please enter a domain');
      return;
    }
    try {
      // Send domain to backend to start scan
      const token = localStorage.getItem("token");
      console.log("Token being sent:", token);
      const res = await fetch(`${API_BASE_URL}/domain/scan`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`  
         },
        body: JSON.stringify({ domain }),
      });
      if (!res.ok) throw new Error('Failed to start scan');
      const { scan_id } = await res.json();
      console.log("Scan ID:", scan_id);
      toast.success('Scan started!');
      
      navigate(`/scan-results/${scan_id}`);
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

        <p className="text-app-secondary text-center text-base">
          Enter a domain to perform Open Source Intelligence gathering<br /> using
          industry-standard tools like{" "}
          <span className="text-app-accent font-semibold">theHarvester</span> and{" "}
          <span className="text-app-accent font-semibold">Amass</span>. <br />The results
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
      </div>
    </div>
  );
};

export default ScanDomain;