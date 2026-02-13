"""Agent-to-Agent communication protocol for Yo-tei."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import shortuuid


class MessageType(str, Enum):
    """Types of messages agents can send to each other."""

    # Discovery
    HELLO = "hello"                      # Agent announcing itself
    GOODBYE = "goodbye"                  # Agent going offline

    # Availability
    AVAILABILITY_QUERY = "availability_query"      # "When is your human free?"
    AVAILABILITY_RESPONSE = "availability_response"  # "Free these windows..."

    # Preferences
    PREFERENCE_QUERY = "preference_query"      # "Any preferences for X?"
    PREFERENCE_RESPONSE = "preference_response"  # "Prefers Y, avoids Z"

    # Proposals
    PROPOSAL = "proposal"                # "How about this plan?"
    PROPOSAL_RESPONSE = "proposal_response"  # "Accepted/Modified/Declined"

    # Nudges
    NUDGE = "nudge"                      # "Gentle reminder about X"
    NUDGE_ACK = "nudge_ack"              # "Nudge received"

    # Event updates
    EVENT_UPDATE = "event_update"        # "Status changed to X"
    EVENT_CANCELLED = "event_cancelled"  # "Event has been cancelled"

    # Social
    VIBE_CHECK = "vibe_check"            # "How's your human feeling about this?"
    VIBE_RESPONSE = "vibe_response"      # "Enthusiasm level: 4/5"

    # Conflict resolution
    CONFLICT_FLAG = "conflict_flag"      # "Potential issue detected"
    MEDIATION_REQUEST = "mediation_request"  # "Need help resolving..."
    MEDIATION_RESPONSE = "mediation_response"  # "Suggested resolution..."

    # System
    PING = "ping"                        # Heartbeat
    PONG = "pong"                        # Heartbeat response
    ERROR = "error"                      # Error message


class AgentMessage(BaseModel):
    """A message between agents."""

    # Identity
    id: str = Field(default_factory=lambda: f"MSG-{shortuuid.uuid()[:12]}")
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Routing
    sender_agent_id: str
    recipient_agent_id: str  # Can be "broadcast" for all agents in an event
    event_id: Optional[str] = None  # Event this message relates to

    # Content
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Privacy control
    shareable: bool = True  # If false, should not be logged or stored

    # Tracking
    reply_to: Optional[str] = None  # ID of message this replies to
    requires_response: bool = False
    response_timeout_seconds: int = 300  # 5 minutes default

    def to_wire(self) -> dict:
        """Serialize for transmission."""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender_agent_id,
            "recipient": self.recipient_agent_id,
            "event_id": self.event_id,
            "payload": self.payload,
            "reply_to": self.reply_to,
            "requires_response": self.requires_response,
        }

    @classmethod
    def from_wire(cls, data: dict) -> "AgentMessage":
        """Deserialize from transmission."""
        return cls(
            id=data["id"],
            type=MessageType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sender_agent_id=data["sender"],
            recipient_agent_id=data["recipient"],
            event_id=data.get("event_id"),
            payload=data.get("payload", {}),
            reply_to=data.get("reply_to"),
            requires_response=data.get("requires_response", False),
        )


# Message factory functions for common message types

def create_hello_message(agent_id: str, user_name: str) -> AgentMessage:
    """Create a hello message for agent discovery."""
    return AgentMessage(
        type=MessageType.HELLO,
        sender_agent_id=agent_id,
        recipient_agent_id="broadcast",
        payload={
            "user_name": user_name,
            "capabilities": ["scheduling", "social_intel", "nudges"],
        },
    )


def create_availability_query(
    sender_id: str,
    recipient_id: str,
    event_id: str,
    start_date: str,
    end_date: str,
    event_type: str,
) -> AgentMessage:
    """Create an availability query message."""
    return AgentMessage(
        type=MessageType.AVAILABILITY_QUERY,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        payload={
            "start_date": start_date,
            "end_date": end_date,
            "event_type": event_type,
        },
        requires_response=True,
    )


def create_availability_response(
    sender_id: str,
    recipient_id: str,
    event_id: str,
    reply_to: str,
    available_slots: List[dict],
) -> AgentMessage:
    """Create an availability response message."""
    return AgentMessage(
        type=MessageType.AVAILABILITY_RESPONSE,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        payload={
            "available_slots": available_slots,
        },
        reply_to=reply_to,
    )


def create_proposal_message(
    sender_id: str,
    recipient_id: str,
    event_id: str,
    proposal: dict,
) -> AgentMessage:
    """Create a proposal message."""
    return AgentMessage(
        type=MessageType.PROPOSAL,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        payload=proposal,
        requires_response=True,
    )


def create_proposal_response(
    sender_id: str,
    recipient_id: str,
    event_id: str,
    reply_to: str,
    decision: str,  # "accept", "modify", "decline"
    enthusiasm_level: int,
    modifications: Optional[List[str]] = None,
    reasoning: str = "",
) -> AgentMessage:
    """Create a proposal response message."""
    return AgentMessage(
        type=MessageType.PROPOSAL_RESPONSE,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        payload={
            "decision": decision,
            "enthusiasm_level": enthusiasm_level,
            "modifications_requested": modifications or [],
            "reasoning": reasoning,
        },
        reply_to=reply_to,
    )


def create_nudge_message(
    sender_id: str,
    recipient_id: str,
    event_id: Optional[str],
    topic: str,
    message: str,
) -> AgentMessage:
    """Create a nudge message."""
    return AgentMessage(
        type=MessageType.NUDGE,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        payload={
            "topic": topic,
            "message": message,
        },
    )


def create_vibe_check(
    sender_id: str,
    recipient_id: str,
    event_id: str,
) -> AgentMessage:
    """Create a vibe check message."""
    return AgentMessage(
        type=MessageType.VIBE_CHECK,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        requires_response=True,
    )


def create_vibe_response(
    sender_id: str,
    recipient_id: str,
    event_id: str,
    reply_to: str,
    enthusiasm_level: int,
    concerns: Optional[List[str]] = None,
) -> AgentMessage:
    """Create a vibe check response."""
    return AgentMessage(
        type=MessageType.VIBE_RESPONSE,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        event_id=event_id,
        payload={
            "enthusiasm_level": enthusiasm_level,
            "concerns": concerns or [],
        },
        reply_to=reply_to,
    )


def create_error_message(
    sender_id: str,
    recipient_id: str,
    error_code: str,
    error_message: str,
    reply_to: Optional[str] = None,
) -> AgentMessage:
    """Create an error message."""
    return AgentMessage(
        type=MessageType.ERROR,
        sender_agent_id=sender_id,
        recipient_agent_id=recipient_id,
        payload={
            "error_code": error_code,
            "error_message": error_message,
        },
        reply_to=reply_to,
    )
