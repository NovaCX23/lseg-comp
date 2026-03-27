export interface Message {
  role: 'user' | 'assistant';
  content: string;
  mermaid_code?: string;
}

export interface Session {
  id: string;
  created_at: string;
  updated_at: string;
}

const API_BASE = '/api';

export async function generateDiagram(prompt: string, sessionId?: string): Promise<{
  mermaid: string;
  corrected_prompt: string;
  session_id: string;
}> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, session_id: sessionId }),
  });
  if (!response.ok) throw new Error('Failed to generate diagram');
  return response.json();
}

export async function getHistory(sessionId: string): Promise<Message[]> {
  const response = await fetch(`${API_BASE}/history?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error('Failed to get history');
  return response.json();
}

export async function listSessions(): Promise<Session[]> {
  const response = await fetch(`${API_BASE}/sessions`);
  if (!response.ok) throw new Error('Failed to list sessions');
  return response.json();
}
