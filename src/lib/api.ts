/**
 * SIEM Copilot Enterprise API Client
 * Production-ready bridge with exponential backoff retries and timeout protection.
 */
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
const BASE_URL =
  `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api`;
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000;

export interface UploadResult {
  message: string;
  events_count: number;
  log_source: string;
}

export interface RiskFactor {
  factor: string;
  impact: number;
}

export interface RiskScore {
  overall_score: number;
  severity: string;
  factors: RiskFactor[];
}

export interface DashboardStats {
  total_events: number;
  suspicious_events: number;
  unique_ips: number;
  unique_users: number;
  severity_distribution: Record<string, number>;
  top_source_ips: Array<{ ip: string; count: number; severity?: string }>;
  failed_login_trend: Array<{ time: string; count: number }>;
}

export interface Prediction {
  predicted_next_move: string;
  confidence: string;
  reasoning: string;
  recommended_actions: string[];
}

export interface TimelineEvent {
  timestamp?: string;
  event: string;
  severity: string;
  details?: string;
}

export interface AttackChain {
  incident_name: string;
  source_ip: string;
  severity: string;
  primary_attack_type: string;
  timeline: TimelineEvent[];
  ai_narrative: string;
  prediction: Prediction;
}

export interface Report {
  id: number;
  title: string;
  content: string;
  created_at?: string;
}

export interface ChatResponse {
  reply: string;
  sources_used: number;
}

/**
 * Enhanced fetch with retry logic and timeout protection.
 */
async function apiFetch<T>(endpoint: string, options: RequestInit = {}, retryCount = 0): Promise<T> {
  const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s SaaS timeout

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // SaaS Error Handling: Extract JSON error if possible
      const errorData: unknown = await response.json().catch(() => ({}));
      const errorMessage =
        typeof errorData === "object" && errorData !== null &&
        ("detail" in errorData || "error" in errorData)
          ? String(("detail" in errorData ? errorData.detail : errorData.error))
          : `Error ${response.status}`;

      // Retry logic for 5xx errors
      if (response.status >= 500 && retryCount < MAX_RETRIES) {
        const delay = INITIAL_RETRY_DELAY * Math.pow(2, retryCount);
        console.warn(`[API] Server error (${response.status}). Retrying in ${delay}ms...`);
        await new Promise(res => setTimeout(res, delay));
        return apiFetch(endpoint, options, retryCount + 1);
      }

      throw new Error(errorMessage);
    }

    return response.json() as Promise<T>;
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request timed out after 30 seconds. Please try again.");
    }

    // Retry on network errors
    if (retryCount < MAX_RETRIES) {
      const delay = INITIAL_RETRY_DELAY * Math.pow(2, retryCount);
      console.warn(`[API] Network error. Retrying in ${delay}ms...`);
      await new Promise(res => setTimeout(res, delay));
      return apiFetch(endpoint, options, retryCount + 1);
    }

    throw error;
  }
}

// ── LOGS ──────────────────────────────────────────────────

export async function uploadLog(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/logs/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}: ${JSON.stringify(errorData)}`);
  }

  return response.json() as Promise<UploadResult>;
}

export async function getStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/logs/stats");
}

export async function clearLogs() {
  return apiFetch("/logs/clear", { method: "DELETE" });
}

// ── ANALYSIS ──────────────────────────────────────────────

export async function getRiskScore(): Promise<RiskScore> {
  return apiFetch<RiskScore>("/analysis/risk-score");
}

export async function getAttackChains(): Promise<{ chains: AttackChain[] }> {
  return apiFetch<{ chains: AttackChain[] }>("/analysis/chains");
}

export async function getPredictions() {
  return apiFetch("/analysis/predictions");
}

// ── CHAT ──────────────────────────────────────────────────

export async function sendChat(message: string, contextLimit: number = 30): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/chat/", {
    method: "POST",
    body: JSON.stringify({ message, context_limit: contextLimit }),
  });
}

// ── REPORTS ──────────────────────────────────────────────

export async function generateReport(title: string = "Security Incident Report"): Promise<Report> {
  return apiFetch<Report>("/reports/generate", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function getReports(): Promise<Report[]> {
  return apiFetch<Report[]>("/reports/");
}

export async function getReport(id: number) {
  return apiFetch(`/reports/${id}`);
}
