from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from .base import CommonBaseModel
from typing import Optional, List
from datetime import datetime
from fastapi import Form
from .product_publish import PublishType

class Product(CommonBaseModel, table=True):
    __tablename__ = "product"

    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    title: str = Field(max_length=255)
    description: Optional[str] = None
    images: List["ProductImage"] = Relationship(back_populates="product")
    category: str = Field(max_length=100)
    quantity: float
    quantity_name: str = Field(max_length=100)
    quality: str = Field(max_length=50)

    pickup_address: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    publish: bool = False
    status: str = Field(default="draft", max_length=20)

    publish_detail: Optional["ProductPublish"] = Relationship(
        back_populates="product"
    )
    
class ProductImage(CommonBaseModel, table=True):
    __tablename__ = "product_images"

    product_id: str = Field(foreign_key="product.id", ondelete="CASCADE", index=True)
    image_url: str = Field(max_length=500)
    product: Optional["Product"] = Relationship(back_populates="images")

class ProductCreate(SQLModel):
    title: str
    description: Optional[str] = None
    category: str
    quantity: float
    quantity_name: str
    quality: str
    pickup_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        category: str = Form(...),
        quantity: float = Form(...),
        quantity_name: str = Form(...),
        quality: str = Form(...),
        pickup_address: Optional[str] = Form(None),
        latitude: Optional[float] = Form(None),
        longitude: Optional[float] = Form(None),
    ):
        return cls(
            title=title,
            description=description,
            category=category,
            quantity=quantity,
            quantity_name=quantity_name,
            quality=quality,
            pickup_address=pickup_address,
            latitude=latitude,
            longitude=longitude,
        )

class ProductImageResponse(SQLModel):
    id: str
    image_url: str

class ProductPublishResponse(SQLModel):
    publish_type: PublishType
    amount: Optional[float] = None

class ProductResponse(SQLModel):
    id: str
    user_id: str

    title: str
    description: Optional[str]
    category: str
    quantity: float
    quantity_name: str
    quality: str

    pickup_address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

    publish: bool
    status: str

    created_at: datetime
    updated_at: datetime

    images: List[ProductImageResponse] = []
    publish_detail: Optional[ProductPublishResponse] = None
    