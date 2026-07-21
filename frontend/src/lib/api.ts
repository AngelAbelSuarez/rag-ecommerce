const API_BASE = (import.meta.env.VITE_API_URL ?? "") + "/api";

export interface HealthStatus {
  status: string;
  vectorstore: string;
  llm: string | null;
}

export async function* postChatMessage(
  message: string,
  conversationId?: string
): AsyncGenerator<string> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "Unknown error");
    throw new Error(`Chat request failed (${response.status}): ${text}`);
  }

  if (!response.body) {
    throw new Error("Response body is empty");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      let currentEvent: string | null = null;
      for (const line of lines) {
        if (line.startsWith("event: ")) {
          currentEvent = line.slice(7).trim();
          continue;
        }
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            return;
          }
          if (currentEvent === "error") {
            const parsed = JSON.parse(data) as { message: string };
            throw new Error(parsed.message);
          }
          yield data;
          currentEvent = null;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function checkHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    const text = await response.text().catch(() => "Unknown error");
    throw new Error(`Health check failed (${response.status}): ${text}`);
  }
  return (await response.json()) as HealthStatus;
}
