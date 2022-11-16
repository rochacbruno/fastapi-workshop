"""Post related data models"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

from pydantic import BaseModel, Extra
from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from project_name.security import User


class Post(SQLModel, table=True):
    """Represents the Post Model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    date: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user_id: Optional[int] = Field(foreign_key="user.id")
    reply_id: Optional[int] = Field(foreign_key="post.id")

    # It populates a `.posts` attribute to the `User` model.
    user: Optional["User"] = Relationship(back_populates="posts")

    # TODO: add .replies here


class PostResponse(BaseModel):
    """Serializer for Post Response"""
    text: str
    date: datetime
    user_id: int
    reply_id: Optional[int]


class PostRequest(BaseModel):
    """Serializer for Post request payload"""
    reply_id: Optional[int]
    text: str

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True
