import { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: ReactNode;
  helpText?: string;
  icon?: ReactNode;
  accent?: "brand" | "emerald" | "amber" | "red" | "sky";
}

const ACCENTS: Record<NonNullable<StatCardProps["accent"]>, string> = {
  brand: "bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300",
  emerald: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  amber: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  red: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
  sky: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
};

export function StatCard({ label, value, helpText, icon, accent = "brand" }: StatCardProps) {
  return (
    <div className="card flex items-start justify-between">
      <div>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
        <p className="stat-figure mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{value}</p>
        {helpText && <p className="mt-1 text-xs text-gray-400">{helpText}</p>}
      </div>
      {icon && (
        <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg ${ACCENTS[accent]}`}>
          {icon}
        </div>
      )}
    </div>
  );
}
