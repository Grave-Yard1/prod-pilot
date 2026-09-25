import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { PEOPLE, usePersona } from "../persona";
import type { Role } from "../persona";

const LINKS = [
  { to: "/", label: "Walk", end: true },
  { to: "/floor", label: "Floor", end: false },
  { to: "/report", label: "Report", end: false },
  { to: "/handoff", label: "Handoff", end: false },
];

export function Shell({ children }: { children: ReactNode }) {
  const { role, setRole, name, title } = usePersona();
  const roles = Object.keys(PEOPLE) as Role[];

  return (
    <div className="app">
      <aside className="rail">
        <header className="brand-block">
          <p className="brand-mark">LW</p>
          <div>
            <p className="brand-name">Linewalk</p>
            <p className="brand-sub">Shift A · {name}</p>
          </div>
        </header>
        <div className="persona" role="group" aria-label="Who is holding the phone">
          {roles.map((item) => (
            <button
              key={item}
              type="button"
              className={item === role ? "persona-btn active" : "persona-btn"}
              aria-pressed={item === role}
              onClick={() => setRole(item)}
            >
              {PEOPLE[item].title}
            </button>
          ))}
          <p className="persona-name">
            Walking as <strong>{name}</strong>
            <span>{title}</span>
          </p>
        </div>
        <nav className="dock" aria-label="Floor">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="stage">
        <p className="safety" role="note">
          Recommendation only. You decide. This does not change the line.
        </p>
        <main>{children}</main>
        <p className="fineprint">
          Berlin-style simulated production data. Hackathon prototype. Not a Tesla system.
        </p>
      </div>
    </div>
  );
}
