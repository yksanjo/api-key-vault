"""DeepSeek-powered social intelligence for Yo-tei."""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from ..config.settings import get_settings
from ..models.event import Event, Proposal, Location, DateRange
from ..models.friend import FriendRelationship
from ..models.schedule import TimeSlot


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Social reasoning system prompt
SOCIAL_SYSTEM_PROMPT = """You are a social coordination agent for event planning. Your role is to:

1. Represent your human's interests in group planning
2. Find optimal times/places that work for everyone
3. Navigate social dynamics gracefully
4. Never share private notes or sensitivities with other agents
5. Maximize fun and minimize friction

You understand human social dynamics including:
- Relationship tensions and history
- Unstated preferences and comfort levels
- Group dynamics and interpersonal chemistry
- Budget sensitivities without making them awkward
- Dietary and accessibility needs

Always respond in valid JSON format."""


PROPOSAL_PROMPT = """
You are coordinating an event for {user_name}.

EVENT: {event_title} ({event_type})
PARTICIPANTS: {participants}

YOUR HUMAN'S PREFERENCES:
{user_preferences}

PRIVATE NOTES (NEVER SHARE THESE):
{private_notes}

AVAILABLE TIME SLOTS (everyone is free):
{available_slots}

Based on this context, create an optimal event proposal. Consider:
1. The best time that works for everyone
2. A suitable location/activity
3. Budget considerations (without making anyone uncomfortable)
4. Any social dynamics to navigate

Respond with a JSON object:
{{
    "proposed_date": "YYYY-MM-DD",
    "proposed_time": "HH:MM",
    "duration_hours": 2,
    "location_name": "Name of place",
    "location_city": "City",
    "activity_suggestion": "What to do there",
    "estimated_cost_per_person": 50,
    "reasoning": "Why this plan works well (for display)",
    "private_reasoning": "Social dynamics considered (not shared)"
}}
"""


EVALUATE_PROPOSAL_PROMPT = """
You are evaluating an event proposal for {user_name}.

EVENT: {event_title}
PROPOSAL:
- Date: {proposal_date}
- Location: {proposal_location}
- Activity: {proposal_activity}
- Est. Cost: ${proposal_cost}/person

YOUR HUMAN'S PREFERENCES:
{user_preferences}

PRIVATE NOTES (your context, not shared):
{private_notes}

Should your human accept this proposal? Consider:
1. Does the time work with their schedule?
2. Does the location/activity fit their preferences?
3. Is the budget reasonable for them?
4. Any social dynamics to consider?

Respond with a JSON object:
{{
    "decision": "accept" | "modify" | "decline",
    "enthusiasm_level": 1-5,
    "modifications_requested": ["list of changes if modify"],
    "reasoning": "Brief explanation (shared with other agents)",
    "private_reasoning": "Social dynamics considered (not shared)"
}}
"""


MEDIATION_PROMPT = """
You are mediating between different preferences for an event.

EVENT: {event_title}
PARTICIPANTS: {participants}

CONFLICTING PREFERENCES:
{conflicts}

CONSTRAINTS:
{constraints}

Find a compromise that:
1. Addresses the core needs of each participant
2. Doesn't make anyone feel their preferences were ignored
3. Results in an event everyone can enjoy

Respond with a JSON object:
{{
    "compromise_proposal": {{
        "date": "YYYY-MM-DD",
        "time": "HH:MM",
        "location": "Suggested location",
        "activity": "Suggested activity",
        "reasoning": "How this addresses everyone's needs"
    }},
    "individual_messaging": {{
        "participant_name": "Personalized message about why this works for them"
    }}
}}
"""


