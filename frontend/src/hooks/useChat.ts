import { useCallback, useMemo, useState } from "react";

import { postChatMessage } from "@/lib/api";
import type { ChatState, Conversation, Message } from "@/types/chat";

function generateId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`;
}

function createConversation(): Conversation {
  return {
    id: generateId(),
    title: "Nuevo Chat",
    messages: [],
    createdAt: Date.now(),
  };
}

function createMessage(role: Message["role"], content: string): Message {
  return {
    id: generateId(),
    role,
    content,
    timestamp: Date.now(),
  };
}

export function useChat() {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    activeConversationId: null,
    isStreaming: false,
    error: null,
  });

  const activeConversation = useMemo<Conversation | null>(() => {
    if (!state.activeConversationId) return null;
    return (
      state.conversations.find((c) => c.id === state.activeConversationId) ??
      null
    );
  }, [state.conversations, state.activeConversationId]);

  const newConversation = useCallback(() => {
    const conversation = createConversation();
    setState((prev) => ({
      ...prev,
      conversations: [conversation, ...prev.conversations],
      activeConversationId: conversation.id,
      error: null,
    }));
    return conversation.id;
  }, []);

  const switchConversation = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      activeConversationId: id,
      error: null,
    }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;

      let conversationId = state.activeConversationId;
      let conversation = activeConversation;

      if (!conversation) {
        conversation = createConversation();
        conversationId = conversation.id;
        setState((prev) => ({
          ...prev,
          conversations: [conversation!, ...prev.conversations],
          activeConversationId: conversation!.id,
          error: null,
        }));
      }

      const userMessage = createMessage("user", trimmed);
      const assistantMessage = createMessage("assistant", "");

      setState((prev) => {
        const updatedConversations = prev.conversations.map((c) => {
          if (c.id !== conversationId) return c;
          const isFirstMessage = c.messages.length === 0;
          return {
            ...c,
            title: isFirstMessage ? trimmed : c.title,
            messages: [...c.messages, userMessage, assistantMessage],
          };
        });
        return {
          ...prev,
          conversations: updatedConversations,
          isStreaming: true,
          error: null,
        };
      });

      try {
        for await (const token of postChatMessage(trimmed, conversationId!)) {
          setState((prev) => ({
            ...prev,
            conversations: prev.conversations.map((c) => {
              if (c.id !== conversationId) return c;
              const messages = c.messages.slice();
              const last = messages[messages.length - 1];
              if (last && last.role === "assistant") {
                messages[messages.length - 1] = {
                  ...last,
                  content: last.content + token,
                };
              }
              return { ...c, messages };
            }),
          }));
        }
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "No se pudo conectar con BimBam";
        setState((prev) => ({
          ...prev,
          error: message,
          conversations: prev.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            const messages = c.messages.slice();
            const last = messages[messages.length - 1];
            if (last && last.role === "assistant" && last.content === "") {
              messages[messages.length - 1] = {
                ...last,
                content:
                  "No se pudo conectar con BimBam. Reintentá en unos segundos.",
              };
            }
            return { ...c, messages };
          }),
        }));
      } finally {
        setState((prev) => ({ ...prev, isStreaming: false }));
      }
    },
    [activeConversation, state.activeConversationId]
  );

  return {
    ...state,
    activeConversation,
    newConversation,
    switchConversation,
    sendMessage,
    clearError,
  };
}
