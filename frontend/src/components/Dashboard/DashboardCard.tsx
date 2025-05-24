import React from "react";
import { LucideIcon } from "lucide-react";

interface DashboardCardProps {
  title: string;
  description: string;
  Icon: LucideIcon;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ title, description, Icon }) => {
  return (
    <div className="bg-white bg-opacity-5 backdrop-blur-lg rounded-2xl border border-white/10 shadow-md p-6 space-y-4 hover:shadow-lg transition-all">
      <div className="flex items-center gap-3">
        <Icon className="text-app-primary w-6 h-6" />
        <h3 className="text-lg font-semibold text-app-text">{title}</h3>
      </div>
      <p className="text-sm text-app-secondary">{description}</p>
    </div>
  );
};

export default DashboardCard;
