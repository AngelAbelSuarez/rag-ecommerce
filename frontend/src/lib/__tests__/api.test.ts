import { describe, expect, it, vi } from "vitest";

import { checkHealth, postChatMessage } from "../api";

function createReadableStream(chunks: string[]) {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(new TextEncoder().encode(chunk));
      }
      controller.close();
    },
  });
}

function mockFetch(response: Partial<Response>) {
  global.fetch = vi.fn(() => Promise.resolve(response)) as unknown as typeof fetch;
}

describe("checkHealth", () => {
  it("makes GET to /api/health", async () => {
    mockFetch({
      ok: true,
      json: () =>
        Promise.resolve({
          status: "ok",
          vectorstore: "ok",
          llm: "ok",
        }),
    });

    await checkHealth();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith("/api/health");
  });
});

describe("postChatMessage", () => {
  it("makes POST to /api/chat with message body", async () => {
    mockFetch({
      ok: true,
      body: createReadableStream(["data: [DONE]\n\n"]),
    });

    const generator = postChatMessage("¿Tienen envíos?", "conv-123");
    await generator.next();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "¿Tienen envíos?", conversation_id: "conv-123" }),
    });
  });

  it("SSE parsing yields tokens from the stream", async () => {
    mockFetch({
      ok: true,
      body: createReadableStream([
        "data: Sí, \n\n",
        "data: tenemos envíos a\n\ndata: todo el país.\n\n",
        "data: [DONE]\n\n",
      ]),
    });

    const tokens: string[] = [];
    for await (const token of postChatMessage("¿Envían?")) {
      tokens.push(token);
    }

    expect(tokens).toEqual(["Sí, ", "tenemos envíos a", "todo el país."]);
  });
});
