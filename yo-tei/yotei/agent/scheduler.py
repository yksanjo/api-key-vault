"""Scheduling logic for Yo-tei agents."""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from ..models.schedule import Schedule, TimeSlot, find_common_availability
from ..models.event import Event, EventType


# Typical durations for different event types (in hours)
EVENT_DURATIONS = {
    EventType.TRIP: 48,  # 2 days
    EventType.HANGOUT: 3,
    EventType.DINNER: 2.5,
    EventType.ACTIVITY: 3,
    EventType.PARTY: 4,
    EventType.MOVIE: 3,
    EventType.GAME_NIGHT: 4,
    EventType.OUTDOOR: 5,
}

# Preferred time ranges for different event types
EVENT_PREFERRED_TIMES = {
    EventType.DINNER: (18, 21),  # 6pm - 9pm
    EventType.MOVIE: (14, 21),   # 2pm - 9pm
    EventType.GAME_NIGHT: (19, 23),  # 7pm - 11pm
    EventType.OUTDOOR: (9, 17),  # 9am - 5pm
    EventType.HANGOUT: (10, 22),  # Flexible
    EventType.ACTIVITY: (10, 20),
    EventType.PARTY: (18, 23),
    EventType.TRIP: (0, 24),  # All day
}


class Scheduler:
    """Schedule coordination for events."""

    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}

    def add_schedule(self, user_id: str, schedule: Schedule):
        """Add a participant's schedule."""
        self.schedules[user_id] = schedule

    def find_common_slots(
        self,
        event_type: EventType,
        start_date: date,
        end_date: date,
        min_duration: Optional[float] = None,
    ) -> List[TimeSlot]:
        """Find time slots that work for all participants."""

        if not self.schedules:
            return []

        # Get minimum duration based on event type
        if min_duration is None:
            min_duration = EVENT_DURATIONS.get(event_type, 2)

        # Find common availability
        schedules_list = list(self.schedules.values())
        common_slots = find_common_availability(
            schedules_list,
            start_date,
            end_date,
            min_duration,
        )

        # Filter by preferred times for event type
        if event_type in EVENT_PREFERRED_TIMES:
            pref_start, pref_end = EVENT_PREFERRED_TIMES[event_type]
            filtered = []
            for slot in common_slots:
                slot_hour = slot.start.hour
                if pref_start <= slot_hour < pref_end:
                    filtered.append(slot)
            if filtered:  # Only use filtered if we have results
                common_slots = filtered

        return common_slots

    def rank_slots(
        self,
        slots: List[TimeSlot],
        event_type: EventType,
        preferences: Dict[str, dict],
    ) -> List[Tuple[TimeSlot, float]]:
        """Rank time slots by desirability."""

        ranked = []

        for slot in slots:
            score = 100.0  # Start with perfect score

            # Prefer weekends for social events
            if slot.start.weekday() >= 5:
                score += 10

            # Prefer not too early, not too late
            hour = slot.start.hour
            if 10 <= hour <= 19:
                score += 5
            elif hour < 9 or hour > 21:
                score -= 10

            # Prefer longer slots (more flexibility)
            if slot.duration_hours >= 4:
                score += 5

            # Event-specific preferences
            if event_type == EventType.DINNER:
                if 18 <= hour <= 20:
                    score += 15
            elif event_type == EventType.OUTDOOR:
                if 10 <= hour <= 14:
                    score += 15
            elif event_type == EventType.GAME_NIGHT:
                if 19 <= hour <= 20:
                    score += 15

            # Check against participant preferences
            for user_id, prefs in preferences.items():
                # Budget timing preference (e.g., lunch vs dinner prices)
                if prefs.get("budget_conscious") and hour >= 18:
                    score -= 5  # Dinner tends to be pricier

                # Early bird vs night owl
                if prefs.get("early_bird") and hour >= 20:
                    score -= 10
                elif prefs.get("night_owl") and hour <= 10:
                    score -= 10

            ranked.append((slot, score))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    def suggest_date_range(
        self,
        event_type: EventType,
        preferred_window_days: int = 30,
    ) -> Tuple[date, date]:
        """Suggest a date range to search for availability."""

        today = date.today()
        start = today + timedelta(days=3)  # At least 3 days out

        # Adjust based on event type
        if event_type == EventType.TRIP:
            start = today + timedelta(days=14)  # Trips need more planning
            end = start + timedelta(days=60)
        elif event_type == EventType.DINNER or event_type == EventType.HANGOUT:
            end = start + timedelta(days=preferred_window_days)
        else:
            end = start + timedelta(days=preferred_window_days)

        return start, end

    def get_next_available_slot(
        self,
        event_type: EventType,
        min_duration: Optional[float] = None,
    ) -> Optional[TimeSlot]:
        """Get the next available slot for all participants."""

        start_date, end_date = self.suggest_date_range(event_type)
        slots = self.find_common_slots(event_type, start_date, end_date, min_duration)

        if slots:
            # Return the first (soonest) slot
            return min(slots, key=lambda s: s.start)
        return None

    def check_conflicts(
        self,
        proposed_slot: TimeSlot,
    ) -> Dict[str, bool]:
        """Check which participants have conflicts with a proposed time."""

        conflicts = {}
        for user_id, schedule in self.schedules.items():
            available_slots = schedule.get_availability_for_date(proposed_slot.start.date())
            has_availability = any(
                slot.start <= proposed_slot.start and slot.end >= proposed_slot.end
                for slot in available_slots
            )
            conflicts[user_id] = not has_availability

        return conflicts

    def find_alternatives(
        self,
        original_slot: TimeSlot,
        event_type: EventType,
        days_to_search: int = 14,
    ) -> List[TimeSlot]:
        """Find alternative slots close to the original proposed time."""

        # Search around the original date
        original_date = original_slot.start.date()
        start_date = original_date - timedelta(days=3)
        end_date = original_date + timedelta(days=days_to_search)

        # Ensure we don't go into the past
        if start_date < date.today():
            start_date = date.today() + timedelta(days=1)

        return self.find_common_slots(event_type, start_date, end_date)


def create_scheduler_from_event(event: Event) -> Scheduler:
    """Create a scheduler with all event participants."""
    scheduler = Scheduler()
    # In production, this would fetch schedules from the database
    # For now, it's a placeholder that the Agent will populate
    return scheduler
