export function sentence(text: string): string {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function statusLabel(status: string): string {
  if (status === "running") return "Running";
  if (status === "watch") return "Watch";
  if (status === "alarm") return "Alarm";
  if (status === "down") return "Down";
  if (status === "open") return "Open";
  if (status === "decided") return "Call recorded";
  if (status === "repaired") return "In history";
  return status;
}

export function callWord(action: string): string {
  if (action === "slow") return "Slow";
  if (action === "stop") return "Stop";
  if (action === "continue") return "Continue";
  return action;
}

export function callDetail(action: string): string {
  if (action === "slow") return "Hold the station. Call the trade before you clear anything.";
  if (action === "stop") return "Stop the station. This is still your call to make.";
  return "Keep the station running and watch the next cycle.";
}

export function formatWhen(iso: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    day: "numeric",
    month: "short",
  }).format(new Date(iso));
}

export function metricLabel(metric: string): string {
  if (metric === "vibration") return "Vibration";
  if (metric === "temperature") return "Temperature";
  return metric;
}

export function pointsLabel(points: number): string {
  const value = points / 10;
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

export function partLabel(key: string, families: string[]): string {
  if (key === "machine") return "Same machine";
  if (key === "symptom") return "Symptom match";
  if (key === "family") {
    return families.length ? `Shared ${families.join(", ")} family` : "Shared symptom family";
  }
  if (key === "error_code") return "Error code";
  if (key === "observation") return "Note overlap";
  return key;
}

export const PART_ORDER = ["machine", "symptom", "family", "error_code", "observation"];

export const ZONES = ["Drive Unit", "Body", "Paint", "General Assembly"];
