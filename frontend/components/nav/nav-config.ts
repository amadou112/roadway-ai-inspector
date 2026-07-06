import { Role } from "@/lib/types";

export interface NavItem {
  href: string;
  label: string;
  icon: string;
  roles?: Role[];
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Program Dashboard", icon: "📊" },
  {
    href: "/projects",
    label: "Projects",
    icon: "🗂️",
    roles: ["program_manager", "project_manager", "dot_executive"],
  },
  {
    href: "/rfis",
    label: "RFIs",
    icon: "❓",
    roles: ["program_manager", "project_manager", "resident_engineer", "contractor"],
  },
  {
    href: "/submittals",
    label: "Submittals",
    icon: "📥",
    roles: ["program_manager", "project_manager", "resident_engineer", "designer", "contractor"],
  },
  {
    href: "/risks",
    label: "Risk Register",
    icon: "⚠️",
    roles: ["program_manager", "project_manager", "dot_executive"],
  },
  {
    href: "/ncrs",
    label: "Non-Conformance",
    icon: "🚧",
    roles: ["program_manager", "project_manager", "resident_engineer", "inspector"],
  },
  {
    href: "/safety",
    label: "Safety Issues",
    icon: "🦺",
    roles: ["program_manager", "project_manager", "resident_engineer", "inspector"],
  },
  {
    href: "/schedule",
    label: "Schedule",
    icon: "📅",
    roles: ["program_manager", "project_manager", "resident_engineer", "contractor"],
  },
  {
    href: "/cost",
    label: "Cost Tracking",
    icon: "💵",
    roles: ["program_manager", "project_manager", "dot_executive"],
  },
  {
    href: "/inspections",
    label: "Inspection Reports",
    icon: "📝",
    roles: ["program_manager", "project_manager", "resident_engineer", "inspector"],
  },
  {
    href: "/design-review",
    label: "Design Review",
    icon: "📐",
    roles: ["program_manager", "designer", "project_manager"],
  },
  { href: "/documents", label: "Documents", icon: "📄" },
  { href: "/assistant", label: "AI Assistant", icon: "🤖" },
  { href: "/bridges", label: "Bridge & Roadway Data", icon: "🌉" },
  {
    href: "/reports",
    label: "Executive Reports",
    icon: "📋",
    roles: ["program_manager", "project_manager", "dot_executive"],
  },
];

export function visibleNavItems(role: Role | undefined) {
  if (!role) return [];
  return NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(role));
}
