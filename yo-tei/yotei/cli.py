"""
Yo-tei CLI - Agent-to-Agent Social Planning

Usage:
    yotei init              # First-time setup
    yotei friends           # List your friends
    yotei friend add <code> # Add a friend
    yotei plan "<title>"    # Plan an event
    yotei events            # List events
    yotei status "<title>"  # Check event status
"""

import asyncio
from typing import Optional, List
from datetime import datetime, date, timedelta

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from . import __version__, __app_name__
from .models.user import User, AvailabilityBlock, BudgetRange, CommunicationStyle, SubscriptionTier
from .models.friend import FriendRelationship, RelationshipType
from .models.event import Event, EventType, EventStatus
from .models.schedule import Schedule
from .db.local import get_db, close_db
from .config.settings import get_settings, initialize_with_defaults

app = typer.Typer(
    name=__app_name__,
    help="Yo-tei (予定) - Agent-to-Agent Social Planning CLI",
    add_completion=False,
)

console = Console()

# Sub-apps
friend_app = typer.Typer(help="Manage friends")
schedule_app = typer.Typer(help="Manage your schedule")
agent_app = typer.Typer(help="Agent operations")
app.add_typer(friend_app, name="friend")
app.add_typer(schedule_app, name="schedule")
app.add_typer(agent_app, name="agent")


def run_async(coro):
    """Run async function in sync context."""
    return asyncio.get_event_loop().run_until_complete(coro)


@app.command()
def init():
    """Initialize Yo-tei for first-time use."""
    console.print(Panel.fit(
        "[bold cyan]Welcome to Yo-tei (予定)[/bold cyan]\n"
        "[dim]Where AI agents plan events so you just show up and have fun[/dim]",
        border_style="cyan"
    ))

    async def setup():
        db = await get_db()
        settings = initialize_with_defaults()

        # Check if already initialized
        existing_user = await db.get_current_user()
        if existing_user:
            console.print(f"\n[yellow]Already initialized as {existing_user.name}[/yellow]")
            console.print(f"Friend code: [bold green]{existing_user.friend_code}[/bold green]")
            if not Confirm.ask("Reinitialize? This will delete all data"):
                return
            await db.delete_user(existing_user.id)

        # Get user info
        console.print("\n[bold]Let's set you up![/bold]\n")

        name = Prompt.ask("What's your name?")

        # Create user
        user = User(name=name)
        await db.save_user(user)

        # Update settings
        settings.set_user(user.id, user.agent_id)

        # Create default schedule
        schedule = Schedule(
            user_id=user.id,
            default_availability=[
                AvailabilityBlock(day_of_week=5, start_hour=10, end_hour=22, label="Saturday"),
                AvailabilityBlock(day_of_week=6, start_hour=10, end_hour=22, label="Sunday"),
                AvailabilityBlock(day_of_week=0, start_hour=18, end_hour=22, label="Mon evening"),
                AvailabilityBlock(day_of_week=1, start_hour=18, end_hour=22, label="Tue evening"),
                AvailabilityBlock(day_of_week=2, start_hour=18, end_hour=22, label="Wed evening"),
                AvailabilityBlock(day_of_week=3, start_hour=18, end_hour=22, label="Thu evening"),
                AvailabilityBlock(day_of_week=4, start_hour=18, end_hour=22, label="Fri evening"),
            ]
        )
        await db.save_schedule(schedule)

        # Success!
        console.print("\n[bold green]You're all set![/bold green]\n")
        console.print(f"Your friend code: [bold cyan]{user.friend_code}[/bold cyan]")
        console.print("\nShare this code with friends so they can add you!")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("  yotei friend add <code>  - Add a friend")
        console.print("  yotei schedule set       - Set your availability")
        console.print("  yotei plan \"Trip name\"   - Plan an event")

        await close_db()

    run_async(setup())


@app.command()
def code():
    """Show your friend code."""
    async def show_code():
        db = await get_db()
        user = await db.get_current_user()
        await close_db()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            raise typer.Exit(1)

        console.print(f"\nYour friend code: [bold cyan]{user.friend_code}[/bold cyan]")
        console.print("[dim]Share this with friends so they can add you![/dim]\n")

    run_async(show_code())


