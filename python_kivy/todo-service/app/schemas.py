from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None

class TodoInDBBase(TodoBase):
    id: int
    done: bool

    class Config:
        orm_mode = True

class Todo(TodoInDBBase):
    pass
