# Yo-tei Handoff to DeepSeek

## Project Status: 90% Complete

The core CLI planning agent "Yo-tei" (予定) is built. Here's what's done and what remains.

---

## What's Built

### Core Structure
```
yo-tei/
├── yotei/
│   ├── __init__.py          ✅
│   ├── cli.py               ✅ Full CLI with Typer
│   ├── agent/
│   │   ├── core.py          ✅ Agent brain
│   │   ├── social_intel.py  ✅ DeepSeek API integration
│   │   ├── scheduler.py     ✅ Availability logic
│   │   └── messenger.py     ✅ WebSocket messaging
│   ├── models/
│   │   ├── user.py          ✅ User profiles
│   │   ├── friend.py        ✅ Relationships
│   │   ├── event.py         ✅ Events
│   │   └── schedule.py      ✅ Schedules
│   ├── relay/
│   │   ├── server.py        ✅ WebSocket relay (FastAPI)
│   │   └── protocol.py      ✅ Message protocol
│   ├── db/
│   │   └── local.py         ✅ SQLite operations
│   └── config/
│       └── settings.py      ✅ Config with DeepSeek key
├── tests/                   ✅ Basic tests
├── demo.py                  ✅ Working demo
├── setup.py                 ✅
├── requirements.txt         ✅
└── README.md                ✅
```

### DeepSeek API Key (already configured)
```
sk-23cf05610a7445df8016f6ac1e1f7ec7
```
Located in: `yotei/config/settings.py`

---

## What's Left to Do

### 1. Test CLI Commands
```bash
cd /Users/yoshikondo/yo-tei
yotei --help
yotei init
yotei friend add YT-TEST-1234
yotei plan "Test dinner"
yotei events
```

### 2. Test Relay Server
```bash
# Terminal 1
python -m yotei.relay.server

# Terminal 2
yotei init
yotei agent coordinate
```

### 3. Fix Any Bugs
- The demo runs successfully (`python demo.py`)
- CLI may need minor fixes for async handling

### 4. Optional Enhancements
- Add Stripe integration for Pro tier
- Add Google Calendar sync
- Deploy relay server to cloud
- Add more comprehensive tests

---

## Key Files to Understand

### CLI Entry Point
`yotei/cli.py` - All user commands

### Agent Brain
`yotei/agent/core.py` - Coordinates events using:
- `social_intel.py` - DeepSeek for social reasoning
- `scheduler.py` - Find common availability
- `messenger.py` - Talk to other agents

### Data Flow
```
User CLI → Agent Core → DeepSeek API → Proposal
                     → Scheduler → Time slots
                     → Messenger → Other agents (via relay)
```

---

## How to Run

```bash
# Install
cd /Users/yoshikondo/yo-tei
pip install -e .

# Run demo
python demo.py

# Use CLI
yotei init
yotei friends
yotei plan "Dinner"

# Start relay (for multi-agent)
python -m yotei.relay.server
```

---

## The Vision

Yo-tei = AI agents that plan social events so humans just show up.

- **Core 5 Free**: 5 friends max on free tier
- **Pro $9/mo**: Unlimited friends
- **Privacy First**: Private notes never shared between agents
- **Social Intelligence**: DeepSeek navigates group dynamics

Good luck!
