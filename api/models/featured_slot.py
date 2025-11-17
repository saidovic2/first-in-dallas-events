from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class FeaturedSlot(Base):
    """Paid featured/sponsored event slots for premium visibility"""
    __tablename__ = "featured_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    
    # Slot configuration
    slot_position = Column(Integer, nullable=False)  # 1-4 (1=Platinum, 2=Gold, 3=Silver, 4=Bronze)
    tier = Column(String(20), nullable=False)  # PLATINUM, GOLD, SILVER, BRONZE
    
    # Pricing
    price_paid = Column(DECIMAL(10, 2), nullable=False)
    payment_frequency = Column(String(20), nullable=False, default="WEEKLY")
    
    # Timing
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    
    # Payment tracking
    payment_status = Column(String(20), default="PAID")  # PENDING, PAID, FAILED, REFUNDED, EXPIRED
    payment_method = Column(String(50), default="MANUAL")
    notes = Column(Text, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships (will be enabled after migration)
    # event = relationship("Event", back_populates="featured_slots")
    
    __table_args__ = (
        CheckConstraint('slot_position BETWEEN 1 AND 4', name='check_slot_position'),
        CheckConstraint("tier IN ('PLATINUM', 'GOLD', 'SILVER', 'BRONZE')", name='check_tier'),
        CheckConstraint("payment_status IN ('PENDING', 'PAID', 'FAILED', 'REFUNDED', 'EXPIRED')", name='check_payment_status'),
    )


class FeaturedPricing(Base):
    """Pricing configuration for featured slot tiers"""
    __tablename__ = "featured_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    tier = Column(String(20), nullable=False, unique=True)
    slot_position = Column(Integer, nullable=False, unique=True)
    base_price_weekly = Column(DECIMAL(10, 2), nullable=False)
    discount_monthly = Column(Integer, default=10)
    discount_quarterly = Column(Integer, default=20)
    discount_yearly = Column(Integer, default=35)
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
