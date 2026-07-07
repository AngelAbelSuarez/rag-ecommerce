import type { Conversation } from "@/types/chat";

import { MessageBubble } from "./MessageBubble";

interface MessageListProps {
  conversation: Conversation | null;
  isStreaming: boolean;
}

export function MessageList({ conversation, isStreaming }: MessageListProps) {
  const messages = conversation?.messages ?? [];
  const lastMessage = messages[messages.length - 1];
  const showTyping =
    isStreaming && lastMessage && lastMessage.role === "user";

  return (
    <div className="flex flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {showTyping && (
        <div className="flex w-full justify-start">
          <div className="flex max-w-[85%] items-start gap-3 sm:max-w-[75%]">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--accent-hex)] text-xs font-bold text-white">
              B
            </div>
            <div className="rounded-2xl rounded-bl-none bg-muted px-4 py-3">
              <div className="flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--text-secondary)] [animation-delay:-0.3s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--text-secondary)] [animation-delay:-0.15s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--text-secondary)]" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
