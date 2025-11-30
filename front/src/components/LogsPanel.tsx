interface LogsPanelProps {
  logs: string[];
}

export default function LogsPanel({ logs }: LogsPanelProps) {
  if (logs.length === 0) return null;

  return (
    <div className="border-t border-gray-200 bg-gray-50 p-4 max-h-40 overflow-y-auto">
      <h3 className="font-semibold text-xs text-gray-700 mb-2 uppercase tracking-wide">Server Events</h3>
      <div className="font-mono text-xs text-gray-600 space-y-1">
        {logs.map((log, i) => (
          <div key={i} className="text-blue-600 break-words">{log}</div>
        ))}
      </div>
    </div>
  );
}
