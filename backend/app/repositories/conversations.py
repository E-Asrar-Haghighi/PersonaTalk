import json
import uuid
from datetime import UTC, datetime

from ..database import db_cursor
from ..schemas.chat import ConversationCreate, ConversationSummary, ConversationUpdate, PersonaSnapshot


class ConversationRepository:
    def list(self, query: str | None = None) -> list[ConversationSummary]:
        sql = """
            SELECT c.id, c.title, c.persona_id, c.persona_name, c.persona_snapshot, c.temperature,
                   c.voice_preference, c.mode, c.created_at, c.updated_at,
                   COALESCE(
                     (
                       SELECT m.content_text
                       FROM messages m
                       WHERE m.conversation_id = c.id
                       ORDER BY m.created_at DESC
                       LIMIT 1
                     ),
                     ''
                   ) AS preview
            FROM conversations c
        """
        params: tuple[object, ...] = ()
        if query:
            sql += """
            WHERE c.title LIKE ?
               OR EXISTS (
                   SELECT 1 FROM messages m2
                   WHERE m2.conversation_id = c.id AND m2.content_text LIKE ?
               )
            """
            pattern = f"%{query}%"
            params = (pattern, pattern)
        sql += " ORDER BY c.updated_at DESC"

        with db_cursor() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [self._to_summary(dict(row)) for row in rows]

    def get(self, conversation_id: str) -> ConversationSummary | None:
        with db_cursor() as connection:
            row = connection.execute(
                """
                SELECT c.id, c.title, c.persona_id, c.persona_name, c.persona_snapshot, c.temperature,
                       c.voice_preference, c.mode, c.created_at, c.updated_at,
                       COALESCE(
                         (
                           SELECT m.content_text
                           FROM messages m
                           WHERE m.conversation_id = c.id
                           ORDER BY m.created_at DESC
                           LIMIT 1
                         ),
                         ''
                       ) AS preview
                FROM conversations c
                WHERE c.id = ?
                """,
                (conversation_id,),
            ).fetchone()
        return self._to_summary(dict(row)) if row else None

    def create(self, payload: ConversationCreate) -> ConversationSummary:
        now = datetime.now(UTC).isoformat()
        conversation_id = str(uuid.uuid4())
        with db_cursor() as connection:
            connection.execute(
                """
                INSERT INTO conversations (
                    id, title, persona_id, persona_name, persona_snapshot, temperature,
                    voice_preference, mode, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    payload.title,
                    payload.persona_id,
                    payload.persona_snapshot.name,
                    payload.persona_snapshot.model_dump_json(),
                    payload.persona_snapshot.temperature,
                    payload.persona_snapshot.voice_preference,
                    payload.mode,
                    now,
                    now,
                ),
            )
        return self.get(conversation_id)

    def update(self, conversation_id: str, payload: ConversationUpdate) -> ConversationSummary | None:
        current = self.get(conversation_id)
        if not current:
            return None

        snapshot = payload.persona_snapshot or current.persona_snapshot
        title = payload.title or current.title
        mode = payload.mode or current.mode
        persona_id = payload.persona_id if payload.persona_id is not None else current.persona_id
        updated_at = datetime.now(UTC).isoformat()

        with db_cursor() as connection:
            connection.execute(
                """
                UPDATE conversations
                SET title = ?, persona_id = ?, persona_name = ?, persona_snapshot = ?, temperature = ?,
                    voice_preference = ?, mode = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    title,
                    persona_id,
                    snapshot.name,
                    snapshot.model_dump_json(),
                    snapshot.temperature,
                    snapshot.voice_preference,
                    mode,
                    updated_at,
                    conversation_id,
                ),
            )
        return self.get(conversation_id)

    def touch(self, conversation_id: str) -> None:
        with db_cursor() as connection:
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (datetime.now(UTC).isoformat(), conversation_id),
            )

    def delete(self, conversation_id: str) -> bool:
        with db_cursor() as connection:
            result = connection.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        return result.rowcount > 0

    def _to_summary(self, row: dict) -> ConversationSummary:
        row["persona_snapshot"] = PersonaSnapshot.model_validate(json.loads(row["persona_snapshot"]))
        return ConversationSummary.model_validate(row)
