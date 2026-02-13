"""SQLite database operations for Yo-tei."""

import json
import aiosqlite
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from ..models.user import User
from ..models.friend import FriendRelationship, SocialGraph
from ..models.event import Event
from ..models.schedule import Schedule


def get_db_path() -> Path:
    """Get the database file path."""
    data_dir = Path.home() / ".yotei"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "yotei.db"


class Database:
    """SQLite database for Yo-tei local storage."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_db_path()
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Connect to the database."""
        self._connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()

    async def close(self):
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def _create_tables(self):
        """Create database tables if they don't exist."""
        async with self._connection.cursor() as cursor:
            # Users table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Friends table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS friends (
                    user_id TEXT NOT NULL,
                    friend_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, friend_id)
                )
            """)

            # Events table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    creator_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Event participants (for querying)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_participants (
                    event_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    PRIMARY KEY (event_id, user_id),
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            """)

            # Schedules table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    user_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Group dynamics table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_dynamics (
                    user_id TEXT NOT NULL,
                    group_key TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (user_id, group_key)
                )
            """)

            await self._connection.commit()

    # User operations
    async def save_user(self, user: User) -> None:
        """Save or update a user."""
        now = datetime.utcnow().isoformat()
        async with self._connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO users (id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (user.id, user.model_dump_json(), user.created_at.isoformat(), now))
            await self._connection.commit()

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT data FROM users WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return User.model_validate_json(row[0])
        return None

    async def get_current_user(self) -> Optional[User]:
        """Get the current (first) user - for single-user CLI."""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT data FROM users LIMIT 1")
            row = await cursor.fetchone()
            if row:
                return User.model_validate_json(row[0])
        return None

    async def delete_user(self, user_id: str) -> None:
        """Delete a user and all related data."""
        async with self._connection.cursor() as cursor:
            await cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            await cursor.execute("DELETE FROM friends WHERE user_id = ?", (user_id,))
            await cursor.execute("DELETE FROM schedules WHERE user_id = ?", (user_id,))
            await cursor.execute("DELETE FROM group_dynamics WHERE user_id = ?", (user_id,))
            await self._connection.commit()

    # Friend operations
    async def save_friend(self, user_id: str, friend: FriendRelationship) -> None:
        """Save or update a friend relationship."""
        now = datetime.utcnow().isoformat()
        async with self._connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO friends (user_id, friend_id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, friend.friend_id, friend.model_dump_json(), friend.connected_at.isoformat(), now))
            await self._connection.commit()

    async def get_friend(self, user_id: str, friend_id: str) -> Optional[FriendRelationship]:
        """Get a specific friend relationship."""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "SELECT data FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id)
            )
            row = await cursor.fetchone()
            if row:
                return FriendRelationship.model_validate_json(row[0])
        return None

    async def get_all_friends(self, user_id: str) -> List[FriendRelationship]:
        """Get all friends for a user."""
        friends = []
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT data FROM friends WHERE user_id = ?", (user_id,))
            rows = await cursor.fetchall()
            for row in rows:
                friends.append(FriendRelationship.model_validate_json(row[0]))
        return friends

    async def delete_friend(self, user_id: str, friend_id: str) -> None:
        """Delete a friend relationship."""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id)
            )
            await self._connection.commit()

    async def get_friends_count(self, user_id: str) -> int:
        """Get the number of friends for a user."""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "SELECT COUNT(*) FROM friends WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    # Event operations
    async def save_event(self, event: Event) -> None:
        """Save or update an event."""
        now = datetime.utcnow().isoformat()
        async with self._connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO events (id, creator_id, data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event.id, event.creator_id, event.model_dump_json(), event.status.value, event.created_at.isoformat(), now))

            # Update participants
            await cursor.execute("DELETE FROM event_participants WHERE event_id = ?", (event.id,))
            for participant in event.participants:
                await cursor.execute(
                    "INSERT INTO event_participants (event_id, user_id) VALUES (?, ?)",
                    (event.id, participant.user_id)
                )

            await self._connection.commit()

    async def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID."""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT data FROM events WHERE id = ?", (event_id,))
            row = await cursor.fetchone()
            if row:
                return Event.model_validate_json(row[0])
        return None

    async def get_user_events(self, user_id: str, status: Optional[str] = None) -> List[Event]:
        """Get all events for a user (as creator or participant)."""
        events = []
        async with self._connection.cursor() as cursor:
            query = """
                SELECT DISTINCT e.data FROM events e
                LEFT JOIN event_participants ep ON e.id = ep.event_id
                WHERE e.creator_id = ? OR ep.user_id = ?
            """
            params = [user_id, user_id]

            if status:
                query += " AND e.status = ?"
                params.append(status)

            query += " ORDER BY e.updated_at DESC"

            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            for row in rows:
                events.append(Event.model_validate_json(row[0]))
        return events

    async def get_active_events(self, user_id: str) -> List[Event]:
        """Get all active (planning/proposed/confirmed) events."""
        return await self.get_user_events(user_id)

    async def delete_event(self, event_id: str) -> None:
        """Delete an event."""
        async with self._connection.cursor() as cursor:
            await cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            await cursor.execute("DELETE FROM event_participants WHERE event_id = ?", (event_id,))
            await self._connection.commit()

    # Schedule operations
    async def save_schedule(self, schedule: Schedule) -> None:
        """Save or update a user's schedule."""
        now = datetime.utcnow().isoformat()
        async with self._connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO schedules (user_id, data, updated_at)
                VALUES (?, ?, ?)
            """, (schedule.user_id, schedule.model_dump_json(), now))
            await self._connection.commit()

    async def get_schedule(self, user_id: str) -> Optional[Schedule]:
        """Get a user's schedule."""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT data FROM schedules WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return Schedule.model_validate_json(row[0])
        return None


# Singleton instance
_db: Optional[Database] = None


async def get_db() -> Database:
    """Get the database singleton."""
    global _db
    if _db is None:
        _db = Database()
        await _db.connect()
    return _db


async def close_db() -> None:
    """Close the database connection."""
    global _db
    if _db is not None:
        await _db.close()
        _db = None
