import os
import sqlite3
from datetime import datetime, timezone


USAGE_DB = os.getenv(
    "AI_CACHE_DB",
    "/app/data/ai_explanations.db"
)

DAILY_CALL_LIMIT = int(
    os.getenv("AI_DAILY_CALL_LIMIT", "100")
)


def get_connection():
    os.makedirs(os.path.dirname(USAGE_DB), exist_ok=True)

    connection = sqlite3.connect(USAGE_DB)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_time TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            total_tokens INTEGER NOT NULL DEFAULT 0,
            success INTEGER NOT NULL
        )
        """
    )

    connection.commit()

    return connection


def get_today_call_count():
    today = datetime.now(timezone.utc).date().isoformat()

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*)
            FROM ai_usage
            WHERE substr(request_time, 1, 10) = ?
            """,
            (today,)
        ).fetchone()

        return row[0]

    finally:
        connection.close()


def can_make_ai_request():
    return get_today_call_count() < DAILY_CALL_LIMIT


def record_ai_request(
    model,
    input_tokens=0,
    output_tokens=0,
    total_tokens=0,
    success=True
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO ai_usage (
                request_time,
                model,
                input_tokens,
                output_tokens,
                total_tokens,
                success
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                model,
                input_tokens,
                output_tokens,
                total_tokens,
                1 if success else 0
            )
        )

        connection.commit()

    finally:
        connection.close()