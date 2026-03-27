import Editor from '@monaco-editor/react';

interface DiagramEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export function DiagramEditor({ value, onChange }: DiagramEditorProps) {
  return (
    <div className="h-full">
      <Editor
        height="100%"
        defaultLanguage="markdown"
        theme="vs-dark"
        value={value}
        onChange={(val) => onChange(val || '')}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'off',
          folding: false,
          wordWrap: 'on',
          scrollBeyondLastLine: false,
          padding: { top: 16 },
        }}
      />
    </div>
  );
}
