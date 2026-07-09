from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter()


@router.get("/interactions")
def list_interactions(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Interaction)
        .order_by(models.Interaction.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "hcpName": r.hcp_name,
            "interactionType": r.interaction_type,
            "date": r.date,
            "time": r.time,
            "attendees": r.attendees,
            "topicsDiscussed": r.topics_discussed,
            "materialsShared": r.materials_shared or [],
            "samplesDistributed": r.samples_distributed or [],
            "sentiment": r.sentiment,
            "outcomes": r.outcomes,
            "followUpDate": r.follow_up_date,
            "followUpActions": r.follow_up_actions,
            "summary": r.summary,
            "createdAt": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/hcps")
def list_hcps(db: Session = Depends(get_db)):
    return [
        {
            "id": h.id,
            "name": h.name,
            "specialty": h.specialty,
            "institution": h.institution,
        }
        for h in db.query(models.HCP).order_by(models.HCP.name).all()
    ]
