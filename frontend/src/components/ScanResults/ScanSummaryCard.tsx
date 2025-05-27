import React from "react";

interface ScanSummaryCardProps {
  title: string;
  domain?: string;
  startedAt?: string;
  finishedAt?: string;
  results?: {
    subdomains?: any[];
    emails?: any[];
    hosts?: any[];
    ips?: any[];
    [key: string]: any;
  };
  onShowDetails?: () => void;
}

const ScanSummaryCard: React.FC<ScanSummaryCardProps> = ({
  domain,
  startedAt,
  finishedAt,
  results,
  onShowDetails,
}) => {
  return (
    <div className="bg-black/20 p-4 rounded-lg shadow flex flex-col gap-2 mb-4">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-2">
        <span className="font-bold text-lg text-app-primary">
           {domain}
        </span>
        <span className="text-sm text-app-secondary">
          Started: {startedAt ? new Date(startedAt).toLocaleString() : "-"}
        </span>
        <span className="text-sm text-app-secondary">
          Finished: {finishedAt ? new Date(finishedAt).toLocaleString() : "-"}
        </span>
      </div>
      <div className="border-t border-white/10 my-2" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {results?.subdomains?.length ?? 0}
          </div>
          <div className="text-sm text-app-secondary">Subdomains</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {results?.emails?.length ?? 0}
          </div>
          <div className="text-sm text-app-secondary">Emails</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {results?.hosts?.length ?? 0}
          </div>
          <div className="text-sm text-app-secondary">Hosts</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {results?.ips?.length ?? 0}
          </div>
          <div className="text-sm text-app-secondary">IPs</div>
        </div>
      </div>
      <button
        className="mt-4 bg-app-accent text-black px-4 py-2 rounded hover:bg-app-primary transition"
        onClick={onShowDetails}
      >
        Show Details
      </button>
    </div>
  );
};

export default ScanSummaryCard;