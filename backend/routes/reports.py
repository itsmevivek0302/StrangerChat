from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Report
from schemas import ReportIn
from auth import current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/{target_id}")
def report(target_id: int, data: ReportIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if target_id == user.id or not db.get(User, target_id):
        raise HTTPException(400, "Invalid target")
    db.add(Report(reporter_id=user.id, reported_id=target_id, reason=data.reason.strip()))
    db.commit()
    return {"ok": True, "message": "Report submitted"}
