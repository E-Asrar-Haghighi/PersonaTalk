import type { LLMProvider, Persona, VoicePreference } from "../api/types";

interface Props {
  personas: Persona[];
  selectedPersonaId: string | null;
  draftName: string;
  draftPrompt: string;
  draftTemperature: number;
  draftVoice: VoicePreference;
  llmProvider: LLMProvider;
  onSelectPersona: (personaId: string) => void;
  onFieldChange: (field: "name" | "system_prompt" | "temperature" | "voice_preference", value: string | number) => void;
  onLLMProviderChange: (provider: LLMProvider) => void;
  onSavePersona: () => void;
  onCreatePersona: () => void;
  onDeletePersona: () => void;
}

export function PersonaPanel(props: Props) {
  const {
    personas,
    selectedPersonaId,
    draftName,
    draftPrompt,
    draftTemperature,
    draftVoice,
    llmProvider,
    onSelectPersona,
    onFieldChange,
    onLLMProviderChange,
    onSavePersona,
    onCreatePersona,
    onDeletePersona
  } = props;

  return (
    <aside className="panel persona-panel">
      <div className="panel-header">
        <h2>Personas</h2>
        <button className="secondary-button" onClick={onCreatePersona}>
          New persona
        </button>
      </div>

      <div className="persona-list">
        {personas.map((persona) => (
          <button
            type="button"
            key={persona.id}
            className={`persona-chip ${selectedPersonaId === persona.id ? "active" : ""}`}
            onClick={() => onSelectPersona(persona.id)}
          >
            {persona.name}
          </button>
        ))}
      </div>

      <label>
        Persona name
        <input value={draftName} onChange={(event) => onFieldChange("name", event.target.value)} />
      </label>

      <label>
        System prompt
        <textarea
          value={draftPrompt}
          rows={10}
          onChange={(event) => onFieldChange("system_prompt", event.target.value)}
        />
      </label>

      <label>
        Temperature
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={draftTemperature}
          onChange={(event) => onFieldChange("temperature", Number(event.target.value))}
        />
        <span className="slider-value">{draftTemperature.toFixed(1)}</span>
      </label>

      <label>
        Voice
        <select value={draftVoice} onChange={(event) => onFieldChange("voice_preference", event.target.value)}>
          <option value="female">Female</option>
          <option value="male">Male</option>
        </select>
      </label>

      <label>
        Model
        <select value={llmProvider} onChange={(event) => onLLMProviderChange(event.target.value as LLMProvider)}>
          <option value="openai">GPT-4o mini</option>
          <option value="lm_studio">LM Studio Local</option>
          <option value="llama_cpp">Local GGUF</option>
        </select>
      </label>

      <div className="persona-actions">
        <button className="primary-button" onClick={onSavePersona}>
          Save persona
        </button>
        <button className="danger-button" onClick={onDeletePersona} disabled={!selectedPersonaId}>
          Delete
        </button>
      </div>
    </aside>
  );
}
