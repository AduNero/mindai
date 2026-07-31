export type MessageSender = "user" | "assistant";

export interface ChatMessage {
  id: string;
  sender: MessageSender;
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  started_at: string;
  last_message_at: string | null;
  is_archived: boolean;
  message_count: number;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface ChatSearchResult {
  session_id: string;
  session_title: string;
  message_id: string;
  snippet: string;
  created_at: string;
}
