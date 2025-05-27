import React from "react";
import * as XLSX from "xlsx";

interface ScanDetailsModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  domain?: string;
  startedAt?: string;
  finishedAt?: string;
  results?: { [key: string]: any };
}

const ScanDetailsModal: React.FC<ScanDetailsModalProps> = ({
  open,
  onClose,
  title,
  domain,
  startedAt,
  finishedAt,
  results,
}) => {
  if (!open) return null;
  const handleExport = () => {
    const data: any[] = [];
    if (results) {
      Object.entries(results).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((item) => {
            data.push({ Type: key, Value: typeof item === "object" ? JSON.stringify(item) : item });
          });
        } else {
          data.push({ Type: key, Value: typeof value === "object" ? JSON.stringify(value) : value });
        }
      });
    }
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Details");
    XLSX.writeFile(wb, `${title}_${domain || "scan"}.xlsx`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-white rounded-xl shadow-lg max-w-2xl w-full p-6 relative">
        <button
          className="absolute top-2 right-4 text-xl text-gray-500 hover:text-red-500"
          onClick={onClose}
        >
          ×
        </button>
        <h2 className="text-2xl font-bold mb-2 text-app-primary">{title} - {domain}</h2>
        <div className="mb-2 text-sm text-black">
          <span>Started: {startedAt ? new Date(startedAt).toLocaleString() : "-"}</span> |{" "}
          <span>Finished: {finishedAt ? new Date(finishedAt).toLocaleString() : "-"}</span>
        </div>
        <div className="max-h-80 overflow-y-auto mb-4">
          <ul className="list-disc pl-5 text-gray-900 space-y-1">
            {results &&
              Object.entries(results).map(([key, value]) =>
                Array.isArray(value) ? (
                  <li key={key}>
                    <span className="font-semibold">{key}:</span> {value.length} פריטים
                    <ul className="list-decimal pl-5 text-xs">
                      {value.map((item, idx) => (
                        <li key={idx}>{typeof item === "object" ? JSON.stringify(item) : item}</li>
                      ))}
                    </ul>
                  </li>
                ) : (
                  <li key={key}>
                    <span className="font-semibold">{key}:</span> {typeof value === "object" ? JSON.stringify(value) : value}
                  </li>
                )
              )}
          </ul>
        </div>
        <button
          className="bg-app-accent text-black px-4 py-2 rounded hover:bg-app-primary transition"
          onClick={handleExport}
        >
          ייצוא לאקסל
        </button>
      </div>
    </div>
  );
};

export default ScanDetailsModal;