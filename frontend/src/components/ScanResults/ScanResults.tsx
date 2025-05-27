import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ScanSummaryCard from './ScanSummaryCard';
import ScanDetailsModal from './ScanDetailsModal';

const ScanResults: React.FC = () => {
  const { scan_id } = useParams();
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [scannedDomain, setScannedDomain] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState<"theHarvester" | "amass" | null>(null);
  const navigate = useNavigate();

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    let interval: NodeJS.Timeout;
    let progressInterval: NodeJS.Timeout;

    // Simulate loading bar progress
    progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) return prev; 
        return Math.min(prev + 0.32, 95); 
      });
    }, 400);

    interval = setInterval(async () => {
      const token = localStorage.getItem("token");
      console.log("Sending request for results with token:", token);
      const res = await fetch(`${API_BASE_URL}/scan/${scan_id}/results`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        if (data.domain) setScannedDomain(data.domain);
        console.log("Received scan results:", data);
        setResults(data);
        if (data.status && data.status.toLowerCase() === 'finished') {
          clearInterval(interval);
          clearInterval(progressInterval);
          setProgress(100);
          setLoading(false);
        }
      } else if (res.status === 401) {
        setLoading(false);
        clearInterval(interval);
        clearInterval(progressInterval);
        navigate("/login");
      }
    }, 2000);

    return () => {
      clearInterval(interval);
      clearInterval(progressInterval);
    };
  }, [scan_id, API_BASE_URL, navigate]);
  console.log("loading:", loading, "results:", results, "progress:", progress); ;


return (
    <div className="min-h-screen bg-app-bg text-app-text flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-white bg-opacity-5 backdrop-blur-md border border-white/10 rounded-2xl shadow-lg p-8 space-y-6">
        {loading ? (
          <div className="space-y-4 text-center">
            <h1 className="text-2xl font-bold text-app-primary">Running OSINT scan - gathering intelligence...</h1>
            <p className="text-app-accent text-lg">
              {scannedDomain ? `Scanning domain: ${scannedDomain}` : "Loading domain..."}
            </p>
            <div className="w-full h-5 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="text-app-secondary text-sm">
              Scanning... Please wait while the scan completes.
            </p>
          </div>
        ) : results ? (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-app-primary to-app-accent bg-clip-text text-transparent hover:scale-105 hover:drop-shadow-glow transition duration-300 text-center">Scan Results</h1>

            <div>
              <h2 className="text-2xl font-semibold text-app-accent mb-2">theHarvester</h2>
                <ScanSummaryCard
                title="theHarvester"
                domain={scannedDomain || results.domain}
                startedAt={results.started_at}
                finishedAt={results.finished_at}
                results={results.theHarvester}
                onShowDetails={() => setShowDetails("theHarvester")}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-app-accent mb-2">Amass</h2>
              <pre className="bg-black/30 p-4 rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(results.amass, null, 2)}
              </pre>
            </div>
          </div>
        ) : (
          <p className="text-center text-app-secondary">No results found.</p>
        )}
      </div>
       <ScanDetailsModal
        open={showDetails === "theHarvester"}
        onClose={() => setShowDetails(null)}
        title="theHarvester"
        domain={scannedDomain || results?.domain}
        startedAt={results?.started_at}
        finishedAt={results?.finished_at}
        results={results?.theHarvester}
      />
    </div>
  );
};

export default ScanResults;

