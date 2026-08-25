import json
import os
import sqlite3
from datetime import datetime, timezone


CACHE_DB = os.getenv(
    "AI_CACHE_DB",
    "/app/data/ai_explanations.db"
)

CACHE_VERSION = "v2"


def get_connection():
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)

    connection = sqlite3.connect(CACHE_DB)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS explanations (
            cache_key TEXT PRIMARY KEY,
            alert_title TEXT NOT NULL,
            risk TEXT NOT NULL,
            analysis TEXT NOT NULL,
            why_it_matters TEXT NOT NULL,
            recommended_actions TEXT NOT NULL,
            model TEXT,
            cache_version TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    return connection


def build_cache_key(alert):
    title = alert.get("title", "Unknown Security Event")
    risk = alert.get("risk", "Unknown")

    return f"{CACHE_VERSION}|{risk}|{title}".lower()


def get_cached_explanation(alert):
    cache_key = build_cache_key(alert)

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                analysis,
                why_it_matters,
                recommended_actions,
                model,
                created_at
            FROM explanations
            WHERE cache_key = ?
            """,
            (cache_key,)
        ).fetchone()

        if not row:
            return None

        return {
            "analysis": row[0],
            "why_it_matters": row[1],
            "recommended_actions": json.loads(row[2]),
            "model": row[3],
            "created_at": row[4]
        }

    finally:
        connection.close()


def save_explanation(alert, explanation, model):
    cache_key = build_cache_key(alert)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO explanations (
                cache_key,
                alert_title,
                risk,
                analysis,
                why_it_matters,
                recommended_actions,
                model,
                cache_version,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cache_key,
                alert.get("title", "Unknown Security Event"),
                alert.get("risk", "Unknown"),
                explanation["analysis"],
                explanation["why_it_matters"],
                json.dumps(explanation["recommended_actions"]),
                model,
                CACHE_VERSION,
                datetime.now(timezone.utc).isoformat()
            )
        )

        connection.commit()

    finally:
        connection.close()