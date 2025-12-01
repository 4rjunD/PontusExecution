from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class RouteSegmentModel(Base):
    __tablename__ = "route_segments"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_type = Column(String(50), nullable=False, index=True)
    from_asset = Column(String(10), nullable=False, index=True)
    to_asset = Column(String(10), nullable=False, index=True)
    from_network = Column(String(50), nullable=True, index=True)
    to_network = Column(String(50), nullable=True, index=True)
    cost = Column(JSON, nullable=False)
    latency = Column(JSON, nullable=False)
    reliability_score = Column(Float, nullable=False, default=1.0)
    constraints = Column(JSON, nullable=False, default={})
    provider = Column(String(100), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_segment_lookup', 'segment_type', 'from_asset', 'to_asset'),
    )


class SnapshotModel(Base):
    __tablename__ = "snapshots"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_data = Column(JSON, nullable=False)
    segment_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

