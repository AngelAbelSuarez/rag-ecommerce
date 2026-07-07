import { useEffect, useRef } from "react";

import type { Conversation } from "@/types/chat";

import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";

interface ChatAreaProps {
  conversation: Conversation | null;
  isStreaming: boolean;
  error: string | null;
  onSendMessage: (text: string) => void;
  onClearError: () => void;
}

export function ChatArea({
  conversation,
  isStreaming,
  error,
  onSendMessage,
  onClearError,
}: ChatAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [conversation?.messages, isStreaming]);

  const isEmpty = (conversation?.messages.length ?? 0) === 0;

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scroll-smooth"
      >
        {isEmpty ? (
          <div className="flex h-full flex-col items-center justify-center px-4 text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--accent-hex)] text-2xl font-bold text-white">
              B
            </div>
            <h2 className="mb-2 text-2xl font-semibold">
              ¿En qué puedo ayudarte hoy?
            </h2>
            <p className="max-w-md text-[var(--text-secondary)]">
              Preguntá sobre envíos, garantías, pagos, reembolsos o cualquier
              duda de BimBam Buy.
            </p>
          </div>
        ) : (
          <MessageList conversation={conversation} isStreaming={isStreaming} />
        )}
      </div>

      {error && (
        <div className="mx-4 mb-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-200 sm:mx-6">
          <div className="flex items-start justify-between gap-2">
            <span>{error}</span>
            <button
              onClick={onClearError}
              className="text-xs font-medium underline"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      <ChatInput isStreaming={isStreaming} onSendMessage={onSendMessage} />
    </div>
  );
}
