import type { Chat } from "../types";

interface SidebarProps {
  chats: Chat[];
  activeId: string;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
}

export default function Sidebar({
  chats,
  activeId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: SidebarProps) {
  return (
    <div className="w-64 bg-gray-50 text-gray-900 flex flex-col h-screen border-r border-gray-200 flex-shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <button
          onClick={onNewChat}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          + New Chat
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`flex items-center gap-2 px-4 py-3 cursor-pointer border-l-2 transition-colors ${
              activeId === chat.id
                ? "border-blue-600 bg-blue-50"
                : "border-transparent hover:bg-gray-100"
            }`}
            onClick={() => onSelectChat(chat.id)}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate text-gray-900">{chat.title}</p>
              <p className="text-xs text-gray-500">
                {chat.createdAt.toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
              className="opacity-0 hover:opacity-100 p-1 hover:bg-red-100 rounded text-red-600 text-sm"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4 text-xs text-gray-600 bg-white">
        <p className="font-medium">Model Routing</p>
        <p>Chat Interface v1.0</p>
      </div>
    </div>
  );
}
