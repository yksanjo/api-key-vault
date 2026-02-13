# Yo-tei (予定)

**Agent-to-Agent Social Planning CLI**

Where AI agents coordinate events so humans just show up and have fun.

## The Problem

Planning group activities is a nightmare:
- Endless "are you free?" messages
- Social pressure to say yes when you're not sure
- Hidden tensions that make planning awkward
- Someone always feels left out of decisions

## The Solution

Yo-tei creates AI agents that talk to each other on your behalf. Each person has their own agent that:
- Knows their schedule and preferences
- Understands their social dynamics (private notes never shared)
- Negotiates with other agents to find the perfect plan
- Handles gentle reminders without awkward follow-ups

## Quick Start

```bash
# Install
cd yo-tei
pip install -e .

# Initialize
yotei init

# Add friends (exchange friend codes)
yotei friend add YT-ABBY-1234

# Plan an event
yotei plan "Ski trip to Tahoe"

# Check status
yotei status "Ski trip"
```

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sarah's   │     │   Yo-tei    │     │   Abby's    │
│   Agent     │◄───►│   Relay     │◄───►│   Agent     │
│  (CLI/API)  │     │   Server    │     │  (CLI/API)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
   Sarah's            DeepSeek LLM         Abby's
   Schedule &         (Social Intel)       Schedule &
   Preferences                             Preferences
```

### What Gets Shared vs What Stays Private

| Data | Shared? | Example |
|------|---------|---------|
| Availability windows | ✓ | "Free Saturday 2-8pm" |
| Dietary restrictions | ✓ | "Vegetarian" |
| Budget range | ✓ | "$50-100" |
| **Private notes** | ✗ | "Avoid mentioning her ex" |
| **Sensitivities** | ✗ | "Money topics" |
| **Relationship history** | ✗ | "Had a falling out last year" |

## Features

### Core Features
- **Friend Codes**: Share `YT-NAME-XXXX` to connect
- **Smart Scheduling**: Find times that work for everyone
- **Social Intelligence**: Navigate group dynamics gracefully
- **Gentle Nudges**: Reminders that don't feel pushy

### Pricing
- **Free**: Core 5 friends, unlimited events
- **Pro ($9/mo)**: Unlimited friends, calendar sync, advanced features

## CLI Commands

```bash
# Setup
yotei init              # First-time setup
yotei code              # Show your friend code

# Friends
yotei friends           # List your friends
yotei friend add <code> # Add a friend
yotei friend edit <name> # Edit private notes

# Planning
yotei plan "<title>"    # Start planning
yotei events            # List all events
yotei status "<title>"  # Check event status
yotei nudge <name> <topic> # Send gentle reminder

# Schedule
yotei schedule set      # Set availability
yotei schedule show     # View your schedule

# Agent
yotei agent status      # Check agent status
yotei agent coordinate  # Trigger coordination
```

## Running the Demo

```bash
python demo.py
```

## Running the Relay Server

For multi-user testing:

```bash
# Start the relay server
python -m yotei.relay.server

# In another terminal, use the CLI
yotei init
yotei agent coordinate
```

## Architecture

```
yo-tei/
├── yotei/
│   ├── cli.py              # CLI interface (Typer)
│   ├── agent/
│   │   ├── core.py         # Agent brain
│   │   ├── social_intel.py # DeepSeek integration
│   │   ├── scheduler.py    # Availability logic
│   │   └── messenger.py    # Agent-to-agent comms
│   ├── models/
│   │   ├── user.py         # User profiles
│   │   ├── friend.py       # Relationships
│   │   ├── event.py        # Events
│   │   └── schedule.py     # Schedules
│   ├── relay/
│   │   ├── server.py       # WebSocket relay
│   │   └── protocol.py     # Message protocol
│   ├── db/
│   │   └── local.py        # SQLite storage
│   └── config/
│       └── settings.py     # Configuration
├── tests/
├── demo.py
└── requirements.txt
```

## Tech Stack

- **CLI**: Python + Typer + Rich
- **LLM**: DeepSeek API
- **Communication**: WebSocket (FastAPI)
- **Storage**: SQLite
- **Async**: asyncio + aiosqlite

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with verbose output
yotei --help
```

## Privacy Philosophy

Yo-tei is designed with privacy at its core:

1. **Local-first**: Your data stays on your device
2. **Private notes never shared**: Agents use context without exposing it
3. **Minimal data exchange**: Only what's needed for coordination
4. **Transparent reasoning**: You can see why decisions were made

## License

MIT

---

Built with love for people who just want to hang out without the hassle.
