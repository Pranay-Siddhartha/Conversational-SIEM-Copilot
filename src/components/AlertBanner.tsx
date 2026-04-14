"use client";
import { AlertCircle, CheckCircle, Info, X } from "lucide-react";

interface AlertProps {
  type?: "info" | "success" | "warning" | "error";
  message: string;
  onClose?: () => void;
}

export function AlertBanner({ type = "info", message, onClose }: AlertProps) {
  const styles = {
    info: { bg: "rgba(0, 163, 255, 0.1)", border: "var(--info)", icon: <Info size={18} className="text-[#00a3ff]" /> },
    success: { bg: "rgba(0, 255, 102, 0.1)", border: "var(--success)", icon: <CheckCircle size={18} className="text-[#00ff66]" /> },
    warning: { bg: "rgba(255, 184, 0, 0.1)", border: "var(--warning)", icon: <AlertCircle size={18} className="text-[#ffb800]" /> },
    error: { bg: "rgba(255, 0, 85, 0.1)", border: "var(--danger)", icon: <AlertCircle size={18} className="text-[#ff0055]" /> },
  };

  const { bg, border, icon } = styles[type];

  return (
    <div 
      style={{ background: bg, borderColor: border }}
      className="flex items-center gap-3 p-4 border rounded-md mb-6 animate-fadeIn"
    >
      {icon}
      <p className="flex-1 text-sm font-medium">{message}</p>
      {onClose && (
        <button onClick={onClose} className="text-[var(--text-muted)] hover:text-white transition-colors">
          <X size={18} />
        </button>
      )}
    </div>
  );
}
