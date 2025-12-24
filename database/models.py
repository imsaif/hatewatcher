from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Float, Boolean,
    DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from database.connection import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    title = Column(String(255))
    description = Column(Text)
    member_count = Column(Integer)
    country = Column(String(100))
    language = Column(String(10))
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = relationship("Post", back_populates="channel")
    spikes = relationship("Spike", back_populates="channel")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"))

    # Content
    text = Column(Text, nullable=False)
    text_language = Column(String(10))

    # Telegram metadata
    posted_at = Column(DateTime, nullable=False)
    views = Column(Integer)
    forwards = Column(Integer)
    reply_count = Column(Integer)

    # Perspective API scores (0.0 to 1.0)
    toxicity_score = Column(Float)
    severe_toxicity_score = Column(Float)
    identity_attack_score = Column(Float)
    insult_score = Column(Float)
    threat_score = Column(Float)

    # HateWatch analysis
    is_hate_speech = Column(Boolean)
    target_group = Column(String(255))
    extracted_location = Column(String(255))

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    channel = relationship("Channel", back_populates="posts")
    spike_posts = relationship("SpikePost", back_populates="post")

    __table_args__ = (
        UniqueConstraint("channel_id", "telegram_message_id", name="uix_channel_message"),
        Index("idx_posts_channel_posted", "channel_id", "posted_at"),
        Index("idx_posts_toxicity", "toxicity_score"),
        Index("idx_posts_posted_at", "posted_at"),
    )


class Spike(Base):
    __tablename__ = "spikes"

    id = Column(Integer, primary_key=True)

    # What spiked
    channel_id = Column(Integer, ForeignKey("channels.id"))
    country = Column(String(100))
    target_group = Column(String(255))

    # Spike metrics
    spike_start = Column(DateTime, nullable=False)
    spike_end = Column(DateTime)
    baseline_avg = Column(Float)
    spike_avg = Column(Float)
    spike_percentage = Column(Float)
    post_count = Column(Integer)

    # Status
    severity = Column(String(20))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channel = relationship("Channel", back_populates="spikes")
    spike_posts = relationship("SpikePost", back_populates="spike")


class SpikePost(Base):
    __tablename__ = "spike_posts"

    spike_id = Column(Integer, ForeignKey("spikes.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)

    spike = relationship("Spike", back_populates="spike_posts")
    post = relationship("Post", back_populates="spike_posts")
