import { Role } from "./types";

export interface DemoAccount {
  email: string;
  label: string;
  role: Role;
}

export const DEMO_ACCOUNTS: DemoAccount[] = [
  { email: "pm@demo.gov", label: "Program Manager", role: "program_manager" },
  { email: "projectmanager@demo.gov", label: "Project Manager", role: "project_manager" },
  { email: "resident-engineer@demo.gov", label: "Resident Engineer", role: "resident_engineer" },
  { email: "inspector@demo.gov", label: "Inspector", role: "inspector" },
  { email: "designer@demo.gov", label: "Designer", role: "designer" },
  { email: "contractor@demo.gov", label: "Contractor", role: "contractor" },
  { email: "executive@demo.gov", label: "DOT Executive", role: "dot_executive" },
];

export const DEMO_PASSWORD = "RoadwayDemo!2026";

export const DEFAULT_DEMO_ACCOUNT = DEMO_ACCOUNTS[0];
