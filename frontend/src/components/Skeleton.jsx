/** Sprint 4 — Shimmer skeleton placeholders. */

export function Skeleton({ w = '100%', h = 16, radius = 6, style }) {
  return (
    <span
      className="skeleton"
      style={{ width: w, height: h, borderRadius: radius, display: 'inline-block', ...style }}
    />
  );
}

export function KpiSkeleton() {
  return (
    <div className="kpi-card kpi-card-skeleton">
      <Skeleton w={44} h={44} radius={12} />
      <div style={{ flex: 1 }}>
        <Skeleton w="40%" h={22} />
        <div style={{ height: 6 }} />
        <Skeleton w="60%" h={12} />
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 4, cols = 5 }) {
  return (
    <div className="skeleton-table">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton-row">
          {Array.from({ length: cols }).map((__, j) => (
            <Skeleton key={j} w="100%" h={14} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton({ height = 220 }) {
  return <Skeleton w="100%" h={height} radius={12} />;
}
