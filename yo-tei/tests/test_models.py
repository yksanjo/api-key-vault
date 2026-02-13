"""Tests for Yo-tei data models."""

import pytest
from datetime import datetime, date, timedelta

from yotei.models.user import User, AvailabilityBlock, BudgetRange, generate_friend_code
from yotei.models.friend import FriendRelationship, RelationshipType, SocialGraph
from yotei.models.event import Event, EventType, EventStatus, Proposal
from yotei.models.schedule import Schedule, TimeSlot, find_common_availability


class TestUser:
    """Tests for User model."""

    def test_user_creation(self):
        user = User(name="Sarah")
        assert user.name == "Sarah"
        assert user.id.startswith("YT-")
        assert user.agent_id.startswith("AGENT-")

    def test_friend_code_generation(self):
        user = User(name="Sarah")
        code = user.friend_code
        assert code.startswith("YT-SARAH-")

    def test_can_add_friends_free_tier(self):
        user = User(name="Test", friends_count=0)
        assert user.can_add_friends

        user.friends_count = 5
        assert not user.can_add_friends

    def test_availability_check(self):
        user = User(
            name="Test",
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=10, end_hour=18),  # Saturday
            ]
        )

        # Find a Saturday at 14:00
        saturday = date.today()
        while saturday.weekday() != 5:
            saturday += timedelta(days=1)

        saturday_2pm = datetime.combine(saturday, datetime.min.time().replace(hour=14))
        assert user.is_available(saturday_2pm)

        # Monday should not be available
        monday = saturday + timedelta(days=2)
        monday_2pm = datetime.combine(monday, datetime.min.time().replace(hour=14))
        assert not user.is_available(monday_2pm)


class TestFriendRelationship:
    """Tests for FriendRelationship model."""

    def test_friend_creation(self):
        friend = FriendRelationship(
            friend_id="YT-ABBY-1234",
            friend_name="Abby",
            friend_code="YT-ABBY-1234",
            relationship_type=RelationshipType.CLOSE_FRIEND,
            private_notes="Best friend since college",
        )

        assert friend.friend_name == "Abby"
        assert friend.relationship_type == RelationshipType.CLOSE_FRIEND

    def test_shareable_dict_excludes_private(self):
        friend = FriendRelationship(
            friend_id="YT-ABBY-1234",
            friend_name="Abby",
            friend_code="YT-ABBY-1234",
            private_notes="Secret notes",
            sensitivities=["money"],
        )

        shareable = friend.to_shareable_dict()
        assert "private_notes" not in shareable
        assert "sensitivities" not in shareable
        assert shareable["friend_name"] == "Abby"


class TestEvent:
    """Tests for Event model."""

    def test_event_creation(self):
        event = Event(
            creator_id="YT-TEST-1234",
            title="Ski Trip",
            event_type=EventType.TRIP,
        )

        assert event.title == "Ski Trip"
        assert event.status == EventStatus.PLANNING
        assert event.id.startswith("EVT-")

    def test_add_participant(self):
        event = Event(
            creator_id="YT-TEST-1234",
            title="Dinner",
        )

        event.add_participant("YT-FRIEND-1", "Friend1", "AGENT-1")
        event.add_participant("YT-FRIEND-2", "Friend2", "AGENT-2")

        assert len(event.participants) == 2
        assert event.participants[0].user_name == "Friend1"

    def test_check_consensus(self):
        event = Event(
            creator_id="YT-TEST-1234",
            title="Dinner",
        )

        # Add participants
        from yotei.models.event import ParticipantStatus
        event.participants = [
            ParticipantStatus(user_id="U1", user_name="User1", agent_id="A1"),
            ParticipantStatus(user_id="U2", user_name="User2", agent_id="A2"),
        ]

        # Create proposal
        proposal = Proposal(proposer_agent_id="A1")
        event.add_proposal(proposal)

        # No consensus yet
        assert not event.check_consensus()

        # Add acceptances
        proposal.responses["A1"] = "accept"
        proposal.responses["A2"] = "accept"

        assert event.check_consensus()
        assert event.consensus_reached
        assert event.status == EventStatus.CONFIRMED


class TestSchedule:
    """Tests for Schedule model."""

    def test_availability_for_date(self):
        schedule = Schedule(
            user_id="TEST",
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=10, end_hour=20),  # Saturday
            ]
        )

        # Find a Saturday
        saturday = date.today()
        while saturday.weekday() != 5:
            saturday += timedelta(days=1)

        slots = schedule.get_availability_for_date(saturday)
        assert len(slots) == 1
        assert slots[0].start.hour == 10
        assert slots[0].end.hour == 20

    def test_find_common_availability(self):
        # Two users with overlapping Saturday availability
        schedule1 = Schedule(
            user_id="U1",
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=10, end_hour=18),
            ]
        )

        schedule2 = Schedule(
            user_id="U2",
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=14, end_hour=22),
            ]
        )

        # Find a Saturday
        saturday = date.today()
        while saturday.weekday() != 5:
            saturday += timedelta(days=1)

        common = find_common_availability(
            [schedule1, schedule2],
            saturday,
            saturday + timedelta(days=7),
            min_duration_hours=2.0,
        )

        # Should find overlapping slot (14:00 - 18:00)
        assert len(common) >= 1
        slot = common[0]
        assert slot.start.hour == 14
        assert slot.end.hour == 18


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
