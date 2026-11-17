export interface IncidentInput {
  title: string;
  description: string;
  service: string;
  environment: string;
  severity: string;
  operator_id: string;
}

export interface AgentEvent {
  sequence: number;
  run_id: string;
  node: string;
  event: string;
  message: string;
  data: Record<string, unknown>;
  created_at: string;
}

export interface Evidence {
  id: string;
  source: string;
  content: string;
}

export interface ToolCall {
  call_id: string;
  tool: string;
  arguments: Record<string, unknown>;
  status: string;
  latency_ms: number;
  result: Record<string, unknown>;
  error?: string | null;
}

export interface AgentRun {
  run_id: string;
  thread_id: string;
  status: string;
  incident: IncidentInput;
  classification?: Record<string, unknown> | null;
  evidence: Evidence[];
  tool_calls: ToolCall[];
  diagnosis?: Record<string, unknown> | null;
  plan?: Record<string, unknown> | null;
  pending_action?: Record<string, unknown> | null;
  approval?: Record<string, unknown> | null;
  execution?: Record<string, unknown> | null;
  verification?: Record<string, unknown> | null;
  context_usage?: Record<string, unknown> | null;
  events: AgentEvent[];
}
