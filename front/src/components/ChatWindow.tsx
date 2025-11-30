import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import type { Chat, Message } from "../types";

interface ChatWindowProps {
  chat: Chat;
  onUpdateMessages: (messages: Message[]) => void;
  onLogsUpdate?: (logs: string[]) => void;
}

export default function ChatWindow({ chat, onUpdateMessages, onLogsUpdate }: ChatWindowProps) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat.messages]);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    const updatedMessages = [...chat.messages, userMsg];
    onUpdateMessages(updatedMessages);
    setInput("");
    setLoading(true);
    setLogs([]);

    try {
      // Step 1: Create a new session
      const sessionRes = await fetch("http://localhost:5000/api/start_session", {
        method: "POST",
      });
      const sessionData = await sessionRes.json();
      const sessionId = sessionData.session_id;

      // Step 2: Start the routing process
      await fetch("http://localhost:5000/api/start_routing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input, session_id: sessionId }),
      });

      // Step 3: Poll for logs and result
      const lastLogCount = { count: 0 };

      const pollLogs = async () => {
        try {
          const res = await fetch(`http://localhost:5000/api/get_logs/${sessionId}`);
          const data = await res.json();

          // Update logs if there are new ones
          if (data.logs.length > lastLogCount.count) {
            const newLogs = data.logs.slice(lastLogCount.count);
            setLogs((prev) => {
              const updated = [...prev, ...newLogs];
              onLogsUpdate?.(updated);
              return updated;
            });
            lastLogCount.count = data.logs.length;
          }

          // Check if routing is complete
          if (data.status === "complete") {
            const botMsg: Message = {
              role: "assistant",
              content: data.result?.output || "No response received",
            };
            onUpdateMessages([...updatedMessages, botMsg]);
            setLoading(false);
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
          } else if (data.status === "error") {
            const botMsg: Message = {
              role: "assistant",
              content: `Error: ${data.error}`,
            };
            onUpdateMessages([...updatedMessages, botMsg]);
            setLoading(false);
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      };

      // Poll every 500ms
      pollIntervalRef.current = setInterval(pollLogs, 500);
      // Also poll immediately
      pollLogs();
    } catch (error) {
      console.error("Error:", error);
      const botMsg: Message = {
        role: "assistant",
        content: "Error: Failed to send message",
      };
      onUpdateMessages([...updatedMessages, botMsg]);
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 bg-white">
        <h2 className="text-lg font-semibold text-gray-900">{chat.title}</h2>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {chat.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <p className="text-2xl font-bold mb-2 text-gray-900">Start a new conversation</p>
              <p className="text-sm">Ask anything using the model routing framework</p>
            </div>
          </div>
        ) : (
          <>
            {chat.messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}
            {loading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-2 border border-gray-200">
                  <div className="flex gap-1">
                    <span className="animate-pulse">●</span>
                    <span className="animate-pulse">●</span>
                    <span className="animate-pulse">●</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Logs Panel */}
      {logs.length > 0 && (
        <div className="border-t border-gray-200 bg-gray-50 p-4 max-h-40 overflow-y-auto">
          <h3 className="font-semibold text-xs text-gray-700 mb-2 uppercase tracking-wide">Server Events</h3>
          <div className="font-mono text-xs text-gray-600 space-y-1">
            {logs.map((log, i) => (
              <div key={i} className="text-blue-600 break-words">{log}</div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-6 bg-white">
        <div className="flex gap-3">
          <input
            className="flex-1 bg-gray-50 text-gray-900 placeholder-gray-400 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage()}
            disabled={loading}
          />
          <button
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
