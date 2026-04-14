"use client";
import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, AlertTriangle, Globe, Users, TrendingUp, Zap } from "lucide-react";
import { getStats, getRiskScore } from "@/lib/api";
import { StatSkeleton, Skeleton } from "@/components/Skeleton";
import { AlertBanner } from "@/components/AlertBanner";

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ff0000",
  high: "#ef4444",
  medium: "#f59e0b",
  low: "#10b981",
  info: "#0ea5e9",
};

const containerVars = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVars = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [risk, setRisk] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getStats(), getRiskScore()])
      .then(([s, r]) => { setStats(s); setRisk(r); })
      .catch((err) => {
        console.error("Dashboard data load failure", err);
        setError("Unable to synchronize with SIEM backend. Retrying automatically...");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-8 p-8">
        <div className="page-header">
          <Skeleton className="h-10 w-64 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="stats-grid">
          {[1, 2, 3, 4].map(i => <StatSkeleton key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
           <Skeleton className="h-64 w-full" />
           <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-20 text-center px-4">
        <AlertTriangle size={64} className="text-[var(--danger)] mx-auto mb-6" />
        <h2 className="text-2xl font-bold mb-4">Core Service Unavailable</h2>
        <AlertBanner type="error" message={error} />
        <button onClick={() => window.location.reload()} className="btn btn-primary mt-4">
          Attempt Manual Reconnect
        </button>
      </div>
    );
  }

  if (!stats || stats.total_events === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center py-20 px-4"
      >
        <div className="relative inline-block mb-8">
            <Shield size={80} className="text-[var(--accent-primary)] opacity-20" />
            <Zap size={40} className="text-[var(--accent-primary)] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </div>
        <h2 className="text-3xl font-bold mb-3">Initialize SIEM Operations</h2>
        <p className="text-[var(--text-muted)] max-w-md mx-auto mb-10 text-lg">
          No datasets detected in the current SOC environment. Connect a log source to activate AI threat detection.
        </p>
        <div className="flex justify-center gap-4">
            <a href="/upload" className="btn btn-primary px-8 py-3">
              Deploy Logs
            </a>
            <a href="/chat" className="btn btn-outline px-8 py-3">
              Launch Copilot
            </a>
        </div>
      </motion.div>
    );
  }

  const severityData = stats.severity_distribution
    ? Object.entries(stats.severity_distribution).map(([name, value]) => ({
        name,
        value: value as number,
        fill: SEVERITY_COLORS[name] || "#64748b",
      }))
    : [];

  return (
    <motion.div 
      variants={containerVars}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      <div className="page-header">
        <motion.h1 variants={itemVars} className="text-3xl font-bold tracking-tight">
            🛡️ Security Operations Center
        </motion.h1>
        <motion.p variants={itemVars} className="text-[var(--text-muted)] mt-1">
            Real-time telemetry and AI-driven incident analysis
        </motion.p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <motion.div variants={itemVars} className="stat-card indigo">
          <div className="flex justify-between items-start">
            <div>
              <div className="stat-value">{stats.total_events?.toLocaleString()}</div>
              <div className="stat-label">Ingested Events</div>
            </div>
            <TrendingUp size={20} className="text-[var(--accent-primary)]" />
          </div>
        </motion.div>
        
        <motion.div variants={itemVars} className="stat-card red">
          <div className="flex justify-between items-start">
            <div>
              <div className="stat-value text-[var(--danger)]">{stats.suspicious_events}</div>
              <div className="stat-label">Filtered Threats</div>
            </div>
            <AlertTriangle size={20} className="text-[var(--danger)]" />
          </div>
        </motion.div>

        <motion.div variants={itemVars} className="stat-card green">
          <div className="flex justify-between items-start">
            <div>
              <div className="stat-value text-[var(--success)]">{stats.unique_ips}</div>
              <div className="stat-label">Active Vectors</div>
            </div>
            <Globe size={20} className="text-[var(--success)]" />
          </div>
        </motion.div>

        <motion.div variants={itemVars} className="stat-card amber">
          <div className="flex justify-between items-start">
            <div>
              <div className="stat-value text-[var(--warning)]">{stats.unique_users}</div>
              <div className="stat-label">Tracked Accounts</div>
            </div>
            <Users size={20} className="text-[var(--warning)]" />
          </div>
        </motion.div>
      </div>

      {/* Risk Score + Severity Pie */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div variants={itemVars} className="card overflow-hidden">
          <div className="card-header pb-6 border-b border-[var(--border-color)] mb-6">
            <h3 className="card-title flex items-center gap-2">
                <Zap size={18} className="text-[var(--accent-primary)]" />
                Aggregated Risk Vector
            </h3>
          </div>
          {risk && (
            <div className="flex flex-col md:flex-row items-center gap-12">
              <div className={`risk-circle ${risk.severity} shrink-0`}>
                <span className="score">{Math.round(risk.overall_score)}</span>
                <span className="label">Index</span>
              </div>
              <div className="flex-1 w-full space-y-4">
                {risk.factors?.map((f: any, i: number) => (
                  <div key={i}>
                    <div className="flex justify-between text-xs mb-1.5 px-0.5">
                      <span className="text-[var(--text-secondary)] font-medium uppercase tracking-wider">{f.factor}</span>
                      <span className="text-[var(--accent-secondary)] font-bold">+{f.impact}</span>
                    </div>
                    <div className="h-1.5 w-full bg-[rgba(255,255,255,0.03)] rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(f.impact * 4, 100)}%` }}
                        transition={{ duration: 2, ease: "easeOut", delay: 0.5 + (i * 0.1) }}
                        className="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--danger)]" 
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        <motion.div variants={itemVars} className="card">
          <div className="card-header pb-2">
            <h3 className="card-title">Event Severity Matrix</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                innerRadius={55}
                dataKey="value"
                stroke="none"
                paddingAngle={2}
              >
                {severityData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: "rgba(2, 4, 8, 0.95)", border: "1px solid var(--border-color)", borderRadius: 8, fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-3 mt-4">
            {severityData.map((d) => (
              <div key={d.name} className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ background: d.fill, boxShadow: `0 0 8px ${d.fill}` }} />
                <span className="text-xs text-[var(--text-muted)] capitalize truncate">
                  {d.name}: {d.value}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Top IPs + Failed Login Trend */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <motion.div variants={itemVars} className="card">
          <div className="card-header border-b border-[var(--border-color)] pb-4 mb-6">
            <h3 className="card-title">Hostile Infrastructure (Source IPs)</h3>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={stats.top_source_ips?.slice(0, 10)} layout="vertical" margin={{ left: -10, right: 20 }}>
              <XAxis type="number" hide />
              <YAxis dataKey="ip" type="category" stroke="var(--text-muted)" fontSize={11} width={120} axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                contentStyle={{ background: "rgba(2, 4, 8, 0.95)", border: "1px solid var(--border-color)", borderRadius: 8, fontSize: 12 }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={16}>
                {stats.top_source_ips?.map((entry: any, i: number) => (
                  <Cell
                    key={i}
                    fill={SEVERITY_COLORS[entry.severity] || "var(--accent-secondary)"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div variants={itemVars} className="card">
          <div className="card-header border-b border-[var(--border-color)] pb-4 mb-6">
            <h3 className="card-title">Anomalous Access Pulse (Failed Logins)</h3>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={stats.failed_login_trend}>
              <XAxis
                dataKey="time"
                stroke="var(--text-muted)"
                fontSize={10}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: string) => v.split(" ")[1] || v}
              />
              <YAxis stroke="var(--text-muted)" fontSize={10} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: "rgba(2, 4, 8, 0.95)", border: "1px solid var(--border-color)", borderRadius: 8, fontSize: 12 }}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="var(--danger)"
                strokeWidth={3}
                dot={{ fill: "var(--danger)", r: 4, strokeWidth: 0 }}
                activeDot={{ r: 6, fill: "#fff", stroke: "var(--danger)", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </motion.div>
  );
}
