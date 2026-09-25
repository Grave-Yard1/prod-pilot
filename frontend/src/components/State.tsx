export function Loading({ label = "Reading the floor…" }: { label?: string }) {
  return (
    <p className="state" role="status">
      {label}
    </p>
  );
}

export function Failure({ message }: { message: string }) {
  return (
    <p className="state error" role="alert">
      {message}
    </p>
  );
}

export function Lamp({ status }: { status: string }) {
  return <span className={`lamp ${status}`} aria-hidden="true" />;
}
