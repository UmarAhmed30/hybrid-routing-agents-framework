import { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import type { Chat } from "./types";

export default function App() {
  const [chats, setChats] = useState<Chat[]>([
    {
      id: "1",
      title: "Welcome",
      messages: [],
      createdAt: new Date(),
    },
  ]);

  const [activeId, setActiveId] = useState<string>("1");

  const activeChat = chats.find((c) => c.id === activeId) || chats[0];

  const updateActiveChat = (messages: any[]) => {
    setChats((prev) =>
      prev.map((c) =>
        c.id === activeId
          ? {
              ...c,
              messages,
              title:
                messages.length > 0
                  ? messages[0].content.substring(0, 30) + "..."
                  : c.title,
            }
          : c
      )
    );
  };

  const createNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [],
      createdAt: new Date(),
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveId(newChat.id);
  };

  const deleteChat = (id: string) => {
    if (chats.length === 1) return;
    setChats((prev) => prev.filter((c) => c.id !== id));
    if (activeId === id) {
      setActiveId(chats[0].id);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-white overflow-hidden">
      <Sidebar
        chats={chats}
        activeId={activeId}
        onSelectChat={setActiveId}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
      />
      <div className="flex-1 overflow-hidden">
        <ChatWindow chat={activeChat} onUpdateMessages={updateActiveChat} />
      </div>
    </div>
  );
}
