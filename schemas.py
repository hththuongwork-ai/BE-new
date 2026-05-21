from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    done: bool = False

class TodoResponse(TodoCreate):
    id: int

    class Config:
        from_attributes = True