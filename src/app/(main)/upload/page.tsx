"use client";
import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, CheckCircle, AlertCircle, FileText, Database, ArrowRight, Activity } from "lucide-react";
import { uploadLog, clearLogs } from "@/lib/api";
import { AlertBanner } from "@/components/AlertBanner";

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [dragover, setDragover] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setUploading(true);
    setError("");
    setResult(null);

    try {
      const data = await uploadLog(file);
      setResult(data);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "System encountered an error during telemetry ingestion."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragover(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleClear = async () => {
    if (!confirm("This will permanently purge all telemetry records from Supabase. Proceed?")) return;
    try {
      await clearLogs();
      setResult(null);
      setError("");
      alert("Telemetry storage purged successfully.");
    } catch {
      setError("Critical failure while attempting to purge logs.");
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="max-w-5xl"
    >
      <div className="page-header mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
            <Database className="text-[var(--accent-primary)]" />
            Telemetry Ingestion
        </h1>
        <p className="text-[var(--text-muted)] mt-1">Deploy raw security logs to the AI-augmented SOC environment</p>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
            <AlertBanner type="error" message={error} onClose={() => setError("")} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Zone */}
      <motion.div
        whileHover={{ scale: 1.005 }}
        whileTap={{ scale: 0.995 }}
        className={`upload-zone relative overflow-hidden ${dragover ? "dragover" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
        onDragLeave={() => setDragover(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-[var(--border-color)]">
            {uploading && (
                <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] shadow-[0_0_10px_var(--accent-primary)]"
                />
            )}
        </div>

        <input
          ref={fileRef}
          type="file"
          style={{ display: "none" }}
          accept=".log,.csv,.json,.txt"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
        {uploading ? (
          <div className="py-8">
            <Activity className="animate-spin text-[var(--accent-primary)] mx-auto mb-4" size={40} />
            <h3 className="text-xl font-bold">Synchronizing Investigation Data...</h3>
            <p className="text-[var(--text-muted)]">Parsing headers, normalizing timestamps, and indexing records</p>
          </div>
        ) : (
          <div className="py-8">
            <Upload size={56} className="text-[var(--accent-primary)] mx-auto mb-6 opacity-80" />
            <h3 className="text-xl font-bold">Transmit Telemetry Package</h3>
            <p className="text-[var(--text-muted)] mb-6">Drop log bundle here or click to authenticate file selection</p>
            <div className="flex justify-center gap-3">
              <span className="format-badge px-3 py-1 bg-[rgba(0,243,255,0.05)] border border-[rgba(0,243,255,0.1)] rounded text-xs font-mono">.LOG</span>
              <span className="format-badge px-3 py-1 bg-[rgba(0,243,255,0.05)] border border-[rgba(0,243,255,0.1)] rounded text-xs font-mono">.CSV</span>
              <span className="format-badge px-3 py-1 bg-[rgba(0,243,255,0.05)] border border-[rgba(0,243,255,0.1)] rounded text-xs font-mono">.JSON</span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Success Result */}
      <AnimatePresence>
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card mt-12 border-[var(--success)] shadow-[0_0_30px_rgba(16,185,129,0.05)]"
          >
            <div className="flex items-center gap-4 mb-8">
              <div className="p-2 bg-[rgba(16,185,129,0.1)] rounded-full border border-[rgba(16,185,129,0.2)]">
                <CheckCircle size={28} className="text-[var(--success)]" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-[var(--success)]">Deployment Successful</h3>
                <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Telemetry Indexing Verified</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="stat-card indigo bg-[rgba(0,243,255,0.03)] border-[rgba(0,243,255,0.1)]">
                <div className="stat-value text-3xl font-bold">{result.events_count?.toLocaleString()}</div>
                <div className="stat-label text-xs uppercase text-[var(--text-muted)]">Events Indexed</div>
              </div>
              <div className="stat-card green bg-[rgba(16,185,129,0.03)] border-[rgba(16,185,129,0.1)]">
                <div className="stat-value text-xl font-bold uppercase truncate">{result.log_source}</div>
                <div className="stat-label text-xs uppercase text-[var(--text-muted)]">Schema Detected</div>
              </div>
              <div className="stat-card amber bg-[rgba(245,158,11,0.03)] border-[rgba(245,158,11,0.1)] flex items-center gap-3">
                <Activity size={20} className="text-[var(--warning)]" />
                <span className="text-sm font-medium">{result.message}</span>
              </div>
            </div>

            <div className="mt-10 flex flex-wrap gap-4 pt-8 border-t border-[var(--border-color)]">
              <a href="/" className="btn btn-primary px-6 flex items-center gap-2">
                Launch SOC Dashboard <ArrowRight size={16} />
              </a>
              <a href="/chat" className="btn btn-outline px-6">Investigate Alerts</a>
              <a href="/timeline" className="btn btn-outline px-6">View Event Timeline</a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Auxiliary Actions */}
      <div className="mt-12 flex flex-wrap gap-6 items-center">
        <button className="btn btn-danger px-6 py-2.5" onClick={handleClear}>
          Purge Telemetry Storage
        </button>
        
        <div className="h-6 w-px bg-[var(--border-color)] hidden md:block" />
        
        <a href="/sample_auth.log" download className="text-sm flex items-center gap-2 text-[var(--accent-secondary)] hover:text-white transition-colors">
          <FileText size={16} /> Download Enterprise Sample Deck
        </a>

        <div className="hidden lg:flex items-center gap-3 text-[10px] text-[var(--success)] bg-[rgba(16,185,129,0.05)] px-4 py-2 border border-[rgba(16,185,129,0.15)] rounded uppercase font-bold tracking-widest">
          <Activity size={12} /> Live Environment
        </div>
      </div>
    </motion.div>
  );
}
