import json
from typing import Dict, List, Set, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import decode_token
from app.api.deps import get_current_user
from app.models.user import User
from app.models.gig import Gig
from app.models.contract import Contract
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter(tags=["In-App Chat"])


# In-memory WebSocket connection manager per gig
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, gig_id: str, websocket: WebSocket):
        await websocket.accept()
        if gig_id not in self.active_connections:
            self.active_connections[gig_id] = set()
        self.active_connections[gig_id].add(websocket)

    def disconnect(self, gig_id: str, websocket: WebSocket):
        if gig_id in self.active_connections:
            self.active_connections[gig_id].discard(websocket)
            if not self.active_connections[gig_id]:
                del self.active_connections[gig_id]

    async def broadcast_to_gig(self, gig_id: str, message_dict: dict):
        if gig_id in self.active_connections:
            data = json.dumps(message_dict, default=str)
            dead_connections = set()
            for connection in self.active_connections[gig_id]:
                try:
                    await connection.send_text(data)
                except Exception:
                    dead_connections.add(connection)
            for dead in dead_connections:
                self.active_connections[gig_id].discard(dead)


manager = ConnectionManager()


@router.get("/gigs/{gig_id}/messages", response_model=List[MessageRead], summary="Get chat messages for a gig")
async def get_messages(
    gig_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Message)
        .where(Message.gig_id == gig_id)
        .options(selectinload(Message.sender))
        .order_by(Message.created_at.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        MessageRead(
            id=m.id,
            gig_id=m.gig_id,
            sender_id=m.sender_id,
            sender_name=m.sender.name if m.sender else "User",
            body=m.body,
            attachment_url=m.attachment_url,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/gigs/{gig_id}/messages", response_model=MessageRead, summary="Send a chat message")
async def send_message(
    gig_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify gig exists
    g_stmt = select(Gig).where(Gig.id == gig_id)
    gig = (await db.execute(g_stmt)).scalar_one_or_none()
    if not gig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gig not found")

    message = Message(
        gig_id=gig_id,
        sender_id=current_user.id,
        body=payload.body.strip(),
        attachment_url=payload.attachment_url,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    msg_data = {
        "id": message.id,
        "gig_id": message.gig_id,
        "sender_id": message.sender_id,
        "sender_name": current_user.name,
        "body": message.body,
        "attachment_url": message.attachment_url,
        "created_at": message.created_at.isoformat(),
    }

    # Broadcast via WebSocket to connected clients in this gig
    await manager.broadcast_to_gig(gig_id, msg_data)

    return MessageRead(
        id=message.id,
        gig_id=message.gig_id,
        sender_id=message.sender_id,
        sender_name=current_user.name,
        body=message.body,
        attachment_url=message.attachment_url,
        created_at=message.created_at,
    )


@router.websocket("/ws/gigs/{gig_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    gig_id: str,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time gig chat streaming.
    Clients connect with ?token=<JWT_ACCESS_TOKEN>.
    """
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(gig_id, websocket)
    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
                body = data.get("body", "").strip()
                attachment_url = data.get("attachment_url")

                if body:
                    async with AsyncSessionLocal() as session:
                        # Fetch sender
                        u_res = await session.execute(select(User).where(User.id == user_id))
                        sender = u_res.scalar_one_or_none()
                        sender_name = sender.name if sender else "User"

                        msg = Message(
                            gig_id=gig_id,
                            sender_id=user_id,
                            body=body,
                            attachment_url=attachment_url,
                        )
                        session.add(msg)
                        await session.commit()
                        await session.refresh(msg)

                        broadcast_payload = {
                            "id": msg.id,
                            "gig_id": gig_id,
                            "sender_id": user_id,
                            "sender_name": sender_name,
                            "body": msg.body,
                            "attachment_url": msg.attachment_url,
                            "created_at": msg.created_at.isoformat(),
                        }
                        await manager.broadcast_to_gig(gig_id, broadcast_payload)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(gig_id, websocket)
