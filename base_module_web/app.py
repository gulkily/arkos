import base64
import json
import logging
import os
import secrets
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from agent_module.agent import Agent
from memory_module.memory import Memory
from model_module.ArkModelNew import AIMessage, ArkModelLink, SystemMessage, UserMessage
from state_module.state_handler import StateHandler

APP_VERSION = os.getenv("ARK_WEB_VERSION", "0.1.0")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
DATA_DIR = Path(__file__).resolve().parent / "data"
STATE_GRAPH_PATH = PROJECT_ROOT / "state_module" / "state_graph.yaml"

DATA_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ARK Base Module Web Prototype", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class _BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, username: str, password: str):
        super().__init__(app)
        self.username = username
        self.password = password

    async def dispatch(self, request, call_next):
        header = request.headers.get("Authorization")
        if not header or not header.startswith("Basic "):
            return PlainTextResponse(
                "Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )

        encoded_credentials = header.split(" ", 1)[1]
        try:
            decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        except (base64.binascii.Error, UnicodeDecodeError):
            return PlainTextResponse(
                "Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )

        provided_username, _, provided_password = decoded.partition(":")
        if not (
            secrets.compare_digest(provided_username, self.username)
            and secrets.compare_digest(provided_password, self.password)
        ):
            return PlainTextResponse(
                "Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )

        return await call_next(request)


_basic_user = os.getenv("ARK_BASIC_USER", "ark")
_basic_password = os.getenv("ARK_BASIC_PASS", "arkos")
app.add_middleware(_BasicAuthMiddleware, username=_basic_user, password=_basic_password)


class MessageRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str
    error: Optional[str] = None


class SessionPayload(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    status: str = "ok"


class AgentSession:
    def __init__(self, agent: Agent, memory_path: Path):
        self.agent = agent
        self.memory_path = memory_path

    @property
    def history(self) -> List:
        return self.agent.context.setdefault("messages", [])

    def cleanup(self) -> None:
        if not self.memory_path:
            return
        try:
            if self.memory_path.exists():
                self.memory_path.unlink()
        except FileNotFoundError:
            return
        except OSError as exc:
            logger.warning("Failed to remove memory file %s: %s", self.memory_path, exc)


_session_store: Dict[str, AgentSession] = {}


def _llm_base_url() -> str:
    return os.getenv("ARK_LLM_BASE_URL", "http://localhost:30000/v1")


def _normalise_content(value) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value)
    except TypeError:
        return str(value)


def _serialise_history(history: List) -> List[ChatMessage]:
    serialised: List[ChatMessage] = []
    for item in history:
        if getattr(item, "role", "") == "system":
            continue
        serialised.append(
            ChatMessage(role=getattr(item, "role", "assistant"), content=_normalise_content(getattr(item, "content", "")))
        )
    return serialised


def _bootstrap_session(session_id: str) -> AgentSession:
    flow = StateHandler(yaml_path=str(STATE_GRAPH_PATH))
    memory_file = DATA_DIR / f"memory_{session_id}.csv"
    memory = Memory(agent_id=session_id, filename=str(memory_file))
    llm = ArkModelLink(base_url=_llm_base_url())

    agent = Agent(agent_id=session_id, flow=flow, memory=memory, llm=llm)
    history = agent.context.setdefault("messages", [])
    system_message = SystemMessage(
        content="You are ARK, a helpful assistant with tool access and recall abilities. Greet the user on first contact."
    )
    history.append(system_message)

    try:
        greeting = agent.call_llm(context=history)
    except Exception as exc:  # Fallback when the LLM endpoint is not available
        logger.exception("LLM initialization failed for session %s", session_id)
        greeting = AIMessage(content=f"LLM initialization failed: {exc}")

    if isinstance(greeting, AIMessage):
        history.append(greeting)
    else:
        history.append(AIMessage(content=str(greeting)))

    return AgentSession(agent=agent, memory_path=memory_file)


@app.get("/", response_class=HTMLResponse)
async def landing_page() -> HTMLResponse:
    html_path = STATIC_DIR / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="UI assets missing")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/healthz")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}


@app.post("/sessions", response_model=SessionPayload)
async def create_session() -> SessionPayload:
    session_id = uuid.uuid4().hex
    session = _bootstrap_session(session_id)
    _session_store[session_id] = session
    messages = _serialise_history(session.history)
    return SessionPayload(session_id=session_id, messages=messages)


@app.post("/sessions/{session_id}/message", response_model=SessionPayload)
async def send_message(session_id: str, payload: MessageRequest) -> SessionPayload:
    if session_id not in _session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _session_store[session_id]
    history = session.history

    content = payload.message.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    user_message = UserMessage(content=content)
    history.append(user_message)

    payload_status = "ok"
    try:
        response = session.agent.call_llm(context=history)
    except Exception as exc:
        payload_status = "error"
        logger.exception("LLM call failed for session %s", session_id)
        response = AIMessage(content=f"LLM call failed: {exc}")

    if isinstance(response, AIMessage):
        history.append(response)
    else:
        history.append(AIMessage(content=str(response)))

    messages = _serialise_history(history)
    return SessionPayload(session_id=session_id, messages=messages, status=payload_status)


@app.delete("/sessions/{session_id}", status_code=204)
async def end_session(session_id: str) -> None:
    session = _session_store.pop(session_id, None)
    if session:
        session.cleanup()
        memory_file = DATA_DIR / f"memory_{session_id}.csv"
        if memory_file.exists():
            try:
                memory_file.unlink()
            except OSError:
                pass
    return None
