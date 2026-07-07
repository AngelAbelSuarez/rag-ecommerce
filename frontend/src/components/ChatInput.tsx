import { ArrowUp } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";

interface ChatInputProps {
  isStreaming: boolean;
  onSendMessage: (text: string) => void;
}

export function ChatInput({ isStreaming, onSendMessage }: ChatInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [text, adjustHeight]);

  const handleSubmit = useCallback(() => {
    if (!text.trim() || isStreaming) return;
    onSendMessage(text);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [text, isStreaming, onSendMessage]);

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="border-t border-[var(--border-hex)] bg-[var(--bg-primary)] p-4">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-[var(--border-hex)] bg-[var(--bg-input)] p-2 shadow-sm">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Preguntá sobre envíos, garantías, reembolsos..."
          disabled={isStreaming}
          rows={1}
          className="max-h-[200px] min-h-[44px] flex-1 resize-none bg-transparent px-3 py-2.5 text-sm outline-none placeholder:text-[var(--text-secondary)]"
        />
        <Button
          onClick={handleSubmit}
          disabled={!text.trim() || isStreaming}
          size="icon"
          className="h-9 w-9 shrink-0 rounded-xl"
          aria-label="Enviar mensaje"
        >
          <ArrowUp className="h-4 w-4" />
        </Button>
      </div>
      <p className="mt-2 text-center text-xs text-[var(--text-secondary)]">
        Enter para enviar · Shift + Enter para nueva línea
      </p>
    </div>
  );
}
