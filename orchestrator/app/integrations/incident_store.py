import sqlite3
import json
from pathlib import Path
from contextlib import closing
from datetime import datetime, timezone


# data/incidents.db
class IncidentStore:
    def __init__(self, database_path: str | None = None) -> None:
        if database_path is None:
            self.database_path = Path("data/incidents.db")
        else:
            self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL,
                        namespace TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        resource_name TEXT NOT NULL,
                        trigger TEXT NOT NULL,
                        diagnosis TEXT,
                        action TEXT,
                        status TEXT NOT NULL,
                        details TEXT
                    )
                """)

    def create_incident(
        self,
        namespace: str,
        resource_type: str,
        resource_name: str,
        trigger: str,
        status: str,
        diagnosis: str | None = None,
        action: str | None = None,
        details: dict | None = None,
    ) -> dict:

        created_at = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details) if details is not None else None

        incident = {
            "created_at": created_at,
            "namespace": namespace,
            "resource_type": resource_type,
            "resource_name": resource_name,
            "trigger": trigger,
            "diagnosis": diagnosis,
            "action": action,
            "status": status,
            "details": details,
        }

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO incidents (
                        created_at, namespace, resource_type,
                        resource_name, trigger, diagnosis,
                        action, status, details
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        created_at,
                        namespace,
                        resource_type,
                        resource_name,
                        trigger,
                        diagnosis,
                        action,
                        status,
                        details_json,
                    ),
                )
                incident["id"] = cursor.lastrowid

        return incident

    def list_incidents(self, limit: int = 100, offset: int = 0) -> list[dict]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT * FROM incidents
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()

        incidents = []
        for row in rows:
            incident = dict(row)
            incident["details"] = (
                json.loads(incident["details"])
                if incident["details"] is not None
                else None
            )
            incidents.append(incident)

        return incidents

    def get_incident(self, incident_id: int) -> dict | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?",
                (incident_id,),
            ).fetchone()

        if row is None:
            return None

        incident = dict(row)
        incident["details"] = (
            json.loads(incident["details"]) if incident["details"] is not None else None
        )

        return incident
