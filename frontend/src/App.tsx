import { useState, useCallback } from 'react';
import { ChatInput, DiagramPreview, DiagramEditor, HistorySidebar } from './components';
import { generateDiagram } from './services/api';
import type { Message } from './services/api';

function App() {
  const [mermaidCode, setMermaidCode] = useState('');
  const [correctedPrompt, setCorrectedPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showCorrected, setShowCorrected] = useState(false);

  const handleSubmit = useCallback(async (prompt: string) => {
    setIsLoading(true);
    setError(null);
    setShowCorrected(false);
    
    try {
      const result = await generateDiagram(prompt, sessionId || undefined);
      setMermaidCode(result.mermaid);
      setCorrectedPrompt(result.corrected_prompt);
      setSessionId(result.session_id);
      setShowCorrected(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate diagram');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const handleSelectSession = useCallback((newSessionId: string, messages: Message[]) => {
    setSessionId(newSessionId);
    const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant');
    if (lastAssistant?.mermaid_code) {
      setMermaidCode(lastAssistant.mermaid_code);
      setCorrectedPrompt(lastAssistant.content);
      setShowCorrected(true);
    }
  }, []);

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      <HistorySidebar 
        currentSessionId={sessionId}
        onSelectSession={handleSelectSession}
      />
      
      <div className="flex-1 flex flex-col">
        <header className="p-4 border-b border-gray-800 bg-gray-900">
          <h1 className="text-xl font-bold">LSEG Diagram Generator</h1>
          <p className="text-sm text-gray-400 mt-1">
            Describe your architecture and watch the diagram come to life
          </p>
        </header>

        {error && (
          <div className="mx-4 mt-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {showCorrected && correctedPrompt && (
          <div className="mx-4 mt-4 p-3 bg-blue-900/30 border border-blue-700 rounded-lg text-sm">
            <span className="text-blue-400 font-semibold">Corrected prompt:</span>{' '}
            {correctedPrompt}
          </div>
        )}

        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
          <div className="flex-1 flex flex-col border-r border-gray-800 min-h-0">
            <div className="px-4 py-2 border-b border-gray-800 bg-gray-900/50">
              <span className="text-sm font-medium text-gray-400">Mermaid Code</span>
            </div>
            <div className="flex-1 min-h-0">
              <DiagramEditor value={mermaidCode} onChange={setMermaidCode} />
            </div>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            <div className="px-4 py-2 border-b border-gray-800 bg-gray-900/50">
              <span className="text-sm font-medium text-gray-400">Preview</span>
            </div>
            <div className="flex-1 overflow-auto bg-gray-900/30">
              <DiagramPreview code={mermaidCode} />
            </div>
          </div>
        </div>

        <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default App;
