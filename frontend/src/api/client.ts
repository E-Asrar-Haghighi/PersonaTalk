import type {
  ConversationSummary,
  Message,
  Persona,
  PersonaSnapshot,
  SendMessageResponse,
  VoicePreference,
  VoiceReplyResponse
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data.detail ?? detail;
    } catch {
      detail = await response.text();
    }
    throw new Error(detail || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  listPersonas: () => request<Persona[]>("/personas"),
  createPersona: (payload: Omit<Persona, "id" | "created_at" | "updated_at">) =>
    request<Persona>("/personas", { method: "POST", body: JSON.stringify(payload) }),
  updatePersona: (
    personaId: string,
    payload: Partial<Pick<Persona, "name" | "system_prompt" | "temperature" | "voice_preference">>
  ) => request<Persona>(`/personas/${personaId}`, { method: "PUT", body: JSON.stringify(payload) }),
  deletePersona: (personaId: string) => request<void>(`/personas/${personaId}`, { method: "DELETE" }),
  listConversations: (query = "") =>
    request<ConversationSummary[]>(`/conversations${query ? `?q=${encodeURIComponent(query)}` : ""}`),
  createConversation: (payload: { title: string; persona_id: string | null; persona_snapshot: PersonaSnapshot; mode: string }) =>
    request<ConversationSummary>("/conversations", { method: "POST", body: JSON.stringify(payload) }),
  getMessages: (conversationId: string) => request<Message[]>(`/conversations/${conversationId}/messages`),
  updateConversation: (conversationId: string, payload: object) =>
    request<ConversationSummary>(`/conversations/${conversationId}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteConversation: (conversationId: string) => request<void>(`/conversations/${conversationId}`, { method: "DELETE" }),
  sendMessage: (payload: {
    conversation_id: string;
    content_text: string;
    mode: string;
    system_prompt_override: string;
    temperature_override: number;
    voice_preference_override: VoicePreference;
  }) => request<SendMessageResponse>("/messages", { method: "POST", body: JSON.stringify(payload) }),
  sendVoiceMessage: async (
    conversationId: string,
    audioBlob: Blob,
    overrides: {
      systemPrompt: string;
      temperature: number;
      voicePreference: VoicePreference;
    }
  ) => {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");
    formData.append("system_prompt_override", overrides.systemPrompt);
    formData.append("temperature_override", String(overrides.temperature));
    formData.append("voice_preference_override", overrides.voicePreference);

    const response = await fetch(`${API_BASE}/voice/${conversationId}`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      let detail = response.statusText;
      try {
        const data = await response.json();
        detail = data.detail ?? detail;
      } catch {
        detail = await response.text();
      }
      throw new Error(detail || "Voice request failed");
    }

    return (await response.json()) as VoiceReplyResponse;
  }
};
