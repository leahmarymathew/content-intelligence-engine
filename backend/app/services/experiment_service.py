from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.experiment_model import Experiment, ExperimentEvent
from app.schemas.experiment_schema import ExperimentCreate, ExperimentResponse, VariantMetrics


def _compute(db: Session, exp: Experiment) -> ExperimentResponse:
    """Compute live metrics from tracked events and return a full response."""
    rows = (
        db.query(
            ExperimentEvent.variant,
            ExperimentEvent.event_type,
            func.count(ExperimentEvent.id).label("n"),
        )
        .filter(ExperimentEvent.experiment_id == exp.id)
        .group_by(ExperimentEvent.variant, ExperimentEvent.event_type)
        .all()
    )

    counts: dict[tuple, int] = {(r.variant, r.event_type): r.n for r in rows}

    imp_a  = counts.get(("A", "impression"),  0)
    conv_a = counts.get(("A", "conversion"),  0)
    imp_b  = counts.get(("B", "impression"),  0)
    conv_b = counts.get(("B", "conversion"),  0)

    rate_a = round(conv_a / imp_a * 100, 1) if imp_a > 0 else None
    rate_b = round(conv_b / imp_b * 100, 1) if imp_b > 0 else None

    improvement = None
    if rate_a and rate_b and rate_a > 0:
        improvement = round((rate_b - rate_a) / rate_a * 100, 1)

    return ExperimentResponse(
        id=exp.id,
        name=exp.name,
        hypothesis=exp.hypothesis,
        status=exp.status,
        metric_label=exp.metric_label or "",
        improvement=improvement,
        participants=imp_a + imp_b,
        traffic_split=exp.traffic_split or 50,
        start_date=exp.start_date or "",
        end_date=exp.end_date or "",
        variant_a=VariantMetrics(
            name=exp.variant_a_name or "Variant A",
            copy=exp.variant_a_copy,
            metric=rate_a,
            label=exp.metric_label or "",
            impressions=imp_a,
            conversions=conv_a,
        ),
        variant_b=VariantMetrics(
            name=exp.variant_b_name or "Variant B",
            copy=exp.variant_b_copy,
            metric=rate_b,
            label=exp.metric_label or "",
            impressions=imp_b,
            conversions=conv_b,
        ),
    )


def create_experiment(db: Session, data: ExperimentCreate) -> ExperimentResponse:
    exp = Experiment(
        name=data.name,
        hypothesis=data.hypothesis,
        status="Draft",
        variant_a_name=data.variant_a_name,
        variant_a_copy=data.variant_a_copy,
        variant_b_name=data.variant_b_name,
        variant_b_copy=data.variant_b_copy,
        metric_label=data.metric_label,
        traffic_split=data.traffic_split,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _compute(db, exp)


def list_experiments(db: Session) -> list[ExperimentResponse]:
    exps = db.query(Experiment).order_by(Experiment.created_at.desc()).all()
    return [_compute(db, e) for e in exps]


def get_experiment(db: Session, exp_id: int) -> ExperimentResponse | None:
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    return _compute(db, exp) if exp else None


def update_status(db: Session, exp_id: int, status: str) -> ExperimentResponse | None:
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if not exp:
        return None
    exp.status = status
    db.commit()
    db.refresh(exp)
    return _compute(db, exp)


def track_event(db: Session, exp_id: int, variant: str, event_type: str) -> dict:
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if not exp:
        return {"error": "Experiment not found"}
    if exp.status != "Active":
        return {"error": f"Experiment is {exp.status} — only Active experiments accept events"}

    event = ExperimentEvent(
        experiment_id=exp_id,
        variant=variant.upper(),
        event_type=event_type.lower(),
    )
    db.add(event)
    db.commit()
    return {"ok": True, "experiment_id": exp_id, "variant": variant, "event_type": event_type}
