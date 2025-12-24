from datetime import datetime
from pydantic import BaseModel


class PostSchema(BaseModel):
    id: int
    text: str
    toxicity_score: float | None
    posted_at: datetime
    channel_username: str | None = None

    class Config:
        from_attributes = True


class AlertSchema(BaseModel):
    id: int
    channel_id: int | None
    channel_username: str | None
    country: str | None
    target_group: str | None
    severity: str
    spike_percentage: float
    post_count: int
    baseline_avg: float | None
    spike_avg: float | None
    started_at: datetime
    is_active: bool
    sample_posts: list[PostSchema] = []

    class Config:
        from_attributes = True


class AlertDetailSchema(AlertSchema):
    posts: list[PostSchema] = []


class StatsSchema(BaseModel):
    total_posts_24h: int
    avg_toxicity_24h: float | None
    active_spikes: int
    channels_monitored: int


class TimelinePointSchema(BaseModel):
    timestamp: datetime
    avg_toxicity: float | None
    post_count: int


class TimelineSchema(BaseModel):
    timeline: list[TimelinePointSchema]


class ChannelSchema(BaseModel):
    id: int
    username: str | None
    title: str | None
    country: str | None
    language: str | None
    category: str | None
    member_count: int | None
    is_active: bool

    class Config:
        from_attributes = True
