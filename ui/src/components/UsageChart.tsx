"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { format, subDays } from "date-fns";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface UsageChartProps {
  orgId: string;
}

export function UsageChart({ orgId }: UsageChartProps) {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      const to = new Date();
      const from = subDays(to, 6);

      try {
        const res = await fetch(
          `${API_URL}/v1/aggregate/daily?org_id=${orgId}&from=${format(from, "yyyy-MM-dd")}&to=${format(to, "yyyy-MM-dd")}&group_by=provider`
        );
        const json = await res.json();

        // Group by date
        const grouped: Record<string, any> = {};
        json.data?.forEach((item: any) => {
          if (!grouped[item.date]) {
            grouped[item.date] = { date: item.date, calls: 0, kwh: 0, co2: 0 };
          }
          grouped[item.date].calls += item.call_count;
          grouped[item.date].kwh += item.kwh;
          grouped[item.date].co2 += item.co2_kg;
        });

        setData(Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date)));
      } catch (err) {
        console.error("Failed to fetch chart data:", err);
      }
    }
    fetchData();
  }, [orgId]);

  if (data.length === 0) {
    return <p className="text-slate-500 text-center py-8">No data available for the past 7 days</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <Line yAxisId="left" type="monotone" dataKey="calls" stroke="#3b82f6" name="API Calls" />
        <Line yAxisId="right" type="monotone" dataKey="co2" stroke="#ef4444" name="CO₂ (kg)" />
      </LineChart>
    </ResponsiveContainer>
  );
}
