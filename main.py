import json
import os
import re
from pathlib import Path

import models
import schemas
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> bool:
        return False

load_dotenv()

Base.metadata.create_all(bind=engine)

DEFAULT_CATEGORIES = [
    ("Work", "work"),
    ("My Daily Life", "daily-life"),
    ("My Pet", "pet"),
    ("My Travel", "travel"),
]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "category"


def _ensure_post_category_column() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("posts"):
        return
    columns = {column["name"] for column in inspector.get_columns("posts")}
    if "category" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE posts ADD COLUMN category VARCHAR DEFAULT 'daily-life'"))


def _ensure_default_categories() -> None:
    with Session(engine) as db:
        for name, slug in DEFAULT_CATEGORIES:
            existing = db.query(models.Category).filter(models.Category.slug == slug).first()
            if not existing:
                db.add(models.Category(name=name, slug=slug))
        db.commit()


_ensure_post_category_column()
_ensure_default_categories()

app = FastAPI(title="My API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Đang dev thì để *, production thì đổi thành domain FE
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_PASS") or "Thuong@9090@"
CLOUDINARY_CLOUD = os.getenv("CLOUDINARY_CLOUD", "dffjnmuq4")
CLOUDINARY_PRESET = os.getenv("CLOUDINARY_PRESET", "pcdnav5l")


class LoginRequest(BaseModel):
    password: str


def _post_to_response(post: models.Post) -> schemas.PostResponse:
    images = None
    if post.images:
        try:
            parsed = json.loads(post.images)
            images = parsed if isinstance(parsed, list) else None
        except json.JSONDecodeError:
            images = None

    return schemas.PostResponse(
        id=post.id,
        type=post.type,
        title=post.title,
        body=post.body,
        images=images,
        caption=post.caption,
        embed_url=post.embed_url,
        url=post.url,
        category=post.category or "daily-life",
        date=post.date,
    )


def _get_category_or_404(db: Session, slug: str) -> models.Category:
    category = db.query(models.Category).filter(models.Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy tab")
    return category


@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy index.html")
    return FileResponse(index_path)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest):
    if payload.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Sai mật khẩu")
    return {"ok": True}


# ── CATEGORIES ──
@app.get("/categories", response_model=list[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.id.asc()).all()


@app.post("/categories", response_model=schemas.CategoryResponse, status_code=201)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    slug = _slugify(category.slug or category.name)
    existing = db.query(models.Category).filter(models.Category.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tab đã tồn tại")
    new_category = models.Category(name=category.name.strip(), slug=slug)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@app.delete("/categories/{slug}")
def delete_category(slug: str, db: Session = Depends(get_db)):
    if slug in {default_slug for _, default_slug in DEFAULT_CATEGORIES}:
        raise HTTPException(status_code=400, detail="Không thể xóa tab mặc định")
    category = _get_category_or_404(db, slug)
    db.query(models.Post).filter(models.Post.category == slug).update({"category": "daily-life"})
    db.delete(category)
    db.commit()
    return {"message": "Đã xóa tab"}


# ── TODOS ──
@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@app.get("/todos", response_model=list[schemas.TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).order_by(models.Todo.id.desc()).all()


@app.get("/todos/{id}", response_model=schemas.TodoResponse)
def get_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return todo


@app.put("/todos/{id}", response_model=schemas.TodoResponse)
def update_todo(id: int, data: schemas.TodoCreate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    for key, value in data.model_dump().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    db.delete(todo)
    db.commit()
    return {"message": "Đã xóa"}


# ── POSTS ──
@app.post("/posts", response_model=schemas.PostResponse, status_code=201)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    _get_category_or_404(db, post.category)
    data = post.model_dump(by_alias=False)
    if data.get("images") is not None:
        data["images"] = json.dumps(data["images"])  # List → JSON string
    new_post = models.Post(**data)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return _post_to_response(new_post)

@app.get("/posts", response_model=list[schemas.PostResponse])
def get_posts(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Post)
    if category:
        query = query.filter(models.Post.category == category)
    posts = query.order_by(models.Post.id.desc()).all()
    return [_post_to_response(post) for post in posts]

@app.delete("/posts/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    db.delete(post)
    db.commit()
    return {"message": "Đã xóa"}

@app.put("/posts/{id}", response_model=schemas.PostResponse)
def update_post(id: int, data: schemas.PostCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    _get_category_or_404(db, data.category)
    update_data = data.model_dump(by_alias=False)
    if update_data.get("images") is not None:
        update_data["images"] = json.dumps(update_data["images"])
    for key, value in update_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return _post_to_response(post)

# ── UPLOAD ẢNH (gọi Cloudinary từ BE) ──
@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        import httpx
    except ModuleNotFoundError:
        raise HTTPException(status_code=500, detail="Thiếu dependency httpx")

    contents = await image.read()
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD}/image/upload",
            data={"upload_preset": CLOUDINARY_PRESET},
            files={"file": (image.filename, contents, image.content_type)}
        )
    data = res.json()
    if "secure_url" not in data:
        raise HTTPException(status_code=502, detail="Upload ảnh thất bại")
    return {"url": data["secure_url"]}