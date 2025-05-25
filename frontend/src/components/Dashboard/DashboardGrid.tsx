// import React from "react";
import { Search, ShieldCheck, Network, Eye } from "lucide-react";
import DashboardCard from "./DashboardCard";

const DashboardGrid = () => {
  const cards = [
    {
      title: "What is OSINT?",
      description:
        "OSINT stands for Open Source Intelligence—gathered legally from publicly available sources to aid in investigations.",
      Icon: Eye,
    },
    {
      title: "Recon Tools",
      description:
        "Tools like theHarvester and Amass help automate information collection on emails, subdomains, and IPs.",
      Icon: Search,
    },
    {
      title: "Network Mapping",
      description:
        "Understanding your target's infrastructure via DNS records, IP ranges, and ASN lookups is key in OSINT.",
      Icon: Network,
    },
    {
      title: "Security Awareness",
      description:
        "OSINT highlights how leaked or exposed data can be exploited—educating users is vital for prevention.",
      Icon: ShieldCheck,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-10">
      {cards.map((card, index) => (
        <DashboardCard key={index} {...card} />
      ))}
    </div>
  );
};

export default DashboardGrid;
