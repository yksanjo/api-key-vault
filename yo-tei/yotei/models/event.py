"""Event model for Yo-tei."""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import shortuuid


class EventType(str, Enum):
    TRIP = "trip"
    HANGOUT = "hangout"
    DINNER = "dinner"
    ACTIVITY = "activity"
    PARTY = "party"
    MOVIE = "movie"
    GAME_NIGHT = "game-night"
    OUTDOOR = "outdoor"


class EventStatus(str, Enum):
    PLANNING = "planning"  # Agents are coordinating
    PROPOSED = "proposed"  # Proposal sent, waiting for responses
    CONFIRMED = "confirmed"  # Everyone agreed
    COMPLETED = "completed"  # Event happened
    CANCELLED = "cancelled"  # Event was cancelled


class Location(BaseModel):
    """Event location."""
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: str = ""  # e.g., "Park near the big oak tree"


class DateRange(BaseModel):
    """A date/time range for an event."""
    start: datetime
    end: datetime

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600


class Proposal(BaseModel):
    """A proposed plan from an agent."""

    id: str = Field(default_factory=lambda: f"PROP-{shortuuid.uuid()[:8]}")
    proposer_agent_id: str
    proposed_at: datetime = Field(default_factory=datetime.utcnow)

    # The proposal
    date_range: Optional[DateRange] = None
    location: Optional[Location] = None
    activity_suggestion: str = ""
    estimated_cost_per_person: Optional[float] = None

    # Reasoning (for transparency)
    reasoning: str = ""  # Why this proposal makes sense

    # Responses from other agents
    responses: Dict[str, str] = Field(default_factory=dict)  # agent_id -> "accept"/"modify"/"decline"
    modifications_requested: List[str] = Field(default_factory=list)

    @property
    def is_unanimous(self) -> bool:
        return all(r == "accept" for r in self.responses.values())


class AgentNote(BaseModel):
    """A note from agent coordination (for debugging/transparency)."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    note_type: str  # "negotiation", "concern", "suggestion", "decision"
    content: str
    private: bool = True  # If true, only visible to this user


class ParticipantStatus(BaseModel):
    """Status of a participant in an event."""

    user_id: str
    user_name: str
    agent_id: str

    # Status
    confirmed: bool = False
    enthusiasm_level: int = 3  # 1-5
    constraints_shared: List[str] = Field(default_factory=list)  # e.g., ["budget:$50-100"]

    # Agent state
    agent_responded: bool = False
    last_response_at: Optional[datetime] = None


class Event(BaseModel):
    """An event being planned by agents."""

    # Identity
    id: str = Field(default_factory=lambda: f"EVT-{shortuuid.uuid()[:8]}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Basic info
    creator_id: str
    title: str
    description: str = ""
    event_type: EventType = EventType.HANGOUT

    # Participants
    participants: List[ParticipantStatus] = Field(default_factory=list)

    # Status
    status: EventStatus = EventStatus.PLANNING

    # Decided details (filled in as agents coordinate)
    date_range: Optional[DateRange] = None
    location: Optional[Location] = None
    budget_per_person: Optional[float] = None

    # Coordination
    proposals: List[Proposal] = Field(default_factory=list)
    current_proposal_id: Optional[str] = None
    consensus_reached: bool = False

    # Agent activity log
    agent_notes: List[AgentNote] = Field(default_factory=list)

    # Nudges
    pending_nudges: Dict[str, List[str]] = Field(default_factory=dict)  # user_id -> [topics]

    def add_participant(self, user_id: str, user_name: str, agent_id: str):
        """Add a participant to the event."""
        if any(p.user_id == user_id for p in self.participants):
            return
        self.participants.append(
            ParticipantStatus(
                user_id=user_id,
                user_name=user_name,
                agent_id=agent_id,
            )
        )
        self.updated_at = datetime.utcnow()

    def add_proposal(self, proposal: Proposal):
        """Add a new proposal."""
        self.proposals.append(proposal)
        self.current_proposal_id = proposal.id
        self.updated_at = datetime.utcnow()

    def add_agent_note(self, agent_id: str, note_type: str, content: str, private: bool = True):
        """Add a coordination note."""
        self.agent_notes.append(
            AgentNote(
                agent_id=agent_id,
                note_type=note_type,
                content=content,
                private=private,
            )
        )
        self.updated_at = datetime.utcnow()

    def check_consensus(self) -> bool:
        """Check if all participants have confirmed."""
        if not self.current_proposal_id:
            return False

        current = next((p for p in self.proposals if p.id == self.current_proposal_id), None)
        if not current:
            return False

        # All participants need to accept
        participant_agents = {p.agent_id for p in self.participants}
        for agent_id in participant_agents:
            if current.responses.get(agent_id) != "accept":
                return False

        self.consensus_reached = True
        self.status = EventStatus.CONFIRMED
        self.date_range = current.date_range
        self.location = current.location
        self.updated_at = datetime.utcnow()
        return True

    def get_summary(self) -> dict:
        """Get a summary of the event for display."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.event_type.value,
            "status": self.status.value,
            "participants": [p.user_name for p in self.participants],
            "date": self.date_range.start.strftime("%b %d, %Y") if self.date_range else "TBD",
            "location": self.location.name if self.location else "TBD",
            "consensus": self.consensus_reached,
        }
