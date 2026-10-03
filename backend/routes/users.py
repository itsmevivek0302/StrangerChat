from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, Block
from schemas import UserOut
from auth import current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user

@router.get("/discover", response_model=list[UserOut])
def discover(
    q: str = "",
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    blocked = {x.blocked_id for x in db.query(Block).filter(Block.blocker_id == user.id).all()}
    blocked_by = {x.blocker_id for x in db.query(Block).filter(Block.blocked_id == user.id).all()}
    ids = blocked | blocked_by | {user.id}
    query = db.query(User).filter(~User.id.in_(ids))
    if q.strip():
        query = query.filter(or_(User.username.ilike(f"%{q.strip()}%"), User.bio.ilike(f"%{q.strip()}%")))
    return query.order_by(User.is_online.desc(), User.username.asc()).limit(limit).all()

@router.patch("/me", response_model=UserOut)
def update_me(bio: str = "", db: Session = Depends(get_db), user=Depends(current_user)):
    user.bio = bio[:500]
    db.commit(); db.refresh(user)
    return user

@router.post("/{target_id}/block")
def block(target_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    if target_id == user.id or not db.get(User, target_id):
        raise HTTPException(400, "Invalid target")
    if not db.query(Block).filter_by(blocker_id=user.id, blocked_id=target_id).first():
        db.add(Block(blocker_id=user.id, blocked_id=target_id)); db.commit()
    return {"ok": True}

@router.delete("/{target_id}/block")
def unblock(target_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    row = db.query(Block).filter_by(blocker_id=user.id, blocked_id=target_id).first()
    if row: db.delete(row); db.commit()
    return {"ok": True}
