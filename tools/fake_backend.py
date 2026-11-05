"""
极简假后端：FastAPI + 内存存储
运行：
    pip install fastapi uvicorn python-multipart
    uvicorn fake_backend:app --reload --port 3000
"""
from __future__ import annotations

import os
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------- 数据模型 ----------
class User(BaseModel):
    id: int
    username: str
    role: str = "user"
    email: Optional[str] = None
    avatar: Optional[str] = None
    created_at: str

class UserPublic(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    created_at: str

class Category(BaseModel):
    id: int
    name: str
    slug: str

class CategoryIn(BaseModel):
    name: str
    slug: str

class Tag(BaseModel):
    id: int
    name: str
    slug: str

class Post(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    category: Optional[Category] = None
    tags: list[Tag] = []
    featured: bool = False
    author: Optional[UserPublic] = None
    created_at: str
    updated_at: str

class LoginIn(BaseModel):
    username: str
    password: str

class RegisterIn(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class AuthOut(BaseModel):
    token: str
    user: User

class PostIn(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None
    tag_ids: list[int] = []
    featured: bool = False

class PageOut(BaseModel):
    data: list[Post]
    total: int
    page: int
    limit: int

class Comment(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    author: Optional[UserPublic] = None
    created_at: str

class CommentIn(BaseModel):
    content: str

# ---------- 内存存储 ----------
now = lambda: datetime.now(timezone.utc).isoformat()

users: dict[int, dict] = {}
usernames: dict[str, int] = {}
posts: dict[int, dict] = {}
tokens: dict[str, int] = {}
comments: dict[int, dict] = {}
categories: dict[int, dict] = {}
tags: dict[int, dict] = {}
post_tags: dict[int, set[int]] = {}

_next_uid = 1
_next_pid = 1
_next_cid = 1
_next_cat = 1
_next_tag = 1

UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_BYTES = 2 * 1024 * 1024

# ---------- 构造辅助 ----------
def make_user(username: str, password: str, email: str | None = None, role: str = "user") -> dict:
    global _next_uid
    u = {
        "id": _next_uid, "username": username, "password": password,
        "role": role, "email": email, "avatar": None, "created_at": now(),
    }
    users[u["id"]] = u
    usernames[username] = u["id"]
    _next_uid += 1
    return u

def public_user(u: dict) -> UserPublic:
    return UserPublic(
        id=u["id"], username=u["username"], email=u.get("email"),
        avatar=u.get("avatar"), created_at=u["created_at"],
    )

def self_user(u: dict) -> User:
    return User(
        id=u["id"], username=u["username"], role=u["role"],
        email=u.get("email"), avatar=u.get("avatar"), created_at=u["created_at"],
    )

def make_post(user_id: int, title: str, content: str,
              category_id: int | None = None,
              tag_ids: list[int] | None = None,
              featured: bool = False) -> dict:
    global _next_pid
    ts = now()
    p = {
        "id": _next_pid, "title": title, "content": content,
        "user_id": user_id, "category_id": category_id,
        "featured": featured, "created_at": ts, "updated_at": ts,
    }
    posts[p["id"]] = p
    if tag_ids:
        post_tags[p["id"]] = set(tag_ids)
    _next_pid += 1
    return p

def post_out(p: dict) -> Post:
    author = users.get(p["user_id"])
    cat = categories.get(p.get("category_id"))
    tids = post_tags.get(p["id"], set())
    return Post(
        id=p["id"], title=p["title"], content=p["content"], user_id=p["user_id"],
        author=public_user(author) if author else None,
        category=Category(**cat) if cat else None,
        tags=[Tag(**tags[t]) for t in tids if t in tags],
        featured=bool(p.get("featured")),
        created_at=p["created_at"], updated_at=p["updated_at"],
    )

def make_comment(post_id: int, user_id: int, content: str) -> dict:
    global _next_cid
    c = {
        "id": _next_cid, "post_id": post_id, "user_id": user_id,
        "content": content, "created_at": now(),
    }
    comments[c["id"]] = c
    _next_cid += 1
    return c

def comment_out(c: dict) -> Comment:
    author = users.get(c["user_id"])
    return Comment(
        id=c["id"], post_id=c["post_id"], user_id=c["user_id"],
        content=c["content"], created_at=c["created_at"],
        author=public_user(author) if author else None,
    )

def make_category(name: str, slug: str) -> dict:
    global _next_cat
    c = {"id": _next_cat, "name": name, "slug": slug}
    categories[c["id"]] = c
    _next_cat += 1
    return c

def make_tag(name: str, slug: str) -> dict:
    global _next_tag
    t = {"id": _next_tag, "name": name, "slug": slug}
    tags[t["id"]] = t
    _next_tag += 1
    return t

# ---------- 种子数据（一次性，不重复） ----------
alice = make_user("alice", "alice123", "alice@example.com", role="admin")
bob = make_user("bob", "bob123")

cat_frontend = make_category("前端", "frontend")
cat_life = make_category("生活", "life")
tag_vue = make_tag("Vue", "vue")
tag_nuxt = make_tag("Nuxt", "nuxt")
tag_note = make_tag("随笔", "note")

p1 = make_post(alice["id"], "Hello World",
               "# 你好\n\n这是**第一篇**文章。\n\n- 支持列表\n- 支持 `code`",
               category_id=cat_frontend["id"], tag_ids=[tag_vue["id"]], featured=True)
p2 = make_post(alice["id"], "Markdown 测试",
               "## 二级标题\n\n```python\nprint('hi')\n```",
               category_id=cat_frontend["id"], tag_ids=[tag_nuxt["id"]])
p3 = make_post(bob["id"], "Bob 的文章",
               "我是 Bob。\n\n> 引用一段话。",
               category_id=cat_life["id"], tag_ids=[tag_note["id"]])

make_comment(p1["id"], bob["id"], "写得不错！")
make_comment(p1["id"], alice["id"], "谢谢～")

# ---------- 鉴权依赖 ----------
def get_me(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "未登录")
    token = authorization.removeprefix("Bearer ").strip()
    uid = tokens.get(token)
    if not uid or uid not in users:
        raise HTTPException(401, "登录已失效")
    return users[uid]

# ---------- 应用 ----------
app = FastAPI(title="Fake Backend")
app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ===== 用户 =====
@app.get("/api/user/me", response_model=User)
def user_me(me: dict = Depends(get_me)):
    return self_user(me)

@app.post("/api/user/login", response_model=AuthOut)
def login(body: LoginIn):
    uid = usernames.get(body.username)
    if not uid or users[uid]["password"] != body.password:
        raise HTTPException(401, "用户名或密码错误")
    token = secrets.token_hex(16)
    tokens[token] = uid
    return AuthOut(token=token, user=self_user(users[uid]))

@app.post("/api/user/logout", status_code=204)
def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        tokens.pop(authorization.removeprefix("Bearer ").strip(), None)
    return None

@app.post("/api/user/register", response_model=AuthOut)
def register(body: RegisterIn):
    if body.username in usernames:
        raise HTTPException(409, "用户名已存在")
    u = make_user(body.username, body.password, body.email)
    token = secrets.token_hex(16)
    tokens[token] = u["id"]
    return AuthOut(token=token, user=self_user(u))

@app.get("/api/user/{user_id}", response_model=UserPublic)
def user_detail(user_id: int):
    u = users.get(user_id)
    if not u:
        raise HTTPException(404, "用户不存在")
    return public_user(u)

# ===== 分类 / 标签 =====
@app.get("/api/categories", response_model=list[Category])
def list_categories():
    return [Category(**c) for c in categories.values()]

@app.get("/api/tags", response_model=list[Tag])
def list_tags():
    return [Tag(**t) for t in tags.values()]

@app.post("/api/categories", response_model=Category, status_code=201)
def create_category(body: CategoryIn, me: dict = Depends(get_me)):
    if me["role"] != "admin":
        raise HTTPException(403, "需要管理员")
    c = make_category(body.name, body.slug)
    return Category(**c)

# ===== 博客 =====
@app.get("/api/posts", response_model=PageOut)
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    featured: Optional[bool] = None,
):
    items = sorted(posts.values(), key=lambda p: p["id"], reverse=True)
    if user_id is not None:
        items = [p for p in items if p["user_id"] == user_id]
    if category:
        cat = next((c for c in categories.values() if c["slug"] == category), None)
        if not cat:
            raise HTTPException(404, "分类不存在")
        items = [p for p in items if p.get("category_id") == cat["id"]]
    if tag:
        t = next((t for t in tags.values() if t["slug"] == tag), None)
        if not t:
            raise HTTPException(404, "标签不存在")
        items = [p for p in items if t["id"] in post_tags.get(p["id"], set())]
    if featured is not None:
        items = [p for p in items if bool(p.get("featured")) == featured]
    total = len(items)
    start = (page - 1) * limit
    return PageOut(data=[post_out(p) for p in items[start:start + limit]],
                   total=total, page=page, limit=limit)

@app.get("/api/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    p = posts.get(post_id)
    if not p:
        raise HTTPException(404, "文章不存在")
    return post_out(p)

@app.post("/api/posts", response_model=Post, status_code=201)
def create_post(body: PostIn, me: dict = Depends(get_me)):
    if not body.title.strip() or not body.content.strip():
        raise HTTPException(400, "标题和内容不能为空")
    if body.category_id and body.category_id not in categories:
        raise HTTPException(400, "分类不存在")
    if body.featured and me["role"] != "admin":
        raise HTTPException(403, "只有管理员可设精选")
    p = make_post(me["id"], body.title, body.content,
                  category_id=body.category_id, tag_ids=body.tag_ids,
                  featured=body.featured)
    return post_out(p)

def ensure_can_modify(p: dict, me: dict):
    if p["user_id"] != me["id"] and me["role"] != "admin":
        raise HTTPException(403, "无权操作")

@app.put("/api/posts/{post_id}", response_model=Post)
def update_post(post_id: int, body: PostIn, me: dict = Depends(get_me)):
    p = posts.get(post_id)
    if not p:
        raise HTTPException(404, "文章不存在")
    ensure_can_modify(p, me)
    if body.category_id and body.category_id not in categories:
        raise HTTPException(400, "分类不存在")
    if body.featured and me["role"] != "admin":
        raise HTTPException(403, "只有管理员可设精选")
    p["title"] = body.title
    p["content"] = body.content
    p["category_id"] = body.category_id
    p["featured"] = body.featured
    p["updated_at"] = now()
    post_tags[p["id"]] = set(body.tag_ids)
    return post_out(p)

@app.delete("/api/posts/{post_id}", status_code=204)
def delete_post(post_id: int, me: dict = Depends(get_me)):
    p = posts.get(post_id)
    if not p:
        raise HTTPException(404, "文章不存在")
    ensure_can_modify(p, me)
    del posts[post_id]
    post_tags.pop(post_id, None)
    return None

# ===== 评论 =====
@app.get("/api/posts/{post_id}/comments", response_model=list[Comment])
def list_comments(post_id: int):
    if post_id not in posts:
        raise HTTPException(404, "文章不存在")
    items = [c for c in comments.values() if c["post_id"] == post_id]
    items.sort(key=lambda c: c["id"])
    return [comment_out(c) for c in items]

@app.post("/api/posts/{post_id}/comments", response_model=Comment, status_code=201)
def create_comment(post_id: int, body: CommentIn, me: dict = Depends(get_me)):
    if post_id not in posts:
        raise HTTPException(404, "文章不存在")
    if not body.content.strip():
        raise HTTPException(400, "评论内容不能为空")
    c = make_comment(post_id, me["id"], body.content.strip())
    return comment_out(c)

@app.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, me: dict = Depends(get_me)):
    c = comments.get(comment_id)
    if not c:
        raise HTTPException(404, "评论不存在")
    post = posts.get(c["post_id"])
    is_comment_author = c["user_id"] == me["id"]
    is_post_author = post and post["user_id"] == me["id"]
    is_admin = me["role"] == "admin"
    if not (is_comment_author or is_post_author or is_admin):
        raise HTTPException(403, "无权删除")
    del comments[comment_id]
    return None

# ===== 头像 =====
@app.post("/api/user/me/avatar", response_model=User)
async def upload_avatar(file: UploadFile = File(...), me: dict = Depends(get_me)):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "仅支持 png/jpeg/webp/gif")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "文件超过 2MB")
    ext = {"image/png": ".png", "image/jpeg": ".jpg",
           "image/webp": ".webp", "image/gif": ".gif"}[file.content_type]
    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, name)
    with open(path, "wb") as f:
        f.write(data)
    old = me.get("avatar")
    if old and old.startswith("/static/avatars/"):
        old_path = os.path.join("uploads", old.removeprefix("/static/"))
        if os.path.isfile(old_path):
            os.remove(old_path)
    me["avatar"] = f"/static/avatars/{name}"
    return self_user(me)

@app.delete("/api/user/me/avatar", response_model=User)
def delete_avatar(me: dict = Depends(get_me)):
    old = me.get("avatar")
    if old and old.startswith("/static/avatars/"):
        old_path = os.path.join("uploads", old.removeprefix("/static/"))
        if os.path.isfile(old_path):
            os.remove(old_path)
    me["avatar"] = None
    return self_user(me)