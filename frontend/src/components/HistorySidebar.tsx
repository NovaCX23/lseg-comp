import { useEffect, useState } from 'react';
import { Session, listSessions, getHistory } from '../services/api';
import type { Message } from '../services/api';

interface HistorySidebarProps {
  currentSessionId: string | null;
  onSelectSession: (sessionId: string, messages: Message[]) => void;
}

export function HistorySidebar({ currentSessionId, onSelectSession }: HistorySidebarProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const data = await listSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleSelectSession = async (session: Session) => {
    if (session.id === currentSessionId) return;
    try {
      const messages = await getHistory(session.id);
      onSelectSession(session.id, messages);
    } catch (err) {
      console.error('Failed to load session history:', err);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">History</h2>
      </div>
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="p-4 text-gray-500">Loading...</div>
        ) : sessions.length === 0 ? (
          <div className="p-4 text-gray-500 text-sm">No previous diagrams</div>
        ) : (
          <ul className="divide-y divide-gray-800">
            {sessions.map((session) => (
              <li key={session.id}>
                <button
                  onClick={() => handleSelectSession(session)}
                  className={`w-full text-left p-4 hover:bg-gray-800 transition-colors ${
                    session.id === currentSessionId ? 'bg-gray-800' : ''
                  }`}
                >
                  <p className="text-sm text-white truncate">
                    {formatDate(session.updated_at)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {session.id.slice(0, 8)}...
                  </p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={loadSessions}
          className="w-full px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm transition-colors"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}
