"""Agent messenger for communicating with other agents via the relay."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable, Any
import websockets
from websockets.exceptions import ConnectionClosed

from ..config.settings import get_settings
from ..relay.protocol import (
    AgentMessage,
    MessageType,
    create_hello_message,
    create_availability_query,
    create_availability_response,
    create_proposal_message,
    create_proposal_response,
    create_nudge_message,
    create_vibe_check,
    create_vibe_response,
)


class Messenger:
    """Handles agent-to-agent communication via the relay server."""

    def __init__(self, agent_id: str, user_name: str):
        self.agent_id = agent_id
        self.user_name = user_name
        self.settings = get_settings()
        self.websocket = None
        self.connected = False
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self._receive_task = None

    async def connect(self) -> bool:
        """Connect to the relay server."""
        try:
            self.websocket = await websockets.connect(
                f"{self.settings.relay.url}/ws/{self.agent_id}"
            )
            self.connected = True

            # Start receiving messages
            self._receive_task = asyncio.create_task(self._receive_loop())

            # Send hello message
            hello = create_hello_message(self.agent_id, self.user_name)
            await self.send(hello)

            return True
        except Exception as e:
            print(f"Failed to connect to relay: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from the relay server."""
        self.connected = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def send(self, message: AgentMessage) -> bool:
        """Send a message through the relay."""
        if not self.connected or not self.websocket:
            return False

        try:
            await self.websocket.send(json.dumps(message.to_wire()))
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False

    async def send_and_wait(
        self,
        message: AgentMessage,
        timeout: float = 300.0,
    ) -> Optional[AgentMessage]:
        """Send a message and wait for a response."""
        if not message.requires_response:
            message.requires_response = True

        # Create a future for the response
        future = asyncio.get_event_loop().create_future()
        self.pending_responses[message.id] = future

        # Send the message
        if not await self.send(message):
            del self.pending_responses[message.id]
            return None

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            print(f"Timeout waiting for response to {message.id}")
            return None
        finally:
            self.pending_responses.pop(message.id, None)

    async def _receive_loop(self):
        """Background loop for receiving messages."""
        while self.connected and self.websocket:
            try:
                raw = await self.websocket.recv()
                data = json.loads(raw)

                # Handle system messages
                if "cmd" in data:
                    if data["cmd"] == "pong":
                        continue
                    elif data.get("type") == "agent_connected":
                        print(f"Agent connected: {data.get('agent_id')}")
                        continue
                    elif data.get("type") == "agent_disconnected":
                        print(f"Agent disconnected: {data.get('agent_id')}")
                        continue

                # Parse as AgentMessage
                try:
                    message = AgentMessage.from_wire(data)
                except Exception:
                    continue

                # Check if this is a response to a pending request
                if message.reply_to and message.reply_to in self.pending_responses:
                    self.pending_responses[message.reply_to].set_result(message)
                    continue

                # Call registered handlers
                await self._handle_message(message)

            except ConnectionClosed:
                self.connected = False
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error receiving message: {e}")

    async def _handle_message(self, message: AgentMessage):
        """Handle an incoming message."""
        handlers = self.message_handlers.get(message.type, [])
        for handler in handlers:
            try:
                result = handler(message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"Handler error for {message.type}: {e}")

    def on_message(self, message_type: MessageType):
        """Decorator to register a message handler."""
        def decorator(func: Callable):
            if message_type not in self.message_handlers:
                self.message_handlers[message_type] = []
            self.message_handlers[message_type].append(func)
            return func
        return decorator

    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler programmatically."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def subscribe_to_event(self, event_id: str) -> bool:
        """Subscribe to updates for an event."""
        if not self.connected or not self.websocket:
            return False

        try:
            await self.websocket.send(json.dumps({
                "cmd": "subscribe",
                "event_id": event_id,
            }))
            return True
        except Exception:
            return False

    async def unsubscribe_from_event(self, event_id: str) -> bool:
        """Unsubscribe from event updates."""
        if not self.connected or not self.websocket:
            return False

        try:
            await self.websocket.send(json.dumps({
                "cmd": "unsubscribe",
                "event_id": event_id,
            }))
            return True
        except Exception:
            return False

    async def ping(self) -> bool:
        """Send a ping to keep the connection alive."""
        if not self.connected or not self.websocket:
            return False

        try:
            await self.websocket.send(json.dumps({"cmd": "ping"}))
            return True
        except Exception:
            return False

    # High-level messaging methods

    async def query_availability(
        self,
        recipient_id: str,
        event_id: str,
        start_date: str,
        end_date: str,
        event_type: str,
    ) -> Optional[dict]:
        """Query another agent for availability."""
        message = create_availability_query(
            self.agent_id,
            recipient_id,
            event_id,
            start_date,
            end_date,
            event_type,
        )

        response = await self.send_and_wait(message, timeout=60.0)
        if response and response.type == MessageType.AVAILABILITY_RESPONSE:
            return response.payload
        return None

    async def send_availability(
        self,
        recipient_id: str,
        event_id: str,
        reply_to: str,
        available_slots: List[dict],
    ) -> bool:
        """Send availability in response to a query."""
        message = create_availability_response(
            self.agent_id,
            recipient_id,
            event_id,
            reply_to,
            available_slots,
        )
        return await self.send(message)

    async def send_proposal(
        self,
        recipient_id: str,
        event_id: str,
        proposal: dict,
    ) -> Optional[dict]:
        """Send a proposal and wait for response."""
        message = create_proposal_message(
            self.agent_id,
            recipient_id,
            event_id,
            proposal,
        )

        response = await self.send_and_wait(message, timeout=120.0)
        if response and response.type == MessageType.PROPOSAL_RESPONSE:
            return response.payload
        return None

    async def respond_to_proposal(
        self,
        recipient_id: str,
        event_id: str,
        reply_to: str,
        decision: str,
        enthusiasm_level: int,
        modifications: Optional[List[str]] = None,
        reasoning: str = "",
    ) -> bool:
        """Respond to a proposal."""
        message = create_proposal_response(
            self.agent_id,
            recipient_id,
            event_id,
            reply_to,
            decision,
            enthusiasm_level,
            modifications,
            reasoning,
        )
        return await self.send(message)

    async def send_nudge(
        self,
        recipient_id: str,
        topic: str,
        message_text: str,
        event_id: Optional[str] = None,
    ) -> bool:
        """Send a nudge to another agent."""
        message = create_nudge_message(
            self.agent_id,
            recipient_id,
            event_id,
            topic,
            message_text,
        )
        return await self.send(message)

    async def check_vibe(
        self,
        recipient_id: str,
        event_id: str,
    ) -> Optional[dict]:
        """Send a vibe check and wait for response."""
        message = create_vibe_check(
            self.agent_id,
            recipient_id,
            event_id,
        )

        response = await self.send_and_wait(message, timeout=60.0)
        if response and response.type == MessageType.VIBE_RESPONSE:
            return response.payload
        return None

    async def respond_to_vibe_check(
        self,
        recipient_id: str,
        event_id: str,
        reply_to: str,
        enthusiasm_level: int,
        concerns: Optional[List[str]] = None,
    ) -> bool:
        """Respond to a vibe check."""
        message = create_vibe_response(
            self.agent_id,
            recipient_id,
            event_id,
            reply_to,
            enthusiasm_level,
            concerns,
        )
        return await self.send(message)


class MessengerPool:
    """Manages multiple messenger connections for testing."""

    def __init__(self):
        self.messengers: Dict[str, Messenger] = {}

    async def create_messenger(self, agent_id: str, user_name: str) -> Messenger:
        """Create and connect a new messenger."""
        messenger = Messenger(agent_id, user_name)
        await messenger.connect()
        self.messengers[agent_id] = messenger
        return messenger

    async def get_messenger(self, agent_id: str) -> Optional[Messenger]:
        """Get an existing messenger."""
        return self.messengers.get(agent_id)

    async def close_all(self):
        """Close all messenger connections."""
        for messenger in self.messengers.values():
            await messenger.disconnect()
        self.messengers.clear()
