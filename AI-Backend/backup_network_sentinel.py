import os
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


DATA_DIR = Path("/app/data")

BACKUP_ROOT = Path(
    os.getenv(
        "BACKUP_ROOT",
        "/app/backups"
    )
)

RETENTION_DAYS = int(
    os.getenv(
        "BACKUP_RETENTION_DAYS",
        "7"
    )
)


def backup_sqlite_database(
    source_path,
    destination_path
):
    """
    Create a consistent SQLite backup using SQLite's
    native backup API.
    """

    source_connection = sqlite3.connect(
        source_path
    )

    destination_connection = sqlite3.connect(
        destination_path
    )

    try:
        source_connection.backup(
            destination_connection
        )

    finally:
        destination_connection.close()
        source_connection.close()


def copy_if_exists(
    source_path,
    destination_path
):
    """
    Copy a normal file if it exists.
    """

    if source_path.exists():
        shutil.copy2(
            source_path,
            destination_path
        )


def remove_old_backups():
    """
    Remove timestamped backup directories older than
    the configured retention period.
    """

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(days=RETENTION_DAYS)
    )

    if not BACKUP_ROOT.exists():
        return

    for backup_dir in BACKUP_ROOT.iterdir():

        if not backup_dir.is_dir():
            continue

        try:
            backup_time = datetime.strptime(
                backup_dir.name,
                "%Y-%m-%d_%H-%M-%S"
            ).replace(
                tzinfo=timezone.utc
            )

        except ValueError:
            continue

        if backup_time < cutoff:
            shutil.rmtree(
                backup_dir
            )


def create_backup():
    """
    Create a timestamped Network Sentinel runtime backup.
    """

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_dir = (
        BACKUP_ROOT
        / timestamp
    )

    backup_dir.mkdir()

    ai_db = (
        DATA_DIR
        / "ai_explanations.db"
    )

    notification_db = (
        DATA_DIR
        / "notification_state.db"
    )

    threat_feed = (
        DATA_DIR
        / "spamhaus_drop.txt"
    )

    if ai_db.exists():
        backup_sqlite_database(
            ai_db,
            backup_dir
            / "ai_explanations.db"
        )

    if notification_db.exists():
        backup_sqlite_database(
            notification_db,
            backup_dir
            / "notification_state.db"
        )

    copy_if_exists(
        threat_feed,
        backup_dir
        / "spamhaus_drop.txt"
    )

    remove_old_backups()

    print(
        f"Backup completed: {backup_dir}"
    )


if __name__ == "__main__":
    create_backup()