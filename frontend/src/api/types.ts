export type VoicePreference = "male" | "female";
export type ChatMode = "text" | "voice" | "mixed";
export type Role = "user" | "assistant" | "system";

export interface Persona {
  id: string;
  name: string;
  system_prompt: string;
  temperature: number;
  voice_preference: VoicePreference;
  created_at: string;
  updated_at: string;
}

export interface PersonaSnapshot {
  name: string;
  system_prompt: string;
  temperature: number;
  voice_preference: VoicePreference;
}

export interface ConversationSummary {
  id: string;
  title: string;
  persona_id: string | null;
  persona_name: string | null;
  persona_snapshot: PersonaSnapshot;
  temperature: number;
  voice_preference: VoicePreference;
  mode: ChatMode;
  created_at: string;
  updated_at: string;
  preview: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: Role;
  content_text: string;
  audio_path: string | null;
  transcript_source: "text" | "voice" | "voice-fallback";
  created_at: string;
}

export interface SendMessageResponse {
  conversation: ConversationSummary;
  user_message: Message;
  assistant_message: Message;
}

export interface VoiceReplyResponse extends SendMessageResponse {
  transcription_text: string;
  audio_url: string | null;
}
