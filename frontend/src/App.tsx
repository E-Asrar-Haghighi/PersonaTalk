import { useEffect, useState } from "react";

import { api } from "./api/client";
import type {
  ChatMode,
  ConversationSummary,
  Message,
  Persona,
  PersonaSnapshot,
  VoicePreference
} from "./api/types";
import { ChatPane } from "./components/ChatPane";
import { ConversationSidebar } from "./components/ConversationSidebar";
import { PersonaPanel } from "./components/PersonaPanel";
import { useRecorder } from "./hooks/useRecorder";

const blankPersona = {
  id: "",
  name: "Custom Persona",
  system_prompt: "You are a thoughtful, practical AI companion.",
  temperature: 0.7,
  voice_preference: "female" as VoicePreference,
  created_at: "",
  updated_at: ""
};

export default function App() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(null);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [draftName, setDraftName] = useState(blankPersona.name);
  const [draftPrompt, setDraftPrompt] = useState(blankPersona.system_prompt);
  const [draftTemperature, setDraftTemperature] = useState(blankPersona.temperature);
  const [draftVoice, setDraftVoice] = useState<VoicePreference>(blankPersona.voice_preference);
  const [draftMessage, setDraftMessage] = useState("");
  const [mode, setMode] = useState<ChatMode>("text");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isRecording, start, stop, devices, selectedDeviceId, setSelectedDeviceId, refreshDevices } = useRecorder();
  const activeConversation = conversations.find((item) => item.id === activeConversationId) ?? null;

  useEffect(() => {
    void bootstrap();
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      void loadConversations(search);
    }, 180);
    return () => clearTimeout(timeout);
  }, [search]);

  async function bootstrap() {
    try {
      const [personaData, conversationData] = await Promise.all([api.listPersonas(), api.listConversations()]);
      setPersonas(personaData);
      setConversations(conversationData);
      if (personaData[0]) {
        applyPersona(personaData[0]);
      }
      if (conversationData[0]) {
        await selectConversation(conversationData[0].id, conversationData[0]);
      }
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function loadConversations(query = "") {
    try {
      const items = await api.listConversations(query);
      setConversations(items);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  function applyPersona(persona: Persona) {
    setSelectedPersonaId(persona.id);
    setDraftName(persona.name);
    setDraftPrompt(persona.system_prompt);
    setDraftTemperature(persona.temperature);
    setDraftVoice(persona.voice_preference);
  }

  async function selectConversation(conversationId: string, conversationOverride?: ConversationSummary) {
    setActiveConversationId(conversationId);
    setError(null);
    try {
      const conversation = conversationOverride ?? conversations.find((item) => item.id === conversationId) ?? null;
      const messageData = await api.getMessages(conversationId);
      setMessages(messageData);
      if (conversation) {
        setMode(conversation.mode);
        setDraftName(conversation.persona_snapshot.name);
        setDraftPrompt(conversation.persona_snapshot.system_prompt);
        setDraftTemperature(conversation.persona_snapshot.temperature);
        setDraftVoice(conversation.persona_snapshot.voice_preference);
        setSelectedPersonaId(conversation.persona_id);
      }
    } catch (err) {
      setError((err as Error).message);
    }
  }

  function currentSnapshot(): PersonaSnapshot {
    return {
      name: draftName.trim() || "Custom Persona",
      system_prompt: draftPrompt.trim() || blankPersona.system_prompt,
      temperature: draftTemperature,
      voice_preference: draftVoice
    };
  }

  async function ensureConversation(initialMode: ChatMode, openingText?: string) {
    if (activeConversationId) {
      return activeConversationId;
    }

    const titleSeed = openingText?.trim() || currentSnapshot().name;
    const conversation = await api.createConversation({
      title: titleSeed.slice(0, 48),
      persona_id: selectedPersonaId,
      persona_snapshot: currentSnapshot(),
      mode: initialMode
    });
    setActiveConversationId(conversation.id);
    setConversations((current) => [conversation, ...current]);
    return conversation.id;
  }

  async function handleSend() {
    if (!draftMessage.trim()) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const conversationId = await ensureConversation(mode, draftMessage);
      const response = await api.sendMessage({
        conversation_id: conversationId,
        content_text: draftMessage,
        mode,
        system_prompt_override: currentSnapshot().system_prompt,
        temperature_override: currentSnapshot().temperature,
        voice_preference_override: currentSnapshot().voice_preference
      });
      setMessages((current) => [...current, response.user_message, response.assistant_message]);
      setDraftMessage("");
      await refreshAfterReply(response.conversation);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleVoiceToggle() {
    setError(null);
    try {
      if (!isRecording) {
        await start();
        return;
      }

      setLoading(true);
      const audioBlob = await stop();
      const conversationId = await ensureConversation("voice");
      const response = await api.sendVoiceMessage(conversationId, audioBlob, {
        systemPrompt: currentSnapshot().system_prompt,
        temperature: currentSnapshot().temperature,
        voicePreference: currentSnapshot().voice_preference
      });
      setMessages((current) => [...current, response.user_message, response.assistant_message]);
      await refreshAfterReply(response.conversation);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshAfterReply(conversation: ConversationSummary) {
    setMode(conversation.mode);
    setConversations((current) => [conversation, ...current.filter((item) => item.id !== conversation.id)]);
  }

  async function handleNewChat() {
    setActiveConversationId(null);
    setMessages([]);
    setMode("text");
  }

  async function handleSavePersona() {
    setError(null);
    try {
      if (selectedPersonaId) {
        const persona = await api.updatePersona(selectedPersonaId, {
          name: draftName,
          system_prompt: draftPrompt,
          temperature: draftTemperature,
          voice_preference: draftVoice
        });
        setPersonas((current) => current.map((item) => (item.id === persona.id ? persona : item)));
        return;
      }

      const persona = await api.createPersona({
        name: draftName,
        system_prompt: draftPrompt,
        temperature: draftTemperature,
        voice_preference: draftVoice
      });
      setPersonas((current) => [persona, ...current]);
      setSelectedPersonaId(persona.id);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  function handleCreatePersona() {
    setSelectedPersonaId(null);
    setDraftName(blankPersona.name);
    setDraftPrompt(blankPersona.system_prompt);
    setDraftTemperature(blankPersona.temperature);
    setDraftVoice(blankPersona.voice_preference);
  }

  async function handleDeletePersona() {
    if (!selectedPersonaId) {
      return;
    }
    try {
      await api.deletePersona(selectedPersonaId);
      const next = personas.filter((persona) => persona.id !== selectedPersonaId);
      setPersonas(next);
      if (next[0]) {
        applyPersona(next[0]);
      } else {
        handleCreatePersona();
      }
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleDeleteConversation(conversationId: string) {
    try {
      await api.deleteConversation(conversationId);
      setConversations((current) => current.filter((conversation) => conversation.id !== conversationId));
      if (activeConversationId === conversationId) {
        await handleNewChat();
      }
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="app-shell">
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        search={search}
        onSearchChange={setSearch}
        onSelectConversation={(conversationId) => {
          void selectConversation(conversationId);
        }}
        onNewChat={() => {
          void handleNewChat();
        }}
        onDeleteConversation={(conversationId) => {
          void handleDeleteConversation(conversationId);
        }}
      />
      <ChatPane
        title={activeConversation?.title ?? "New conversation"}
        mode={mode}
        messages={messages}
        draft={draftMessage}
        loading={loading}
        canSend={Boolean(draftMessage.trim())}
        isRecording={isRecording}
        error={error}
        devices={devices}
        selectedDeviceId={selectedDeviceId}
        onDraftChange={setDraftMessage}
        onDeviceChange={setSelectedDeviceId}
        onRefreshDevices={() => {
          void refreshDevices();
        }}
        onModeChange={setMode}
        onSend={() => {
          void handleSend();
        }}
        onVoiceToggle={() => {
          void handleVoiceToggle();
        }}
      />
      <PersonaPanel
        personas={personas}
        selectedPersonaId={selectedPersonaId}
        draftName={draftName}
        draftPrompt={draftPrompt}
        draftTemperature={draftTemperature}
        draftVoice={draftVoice}
        onSelectPersona={(personaId) => {
          const persona = personas.find((item) => item.id === personaId);
          if (persona) {
            applyPersona(persona);
          }
        }}
        onFieldChange={(field, value) => {
          if (field === "name") setDraftName(String(value));
          if (field === "system_prompt") setDraftPrompt(String(value));
          if (field === "temperature") setDraftTemperature(Number(value));
          if (field === "voice_preference") setDraftVoice(value as VoicePreference);
        }}
        onSavePersona={() => {
          void handleSavePersona();
        }}
        onCreatePersona={handleCreatePersona}
        onDeletePersona={() => {
          void handleDeletePersona();
        }}
      />
    </div>
  );
}
