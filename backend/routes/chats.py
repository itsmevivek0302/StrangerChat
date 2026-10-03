from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database import get_db
from models import User, Conversation, Message, Block
from schemas import MessageIn, MessageOut
from auth import current_user
from websocket import manager

router = APIRouter(prefix="/api/chats", tags=["chats"])

def get_conversation(db, me, other):
    a,b = sorted([me.id, other.id])
    return db.query(Conversation).filter_by(user_a_id=a, user_b_id=b).first()

def blocked_between(db, first_id, second_id):
    return db.query(Block).filter(or_(
        and_(Block.blocker_id == first_id, Block.blocked_id == second_id),
        and_(Block.blocker_id == second_id, Block.blocked_id == first_id),
    )).first() is not None

def require_conversation(db, conversation_id, user_id):
    conv = db.get(Conversation, conversation_id)
    if not conv or user_id not in (conv.user_a_id, conv.user_b_id):
        raise HTTPException(404, "Conversation not found")
    other_id = conv.user_b_id if conv.user_a_id == user_id else conv.user_a_id
    if blocked_between(db, user_id, other_id):
        raise HTTPException(403, "Chat unavailable")
    return conv

@router.post("/with/{other_id}")
def create_chat(other_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    other = db.get(User, other_id)
    if not other or other.id == user.id:
        raise HTTPException(404, "User not found")
    if blocked_between(db, user.id, other.id):
        raise HTTPException(403, "Chat unavailable")
    conv = get_conversation(db, user, other)
    if not conv:
        a,b = sorted([user.id, other.id])
        conv = Conversation(user_a_id=a, user_b_id=b)
        db.add(conv)
        try:
            db.commit()
            db.refresh(conv)
        except IntegrityError:
            db.rollback()
            conv = get_conversation(db, user, other)
            if conv is None:
                raise
    return {"id": conv.id, "other": {"id": other.id, "username": other.username, "bio": other.bio}}

@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def messages(
    conversation_id: int,
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    require_conversation(db, conversation_id, user.id)
    rows = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.id.desc()).limit(limit).all()
    return list(reversed(rows))

@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(conversation_id: int, data: MessageIn, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = require_conversation(db, conversation_id, user.id)
    other = conv.user_b_id if conv.user_a_id == user.id else conv.user_a_id
    msg = Message(conversation_id=conversation_id, sender_id=user.id, body=data.body)
    db.add(msg); db.commit(); db.refresh(msg)
    payload = {"type":"message","message":MessageOut.model_validate(msg).model_dump(mode="json")}
    await manager.send_user(other, payload)
    await manager.send_user(user.id, payload)
    return msg

@router.post("/{conversation_id}/read")
async def mark_read(conversation_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = require_conversation(db, conversation_id, user.id)
    db.query(Message).filter(Message.conversation_id==conversation_id, Message.sender_id!=user.id).update({"is_read": True})
    db.commit()
    other = conv.user_b_id if conv.user_a_id == user.id else conv.user_a_id
    await manager.send_user(other, {"type": "read", "conversation_id": conversation_id, "reader_id": user.id})
    return {"ok": True}
