interface DashboardCardProps {
  title: string;
  value: string | number;
  unit: string;
  icon: string;
}

export function DashboardCard({ title, value, unit, icon }: DashboardCardProps) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-600 dark:text-slate-400 text-sm font-medium">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold">{value}</span>
        <span className="text-slate-500 text-sm">{unit}</span>
      </div>
    </div>
  );
}
