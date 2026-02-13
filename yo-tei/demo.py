#!/usr/bin/env python3
"""
Demo script for Yo-tei (予定)

This script demonstrates the core functionality of Yo-tei:
1. Creating users and friends
2. Planning an event
3. Agent coordination (simulated)
"""

import asyncio
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from yotei.models.user import User, AvailabilityBlock
from yotei.models.friend import FriendRelationship, RelationshipType
from yotei.models.event import Event, EventType
from yotei.models.schedule import Schedule
from yotei.agent.core import Agent
from yotei.agent.scheduler import Scheduler

console = Console()


async def demo():
    """Run the Yo-tei demo."""

    console.print(Panel.fit(
        "[bold cyan]Yo-tei (予定) Demo[/bold cyan]\n"
        "[dim]Agent-to-Agent Social Planning[/dim]",
        border_style="cyan"
    ))

    # Create users
    console.print("\n[bold]Step 1: Creating Users[/bold]")

    sarah = User(
        name="Sarah",
        default_availability=[
            AvailabilityBlock(day_of_week=5, start_hour=10, end_hour=20, label="Saturday"),
            AvailabilityBlock(day_of_week=6, start_hour=10, end_hour=20, label="Sunday"),
        ]
    )
    console.print(f"  Created: {sarah.name} ({sarah.friend_code})")

    # Create friends (simulating they already exist in the system)
    abby = FriendRelationship(
        friend_id="YT-ABBY-1234",
        friend_name="Abby",
        friend_code="YT-ABBY-1234",
        relationship_type=RelationshipType.CLOSE_FRIEND,
        private_notes="Best friend. Had a falling out last year but made up. Avoid mentioning her ex Mike.",
        sensitivities=["money topics", "diet comments"],
        enthusiasm_baseline=4,
    )

    michael = FriendRelationship(
        friend_id="YT-MICHA-5678",
        friend_name="Michael",
        friend_code="YT-MICHA-5678",
        relationship_type=RelationshipType.FRIEND,
        private_notes="Fun guy, always up for activities. Has a car that fits 4.",
        enthusiasm_baseline=5,
    )

    sam = FriendRelationship(
        friend_id="YT-SAM-9012",
        friend_name="Sam",
        friend_code="YT-SAM-9012",
        relationship_type=RelationshipType.FRIEND,
        private_notes="New to the group. Tight budget. Has a crush on Abby - keep activities group-focused.",
        sensitivities=["expensive activities"],
        enthusiasm_baseline=3,
    )

    console.print(f"  Added friend: {abby.friend_name} ({abby.relationship_type.value})")
    console.print(f"  Added friend: {michael.friend_name} ({michael.relationship_type.value})")
    console.print(f"  Added friend: {sam.friend_name} ({sam.relationship_type.value})")

    # Create an event
    console.print("\n[bold]Step 2: Planning an Event[/bold]")

    event = Event(
        creator_id=sarah.id,
        title="Ski Trip to Tahoe",
        event_type=EventType.TRIP,
    )

    event.add_participant(sarah.id, sarah.name, sarah.agent_id)
    event.add_participant(abby.friend_id, abby.friend_name, f"AGENT-{abby.friend_id}")
    event.add_participant(michael.friend_id, michael.friend_name, f"AGENT-{michael.friend_id}")
    event.add_participant(sam.friend_id, sam.friend_name, f"AGENT-{sam.friend_id}")

    console.print(f"  Event: [cyan]{event.title}[/cyan]")
    console.print(f"  Participants: {', '.join(p.user_name for p in event.participants)}")

    # Show what agents know (private context)
    console.print("\n[bold]Step 3: Agent Private Context[/bold]")
    console.print("[dim]Each agent knows private info about relationships:[/dim]\n")

    for friend in [abby, michael, sam]:
        context = friend.to_agent_context()
        console.print(f"  [cyan]{friend.friend_name}[/cyan]:")
        console.print(f"    Private notes: {context['private_notes'][:50]}...")
        console.print(f"    Sensitivities: {context['sensitivities']}")
        console.print(f"    Enthusiasm baseline: {context['enthusiasm_baseline']}/5")
        console.print()

    # Simulate scheduling
    console.print("[bold]Step 4: Finding Common Availability[/bold]")

    scheduler = Scheduler()

    # Add schedules for each participant
    for user_id in [sarah.id, abby.friend_id, michael.friend_id, sam.friend_id]:
        schedule = Schedule(
            user_id=user_id,
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=8, end_hour=22),
                AvailabilityBlock(day_of_week=6, start_hour=8, end_hour=22),
            ]
        )
        scheduler.add_schedule(user_id, schedule)

    start_date, end_date = scheduler.suggest_date_range(EventType.TRIP)
    slots = scheduler.find_common_slots(EventType.TRIP, start_date, end_date)

    if slots:
        console.print(f"  Found {len(slots)} common time slots")
        console.print(f"  Best slot: {slots[0].start.strftime('%A %b %d, %Y')}")
    else:
        console.print("  [yellow]No common slots found - agents would negotiate[/yellow]")

    # Show what would be shared vs private
    console.print("\n[bold]Step 5: Privacy in Action[/bold]")

    table = Table(title="What Gets Shared Between Agents")
    table.add_column("Data", style="cyan")
    table.add_column("Shared?", style="green")
    table.add_column("Example")

    table.add_row("Availability windows", "Yes", "Free Saturday 10am-8pm")
    table.add_row("Dietary restrictions", "Yes", "Vegetarian")
    table.add_row("Budget range", "Yes (general)", "$50-100")
    table.add_row("Private notes", "[red]NO[/red]", "'Avoid mentioning ex'")
    table.add_row("Sensitivities", "[red]NO[/red]", "'money topics'")
    table.add_row("Relationship history", "[red]NO[/red]", "'Had a falling out'")

    console.print()
    console.print(table)

    # Simulated result
    console.print("\n[bold]Step 6: Consensus Reached![/bold]")
    console.print()
    console.print("[bold green]SKI TRIP TO TAHOE[/bold green]")
    console.print("━" * 40)
    console.print(f"Date: {(datetime.now() + timedelta(days=21)).strftime('%b %d-%d, %Y')} (MLK Weekend)")
    console.print("Location: Airbnb in South Lake Tahoe")
    console.print("Carpool: Michael drives (his car fits 4)")
    console.print()
    console.print("[dim]Why this works (from agent reasoning):[/dim]")
    console.print("  • Only weekend all 4 are free in January")
    console.print("  • Abby prefers South Lake (from her preferences)")
    console.print("  • Budget-friendly option prioritized (Sam's context, never shared)")
    console.print("  • Group activities emphasized (social dynamics)")
    console.print()
    console.print("[bold cyan]All agents confirmed![/bold cyan]")


def main():
    """Entry point."""
    asyncio.run(demo())


if __name__ == "__main__":
    main()