@friend_app.command("add")
def friend_add(friend_code: str):
    """Add a friend by their friend code."""
    async def add_friend():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        # Check friend limit
        friend_count = await db.get_friends_count(user.id)
        if not user.can_add_friends and user.tier == SubscriptionTier.FREE:
            console.print(f"[yellow]You've reached your Core 5 limit ({friend_count}/5).[/yellow]")
            console.print("Upgrade to Pro for unlimited friends: [cyan]yotei upgrade[/cyan]")
            await close_db()
            raise typer.Exit(1)

        # Parse friend code
        friend_code_clean = friend_code.upper().strip()
        console.print(f"\nConnecting to [cyan]{friend_code_clean}[/cyan]...")

        # For MVP, we create a placeholder friend
        # In production, this would query the relay server
        parts = friend_code_clean.split("-")
        if len(parts) != 3 or parts[0] != "YT":
            console.print("[red]Invalid friend code format. Should be like: YT-NAME-XXXX[/red]")
            await close_db()
            raise typer.Exit(1)

        friend_name = parts[1].title()

        # Check if already friends
        existing_friends = await db.get_all_friends(user.id)
        if any(f.friend_code == friend_code_clean for f in existing_friends):
            console.print(f"[yellow]You're already friends with {friend_name}![/yellow]")
            await close_db()
            return

        # Get relationship details
        console.print(f"\n[bold]Adding {friend_name}[/bold]\n")

        rel_type = Prompt.ask(
            "Relationship type",
            choices=["friend", "close-friend", "partner", "family", "colleague"],
            default="friend"
        )

        private_notes = Prompt.ask(
            "Any private notes for your agent? (never shared)",
            default=""
        )

        sensitivities_input = Prompt.ask(
            "Topics to avoid? (comma-separated, or leave empty)",
            default=""
        )
        sensitivities = [s.strip() for s in sensitivities_input.split(",") if s.strip()]

        # Create friend relationship
        friend = FriendRelationship(
            friend_id=f"YT-{parts[1]}-{parts[2]}",
            friend_name=friend_name,
            friend_code=friend_code_clean,
            relationship_type=RelationshipType(rel_type),
            private_notes=private_notes,
            sensitivities=sensitivities,
        )

        await db.save_friend(user.id, friend)

        # Update user's friend count
        user.friends_count = friend_count + 1
        await db.save_user(user)

        console.print(f"\n[bold green]Added {friend_name} to your circle![/bold green]")

        tier_info = f"({user.friends_count}/5 free)" if user.tier == SubscriptionTier.FREE else "(Pro)"
        console.print(f"[dim]Core Circle {tier_info}[/dim]\n")

        await close_db()

    run_async(add_friend())


@friend_app.command("remove")
def friend_remove(name: str):
    """Remove a friend from your circle."""
    async def remove_friend():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        friends = await db.get_all_friends(user.id)
        friend = next((f for f in friends if f.friend_name.lower() == name.lower()), None)

        if not friend:
            console.print(f"[yellow]No friend named '{name}' found.[/yellow]")
            await close_db()
            return

        if Confirm.ask(f"Remove {friend.friend_name} from your circle?"):
            await db.delete_friend(user.id, friend.friend_id)
            user.friends_count = max(0, user.friends_count - 1)
            await db.save_user(user)
            console.print(f"[green]Removed {friend.friend_name}.[/green]")

        await close_db()

    run_async(remove_friend())


@friend_app.command("edit")
def friend_edit(name: str):
    """Edit notes about a friend."""
    async def edit_friend():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        friends = await db.get_all_friends(user.id)
        friend = next((f for f in friends if f.friend_name.lower() == name.lower()), None)

        if not friend:
            console.print(f"[yellow]No friend named '{name}' found.[/yellow]")
            await close_db()
            return

        console.print(f"\n[bold]Editing notes for {friend.friend_name}[/bold]\n")
        console.print(f"[dim]Current notes: {friend.private_notes or '(none)'}[/dim]")
        console.print(f"[dim]Current sensitivities: {', '.join(friend.sensitivities) or '(none)'}[/dim]\n")

        new_notes = Prompt.ask("New private notes (or press enter to keep)", default=friend.private_notes)
        sensitivities_input = Prompt.ask(
            "Topics to avoid (comma-separated)",
            default=", ".join(friend.sensitivities)
        )

        friend.private_notes = new_notes
        friend.sensitivities = [s.strip() for s in sensitivities_input.split(",") if s.strip()]

        await db.save_friend(user.id, friend)
        console.print(f"\n[green]Updated notes for {friend.friend_name}.[/green]\n")

        await close_db()

    run_async(edit_friend())


