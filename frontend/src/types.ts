export type MachineStatus = "running" | "watch" | "alarm" | "down";
export type CallAction = "continue" | "slow" | "stop";

export interface Signal {
  metric: string;
  value: number;
  unit: string;
  limit_value: number;
  recorded_at: string;
}

export interface Series {
  metric: string;
  unit: string;
  limit_value: number;
  points: number[];
  recorded_at: string[];
}

export interface MachineSummary {
  code: string;
  name: string;
  zone: string;
  status: MachineStatus;
  trade: string;
  contact_name: string;
  signals: Signal[];
  open_incident_numbers: number[];
}

export interface MachineDetail extends MachineSummary {
  series: Series[];
  incidents: Array<{
    number: number;
    label: string;
    symptom: string;
    status: string;
    created_at: string;
  }>;
}

export interface Evidence {
  incident_number: number;
  label: string;
  similarity_points: number;
  similarity_percent: number;
  machine_code: string;
  symptom: string;
  observation: string;
  error_code: string | null;
  diagnosis: string;
  action: string;
  downtime_minutes: number;
  outcome: string;
  engineer_name: string;
  parts: Record<string, number>;
  shared_families: string[];
}

export interface Analysis {
  id: number;
  recommendation: CallAction;
  similarity_points: number;
  similarity_percent: number;
  matched_incident_number: number | null;
  matched_label: string | null;
  evidence: Evidence[];
  rationale: string;
  model_id: string;
  narrative_source: string;
  safety_line: string;
  created_at: string;
}

export interface Observation {
  id: number;
  worker_name: string;
  note: string;
  observed_at: string;
}

export interface Decision {
  id: number;
  supervisor_name: string;
  action: CallAction;
  note: string;
  decided_at: string;
}

export interface Repair {
  id: number;
  engineer_name: string;
  diagnosis: string;
  action: string;
  downtime_minutes: number;
  outcome: string;
  repaired_at: string;
}

export interface IncidentMachine {
  code: string;
  name: string;
  zone: string;
  status: MachineStatus;
  trade: string;
  contact_name: string;
}

export interface Incident {
  number: number;
  label: string;
  status: string;
  symptom: string;
  error_code: string | null;
  opened_by: string;
  created_at: string;
  machine: IncidentMachine;
  observations: Observation[];
  analysis: Analysis | null;
  decision: Decision | null;
  repair: Repair | null;
}

export interface Handoff {
  shift_label: string;
  dataset: string;
  generated_at: string;
  safety_line: string;
  waiting: Array<{
    number: number;
    label: string;
    machine_code: string;
    machine_name: string;
    symptom: string;
    recommendation: CallAction | null;
    similarity_percent: number | null;
  }>;
  decisions: Array<{
    incident_number: number;
    label: string;
    machine_code: string;
    machine_name: string;
    symptom: string;
    action: CallAction;
    note: string;
    supervisor_name: string;
    decided_at: string;
  }>;
  repairs: Array<{
    incident_number: number;
    label: string;
    machine_code: string;
    machine_name: string;
    diagnosis: string;
    action: string;
    downtime_minutes: number;
    outcome: string;
    engineer_name: string;
    repaired_at: string;
  }>;
  carry: Array<{ code: string; name: string; zone: string; status: MachineStatus }>;
}
