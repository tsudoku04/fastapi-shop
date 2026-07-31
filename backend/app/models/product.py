from datetime import UTC, datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from ..database import Base


def utc_now():
    return datetime.now(UTC)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
    )

    image_url = Column(String)

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )

    def __repr__(self):
        return (
            f"<Product(id={self.id}, "
            f"name={self.name}, price={self.price})>"
        )