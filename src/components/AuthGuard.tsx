"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [mounted] = useState(
    () => typeof window !== "undefined" && Boolean(localStorage.getItem("siem_username")),
  );

  useEffect(() => {
    const user = localStorage.getItem("siem_username");
    if (!user) {
      router.push("/login");
    }
  }, [router]);

  if (!mounted) {
    return (
      <div className="loading-overlay" style={{ height: "100vh" }}>
        <div className="spinner" />
        <p>Connecting to secure network...</p>
      </div>
    );
  }

  return <>{children}</>;
}
