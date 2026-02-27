"use client";

import { createContext, useContext } from "react";
import type { UserResponse } from "@/lib/api";

interface WorkspaceContextValue {
  user: UserResponse | null;
  workspaceId: string | null;
}

export const WorkspaceContext = createContext<WorkspaceContextValue>({
  user: null,
  workspaceId: null,
});

export function useWorkspace(): WorkspaceContextValue {
  return useContext(WorkspaceContext);
}
