"use client";

import { useEffect, useState } from "react";
import { DashboardCard } from "@/components/DashboardCard";
import { UsageChart } from "@/components/UsageChart";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface TodayData {
  date: string;
  org_id: string;
  call_count: number;
  kwh: number;
  water_liters: number;
  co2_kg: number;
  top_providers: Array<{ provider: string; count: number }>;
  top_models: Array<{ model: string; count: number }>;
}

export default function Home() {
  const [data, setData] = useState<TodayData | null>(null);
  const [loading, setLoading] = useState(true);

  // Demo: use org_demo
  const orgId = "org_demo";

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch(`${API_URL}/v1/today?org_id=${orgId}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Failed to fetch today's data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [orgId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">🌱 Ecomind</h1>
          <p className="text-slate-600 dark:text-slate-400 mb-8">Loading...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">🌱 Ecomind</h1>
          <p className="text-slate-600 dark:text-slate-400">
            Organization: <span className="font-mono">{orgId}</span> • Today: {data?.date}
          </p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <DashboardCard
            title="API Calls"
            value={data?.call_count || 0}
            unit=""
            icon="📊"
          />
          <DashboardCard
            title="Energy"
            value={(data?.kwh || 0).toFixed(4)}
            unit="kWh"
            icon="⚡"
          />
          <DashboardCard
            title="Water"
            value={(data?.water_liters || 0).toFixed(4)}
            unit="L"
            icon="💧"
          />
          <DashboardCard
            title="CO₂"
            value={(data?.co2_kg || 0).toFixed(4)}
            unit="kg"
            icon="🌍"
          />
        </div>

        {/* Top Providers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Top Providers</h2>
            {data?.top_providers && data.top_providers.length > 0 ? (
              <div className="space-y-3">
                {data.top_providers.map((p) => (
                  <div key={p.provider} className="flex justify-between items-center">
                    <span className="font-medium">{p.provider}</span>
                    <span className="text-slate-600 dark:text-slate-400">{p.count} calls</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500">No data yet</p>
            )}
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Top Models</h2>
            {data?.top_models && data.top_models.length > 0 ? (
              <div className="space-y-3">
                {data.top_models.map((m) => (
                  <div key={m.model} className="flex justify-between items-center">
                    <span className="font-medium font-mono text-sm">{m.model}</span>
                    <span className="text-slate-600 dark:text-slate-400">{m.count} calls</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500">No data yet</p>
            )}
          </div>
        </div>

        {/* Usage Chart Placeholder */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Usage Trends (7 days)</h2>
          <UsageChart orgId={orgId} />
        </div>
      </div>
    </main>
  );
}
