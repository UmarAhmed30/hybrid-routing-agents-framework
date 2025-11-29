import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import type { Chat, Message } from "../types";

interface ChatWindowProps {
  chat: Chat;
  onUpdateMessages: (messages: Message[]) => void;
}

export default function ChatWindow({ chat, onUpdateMessages }: ChatWindowProps) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

    try {
      // Call your backend endpoint here
      const response = await fetch("/api/generate_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      if (response.ok) {
        const data = await response.json();
        const botMsg: Message = {
          role: "assistant",
          content: data.output || "No response received",
        };
        onUpdateMessages([...updatedMessages, botMsg]);
      } else {
        const botMsg: Message = {
          role: "assistant",
          content: "Error: Could not reach the server",
        };
        onUpdateMessages([...updatedMessages, botMsg]);
      }
    } catch (error) {
      console.error("Error:", error);
      const botMsg: Message = {
        role: "assistant",
        content: "Error: Failed to send message",
      };
      onUpdateMessages([...updatedMessages, botMsg]);
    } finally {
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
