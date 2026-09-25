import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

export type Role = "worker" | "supervisor" | "engineer";

export const PEOPLE: Record<Role, { name: string; title: string }> = {
  worker: { name: "Sam Keller", title: "Line worker" },
  supervisor: { name: "Alex Novak", title: "Production supervisor" },
  engineer: { name: "Lea Hoffmann", title: "Drive unit engineer" },
};

interface PersonaValue {
  role: Role;
  setRole: (role: Role) => void;
  name: string;
  title: string;
}

const PersonaContext = createContext<PersonaValue | null>(null);

export function PersonaProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>("supervisor");
  const value = useMemo<PersonaValue>(
    () => ({ role, setRole, name: PEOPLE[role].name, title: PEOPLE[role].title }),
    [role],
  );
  return <PersonaContext.Provider value={value}>{children}</PersonaContext.Provider>;
}

export function usePersona(): PersonaValue {
  const value = useContext(PersonaContext);
  if (!value) {
    throw new Error("Persona missing");
  }
  return value;
}
