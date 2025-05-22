import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

const ScanResults: React.FC = () => {
  const { scan_id } = useParams();
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch(`/api/scan/${scan_id}/results`);
      if (res.ok) {
        const data = await res.json();
        setResults(data);
        if (data.status === 'finished') {
          clearInterval(interval);
          setLoading(false);
        }
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [scan_id]);

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', textAlign: 'center' }}>
      <h1>Scan Results</h1>
      {loading && <p>Scanning... (refreshes automatically)</p>}
      {results && (
        <div>
          <h2>theHarvester</h2>
          <pre>{JSON.stringify(results.theHarvester, null, 2)}</pre>
          <h2>Amass</h2>
          <pre>{JSON.stringify(results.amass, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ScanResults;