import { useEffect, useState } from "react";
import { getRun } from "../api/client";
import type { AgentRun } from "../types/agent";

export function useRunState(runId: string | null) {
  const [run, setRun] = useState<AgentRun | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;

    let active = true;

    const load = async () => {
      try {
        const latest = await getRun(runId);
        if (active) {
          setRun(latest);
          setError(null);
        }
      } catch {
        if (active) setError("Unable to refresh run state.");
      }
    };

    load();
    const interval = setInterval(load, 1500);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [runId]);

  return { run, error };
}
