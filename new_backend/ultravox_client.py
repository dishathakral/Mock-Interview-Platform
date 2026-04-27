# ==================== ULTRAVOX WEBSOCKET CLIENT ====================
# Async WebSocket-based Ultravox voice session client
# Handles real-time audio streaming and message parsing

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Callable, Optional

import websockets
from websockets.asyncio.client import ClientConnection

logger = logging.getLogger(__name__)


class UltravoxWebSocketClient:
    """
    Async WebSocket client for Ultravox voice sessions.
    Port of ultravox-client.js (EventEmitter-based) to Python asyncio.
    """

    def __init__(self, join_url: str):
        self.join_url = join_url
        self.state: str = "idle"  # idle, listening, thinking, speaking
        self.socket: Optional[ClientConnection] = None
        self.pending_output: str = ""
        self.pending_user_output: str = ""
        self.transcript_buffer: list[dict] = []
        self.state_history: list[dict] = []
        self._receive_task: Optional[asyncio.Task] = None

        # Callback hooks (replace EventEmitter events)
        self.on_audio: Optional[Callable[[bytes], None]] = None
        self.on_state: Optional[Callable[[str], None]] = None
        self.on_transcript: Optional[Callable[[dict], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        self.on_ended: Optional[Callable[[], None]] = None
        self.on_playback_clear: Optional[Callable[[], None]] = None

    async def start(self) -> None:
        """Connect to the Ultravox WebSocket."""
        logger.info(f"[Ultravox] Connecting to {self.join_url}")
        try:
            self.socket = await websockets.connect(self.join_url)
            logger.info("[Ultravox] WebSocket connected")
            self._receive_task = asyncio.create_task(self._socket_receive())
        except Exception as error:
            logger.error(f"[Ultravox] WebSocket error: {error}")
            if self.on_error:
                self.on_error(error)
            raise

    async def _socket_receive(self) -> None:
        """Background task that reads messages from the WebSocket."""
        try:
            async for message in self.socket:
                try:
                    await self._on_socket_message(message)
                except Exception as error:
                    logger.error(f"[Ultravox] Error handling message: {error}")
                    if self.on_error:
                        self.on_error(error)
        except websockets.ConnectionClosed:
            logger.info("[Ultravox] WebSocket closed")
        finally:
            if self.on_ended:
                self.on_ended()

    async def _on_socket_message(self, payload) -> None:
        """Route incoming messages — binary audio or JSON control messages."""
        # Handle binary audio data
        if isinstance(payload, bytes):
            logger.info(f"[Ultravox] Received audio from Ultravox, size: {len(payload)}")
            if self.on_audio:
                self.on_audio(payload)
            return

        # Handle JSON messages
        try:
            msg = json.loads(payload)
            await self._handle_data_message(msg)
        except json.JSONDecodeError as error:
            logger.error(f"[Ultravox] Failed to parse message: {error}")

    async def _handle_data_message(self, msg: dict) -> None:
        """Dispatch JSON messages by type."""
        msg_type = msg.get("type", "")
        logger.info(f"[Ultravox] Message type: {msg_type} — {msg}")

        if msg_type == "playback_clear_buffer":
            if self.on_playback_clear:
                self.on_playback_clear()

        elif msg_type == "state":
            new_state = msg.get("state", "")
            if new_state != self.state:
                self.state = new_state
                self.state_history.append(
                    {
                        "state": new_state,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
                if self.on_state:
                    self.on_state(new_state)

        elif msg_type == "transcript":
            await self._handle_transcript(msg)

        elif msg_type == "client_tool_invocation":
            await self._handle_client_tool_call(
                msg.get("toolName", ""),
                msg.get("invocationId", ""),
                msg.get("parameters", {}),
            )

        elif msg_type == "debug":
            logger.info(f"[Ultravox Debug] {msg.get('message', '')}")

        elif msg_type == "call_started":
            logger.info("[Ultravox] Call started")

        else:
            logger.warning(f"[Ultravox] Unhandled message type: {msg_type}")

    async def _handle_transcript(self, msg: dict) -> None:
        """Process transcript updates (full text or delta)."""
        role = msg.get("role", "agent")  # 'agent' or 'user'
        text = ""

        # Either full text or delta update
        if msg.get("text"):
            text = msg["text"]
            if role == "agent":
                self.pending_output = text
            else:
                self.pending_user_output = text
        elif msg.get("delta"):
            if role == "agent":
                self.pending_output += msg["delta"]
            else:
                self.pending_user_output += msg["delta"]
            text = self.pending_output if role == "agent" else self.pending_user_output

        # Emit for real-time display
        if self.on_transcript:
            self.on_transcript(
                {
                    "text": text,
                    "final": msg.get("final", False),
                    "role": role,
                    "delta": msg.get("delta"),
                }
            )

        # Store final transcripts
        if msg.get("final"):
            self.transcript_buffer.append(
                {
                    "role": role,
                    "text": text,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            # Clear pending output
            if role == "agent":
                self.pending_output = ""
            else:
                self.pending_user_output = ""

    async def _handle_client_tool_call(
        self, tool_name: str, invocation_id: str, parameters: dict
    ) -> None:
        """Respond to client tool calls from Ultravox."""
        logger.info(f"[Ultravox] Client tool call: {tool_name}")

        # Send error response for unknown tools
        response = {
            "type": "client_tool_result",
            "invocationId": invocation_id,
            "errorType": "undefined",
            "errorMessage": f"Unknown tool: {tool_name}",
        }
        await self.socket.send(json.dumps(response))

    async def send_audio(self, chunk: bytes) -> None:
        """Send an audio chunk to Ultravox."""
        if self.socket and not self.socket.closed:
            logger.info(f"[Ultravox] Sending audio to Ultravox, size: {len(chunk)}")
            await self.socket.send(chunk)
        else:
            logger.warning("[Ultravox] Socket not ready, dropping audio.")

    def get_transcript(self) -> list[dict]:
        """Return the full transcript buffer."""
        return self.transcript_buffer

    def get_state_history(self) -> list[dict]:
        """Return the full state history."""
        return self.state_history

    async def stop(self) -> None:
        """Close the WebSocket and reset state."""
        logger.info("[Ultravox] Stopping session...")
        if self.socket:
            await self.socket.close()
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
        self.state = "idle"
