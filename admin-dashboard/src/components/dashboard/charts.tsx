"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AdminStats } from "@/lib/api/acvs";

const PIE_COLORS = ["#10b981", "#f59e0b", "#f43f5e", "#0ea5e9", "#8b5cf6", "#64748b"];

export function ScanModalityChart({ stats }: { stats: AdminStats | undefined }) {
  const data = useMemo(() => {
    if (!stats) return [];
    return Object.entries(stats.scans.by_modality).map(([name, value]) => ({ name, value }));
  }, [stats]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Scans by modality</CardTitle>
        <CardDescription>Distribution across all detection types</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-muted-foreground py-8 text-center">No data yet</p>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={3}
              >
                {data.map((_, idx) => (
                  <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  borderRadius: 8,
                  border: "1px solid hsl(var(--border))",
                  background: "hsl(var(--popover))",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
          {data.map((d, i) => (
            <div key={d.name} className="flex items-center gap-2">
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ background: PIE_COLORS[i % PIE_COLORS.length] }}
              />
              <span className="capitalize">{d.name.replace("_", " ")}</span>
              <span className="ml-auto font-medium">{d.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ScanLabelChart({ stats }: { stats: AdminStats | undefined }) {
  const data = useMemo(() => {
    if (!stats) return [];
    return Object.entries(stats.scans.by_label).map(([name, value]) => ({ name: name.replace("_", " "), value }));
  }, [stats]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Verdict distribution</CardTitle>
        <CardDescription>Labels assigned by the AI engine</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-muted-foreground py-8 text-center">No data yet</p>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data} margin={{ left: -20, right: 10, top: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  borderRadius: 8,
                  border: "1px solid hsl(var(--border))",
                  background: "hsl(var(--popover))",
                }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {data.map((_, idx) => (
                  <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
