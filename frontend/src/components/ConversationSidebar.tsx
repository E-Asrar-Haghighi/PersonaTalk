import type { ConversationSummary } from "../api/types";

interface Props {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  search: string;
  onSearchChange: (value: string) => void;
  onSelectConversation: (conversationId: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (conversationId: string) => void;
}

export function ConversationSidebar(props: Props) {
  const {
    conversations,
    activeConversationId,
    search,
    onSearchChange,
    onSelectConversation,
    onNewChat,
    onDeleteConversation
  } = props;

  return (
    <aside className="panel sidebar">
      <div className="panel-header">
        <h2>Conversations</h2>
        <button className="primary-button" onClick={onNewChat}>
          New chat
        </button>
      </div>
      <input
        className="search-input"
        value={search}
        onChange={(event) => onSearchChange(event.target.value)}
        placeholder="Search titles or messages"
      />
      <div className="conversation-list">
        {conversations.map((conversation) => (
          <button
            type="button"
            key={conversation.id}
            className={`conversation-card ${activeConversationId === conversation.id ? "active" : ""}`}
            onClick={() => onSelectConversation(conversation.id)}
          >
            <div className="conversation-card__top">
              <strong>{conversation.title}</strong>
              <span>{new Date(conversation.updated_at).toLocaleDateString()}</span>
            </div>
            <div className="conversation-card__meta">
              <span>{conversation.persona_snapshot.name}</span>
              <span>{conversation.mode}</span>
            </div>
            <p>{conversation.preview || "No messages yet."}</p>
            <span
              className="danger-link"
              onClick={(event) => {
                event.stopPropagation();
                onDeleteConversation(conversation.id);
              }}
            >
              Delete
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}