@app.command()
def friends():
    """List your friends."""
    async def list_friends():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        friend_list = await db.get_all_friends(user.id)
        await close_db()

        if not friend_list:
            console.print("\n[yellow]No friends yet![/yellow]")
            console.print("Add friends with: [cyan]yotei friend add <code>[/cyan]\n")
            return

        tier_info = f"{len(friend_list)}/5 free" if user.tier == SubscriptionTier.FREE else "Pro - unlimited"

        table = Table(title=f"Core Circle ({tier_info})")
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Agent", style="yellow")
        table.add_column("Last Hangout", style="dim")

        for i, friend in enumerate(friend_list, 1):
            last_hangout = friend.last_hangout.strftime("%b %d") if friend.last_hangout else "-"
            agent_status = "[green]online[/green]" if friend.agent_online else "[dim]offline[/dim]"
            table.add_row(
                str(i),
                friend.friend_name,
                friend.relationship_type.value,
                agent_status,
                last_hangout
            )

        console.print()
        console.print(table)
        console.print()

    run_async(list_friends())


@app.command()
def plan(title: str, event_type: str = "hangout"):
    """Start planning an event with friends."""
    async def create_plan():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        friend_list = await db.get_all_friends(user.id)

        if not friend_list:
            console.print("\n[yellow]Add some friends first![/yellow]")
            console.print("Use: [cyan]yotei friend add <code>[/cyan]\n")
            await close_db()
            return

        # Show friends and let user select participants
        console.print(f"\n[bold cyan]Planning: {title}[/bold cyan]\n")
        console.print("Who's joining? (comma-separated numbers or names)\n")

        for i, friend in enumerate(friend_list, 1):
            console.print(f"  {i}. {friend.friend_name}")

        console.print()
        selection = Prompt.ask("Participants", default="all")

        # Parse selection
        if selection.lower() == "all":
            participants = friend_list
        else:
            participants = []
            for part in selection.split(","):
                part = part.strip()
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(friend_list):
                        participants.append(friend_list[idx])
                else:
                    match = next((f for f in friend_list if f.friend_name.lower() == part.lower()), None)
                    if match:
                        participants.append(match)

        if not participants:
            console.print("[red]No valid participants selected.[/red]")
            await close_db()
            return

        # Get event type
        try:
            evt_type = EventType(event_type.lower())
        except ValueError:
            evt_type = EventType.HANGOUT

        # Create event
        event = Event(
            creator_id=user.id,
            title=title,
            event_type=evt_type,
        )

        # Add creator as participant
        from .models.event import ParticipantStatus
        event.participants.append(ParticipantStatus(
            user_id=user.id,
            user_name=user.name,
            agent_id=user.agent_id,
            confirmed=True,  # Creator is auto-confirmed
            enthusiasm_level=5,
        ))

        # Add selected friends
        for friend in participants:
            event.add_participant(
                user_id=friend.friend_id,
                user_name=friend.friend_name,
                agent_id=f"AGENT-{friend.friend_id}"  # Placeholder
            )

        await db.save_event(event)
        await close_db()

        # Display planning status
        console.print(f"\n[bold green]Event created![/bold green]")
        console.print(f"\n[bold]{title.upper()}[/bold]")
        console.print("━" * 40)
        console.print(f"Type: {evt_type.value}")
        console.print(f"Participants: {', '.join(p.user_name for p in event.participants)}")
        console.print(f"Status: [yellow]{event.status.value}[/yellow]")
        console.print()

        console.print("[cyan]Your agent is now coordinating with other agents...[/cyan]")
        console.print()
        console.print("[dim]Check status with: yotei status \"" + title + "\"[/dim]")
        console.print("[dim]Or run: yotei agent coordinate[/dim]\n")

    run_async(create_plan())


