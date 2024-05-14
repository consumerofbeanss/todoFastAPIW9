from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, Base, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins
)


class TodoBase(BaseModel):
    id: int
    task: str
    completed: bool
    isEditing: bool


class TodoModel(TodoBase):
    id: int

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)

models.Base.metadata.create_all(bind=engine)


@app.post("/addTask/", response_model=TodoModel)
async def add_task(task: TodoBase, db: Session = db_dependency):
    db_todo = models.TodoMeow(**task.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/getAllTasks/", response_model=List[TodoModel])
async def get_task(db: Session = db_dependency, skip: int=0, limit: int = 100):
    tasks = db.query(models.TodoMeow).offset(skip).limit(limit).all()
    return tasks

@app.get("/getTaskById/{task_id}", response_model=TodoModel)
async def get_task_by_id(task_id: int, db: Session = db_dependency):
    task = db.query(models.TodoMeow).filter(models.TodoMeow.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/getTaskByName/{task_name}", response_model=List[TodoModel])
async def get_task_by_name(task_name: str, db: Session = db_dependency):
    tasks = db.query(models.TodoMeow).filter(models.TodoMeow.task.ilike(f"%{task_name}%")).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks


@app.delete("/deleteAllTasks/")
async def delete_all_tasks(db: Session = db_dependency):
    db.query(models.TodoMeow).delete()
    db.commit()
    return {"message": "All tasks deleted successfully"}


@app.delete("/deleteTaskById/{task_id}")
async def delete_task_by_id(task_id: int, db: Session = db_dependency):
    task = db.query(models.TodoMeow).filter(models.TodoMeow.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@app.delete("/deleteTaskByName/{task_name}")
async def delete_task_by_name(task_name: str, db: Session = db_dependency):
    tasks = db.query(models.TodoMeow).filter(models.TodoMeow.task.ilike(f"%{task_name}%")).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    for task in tasks:
        db.delete(task)
    db.commit()
    return {"message": "Tasks deleted successfully"}


@app.put("/updateTaskById/{task_id}", response_model=TodoModel)
async def update_task_by_id(task_id: int, task: TodoBase, db: Session = db_dependency):
    db_task = db.query(models.TodoMeow).filter(models.TodoMeow.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for var, value in task.dict().items():
        setattr(db_task, var, value)
    db.commit()
    db.refresh(db_task)
    return db_task