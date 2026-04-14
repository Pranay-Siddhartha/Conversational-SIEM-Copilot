"use client";

export function Skeleton({ className = "", ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`animate-pulse rounded-md bg-[rgba(0,243,255,0.05)] ${className}`}
      {...props}
    />
  );
}

export function StatSkeleton() {
  return (
    <div className="stat-card">
      <Skeleton className="h-4 w-24 mb-2" />
      <Skeleton className="h-8 w-16" />
    </div>
  );
}

export function TableSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex gap-4 p-4 border border-[var(--border-color)] rounded-md">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      ))}
    </div>
  );
}
