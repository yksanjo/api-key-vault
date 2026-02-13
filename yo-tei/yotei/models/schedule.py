"""Schedule model for Yo-tei."""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from .user import AvailabilityBlock, BlackoutDate


class TimeSlot(BaseModel):
    """A specific time slot for scheduling."""

    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() / 60)

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600

    def overlaps(self, other: "TimeSlot") -> bool:
        """Check if this slot overlaps with another."""
        return self.start < other.end and other.start < self.end

    def contains(self, dt: datetime) -> bool:
        """Check if a datetime falls within this slot."""
        return self.start <= dt < self.end

    def to_shareable(self) -> dict:
        """Return shareable representation (no private details)."""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_hours": self.duration_hours,
        }


class DaySchedule(BaseModel):
    """Schedule for a single day."""

    date: date
    available_slots: List[TimeSlot] = Field(default_factory=list)
    busy_slots: List[TimeSlot] = Field(default_factory=list)  # Private, not shared

    @property
    def is_fully_busy(self) -> bool:
        return len(self.available_slots) == 0

    def get_free_hours(self) -> float:
        """Get total free hours for the day."""
        return sum(slot.duration_hours for slot in self.available_slots)


class Schedule(BaseModel):
    """A user's schedule with availability."""

    user_id: str
    timezone: str = "America/Los_Angeles"

    # Default weekly availability (from user profile)
    default_availability: List[AvailabilityBlock] = Field(default_factory=list)

    # Specific date overrides
    blackout_dates: List[BlackoutDate] = Field(default_factory=list)
    specific_availability: Dict[str, List[TimeSlot]] = Field(default_factory=dict)  # date_str -> slots
    specific_busy: Dict[str, List[TimeSlot]] = Field(default_factory=dict)  # date_str -> slots (private)

    def get_availability_for_date(self, target_date: date) -> List[TimeSlot]:
        """Get available time slots for a specific date."""
        date_str = target_date.isoformat()

        # Check blackout dates
        for blackout in self.blackout_dates:
            if blackout.start_date <= target_date <= blackout.end_date:
                return []

        # Check specific availability overrides
        if date_str in self.specific_availability:
            return self.specific_availability[date_str]

        # Fall back to default weekly availability
        day_of_week = target_date.weekday()
        slots = []

        for block in self.default_availability:
            if block.day_of_week == day_of_week:
                start = datetime.combine(target_date, datetime.min.time().replace(hour=block.start_hour))
                end = datetime.combine(target_date, datetime.min.time().replace(hour=block.end_hour))
                slots.append(TimeSlot(start=start, end=end))

        # Remove busy slots
        if date_str in self.specific_busy:
            slots = self._subtract_busy_slots(slots, self.specific_busy[date_str])

        return slots

    def _subtract_busy_slots(
        self,
        available: List[TimeSlot],
        busy: List[TimeSlot]
    ) -> List[TimeSlot]:
        """Remove busy periods from available slots."""
        result = []

        for avail in available:
            remaining = [avail]

            for busy_slot in busy:
                new_remaining = []
                for slot in remaining:
                    if not slot.overlaps(busy_slot):
                        new_remaining.append(slot)
                    else:
                        # Split the slot around the busy period
                        if slot.start < busy_slot.start:
                            new_remaining.append(TimeSlot(start=slot.start, end=busy_slot.start))
                        if slot.end > busy_slot.end:
                            new_remaining.append(TimeSlot(start=busy_slot.end, end=slot.end))
                remaining = new_remaining

            result.extend(remaining)

        return result

    def get_availability_range(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, List[TimeSlot]]:
        """Get availability for a date range."""
        result = {}
        current = start_date

        while current <= end_date:
            slots = self.get_availability_for_date(current)
            if slots:
                result[current.isoformat()] = slots
            current += timedelta(days=1)

        return result

    def to_shareable_availability(
        self,
        start_date: date,
        end_date: date
    ) -> dict:
        """Get shareable availability (no private details)."""
        availability = self.get_availability_range(start_date, end_date)
        return {
            "user_id": self.user_id,
            "timezone": self.timezone,
            "availability": {
                date_str: [slot.to_shareable() for slot in slots]
                for date_str, slots in availability.items()
            }
        }


def find_common_availability(
    schedules: List[Schedule],
    start_date: date,
    end_date: date,
    min_duration_hours: float = 2.0
) -> List[TimeSlot]:
    """Find time slots when all participants are available."""

    if not schedules:
        return []

    common_slots = []
    current = start_date

    while current <= end_date:
        # Get each person's availability for this date
        all_slots = [
            schedule.get_availability_for_date(current)
            for schedule in schedules
        ]

        # Find intersections
        if all(slots for slots in all_slots):  # Everyone has some availability
            # Start with first person's slots
            intersections = all_slots[0]

            for other_slots in all_slots[1:]:
                new_intersections = []
                for slot in intersections:
                    for other in other_slots:
                        if slot.overlaps(other):
                            # Find the intersection
                            inter_start = max(slot.start, other.start)
                            inter_end = min(slot.end, other.end)
                            if inter_end > inter_start:
                                new_intersections.append(TimeSlot(start=inter_start, end=inter_end))
                intersections = new_intersections

            # Filter by minimum duration
            for slot in intersections:
                if slot.duration_hours >= min_duration_hours:
                    common_slots.append(slot)

        current += timedelta(days=1)

    return common_slots
