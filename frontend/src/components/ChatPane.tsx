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
  selectedDeviceId: string;
  onDraftChange: (value: string) => void;
  onEditingDraftChange: (value: string) => void;
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
    selectedDeviceId,
    onDraftChange,
    onEditingDraftChange,
    onDeviceChange,
    onRefreshDevices,
    onModeChange,
    onStartEditing,
    onCancelEditing,
    onSaveEditedMessage,
    onSend,
    onVoiceToggle
  } = props;

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
              {message.audio_path ? <audio controls src={`http://localhost:8000${message.audio_path}`} /> : null}
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
