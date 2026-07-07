import { MessageSquare, Plus, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { Conversation } from "@/types/chat";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onNewConversation: () => void;
  onSwitchConversation: (id: string) => void;
}

export function Sidebar({
  conversations,
  activeConversationId,
  isOpen,
  onClose,
  onNewConversation,
  onSwitchConversation,
}: SidebarProps) {
  return (
    <aside
      className={`
        fixed inset-y-0 left-0 z-30 flex w-72 flex-col border-r border-[var(--border-hex)]
        bg-[var(--bg-sidebar)] transition-transform duration-200 ease-in-out
        lg:static lg:translate-x-0
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
      `}
    >
      <div className="flex items-center justify-between border-b border-[var(--border-hex)] p-4">
        <Button
          onClick={onNewConversation}
          variant="outline"
          className="flex-1 justify-start gap-2 border-[var(--border-hex)] bg-transparent hover:bg-[var(--bg-primary)]"
        >
          <Plus className="h-4 w-4" />
          Nuevo Chat
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="ml-2 lg:hidden"
          onClick={onClose}
          aria-label="Cerrar conversaciones"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {conversations.length === 0 ? (
          <p className="px-3 py-2 text-sm text-[var(--text-secondary)]">
            No hay conversaciones aún.
          </p>
        ) : (
          <ul className="space-y-1">
            {conversations.map((conversation, index) => {
              const isActive = conversation.id === activeConversationId;
              return (
                <li key={conversation.id}>
                  <button
                    onClick={() => onSwitchConversation(conversation.id)}
                    className={`
                      flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm
                      transition-colors
                      ${
                        isActive
                          ? "bg-[var(--accent-hex)]/10 text-[var(--accent-hex)]"
                          : "text-[var(--text-secondary)] hover:bg-[var(--bg-primary)] hover:text-[var(--text-primary)]"
                      }
                    `}
                    title={conversation.title}
                  >
                    <MessageSquare className="h-4 w-4 shrink-0" />
                    <span className="truncate">
                      {conversation.title || `Chat ${conversations.length - index}`}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="border-t border-[var(--border-hex)] p-4 text-xs text-[var(--text-secondary)]">
        BimBam Chat
      </div>
    </aside>
  );
}