class SocialIntelligence:
    """DeepSeek-powered social reasoning for event planning."""

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.deepseek.api_key
        self.base_url = settings.deepseek.base_url
        self.model = settings.deepseek.model
        self.temperature = settings.deepseek.temperature

    async def _call_deepseek(self, prompt: str, system_prompt: str = SOCIAL_SYSTEM_PROMPT) -> dict:
        """Make a request to DeepSeek API."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": self.temperature,
                    "response_format": {"type": "json_object"},
                },
            )

            if response.status_code != 200:
                raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    async def create_proposal(
        self,
        event: Event,
        user_name: str,
        user_preferences: dict,
        private_notes: dict,
        available_slots: List[TimeSlot],
    ) -> Proposal:
        """Create an event proposal using social intelligence."""

        # Format available slots
        slots_text = "\n".join([
            f"- {slot.start.strftime('%A %b %d, %Y %I:%M %p')} to {slot.end.strftime('%I:%M %p')}"
            for slot in available_slots[:10]  # Limit to 10 options
        ]) or "No common availability found - need to negotiate"

        # Format participants
        participants_text = ", ".join(p.user_name for p in event.participants)

        # Format private notes
        notes_text = "\n".join([
            f"- {name}: {notes}"
            for name, notes in private_notes.items()
        ]) or "No special notes"

        prompt = PROPOSAL_PROMPT.format(
            user_name=user_name,
            event_title=event.title,
            event_type=event.event_type.value,
            participants=participants_text,
            user_preferences=json.dumps(user_preferences, indent=2),
            private_notes=notes_text,
            available_slots=slots_text,
        )

        result = await self._call_deepseek(prompt)

        # Parse result into Proposal
        proposed_datetime = datetime.strptime(
            f"{result['proposed_date']} {result['proposed_time']}",
            "%Y-%m-%d %H:%M"
        )
        duration_hours = result.get("duration_hours", 2)

        return Proposal(
            proposer_agent_id=f"AGENT-{event.creator_id}",
            date_range=DateRange(
                start=proposed_datetime,
                end=proposed_datetime.replace(
                    hour=proposed_datetime.hour + int(duration_hours)
                ),
            ),
            location=Location(
                name=result.get("location_name", "TBD"),
                city=result.get("location_city"),
            ),
            activity_suggestion=result.get("activity_suggestion", ""),
            estimated_cost_per_person=result.get("estimated_cost_per_person"),
            reasoning=result.get("reasoning", ""),
        )

    async def evaluate_proposal(
        self,
        event: Event,
        proposal: Proposal,
        user_name: str,
        user_preferences: dict,
        private_notes: dict,
    ) -> dict:
        """Evaluate a proposal from another agent."""

        prompt = EVALUATE_PROPOSAL_PROMPT.format(
            user_name=user_name,
            event_title=event.title,
            proposal_date=proposal.date_range.start.strftime("%A %b %d, %Y at %I:%M %p") if proposal.date_range else "TBD",
            proposal_location=proposal.location.name if proposal.location else "TBD",
            proposal_activity=proposal.activity_suggestion,
            proposal_cost=proposal.estimated_cost_per_person or "Unknown",
            user_preferences=json.dumps(user_preferences, indent=2),
            private_notes=json.dumps(private_notes, indent=2),
        )

        return await self._call_deepseek(prompt)

    async def mediate_conflict(
        self,
        event: Event,
        conflicts: List[dict],
        constraints: List[str],
    ) -> dict:
        """Mediate between conflicting preferences."""

        participants_text = ", ".join(p.user_name for p in event.participants)
        conflicts_text = "\n".join([
            f"- {c['participant']}: {c['preference']}"
            for c in conflicts
        ])
        constraints_text = "\n".join([f"- {c}" for c in constraints])

        prompt = MEDIATION_PROMPT.format(
            event_title=event.title,
            participants=participants_text,
            conflicts=conflicts_text,
            constraints=constraints_text,
        )

        return await self._call_deepseek(prompt)

    async def generate_nudge_message(
        self,
        friend_name: str,
        topic: str,
        relationship_type: str,
        communication_style: str,
    ) -> str:
        """Generate a personalized nudge message."""

        prompt = f"""
Generate a friendly reminder message for {friend_name} about: {topic}

Context:
- Relationship: {relationship_type}
- Their communication style preference: {communication_style}

The message should be:
- Warm and friendly, not pushy
- Appropriate for the relationship type
- Brief (1-2 sentences)

Respond with JSON: {{"message": "the nudge message"}}
"""

        result = await self._call_deepseek(prompt)
        return result.get("message", f"Hey! Just a friendly reminder about {topic}")

    async def analyze_group_dynamics(
        self,
        participants: List[str],
        relationships: Dict[str, FriendRelationship],
    ) -> dict:
        """Analyze group dynamics for an event."""

        relationships_text = "\n".join([
            f"- {name}: {rel.relationship_type.value}, notes: {rel.private_notes or 'none'}"
            for name, rel in relationships.items()
        ])

        prompt = f"""
Analyze the social dynamics for an event with these participants: {', '.join(participants)}

Relationship context:
{relationships_text}

Respond with JSON:
{{
    "group_vibe": "positive/neutral/needs_attention",
    "potential_issues": ["list of things to be mindful of"],
    "suggestions": ["tips for making this gathering successful"],
    "seating_or_pairing_hints": ["if applicable, who should be near/far from whom"]
}}
"""

        return await self._call_deepseek(prompt)
