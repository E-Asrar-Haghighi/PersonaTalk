import { API_BASE } from "../api/client";
import ReactMarkdown from "react-markdown";
import type { ChatMode, LLMProvider, Message } from "../api/types";
import type { AudioInputDevice } from "../hooks/useRecorder";

interface Props {
  title: string;
  mode: ChatMode;
  llmProvider: LLMProvider;
  messages: Message[];
  draft: string;
  loading: boolean;
  canSend: boolean;
  isRecording: boolean;
  error: string | null;
  pendingAssistantAudio: boolean;
  latestAssistantTtsStatus: "none" | "pending" | "ready" | "failed" | null;
  editableMessageId: string | null;
  editingMessageId: string | null;
  editingMessageDraft: string;
  devices: AudioInputDevice[];
  hasMicrophoneAccess: boolean;
  selectedDeviceId: string;
  onDraftChange: (value: string) => void;
  onEditingDraftChange: (value: string) => void;
  onEnableMicrophoneAccess: () => void;
  onDeviceChange: (deviceId: string) => void;
  onRefreshDevices: () => void;
  onModeChange: (mode: ChatMode) => void;
  onStartEditing: (message: Message) => void;
  onCancelEditing: () => void;
  onSaveEditedMessage: () => void;
  onSend: () => void;
  onVoiceToggle: () => void;
}

export function ChatPane(props: Props) {
  const {
    title,
    mode,
    llmProvider,
    messages,
    draft,
    loading,
    canSend,
    isRecording,
    error,
    pendingAssistantAudio,
    latestAssistantTtsStatus,
    editableMessageId,
    editingMessageId,
    editingMessageDraft,
    devices,
    hasMicrophoneAccess,
    selectedDeviceId,
    onDraftChange,
    onEditingDraftChange,
    onEnableMicrophoneAccess,
    onDeviceChange,
    onRefreshDevices,
    onModeChange,
    onStartEditing,
    onCancelEditing,
    onSaveEditedMessage,
    onSend,
    onVoiceToggle
  } = props;
  const audioBase = API_BASE.replace(/\/api$/, "");

  return (
    <main className="panel chat-panel">
      <div className="panel-header">
        <div>
          <h1>{title}</h1>
          <p>
            Switch between text and voice in the same thread.
            <span className="model-badge">
              {llmProvider === "openai"
                ? "Model: GPT-4o mini"
                : llmProvider === "lm_studio"
                  ? "Model: LM Studio Local"
                  : "Model: Local GGUF"}
            </span>
          </p>
        </div>
        <div className="mode-toggle">
          {(["text", "voice", "mixed"] as ChatMode[]).map((value) => (
            <button
              key={value}
              className={mode === value ? "mode-button active" : "mode-button"}
              onClick={() => onModeChange(value)}
            >
              {value}
            </button>
          ))}
        </div>
      </div>

      <div className="message-thread">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h3>Start talking</h3>
            <p>Create a new chat or reopen one from the left sidebar.</p>
          </div>
        ) : (
          messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}>
              <div className="message__label">
                <span>{message.role}</span>
                <span>{new Date(message.created_at).toLocaleTimeString()}</span>
              </div>
              {editingMessageId === message.id ? (
                <div className="message-edit">
                  <textarea
                    value={editingMessageDraft}
                    onChange={(event) => onEditingDraftChange(event.target.value)}
                    rows={4}
                  />
                  <div className="message-edit__actions">
                    <button className="secondary-button" onClick={onCancelEditing}>
                      Cancel
                    </button>
                    <button className="primary-button" onClick={onSaveEditedMessage} disabled={!editingMessageDraft.trim()}>
                      Save and regenerate
                    </button>
                  </div>
                </div>
              ) : message.role === "assistant" ? (
                <FormattedAssistantMessage text={message.content_text} />
              ) : (
                <p>{message.content_text}</p>
              )}
              {message.id === editableMessageId && editingMessageId !== message.id ? (
                <div className="message__actions">
                  <button className="message-link" onClick={() => onStartEditing(message)}>
                    {message.transcript_source === "voice" || message.transcript_source === "voice-fallback"
                      ? "Edit transcript"
                      : "Edit last message"}
                  </button>
                </div>
              ) : null}
              {message.audio_path ? <audio controls src={`${audioBase}${message.audio_path}`} /> : null}
            </article>
          ))
        )}
      </div>

      {error ? <div className="error-banner">{error}</div> : null}
      {pendingAssistantAudio ? <div className="status-banner">Generating voice reply in the background...</div> : null}
      {latestAssistantTtsStatus === "failed" ? (
        <div className="status-banner">Voice generation did not finish for the latest reply.</div>
      ) : null}

      <div className="composer">
        <textarea
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
          placeholder="Type a message"
          rows={4}
        />
        {!hasMicrophoneAccess ? (
          <div className="mic-access-banner">
            <span>Enable microphone access to see the real mic names before your first recording.</span>
            <button className="secondary-button" onClick={onEnableMicrophoneAccess} disabled={loading || isRecording}>
              Enable microphone access
            </button>
          </div>
        ) : null}
        <div className="voice-device-row">
          <select value={selectedDeviceId} onChange={(event) => onDeviceChange(event.target.value)} disabled={isRecording}>
            {devices.length === 0 ? <option value="">No microphone detected</option> : null}
            {devices.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label}
              </option>
            ))}
          </select>
          <button className="secondary-button" onClick={onRefreshDevices} disabled={isRecording || loading}>
            Refresh mics
          </button>
        </div>
        <div className="composer-actions">
          <button className="secondary-button" onClick={onVoiceToggle} disabled={loading}>
            {isRecording ? "Stop recording" : "Push to talk"}
          </button>
          <button className="primary-button" onClick={onSend} disabled={!canSend || loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </main>
  );
}

function FormattedAssistantMessage({ text }: { text: string }) {
  const markdown = toDisplayMarkdown(text);

  return (
    <div className="message__rich-text">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
}

function toDisplayMarkdown(text: string): string {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const normalizedLines: string[] = [];

  for (let index = 0; index < lines.length; index += 1) {
    const rawLine = lines[index];
    const trimmed = rawLine.trim();
    if (!trimmed) {
      normalizedLines.push("");
      continue;
    }

    if (/^[-*+]\s+/.test(trimmed) || /^\d+[.)]\s+/.test(trimmed) || /^#{1,6}\s+/.test(trimmed)) {
      normalizedLines.push(trimmed);
      continue;
    }

    const headingMatch = trimmed.match(/^([A-Z][A-Za-z0-9/&(),'\-\s]{1,80}):$/);
    if (headingMatch) {
      normalizedLines.push(`### ${headingMatch[1].trim()}`);
      continue;
    }

    const labelMatch = trimmed.match(/^([A-Z][A-Za-z0-9/&(),'\-\s]{1,80}):\s+(.+)$/);
    if (labelMatch) {
      normalizedLines.push(`**${labelMatch[1].trim()}:** ${labelMatch[2].trim()}`);
      continue;
    }

    normalizedLines.push(rawLine);
  }

  const markdown = normalizedLines.join("\n");
  return markdown.replace(/\n{3,}/g, "\n\n").trim();
}
