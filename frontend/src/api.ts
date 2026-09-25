import { useCallback, useEffect, useRef, useState } from "react";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    let message = response.statusText || "Request failed";
    try {
      const body: unknown = await response.json();
      if (body && typeof body === "object" && "detail" in body && typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // The body was not JSON.
    }
    throw new ApiError(response.status, message);
  }
  return response.json() as Promise<T>;
}

export function useApi<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(path !== null);
  const [tick, setTick] = useState(0);
  const reload = useCallback(() => setTick((value) => value + 1), []);
  const pathRef = useRef(path);

  useEffect(() => {
    if (!path) {
      setData(null);
      setLoading(false);
      return;
    }
    const pathChanged = pathRef.current !== path;
    pathRef.current = path;
    let cancelled = false;
    if (pathChanged) {
      setLoading(true);
      setData(null);
    }
    api<T>(path).then(
      (value) => {
        if (!cancelled) {
          setData(value);
          setError(null);
          setLoading(false);
        }
      },
      (reason: unknown) => {
        if (!cancelled) {
          const message = reason instanceof Error ? reason.message : "Request failed";
          setError(message === "Failed to fetch" ? "The floor feed is not responding." : message);
          setLoading(false);
        }
      },
    );
    return () => {
      cancelled = true;
    };
  }, [path, tick]);

  return { data, error, loading, reload };
}
