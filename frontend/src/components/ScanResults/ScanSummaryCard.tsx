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
  summary?: {
    total_subdomains?: number;
    total_emails?: number;
    total_hosts?: number;
    total_ips?: number;
  };
  onShowDetails?: () => void;
  isSummary?: boolean; 
}

const ScanSummaryCard: React.FC<ScanSummaryCardProps> = ({
  domain,
  startedAt,
  finishedAt,
  results,
  summary,
  onShowDetails,
  isSummary = false,
}) => {
  
  const displayData =
    isSummary && summary
      ? {
          subdomains: summary.total_subdomains ?? 0,
          emails: summary.total_emails ?? 0,
          hosts: summary.total_hosts ?? 0,
          ips: summary.total_ips ?? 0,
      }
      : {
        subdomains: results?.subdomains?.length ?? 0,
        emails: results?.emails?.length ?? 0,
        hosts: results?.hosts?.length ?? 0,
        ips: results?.ips?.length ?? 0,
      };

  return (
    <div className="bg-black/20 p-4 rounded-lg shadow flex flex-col gap-2 mb-4">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-2">
        {!isSummary && (
          <>
          <span className="font-bold text-lg text-app-primary">
            {domain}
          </span>
          
            <span className="text-sm text-app-secondary">
              Started: {startedAt ? new Date(startedAt).toLocaleString() : "-"}
            </span>
            <span className="text-sm text-app-secondary">
              Finished: {finishedAt ? new Date(finishedAt).toLocaleString() : "-"}
            </span>
          </>
        )}
      </div>
      <div className="border-t border-white/10 my-2" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {displayData.subdomains}
          </div>
          <div className="text-sm text-app-secondary">Subdomains</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {displayData.emails}
          </div>
          <div className="text-sm text-app-secondary">Emails</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {displayData.hosts}
          </div>
          <div className="text-sm text-app-secondary">Hosts</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-app-accent">
            {displayData.ips}
          </div>
          <div className="text-sm text-app-secondary">IPs</div>
        </div>
      </div>

      {/* הצג כפתור רק אם זה לא summary */}
      {!isSummary && onShowDetails && (
        <button
          className="mt-4 bg-app-accent text-black px-4 py-2 rounded hover:bg-app-primary transition"
          onClick={onShowDetails}
        >
          Show Details
        </button>
      )}
    </div>
  );
};

export default ScanSummaryCard;