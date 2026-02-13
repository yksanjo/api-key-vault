"""Friend relationship model for Yo-tei."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    FRIEND = "friend"
    CLOSE_FRIEND = "close-friend"
    PARTNER = "partner"
    FAMILY = "family"
    COLLEAGUE = "colleague"


class GroupDynamic(BaseModel):
    """Describes dynamics when multiple friends are together."""

    friend_ids: List[str]  # The group this applies to
    vibe: str  # e.g., "great energy", "can be tense", "needs buffer"
    notes: str = ""  # Private notes about this combination
    avoid_topics: List[str] = Field(default_factory=list)

    @property
    def group_key(self) -> str:
        """Unique key for this group combination."""
        return "+".join(sorted(self.friend_ids))


class FriendRelationship(BaseModel):
    """A friend relationship with private social intelligence."""

    # Identity
    friend_id: str  # The friend's user ID (YT-XXX-XXX)
    friend_name: str
    friend_code: str  # The code used to connect

    # Relationship
    relationship_type: RelationshipType = RelationshipType.FRIEND
    connected_at: datetime = Field(default_factory=datetime.utcnow)

    # PRIVATE - Never shared with other agents
    private_notes: str = ""  # "Had falling out last year, avoid ex Mike"
    sensitivities: List[str] = Field(default_factory=list)  # Topics to avoid
    history_notes: str = ""  # History context
    conflict_history: List[str] = Field(default_factory=list)  # Past issues

    # Social dynamics hints (used by agent, not shared)
    enthusiasm_baseline: int = 3  # 1-5, how excited they usually are
    communication_preference: str = "text"  # How they prefer to hear news
    response_time_typical: str = "same-day"  # How fast they respond

    # Shared metadata (safe to share)
    shared_events_count: int = 0
    last_hangout: Optional[datetime] = None
    mutual_friends: List[str] = Field(default_factory=list)

    # Agent state
    agent_online: bool = False
    last_agent_contact: Optional[datetime] = None

    def to_shareable_dict(self) -> dict:
        """Return only information safe to share with other agents."""
        return {
            "friend_id": self.friend_id,
            "friend_name": self.friend_name,
            "relationship_type": self.relationship_type.value,
            "shared_events_count": self.shared_events_count,
            "mutual_friends": self.mutual_friends,
        }

    def to_agent_context(self) -> dict:
        """Full context for this user's agent (includes private info)."""
        return {
            "friend_id": self.friend_id,
            "friend_name": self.friend_name,
            "relationship_type": self.relationship_type.value,
            "private_notes": self.private_notes,
            "sensitivities": self.sensitivities,
            "history_notes": self.history_notes,
            "enthusiasm_baseline": self.enthusiasm_baseline,
            "communication_preference": self.communication_preference,
            "last_hangout": self.last_hangout.isoformat() if self.last_hangout else None,
        }


class SocialGraph(BaseModel):
    """The full social graph for a user."""

    user_id: str
    friends: Dict[str, FriendRelationship] = Field(default_factory=dict)
    group_dynamics: Dict[str, GroupDynamic] = Field(default_factory=dict)

    def add_friend(self, friend: FriendRelationship) -> bool:
        """Add a friend to the social graph."""
        if friend.friend_id in self.friends:
            return False
        self.friends[friend.friend_id] = friend
        return True

    def get_group_dynamic(self, friend_ids: List[str]) -> Optional[GroupDynamic]:
        """Get dynamics for a specific group combination."""
        key = "+".join(sorted(friend_ids))
        return self.group_dynamics.get(key)

    def get_all_sensitivities_for_group(self, friend_ids: List[str]) -> List[str]:
        """Get all topics to avoid for a group event."""
        sensitivities = set()

        # Individual sensitivities
        for fid in friend_ids:
            if fid in self.friends:
                sensitivities.update(self.friends[fid].sensitivities)

        # Group-specific topics to avoid
        dynamic = self.get_group_dynamic(friend_ids)
        if dynamic:
            sensitivities.update(dynamic.avoid_topics)

        return list(sensitivities)
