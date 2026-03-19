import { useState } from "react";

import type { ConversationSummary } from "../api/types";

interface Props {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  search: string;
  onSearchChange: (value: string) => void;
  onSelectConversation: (conversationId: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (conversationId: string) => void;
  onRenameConversation: (conversationId: string, title: string) => void;
}

export function ConversationSidebar(props: Props) {
  const {
    conversations,
    activeConversationId,
    search,
    onSearchChange,
    onSelectConversation,
    onNewChat,
    onDeleteConversation,
    onRenameConversation
  } = props;
  const [editingConversationId, setEditingConversationId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  function startEditing(conversation: ConversationSummary) {
    setEditingConversationId(conversation.id);
    setEditingTitle(conversation.title);
  }

  function cancelEditing() {
    setEditingConversationId(null);
    setEditingTitle("");
  }

  function saveEditing(conversationId: string) {
    const nextTitle = editingTitle.trim();
    if (!nextTitle) {
      return;
    }
    onRenameConversation(conversationId, nextTitle);
    cancelEditing();
  }

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
              {editingConversationId === conversation.id ? (
                <div
                  className="conversation-title-edit"
                  onClick={(event) => {
                    event.stopPropagation();
                  }}
                >
                  <input
                    value={editingTitle}
                    onChange={(event) => setEditingTitle(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        saveEditing(conversation.id);
                      }
                      if (event.key === "Escape") {
                        event.preventDefault();
                        cancelEditing();
                      }
                    }}
                    autoFocus
                  />
                  <div className="conversation-title-edit__actions">
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => cancelEditing()}
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      className="primary-button"
                      onClick={() => saveEditing(conversation.id)}
                      disabled={!editingTitle.trim()}
                    >
                      Save
                    </button>
                  </div>
                </div>
              ) : (
                <strong>{conversation.title}</strong>
              )}
              <span>{new Date(conversation.updated_at).toLocaleDateString()}</span>
            </div>
            <div className="conversation-card__meta">
              <span>{conversation.persona_snapshot.name}</span>
              <span>{conversation.mode}</span>
            </div>
            <p>{conversation.preview || "No messages yet."}</p>
            <div className="conversation-card__actions">
              {editingConversationId !== conversation.id ? (
                <span
                  className="danger-link"
                  onClick={(event) => {
                    event.stopPropagation();
                    startEditing(conversation);
                  }}
                >
                  Edit title
                </span>
              ) : null}
              <span
                className="danger-link"
                onClick={(event) => {
                  event.stopPropagation();
                  onDeleteConversation(conversation.id);
                }}
              >
                Delete
              </span>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}
