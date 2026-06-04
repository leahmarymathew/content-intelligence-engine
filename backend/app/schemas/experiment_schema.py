from pydantic import BaseModel
from typing import Optional


class ExperimentCreate(BaseModel):
    name:           str
    hypothesis:     str
    variant_a_name: str
    variant_a_copy: Optional[str] = None
    variant_b_name: str
    variant_b_copy: Optional[str] = None
    metric_label:   str
    traffic_split:  int = 50
    start_date:     str
    end_date:       str


class StatusUpdate(BaseModel):
    status: str   # Draft / Active / Paused / Completed


class TrackEvent(BaseModel):
    variant:    str   # 'A' or 'B'
    event_type: str   # 'impression' or 'conversion'


class VariantMetrics(BaseModel):
    name:         str
    copy:         Optional[str]
    metric:       Optional[float]   # conversion rate %
    label:        str
    impressions:  int
    conversions:  int


class ExperimentResponse(BaseModel):
    id:            int
    name:          str
    hypothesis:    str
    status:        str
    variant_a:     VariantMetrics
    variant_b:     VariantMetrics
    metric_label:  str
    improvement:   Optional[float]
    participants:  int
    traffic_split: int
    start_date:    str
    end_date:      str

    class Config:
        from_attributes = True
