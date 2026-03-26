from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.dependencies.database import get_db
from app.models import Interaction, User

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today_start + timedelta(days=1)
    week = today_start - timedelta(days=7)

    # Due today
    due_today = db.query(func.count(Interaction.id)).filter(
        Interaction.follow_up_date >= today_start,
        Interaction.follow_up_date < tomorrow,
        Interaction.status == "pending"
    ).scalar()
    
    # Upcoming
    upcoming = db.query(func.count(Interaction.id)).filter(
        Interaction.follow_up_date >= tomorrow,
        Interaction.follow_up_date < week,
        Interaction.status == "pending"
    ).scalar()

    # Missed
    missed = db.query(func.count(Interaction.id)).filter(
        Interaction.follow_up_date < today_start,
        Interaction.status == "pending"
    ).scalar()

    # Completed today
    completed_today = db.query(func.count(Interaction.id)).filter(
        Interaction.completed_at >= today_start,
        Interaction.status == "completed"
    ).scalar()

    return {
        "due_today": due_today,
        "upcoming": upcoming,
        "missed": missed,
        "completed_today": completed_today
    }

@router.get("/rep-performance")
def rep_performance(db: Session = Depends(get_db)):

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    users = db.query(User).all()
    results = []

    for user in users:
        
        pending = db.query(func.count(Interaction.id)).filter(
            Interaction.user_id == user.id,
            Interaction.status == "pending"
        ).scalar()

        completed_today = db.query(func.count(Interaction.id)).filter(
            Interaction.user_id == user.id,
            Interaction.status == "completed",
            Interaction.completed_at >= today_start
        ).scalar()

        missed = db.query(func.count(Interaction.id)).filter(
            Interaction.user_id == user.id,
            Interaction.status == "pending",
            Interaction.follow_up_date < today_start
        ).scalar()

        results.append({
            "rep": user.name,
            "pending": pending,
            "completed_today": completed_today,
            "missed": missed
        })

    return results
