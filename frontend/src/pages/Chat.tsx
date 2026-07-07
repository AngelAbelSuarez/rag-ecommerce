import { ChatLayout } from "@/components/ChatLayout";
import { useChat } from "@/hooks/useChat";

export default function Chat() {
  const {
    conversations,
    activeConversation,
    isStreaming,
    error,
    newConversation,
    switchConversation,
    sendMessage,
    clearError,
  } = useChat();

  return (
    <ChatLayout
      conversations={conversations}
      activeConversation={activeConversation}
      isStreaming={isStreaming}
      error={error}
      onNewConversation={newConversation}
      onSwitchConversation={switchConversation}
      onSendMessage={sendMessage}
      onClearError={clearError}
    />
  );
}