@app.command()
def events():
    """List all your events."""
    async def list_events():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        event_list = await db.get_user_events(user.id)
        await close_db()

        if not event_list:
            console.print("\n[yellow]No events yet![/yellow]")
            console.print("Plan one with: [cyan]yotei plan \"Event name\"[/cyan]\n")
            return

        table = Table(title="Your Events")
        table.add_column("Title", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Participants")
        table.add_column("Date")
        table.add_column("Status", style="yellow")

        for event in event_list:
            summary = event.get_summary()
            status_color = {
                "planning": "yellow",
                "proposed": "blue",
                "confirmed": "green",
                "completed": "dim",
                "cancelled": "red",
            }.get(summary["status"], "white")

            table.add_row(
                summary["title"],
                summary["type"],
                ", ".join(summary["participants"][:3]) + ("..." if len(summary["participants"]) > 3 else ""),
                summary["date"],
                f"[{status_color}]{summary['status']}[/{status_color}]"
            )

        console.print()
        console.print(table)
        console.print()

    run_async(list_events())


@app.command()
def status(title: str):
    """Check the status of an event."""
    async def show_status():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        events_list = await db.get_user_events(user.id)
        event = next((e for e in events_list if e.title.lower() == title.lower()), None)
        await close_db()

        if not event:
            console.print(f"[yellow]No event found with title '{title}'[/yellow]")
            return

        # Display status
        status_emoji = {
            EventStatus.PLANNING: "🔄",
            EventStatus.PROPOSED: "📨",
            EventStatus.CONFIRMED: "✅",
            EventStatus.COMPLETED: "🎉",
            EventStatus.CANCELLED: "❌",
        }.get(event.status, "❓")

        console.print(f"\n{status_emoji} [bold]{event.title.upper()}[/bold]")
        console.print("━" * 40)
        console.print(f"Type: {event.event_type.value}")
        console.print(f"Status: [yellow]{event.status.value}[/yellow]")
        console.print()

        # Participants
        console.print("[bold]Participants:[/bold]")
        for p in event.participants:
            status = "✓" if p.confirmed else "..."
            console.print(f"  {status} {p.user_name}")
        console.print()

        # Details
        if event.date_range:
            console.print(f"Date: {event.date_range.start.strftime('%b %d, %Y %I:%M %p')}")
        else:
            console.print("Date: [yellow]TBD[/yellow]")

        if event.location:
            console.print(f"Location: {event.location.name}")
        else:
            console.print("Location: [yellow]TBD[/yellow]")

        console.print()

        # Agent notes (public ones)
        public_notes = [n for n in event.agent_notes if not n.private]
        if public_notes:
            console.print("[bold]Agent Activity:[/bold]")
            for note in public_notes[-5:]:  # Last 5 notes
                console.print(f"  • {note.content}")
            console.print()

    run_async(show_status())


@app.command()
def nudge(name: str, topic: str):
    """Send a gentle reminder to a friend about something."""
    async def send_nudge():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        friends = await db.get_all_friends(user.id)
        friend = next((f for f in friends if f.friend_name.lower() == name.lower()), None)

        if not friend:
            console.print(f"[yellow]No friend named '{name}' found.[/yellow]")
            await close_db()
            return

        console.print(f"\n[cyan]Your agent will send a friendly reminder to {friend.friend_name}'s agent about: {topic}[/cyan]")
        console.print("[dim]The nudge will be delivered based on their communication preferences.[/dim]\n")

        await close_db()

    run_async(send_nudge())


@schedule_app.command("set")
def schedule_set():
    """Set your default availability."""
    async def set_schedule():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        console.print("\n[bold]Set Your Availability[/bold]\n")
        console.print("When are you typically free? Let's set your default weekly schedule.\n")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        blocks = []

        for i, day in enumerate(days):
            available = Confirm.ask(f"Available on {day}s?", default=(i >= 5))  # Default yes for weekends
            if available:
                start = Prompt.ask(f"  {day} - Start hour (0-23)", default="10" if i >= 5 else "18")
                end = Prompt.ask(f"  {day} - End hour (0-23)", default="22")
                blocks.append(AvailabilityBlock(
                    day_of_week=i,
                    start_hour=int(start),
                    end_hour=int(end),
                    label=f"{day} {'all day' if i >= 5 else 'evening'}"
                ))

        schedule = await db.get_schedule(user.id)
        if not schedule:
            schedule = Schedule(user_id=user.id)

        schedule.default_availability = blocks
        await db.save_schedule(schedule)
        await close_db()

        console.print("\n[green]Schedule updated![/green]")
        console.print(f"[dim]You're available {len(blocks)} day(s) per week.[/dim]\n")

    run_async(set_schedule())


@schedule_app.command("show")
def schedule_show():
    """Show your current schedule."""
    async def show_schedule():
        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        schedule = await db.get_schedule(user.id)
        await close_db()

        if not schedule or not schedule.default_availability:
            console.print("\n[yellow]No schedule set. Run 'yotei schedule set' first.[/yellow]\n")
            return

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        console.print("\n[bold]Your Weekly Availability[/bold]\n")

        for block in sorted(schedule.default_availability, key=lambda b: b.day_of_week):
            day = days[block.day_of_week]
            console.print(f"  {day}: {block.start_hour:02d}:00 - {block.end_hour:02d}:00")

        console.print()

    run_async(show_schedule())


@agent_app.command("status")
def agent_status():
    """Check your agent's status."""
    settings = get_settings()

    console.print("\n[bold]Agent Status[/bold]\n")

    if settings.user_id:
        console.print(f"User ID: [cyan]{settings.user_id}[/cyan]")
        console.print(f"Agent ID: [cyan]{settings.agent_id}[/cyan]")
    else:
        console.print("[yellow]Not initialized. Run 'yotei init' first.[/yellow]")
        return

    if settings.deepseek.api_key:
        console.print(f"DeepSeek: [green]configured[/green]")
    else:
        console.print(f"DeepSeek: [red]not configured[/red]")

    console.print(f"Relay: {settings.relay.url}")
    console.print()


@agent_app.command("coordinate")
def agent_coordinate():
    """Manually trigger agent coordination for pending events."""
    async def coordinate():
        from .agent.core import Agent

        db = await get_db()
        user = await db.get_current_user()

        if not user:
            console.print("[red]Not initialized. Run 'yotei init' first.[/red]")
            await close_db()
            raise typer.Exit(1)

        events_list = await db.get_user_events(user.id)
        pending_events = [e for e in events_list if e.status == EventStatus.PLANNING]

        if not pending_events:
            console.print("\n[yellow]No events need coordination.[/yellow]\n")
            await close_db()
            return

        console.print(f"\n[cyan]Coordinating {len(pending_events)} event(s)...[/cyan]\n")

        agent = Agent(user.id, user.agent_id)

        for event in pending_events:
            console.print(f"  • {event.title}...")
            result = await agent.coordinate_event(event)
            if result.get("consensus"):
                console.print(f"    [green]Consensus reached![/green]")
                event.status = EventStatus.CONFIRMED
            else:
                console.print(f"    [yellow]Proposal sent, waiting for responses[/yellow]")
                event.status = EventStatus.PROPOSED
            await db.save_event(event)

        await close_db()
        console.print("\n[green]Coordination complete.[/green]\n")

    run_async(coordinate())


@app.command()
def upgrade():
    """Upgrade to Pro for unlimited friends."""
    settings = get_settings()

    console.print("\n[bold cyan]Yo-tei Pro[/bold cyan]\n")
    console.print("Unlock unlimited friends and advanced features!\n")
    console.print("  • Unlimited friends (vs Core 5)")
    console.print("  • Advanced social intelligence")
    console.print("  • Calendar integrations")
    console.print("  • Group templates")
    console.print("  • Priority agent processing")
    console.print()
    console.print("[bold]$9/month[/bold]")
    console.print()
    console.print("[dim]Payment integration coming soon![/dim]\n")


@app.command()
def version():
    """Show version information."""
    console.print(f"Yo-tei (予定) v{__version__}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
