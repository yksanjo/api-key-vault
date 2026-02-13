"""Core Agent for Yo-tei - The brain that coordinates events."""

import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

from ..models.user import User
from ..models.friend import FriendRelationship
from ..models.event import Event, Proposal, EventStatus, AgentNote, ParticipantStatus
from ..models.schedule import Schedule, TimeSlot
from ..db.local import get_db
from ..config.settings import get_settings
from .social_intel import SocialIntelligence
from .scheduler import Scheduler, create_scheduler_from_event


class Agent:
    """The Yo-tei agent - coordinates events using social intelligence."""

    def __init__(self, user_id: str, agent_id: str):
        self.user_id = user_id
        self.agent_id = agent_id
        self.social_intel = SocialIntelligence()
        self.scheduler = Scheduler()

    async def get_user(self) -> Optional[User]:
        """Get the agent's user."""
        db = await get_db()
        return await db.get_current_user()

    async def get_friends(self) -> List[FriendRelationship]:
        """Get all friends."""
        db = await get_db()
        return await db.get_all_friends(self.user_id)

    async def get_friend_context(self, friend_ids: List[str]) -> Dict[str, dict]:
        """Get private context about friends for social intelligence."""
        friends = await self.get_friends()
        context = {}

        for friend in friends:
            if friend.friend_id in friend_ids:
                context[friend.friend_name] = {
                    "relationship": friend.relationship_type.value,
                    "private_notes": friend.private_notes,
                    "sensitivities": friend.sensitivities,
                    "enthusiasm_baseline": friend.enthusiasm_baseline,
                }

        return context

    async def coordinate_event(self, event: Event) -> dict:
        """Main coordination flow for an event."""

        user = await self.get_user()
        if not user:
            return {"error": "User not found"}

        # Get friend IDs from participants
        friend_ids = [p.user_id for p in event.participants if p.user_id != self.user_id]
        friend_context = await self.get_friend_context(friend_ids)

        # Build user preferences
        user_preferences = user.to_shareable_dict()

        # Get user's schedule
        db = await get_db()
        user_schedule = await db.get_schedule(self.user_id)

        # Set up scheduler with user's schedule
        if user_schedule:
            self.scheduler.add_schedule(self.user_id, user_schedule)

        # For other participants, create default schedules (in production, would query their agents)
        for participant in event.participants:
            if participant.user_id != self.user_id:
                # Create a default schedule (weekend + evenings)
                default_schedule = self._create_default_schedule(participant.user_id)
                self.scheduler.add_schedule(participant.user_id, default_schedule)

        # Find common availability
        start_date, end_date = self.scheduler.suggest_date_range(event.event_type)
        available_slots = self.scheduler.find_common_slots(
            event.event_type,
            start_date,
            end_date,
        )

        # Log coordination start
        event.add_agent_note(
            self.agent_id,
            "negotiation",
            f"Starting coordination for {event.title} with {len(event.participants)} participants",
            private=False
        )

        if not available_slots:
            event.add_agent_note(
                self.agent_id,
                "concern",
                "No common availability found in the next 30 days. Expanding search...",
                private=False
            )
            # Try with extended range
            end_date = start_date + timedelta(days=60)
            available_slots = self.scheduler.find_common_slots(
                event.event_type,
                start_date,
                end_date,
            )

        # Build private notes for social intelligence
        private_notes = {
            name: ctx.get("private_notes", "")
            for name, ctx in friend_context.items()
            if ctx.get("private_notes")
        }

        # Create proposal using social intelligence
        try:
            proposal = await self.social_intel.create_proposal(
                event=event,
                user_name=user.name,
                user_preferences=user_preferences,
                private_notes=private_notes,
                available_slots=available_slots,
            )

            event.add_proposal(proposal)
            event.add_agent_note(
                self.agent_id,
                "suggestion",
                f"Proposed: {proposal.date_range.start.strftime('%b %d')} at {proposal.location.name if proposal.location else 'TBD'}",
                private=False
            )

            # In a full implementation, we would now send this proposal to other agents
            # and wait for their responses. For MVP, we simulate acceptance.
            await self._simulate_agent_responses(event, proposal, friend_context)

            # Check for consensus
            consensus = event.check_consensus()

            if consensus:
                event.add_agent_note(
                    self.agent_id,
                    "decision",
                    f"Consensus reached! Event confirmed for {event.date_range.start.strftime('%b %d, %Y')}",
                    private=False
                )

            return {
                "success": True,
                "consensus": consensus,
                "proposal": {
                    "date": proposal.date_range.start.isoformat() if proposal.date_range else None,
                    "location": proposal.location.name if proposal.location else None,
                    "reasoning": proposal.reasoning,
                },
                "participant_responses": proposal.responses,
            }

        except Exception as e:
            event.add_agent_note(
                self.agent_id,
                "concern",
                f"Coordination error: {str(e)}",
                private=True
            )
            return {"error": str(e), "success": False}

    async def _simulate_agent_responses(
        self,
        event: Event,
        proposal: Proposal,
        friend_context: Dict[str, dict]
    ):
        """Simulate responses from other agents (for MVP)."""

        # In production, this would send messages to other agents via the relay
        # and wait for their responses. For now, we use social intelligence
        # to simulate what their response would likely be.

        for participant in event.participants:
            if participant.user_id == self.user_id:
                # Creator auto-accepts
                proposal.responses[participant.agent_id] = "accept"
                participant.confirmed = True
                continue

            # Simulate other participant's agent evaluating the proposal
            friend_name = participant.user_name
            friend_ctx = friend_context.get(friend_name, {})

            # Simple heuristic: accept if enthusiasm baseline is 3+ and no blocking issues
            enthusiasm = friend_ctx.get("enthusiasm_baseline", 3)
            sensitivities = friend_ctx.get("sensitivities", [])

            # Check if proposal conflicts with sensitivities
            has_conflict = any(
                sens.lower() in (proposal.reasoning or "").lower()
                for sens in sensitivities
            )

            if enthusiasm >= 3 and not has_conflict:
                proposal.responses[participant.agent_id] = "accept"
                participant.confirmed = True
                participant.enthusiasm_level = enthusiasm
                event.add_agent_note(
                    participant.agent_id,
                    "decision",
                    f"{friend_name}'s agent accepted the proposal",
                    private=False
                )
            else:
                proposal.responses[participant.agent_id] = "modify"
                event.add_agent_note(
                    participant.agent_id,
                    "concern",
                    f"{friend_name}'s agent requested modifications",
                    private=False
                )

    def _create_default_schedule(self, user_id: str) -> Schedule:
        """Create a default schedule for participants without one."""
        from ..models.user import AvailabilityBlock

        return Schedule(
            user_id=user_id,
            default_availability=[
                # Weekends
                AvailabilityBlock(day_of_week=5, start_hour=10, end_hour=22, label="Saturday"),
                AvailabilityBlock(day_of_week=6, start_hour=10, end_hour=22, label="Sunday"),
                # Weekday evenings
                AvailabilityBlock(day_of_week=0, start_hour=18, end_hour=22, label="Mon evening"),
                AvailabilityBlock(day_of_week=1, start_hour=18, end_hour=22, label="Tue evening"),
                AvailabilityBlock(day_of_week=2, start_hour=18, end_hour=22, label="Wed evening"),
                AvailabilityBlock(day_of_week=3, start_hour=18, end_hour=22, label="Thu evening"),
                AvailabilityBlock(day_of_week=4, start_hour=18, end_hour=22, label="Fri evening"),
            ]
        )

    async def send_nudge(
        self,
        friend: FriendRelationship,
        topic: str,
    ) -> str:
        """Send a nudge to a friend's agent."""

        user = await self.get_user()
        if not user:
            return "Error: User not found"

        # Generate personalized nudge message
        message = await self.social_intel.generate_nudge_message(
            friend_name=friend.friend_name,
            topic=topic,
            relationship_type=friend.relationship_type.value,
            communication_style=friend.communication_preference,
        )

        # In production, this would send the message through the relay
        # For now, just return the message
        return message

    async def analyze_event_group(self, event: Event) -> dict:
        """Analyze group dynamics for an event."""

        friend_ids = [p.user_id for p in event.participants if p.user_id != self.user_id]
        friends = await self.get_friends()

        relationships = {
            f.friend_name: f
            for f in friends
            if f.friend_id in friend_ids
        }

        participant_names = [p.user_name for p in event.participants]

        return await self.social_intel.analyze_group_dynamics(
            participants=participant_names,
            relationships=relationships,
        )


class AgentRunner:
    """Runs the agent as a background service."""

    def __init__(self, user_id: str, agent_id: str):
        self.agent = Agent(user_id, agent_id)
        self.running = False

    async def start(self):
        """Start the agent runner."""
        self.running = True
        while self.running:
            await self._check_pending_events()
            await asyncio.sleep(60)  # Check every minute

    async def stop(self):
        """Stop the agent runner."""
        self.running = False

    async def _check_pending_events(self):
        """Check for events needing coordination."""
        db = await get_db()
        events = await db.get_active_events(self.agent.user_id)

        for event in events:
            if event.status == EventStatus.PLANNING:
                await self.agent.coordinate_event(event)
                await db.save_event(event)
