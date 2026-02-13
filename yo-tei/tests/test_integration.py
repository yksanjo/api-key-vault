"""Integration tests for Yo-tei."""

import asyncio
import pytest
from datetime import date, timedelta

from yotei.models.user import User
from yotei.models.friend import FriendRelationship, RelationshipType
from yotei.models.event import Event, EventType
from yotei.db.local import Database
from yotei.config.settings import Settings
from yotei.agent.core import Agent
from yotei.agent.scheduler import Scheduler
from pathlib import Path
import tempfile


class TestDatabase:
    """Tests for database operations."""

    @pytest.fixture
    async def db(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            await db.connect()
            yield db
            await db.close()

    @pytest.mark.asyncio
    async def test_save_and_get_user(self, db):
        user = User(name="Test User")
        await db.save_user(user)

        retrieved = await db.get_user(user.id)
        assert retrieved is not None
        assert retrieved.name == "Test User"

    @pytest.mark.asyncio
    async def test_save_and_get_friend(self, db):
        user = User(name="Test User")
        await db.save_user(user)

        friend = FriendRelationship(
            friend_id="YT-FRIEND-1234",
            friend_name="Friend",
            friend_code="YT-FRIEND-1234",
            private_notes="Test notes",
        )

        await db.save_friend(user.id, friend)

        friends = await db.get_all_friends(user.id)
        assert len(friends) == 1
        assert friends[0].friend_name == "Friend"
        assert friends[0].private_notes == "Test notes"

    @pytest.mark.asyncio
    async def test_save_and_get_event(self, db):
        event = Event(
            creator_id="YT-TEST-1234",
            title="Test Event",
            event_type=EventType.DINNER,
        )

        event.add_participant("YT-P1", "Participant 1", "AGENT-1")

        await db.save_event(event)

        retrieved = await db.get_event(event.id)
        assert retrieved is not None
        assert retrieved.title == "Test Event"
        assert len(retrieved.participants) == 1


class TestScheduler:
    """Tests for scheduling logic."""

    def test_find_common_slots(self):
        from yotei.models.user import AvailabilityBlock
        from yotei.models.schedule import Schedule

        scheduler = Scheduler()

        # Add two users with some overlap
        schedule1 = Schedule(
            user_id="U1",
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=9, end_hour=18),
                AvailabilityBlock(day_of_week=6, start_hour=10, end_hour=20),
            ]
        )

        schedule2 = Schedule(
            user_id="U2",
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=14, end_hour=22),
                AvailabilityBlock(day_of_week=6, start_hour=8, end_hour=16),
            ]
        )

        scheduler.add_schedule("U1", schedule1)
        scheduler.add_schedule("U2", schedule2)

        # Find slots
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=14)

        slots = scheduler.find_common_slots(
            EventType.DINNER,
            start,
            end,
            min_duration=2.0,
        )

        # Should find some common slots
        assert len(slots) > 0


class TestAgentCoordination:
    """Tests for agent coordination."""

    @pytest.mark.asyncio
    async def test_agent_creates_proposal(self):
        # This test would require mocking the DeepSeek API
        # For now, just test that the agent can be instantiated
        agent = Agent("YT-TEST-1234", "AGENT-TEST")
        assert agent.user_id == "YT-TEST-1234"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
