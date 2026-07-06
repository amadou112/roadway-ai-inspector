"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api } from "./api";
import { ProjectOut } from "./types";
import { useAuth } from "./auth-context";

interface ProjectContextValue {
  projects: ProjectOut[];
  selectedProject: ProjectOut | null;
  selectProject: (id: string) => void;
  loading: boolean;
  refresh: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextValue | undefined>(undefined);

export function ProjectProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [projects, setProjects] = useState<ProjectOut[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    try {
      const data = await api.get<ProjectOut[]>("/api/v1/projects");
      setProjects(data);
      const stored = typeof window !== "undefined" ? localStorage.getItem("selected_project_id") : null;
      const stillExists = data.find((p) => p.id === stored);
      const nextId = stillExists ? stored : data[0]?.id || null;
      setSelectedId(nextId);
      if (nextId && typeof window !== "undefined") localStorage.setItem("selected_project_id", nextId);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user) refresh();
    else setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  function selectProject(id: string) {
    setSelectedId(id);
    if (typeof window !== "undefined") localStorage.setItem("selected_project_id", id);
  }

  const selectedProject = projects.find((p) => p.id === selectedId) || null;

  return (
    <ProjectContext.Provider value={{ projects, selectedProject, selectProject, loading, refresh }}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  const ctx = useContext(ProjectContext);
  if (!ctx) throw new Error("useProject must be used within ProjectProvider");
  return ctx;
}
