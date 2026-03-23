from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from .base import CommonBaseModel
from pydantic import validator

class PublishType(str, Enum):
    FREE = "free"
    EXCHANGE = "exchange"
    PAID = "paid"

class ProductPublish(CommonBaseModel, table=True):
    __tablename__ = "product_publish"

    product_id: str = Field(
        foreign_key="product.id",
        ondelete="CASCADE",
        index=True,
        unique=True
    )
    publish_type: PublishType = Field(default=PublishType.FREE)
    amount: Optional[float] = Field(default=None)

    product: Optional["Product"] = Relationship(back_populates="publish_detail")

class ProductPublishCreate(SQLModel):
    product_id: str
    publish_type: PublishType
    amount: Optional[float] = None

    @validator("amount", always=True)
    def validate_amount(cls, v, values):
        if values.get("publish_type") == PublishType.PAID:
            if v is None or v <= 0:
                raise ValueError("Amount is required and must be greater than 0 for paid products")
        return v
    
class ProductPublishResponse(SQLModel):
    id: str
    product_id: str
    publish_type: PublishType
    amount: Optional[float]

class ProductPublishUpdate(SQLModel):
    publish_type: Optional[PublishType] = None
    amount: Optional[float] = None

class ProductPublishUpdate(SQLModel):
    publish_type: Optional[PublishType] = None
    amount: Optional[float] = None

    @validator("amount", always=True)
    def validate_amount(cls, v, values):
        if values.get("publish_type") == PublishType.PAID:
            if v is None or v <= 0:
                raise ValueError("Amount must be > 0 for paid products")
        return v