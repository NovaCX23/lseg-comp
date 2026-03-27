import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface DiagramPreviewProps {
  code: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
});

export function DiagramPreview({ code }: DiagramPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [svg, setSvg] = useState<string>('');

  useEffect(() => {
    if (!code.trim()) {
      setSvg('');
      setError(null);
      return;
    }

    const renderDiagram = async () => {
      try {
        const id = `mermaid-${Date.now()}`;
        const { svg: renderedSvg } = await mermaid.render(id, code);
        setSvg(renderedSvg);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to render diagram');
        setSvg('');
      }
    };

    renderDiagram();
  }, [code]);

  if (!code.trim()) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <p>Enter a prompt to generate a diagram</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 h-full overflow-auto">
        <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 text-red-200">
          <p className="font-semibold mb-2">Diagram Error:</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="p-4 h-full overflow-auto flex items-start justify-center"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
