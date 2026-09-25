export function Sparkline({ points, limit }: { points: number[]; limit: number }) {
  const width = 280;
  const height = 72;
  const max = Math.max(limit, ...points, 0.1) * 1.15;
  const coords = points
    .map((value, index) => {
      const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width;
      const y = height - (value / max) * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  const limitY = height - (limit / max) * height;
  const over = points[points.length - 1] > limit;

  return (
    <svg className="spark" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Recent readings against the limit">
      <line className="spark-limit" x1="0" y1={limitY} x2={width} y2={limitY} />
      <polyline className={over ? "spark-line over" : "spark-line"} points={coords} />
    </svg>
  );
}
