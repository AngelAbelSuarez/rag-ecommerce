import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useChat } from "../useChat";

const postChatMessage = vi.fn();

vi.mock("@/lib/api", () => ({
  postChatMessage: (...args: unknown[]) => postChatMessage(...args),
}));

describe("useChat", () => {
  it("isStreaming is false initially", () => {
    const { result } = renderHook(() => useChat());
    expect(result.current.isStreaming).toBe(false);
  });

  it("error is null initially", () => {
    const { result } = renderHook(() => useChat());
    expect(result.current.error).toBeNull();
  });

  it("newConversation() creates a fresh active conversation", () => {
    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.newConversation();
    });

    expect(result.current.conversations).toHaveLength(1);
    expect(result.current.activeConversationId).not.toBeNull();
    expect(result.current.activeConversation).not.toBeNull();
    expect(result.current.activeConversation?.title).toBe("Nuevo Chat");
  });

  it("switchConversation(id) switches active session", () => {
    const { result } = renderHook(() => useChat());

    let firstId: string;
    act(() => {
      firstId = result.current.newConversation();
    });

    act(() => {
      result.current.newConversation();
    });

    const secondId = result.current.activeConversationId;

    act(() => {
      result.current.switchConversation(firstId!);
    });

    expect(result.current.activeConversationId).toBe(firstId);
    expect(result.current.activeConversation?.id).toBe(firstId);

    act(() => {
      result.current.switchConversation(secondId!);
    });

    expect(result.current.activeConversationId).toBe(secondId);
  });

  it("sendMessage() adds user message to conversation", async () => {
    postChatMessage.mockImplementation(async function* () {
      yield "¡Hola!";
    });

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("Hola");
    });

    await waitFor(() => {
      expect(result.current.activeConversation?.messages).toHaveLength(2);
    });

    const messages = result.current.activeConversation!.messages;
    expect(messages[0].role).toBe("user");
    expect(messages[0].content).toBe("Hola");
    expect(messages[1].role).toBe("assistant");
    expect(messages[1].content).toBe("¡Hola!");
  });
});
