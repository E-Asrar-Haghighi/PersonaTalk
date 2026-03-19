import uuid
from datetime import UTC, datetime

from ..database import db_cursor
from ..schemas.chat import MessageRecord


class MessageRepository:
    def list_for_conversation(self, conversation_id: str) -> list[MessageRecord]:
        with db_cursor() as connection:
            rows = connection.execute(
                """
                SELECT id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            ).fetchall()
        return [MessageRecord.model_validate(dict(row)) for row in rows]

    def create(
        self,
        conversation_id: str,
        role: str,
        content_text: str,
        transcript_source: str = "text",
        audio_path: str | None = None,
        tts_status: str = "none",
    ) -> MessageRecord:
        message_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        with db_cursor() as connection:
            connection.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (message_id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, now),
            )
        return MessageRecord(
            id=message_id,
            conversation_id=conversation_id,
            role=role,
            content_text=content_text,
            audio_path=audio_path,
            tts_status=tts_status,
            transcript_source=transcript_source,
            created_at=datetime.fromisoformat(now),
        )

    def get(self, message_id: str) -> MessageRecord | None:
        with db_cursor() as connection:
            row = connection.execute(
                """
                SELECT id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, created_at
                FROM messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()
        return MessageRecord.model_validate(dict(row)) if row else None

    def get_latest_user_message(self, conversation_id: str) -> MessageRecord | None:
        with db_cursor() as connection:
            row = connection.execute(
                """
                SELECT id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, created_at
                FROM messages
                WHERE conversation_id = ? AND role = 'user'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (conversation_id,),
            ).fetchone()
        return MessageRecord.model_validate(dict(row)) if row else None

    def update_content(self, message_id: str, content_text: str, transcript_source: str) -> MessageRecord | None:
        with db_cursor() as connection:
            connection.execute(
                """
                UPDATE messages
                SET content_text = ?, audio_path = NULL, tts_status = 'none', transcript_source = ?
                WHERE id = ?
                """,
                (content_text, transcript_source, message_id),
            )
            row = connection.execute(
                """
                SELECT id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, created_at
                FROM messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()
        return MessageRecord.model_validate(dict(row)) if row else None

    def delete_after(self, conversation_id: str, created_at: datetime) -> None:
        with db_cursor() as connection:
            connection.execute(
                """
                DELETE FROM messages
                WHERE conversation_id = ? AND created_at > ?
                """,
                (conversation_id, created_at.isoformat()),
            )

    def update_tts_result(self, message_id: str, audio_path: str | None, tts_status: str) -> MessageRecord | None:
        with db_cursor() as connection:
            connection.execute(
                """
                UPDATE messages
                SET audio_path = ?, tts_status = ?
                WHERE id = ?
                """,
                (audio_path, tts_status, message_id),
            )
            row = connection.execute(
                """
                SELECT id, conversation_id, role, content_text, audio_path, tts_status, transcript_source, created_at
                FROM messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()

        return MessageRecord.model_validate(dict(row)) if row else None
