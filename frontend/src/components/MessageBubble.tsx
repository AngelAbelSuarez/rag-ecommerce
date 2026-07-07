import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import type { Message } from "@/types/chat";

interface MessageBubbleProps {
  message: Message;
}

function renderMarkdownLite(text: string): ReactNode {
  const lines = text.split("\n");
  return (
    <>
      {lines.map((line, lineIndex) => {
        const parts: ReactNode[] = [];
        let remaining = line;
        let key = 0;

        while (remaining.length > 0) {
          const boldMatch = remaining.match(/(\*\*|__)(.+?)\1/);
          const italicMatch = remaining.match(/(\*|_)(.+?)\1/);

          const matches = [
            boldMatch && { type: "bold" as const, match: boldMatch },
            italicMatch && { type: "italic" as const, match: italicMatch },
          ]
            .filter((m): m is { type: "bold" | "italic"; match: RegExpMatchArray } => Boolean(m))
            .sort((a, b) => (a.match.index ?? 0) - (b.match.index ?? 0));

          const first = matches[0];

          if (!first) {
            parts.push(remaining);
            break;
          }

          const { type, match } = first;
          const index = match.index ?? 0;

          if (index > 0) {
            parts.push(remaining.slice(0, index));
          }

          const content = match[2];
          parts.push(
            type === "bold" ? (
              <strong key={`${lineIndex}-${key++}`}>{content}</strong>
            ) : (
              <em key={`${lineIndex}-${key++}`}>{content}</em>
            )
          );

          remaining = remaining.slice(index + match[0].length);
        }

        return (
          <p key={lineIndex} className={lineIndex > 0 ? "mt-2" : undefined}>
            {parts.length === 0 ? "\u00A0" : parts}
          </p>
        );
      })}
    </>
  );
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "flex max-w-[85%] items-start gap-3 sm:max-w-[75%]",
          isUser ? "flex-row-reverse" : "flex-row"
        )}
      >
        <div
          className={cn(
            "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white",
            isUser ? "bg-[var(--avatar-user)]" : "bg-[var(--accent-hex)]"
          )}
        >
          {isUser ? "T" : "B"}
        </div>
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "rounded-br-none bg-primary text-primary-foreground"
              : "rounded-bl-none bg-muted text-foreground"
          )}
        >
          {message.content ? (
            renderMarkdownLite(message.content)
          ) : (
            <span className="italic opacity-70">BimBam está escribiendo...</span>
          )}
        </div>
      </div>
    </div>
  );
}
