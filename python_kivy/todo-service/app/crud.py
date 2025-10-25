from sqlalchemy.orm import Session
from . import models, schemas

def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).offset(skip).limit(limit).all()

def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate):
    db_t = get_todo(db, todo_id)
    if not db_t:
        return None
    if todo.title is not None:
        db_t.title = todo.title
    if todo.description is not None:
        db_t.description = todo.description
    if todo.done is not None:
        db_t.done = todo.done
    db.commit()
    db.refresh(db_t)
    return db_t

def delete_todo(db: Session, todo_id: int):
    db_t = get_todo(db, todo_id)
    if not db_t:
        return None
    db.delete(db_t)
    db.commit()
    return db_t
