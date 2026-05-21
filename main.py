from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)  # Tự tạo bảng nếu chưa có

app = FastAPI()

# CREATE
@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(**todo.dict())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# READ ALL
@app.get("/todos", response_model=list[schemas.TodoResponse])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

# READ ONE
@app.get("/todos/{id}", response_model=schemas.TodoResponse)
def get_one(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return todo

# UPDATE
@app.put("/todos/{id}", response_model=schemas.TodoResponse)
def update(id: int, data: schemas.TodoCreate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    todo.title = data.title
    todo.done  = data.done
    db.commit()
    db.refresh(todo)
    return todo

# DELETE
@app.delete("/todos/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    db.delete(todo)
    db.commit()
    return {"message": "Đã xóa"}