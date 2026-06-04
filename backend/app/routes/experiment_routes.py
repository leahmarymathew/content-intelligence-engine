from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.experiment_schema import ExperimentCreate, ExperimentResponse, StatusUpdate, TrackEvent
from app.services.experiment_service import (
    create_experiment, list_experiments, get_experiment, update_status, track_event
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[ExperimentResponse])
def get_experiments(db: Session = Depends(get_db)):
    return list_experiments(db)


@router.post("", response_model=ExperimentResponse)
def create(data: ExperimentCreate, db: Session = Depends(get_db)):
    return create_experiment(db, data)


@router.get("/{exp_id}", response_model=ExperimentResponse)
def get_one(exp_id: int, db: Session = Depends(get_db)):
    exp = get_experiment(db, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.patch("/{exp_id}/status", response_model=ExperimentResponse)
def set_status(exp_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    exp = update_status(db, exp_id, body.status)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.post("/{exp_id}/track")
def track(exp_id: int, body: TrackEvent, db: Session = Depends(get_db)):
    result = track_event(db, exp_id, body.variant, body.event_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
