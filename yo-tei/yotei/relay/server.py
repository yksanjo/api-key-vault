"""WebSocket relay server for agent-to-agent communication."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .protocol import AgentMessage, MessageType, create_error_message


class AgentConnection:
    """Represents a connected agent."""

    def __init__(self, agent_id: str, websocket: WebSocket):
        self.agent_id = agent_id
        self.websocket = websocket
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.subscribed_events: Set[str] = set()

    async def send(self, message: AgentMessage):
        """Send a message to this agent."""
        await self.websocket.send_json(message.to_wire())

    async def send_json(self, data: dict):
        """Send raw JSON to this agent."""
        await self.websocket.send_json(data)


class RelayServer:
    """WebSocket relay server for routing messages between agents."""

    def __init__(self):
        self.connections: Dict[str, AgentConnection] = {}
        self.event_subscriptions: Dict[str, Set[str]] = {}  # event_id -> {agent_ids}
        self.message_log: list = []  # In production, use proper storage

    async def connect(self, agent_id: str, websocket: WebSocket) -> AgentConnection:
        """Register a new agent connection."""
        await websocket.accept()
        connection = AgentConnection(agent_id, websocket)
        self.connections[agent_id] = connection

        # Broadcast hello to other agents
        await self.broadcast_system({
            "type": "agent_connected",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
        }, exclude={agent_id})

        return connection

    async def disconnect(self, agent_id: str):
        """Remove an agent connection."""
        if agent_id in self.connections:
            del self.connections[agent_id]

            # Remove from all event subscriptions
            for event_id in list(self.event_subscriptions.keys()):
                self.event_subscriptions[event_id].discard(agent_id)
                if not self.event_subscriptions[event_id]:
                    del self.event_subscriptions[event_id]

            # Broadcast goodbye
            await self.broadcast_system({
                "type": "agent_disconnected",
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
            })

    async def handle_message(self, sender_id: str, data: dict):
        """Handle an incoming message from an agent."""

        try:
            message = AgentMessage.from_wire(data)
        except Exception as e:
            # Send error back to sender
            if sender_id in self.connections:
                error = create_error_message(
                    "relay",
                    sender_id,
                    "INVALID_MESSAGE",
                    str(e),
                )
                await self.connections[sender_id].send(error)
            return

        # Log message (excluding sensitive ones)
        if message.shareable:
            self.message_log.append({
                "id": message.id,
                "type": message.type.value,
                "sender": message.sender_agent_id,
                "recipient": message.recipient_agent_id,
                "event_id": message.event_id,
                "timestamp": message.timestamp.isoformat(),
            })

        # Route the message
        if message.recipient_agent_id == "broadcast":
            await self.broadcast(message, exclude={sender_id})
        elif message.recipient_agent_id.startswith("event:"):
            # Broadcast to all agents subscribed to an event
            event_id = message.recipient_agent_id.replace("event:", "")
            await self.broadcast_to_event(event_id, message, exclude={sender_id})
        else:
            # Direct message to specific agent
            await self.route_to_agent(message)

    async def route_to_agent(self, message: AgentMessage):
        """Route a message to a specific agent."""
        recipient_id = message.recipient_agent_id

        if recipient_id in self.connections:
            await self.connections[recipient_id].send(message)
        else:
            # Agent not online - queue for later or send error
            if message.requires_response:
                error = create_error_message(
                    "relay",
                    message.sender_agent_id,
                    "AGENT_OFFLINE",
                    f"Agent {recipient_id} is not online",
                    reply_to=message.id,
                )
                if message.sender_agent_id in self.connections:
                    await self.connections[message.sender_agent_id].send(error)

    async def broadcast(self, message: AgentMessage, exclude: Set[str] = None):
        """Broadcast a message to all connected agents."""
        exclude = exclude or set()

        for agent_id, connection in self.connections.items():
            if agent_id not in exclude:
                try:
                    await connection.send(message)
                except Exception:
                    pass  # Handle disconnected clients

    async def broadcast_to_event(
        self,
        event_id: str,
        message: AgentMessage,
        exclude: Set[str] = None,
    ):
        """Broadcast a message to all agents subscribed to an event."""
        exclude = exclude or set()
        subscribers = self.event_subscriptions.get(event_id, set())

        for agent_id in subscribers:
            if agent_id not in exclude and agent_id in self.connections:
                try:
                    await self.connections[agent_id].send(message)
                except Exception:
                    pass

    async def broadcast_system(self, data: dict, exclude: Set[str] = None):
        """Broadcast a system message."""
        exclude = exclude or set()

        for agent_id, connection in self.connections.items():
            if agent_id not in exclude:
                try:
                    await connection.send_json(data)
                except Exception:
                    pass

    def subscribe_to_event(self, agent_id: str, event_id: str):
        """Subscribe an agent to event updates."""
        if event_id not in self.event_subscriptions:
            self.event_subscriptions[event_id] = set()
        self.event_subscriptions[event_id].add(agent_id)

        if agent_id in self.connections:
            self.connections[agent_id].subscribed_events.add(event_id)

    def unsubscribe_from_event(self, agent_id: str, event_id: str):
        """Unsubscribe an agent from event updates."""
        if event_id in self.event_subscriptions:
            self.event_subscriptions[event_id].discard(agent_id)

        if agent_id in self.connections:
            self.connections[agent_id].subscribed_events.discard(event_id)

    def get_online_agents(self) -> list:
        """Get list of online agent IDs."""
        return list(self.connections.keys())

    def get_agent_status(self, agent_id: str) -> Optional[dict]:
        """Get status of a specific agent."""
        if agent_id in self.connections:
            conn = self.connections[agent_id]
            return {
                "agent_id": agent_id,
                "online": True,
                "connected_at": conn.connected_at.isoformat(),
                "subscribed_events": list(conn.subscribed_events),
            }
        return None


# Create relay server instance
relay = RelayServer()


# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield
    # Cleanup on shutdown
    for agent_id in list(relay.connections.keys()):
        await relay.disconnect(agent_id)


app = FastAPI(
    title="Yo-tei Relay Server",
    description="Agent-to-Agent communication relay",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent connections."""
    connection = await relay.connect(agent_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # Handle special commands
            if data.get("cmd") == "subscribe":
                relay.subscribe_to_event(agent_id, data["event_id"])
                await websocket.send_json({"status": "subscribed", "event_id": data["event_id"]})
            elif data.get("cmd") == "unsubscribe":
                relay.unsubscribe_from_event(agent_id, data["event_id"])
                await websocket.send_json({"status": "unsubscribed", "event_id": data["event_id"]})
            elif data.get("cmd") == "ping":
                connection.last_ping = datetime.utcnow()
                await websocket.send_json({"cmd": "pong"})
            else:
                # Regular message
                await relay.handle_message(agent_id, data)

    except WebSocketDisconnect:
        await relay.disconnect(agent_id)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Yo-tei Relay Server",
        "status": "running",
        "agents_online": len(relay.connections),
    }


@app.get("/agents")
async def list_agents():
    """List online agents."""
    return {
        "agents": relay.get_online_agents(),
        "count": len(relay.connections),
    }


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get status of a specific agent."""
    status = relay.get_agent_status(agent_id)
    if status:
        return status
    return {"error": "Agent not found", "online": False}


def run_server(host: str = "0.0.0.0", port: int = 8765):
    """Run the relay server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
