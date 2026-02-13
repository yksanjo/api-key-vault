"""User model for Yo-tei."""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import shortuuid


class CommunicationStyle(str, Enum):
    DIRECT = "direct"
    GENTLE = "gentle"
    MINIMAL = "minimal"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"


class BudgetRange(BaseModel):
    """Budget preferences for events."""
    min_amount: float = 0
    max_amount: float = 500
    currency: str = "USD"
    flexible: bool = True  # Can stretch for special occasions


class AvailabilityBlock(BaseModel):
    """A recurring availability window."""
    day_of_week: int  # 0=Monday, 6=Sunday
    start_hour: int  # 0-23
    end_hour: int  # 0-23
    label: str = ""  # e.g., "After work"


class BlackoutDate(BaseModel):
    """A date range when user is unavailable."""
    start_date: date
    end_date: date
    reason: str = ""  # Private, never shared


class User(BaseModel):
    """User profile for Yo-tei."""

    # Identity
    id: str = Field(default_factory=lambda: f"YT-{shortuuid.uuid()[:8].upper()}")
    name: str
    agent_id: str = Field(default_factory=lambda: f"AGENT-{shortuuid.uuid()[:12]}")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Schedule preferences
    default_availability: List[AvailabilityBlock] = Field(default_factory=list)
    blackout_dates: List[BlackoutDate] = Field(default_factory=list)
    timezone: str = "America/Los_Angeles"

    # General preferences
    budget_range: BudgetRange = Field(default_factory=BudgetRange)
    dietary: List[str] = Field(default_factory=list)  # e.g., ["vegetarian", "no-nuts"]
    accessibility: List[str] = Field(default_factory=list)  # e.g., ["wheelchair"]
    travel_radius_miles: int = 50
    communication_style: CommunicationStyle = CommunicationStyle.GENTLE

    # Subscription
    tier: SubscriptionTier = SubscriptionTier.FREE
    friends_count: int = 0

    @property
    def friend_code(self) -> str:
        """Human-friendly friend code for sharing."""
        name_part = self.name.upper()[:5].replace(" ", "")
        id_part = self.id.split("-")[1][:4]
        return f"YT-{name_part}-{id_part}"

    @property
    def can_add_friends(self) -> bool:
        """Check if user can add more friends."""
        if self.tier == SubscriptionTier.PRO:
            return True
        return self.friends_count < 5

    def is_available(self, dt: datetime) -> bool:
        """Check if user is available at a given datetime."""
        # Check blackout dates
        for blackout in self.blackout_dates:
            if blackout.start_date <= dt.date() <= blackout.end_date:
                return False

        # Check availability blocks
        day_of_week = dt.weekday()
        hour = dt.hour

        for block in self.default_availability:
            if block.day_of_week == day_of_week:
                if block.start_hour <= hour < block.end_hour:
                    return True

        return False

    def to_shareable_dict(self) -> dict:
        """Return only information safe to share with other agents."""
        return {
            "id": self.id,
            "name": self.name,
            "timezone": self.timezone,
            "travel_radius_miles": self.travel_radius_miles,
            "dietary": self.dietary,  # Shared for event planning
            "accessibility": self.accessibility,  # Shared for accessibility
            "budget_range": {
                "min": self.budget_range.min_amount,
                "max": self.budget_range.max_amount,
                "flexible": self.budget_range.flexible,
            },
        }


def generate_friend_code(name: str) -> str:
    """Generate a shareable friend code."""
    name_part = name.upper()[:5].replace(" ", "").ljust(5, "X")
    random_part = shortuuid.uuid()[:4].upper()
    return f"YT-{name_part}-{random_part}"
