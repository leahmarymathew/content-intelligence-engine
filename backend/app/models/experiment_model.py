from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id           = Column(Integer, primary_key=True)
    name         = Column(String,  nullable=False)
    hypothesis   = Column(Text)
    status       = Column(String,  default="Draft")  # Draft / Active / Paused / Completed

    variant_a_name = Column(String)
    variant_a_copy = Column(Text)
    variant_b_name = Column(String)
    variant_b_copy = Column(Text)
    metric_label   = Column(String)

    traffic_split  = Column(Integer, default=50)   # % of traffic going to variant A
    start_date     = Column(String)
    end_date       = Column(String)
    created_at     = Column(DateTime, default=datetime.utcnow)


class ExperimentEvent(Base):
    __tablename__ = "experiment_events"

    id            = Column(Integer,  primary_key=True)
    experiment_id = Column(Integer,  ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    variant       = Column(String,   nullable=False)   # 'A' or 'B'
    event_type    = Column(String,   nullable=False)   # 'impression' or 'conversion'
    created_at    = Column(DateTime, default=datetime.utcnow)
