from app.model.base import CommonBaseModel
from sqlalchemy import Column
from sqlmodel import Field
from sqlalchemy import Column, Text

class AIQueryHistory(CommonBaseModel, table=True):
    __tablename__ = "ai_query_history"

    user_id: str = Field(foreign_key="users.id", index=True)

    query: str = Field(sa_column=Column(Text, nullable=False))
    response: str = Field(sa_column=Column(Text, nullable=False))