from pydantic import BaseModel
from pydantic import ConfigDict, Field
from typing import Optional, List

class TodoCreate(BaseModel):
    title: str
    done: bool = False

class TodoResponse(TodoCreate):
    id: int
    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

# Schemas cho Post
class PostCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    title: Optional[str] = None
    body: Optional[str] = None
    images: Optional[List[str]] = None   # FE gửi list URL
    caption: Optional[str] = None
    embed_url: Optional[str] = Field(default=None, alias="embedUrl")
    url: Optional[str] = None
    category: str = "daily-life"
    date: str

class PostResponse(PostCreate):
    id: int
    class Config:
        from_attributes = True