import { useEffect, useState } from "react";

import type { Conversation } from "@/types/chat";

import { ChatArea } from "./ChatArea";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface ChatLayoutProps {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  isStreaming: boolean;
  error: string | null;
  onNewConversation: () => void;
  onSwitchConversation: (id: string) => void;
  onSendMessage: (text: string) => void;
  onClearError: () => void;
}

export function ChatLayout({
  conversations,
  activeConversation,
  isStreaming,
  error,
  onNewConversation,
  onSwitchConversation,
  onSendMessage,
  onClearError,
}: ChatLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    if (isSidebarOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isSidebarOpen]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversation?.id ?? null}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onNewConversation={onNewConversation}
        onSwitchConversation={(id) => {
          onSwitchConversation(id);
          setIsSidebarOpen(false);
        }}
      />

      {isSidebarOpen && (
        <button
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
          aria-label="Cerrar sidebar"
        />
      )}

      <div className="flex flex-1 flex-col">
        <TopBar
          title={activeConversation?.title ?? "Nuevo Chat"}
          onMenuClick={() => setIsSidebarOpen(true)}
        />
        <ChatArea
          conversation={activeConversation}
          isStreaming={isStreaming}
          error={error}
          onSendMessage={onSendMessage}
          onClearError={onClearError}
        />
      </div>
    </div>
  );
}
