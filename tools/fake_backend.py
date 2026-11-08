"""
极简假后端：FastAPI + 内存存储（系列 + 标签 + 评论 + 图片池 + 友链 + 搜索）
运行：
    pip install fastapi uvicorn python-multipart pillow
    uvicorn fake_backend:app --reload --port 3000
"""
from __future__ import annotations

import io
import os
import re
import secrets
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
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

class Tag(BaseModel):
    id: int
    name: str
    slug: str
    post_count: int = 0

class Series(BaseModel):
    id: int
    title: str
    slug: str
    description: str = ""
    cover: Optional[str] = None
    user_id: int
    intro_post_id: Optional[int] = None
    author: Optional[UserPublic] = None
    post_count: int = 0
    created_at: str
    updated_at: str

class SeriesIn(BaseModel):
    slug: str
    description: str = ""
    intro_post_id: Optional[int] = None

class PostImage(BaseModel):
    id: int
    url: str

class Post(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    series_id: Optional[int] = None
    series_order: Optional[int] = None
    series: Optional[Series] = None
    tags: list[Tag] = []
    featured: bool = False
    author: Optional[UserPublic] = None
    created_at: str
    updated_at: str
    cover: Optional[str] = None
    images: list[PostImage] = []

class PostIn(BaseModel):
    title: str
    content: str
    tag_ids: list[int] = []
    featured: bool = False
    series_id: Optional[int] = None
    series_order: Optional[int] = None
    cover: Optional[str] = None

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

class PostImageOut(BaseModel):
    url: str

class ProfileIn(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None   # 新增：绑定/解绑头像（null 解绑）

class SearchItem(BaseModel):
    type: str
    id: int
    title: str
    subtitle: str = ""
    url: str
    matched: str = ""

class SearchOut(BaseModel):
    items: list[SearchItem]
    post_filters: dict

class TagIn(BaseModel):
    name: str
    slug: str

class TagUpdateIn(BaseModel):
    name: str

class FriendLink(BaseModel):
    id: int
    name: str
    url: str
    description: str = ""
    avatar: Optional[str] = None
    theme_color: str = "#3b82f6"
    skin: str = "minimal"
    tags: list[str] = []
    order: int = 0
    visible: bool = True
    created_at: str

class FriendLinkIn(BaseModel):
    name: str
    url: str
    description: str = ""
    avatar: Optional[str] = None
    theme_color: str = "#3b82f6"
    skin: str = "minimal"
    tags: list[str] = []
    order: int = 0
    visible: bool = True

class AdjacentOut(BaseModel):
    prev: Optional[Post] = None
    next: Optional[Post] = None
    series: Optional[dict] = None

class PoolImage(BaseModel):
    url: str
    filename: str
    size: int
    mtime: float

# ---------- 内存存储 ----------
now = lambda: datetime.now(timezone.utc).isoformat()

users: dict[int, dict] = {}
usernames: dict[str, int] = {}
posts: dict[int, dict] = {}
tokens: dict[str, int] = {}
comments: dict[int, dict] = {}
tags: dict[int, dict] = {}
post_tags: dict[int, set[int]] = {}
series: dict[int, dict] = {}
friends: dict[int, dict] = {}

_next_fid = 1
_next_uid = 1
_next_pid = 1
_next_cid = 1
_next_tag = 1
_next_sid = 1

UPLOAD_ROOT = "uploads"
POOL_DIR = os.path.join(UPLOAD_ROOT, "pool")
os.makedirs(POOL_DIR, exist_ok=True)

ALLOWED = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_BYTES = 2 * 1024 * 1024
MAX_DIMENSION = 2048
OUTPUT_FORMAT = "WEBP"
OUTPUT_EXT = ".webp"
ALLOWED_SKINS = {"minimal", "neon", "tilt"}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

PIL_FORMAT_MAP = {
    "image/png": "PNG",
    "image/jpeg": "JPEG",
    "image/webp": "WEBP",
    "image/gif": "GIF",
}

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

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

def tag_post_count(tag_id: int) -> int:
    return sum(1 for tids in post_tags.values() if tag_id in tids)

def tag_out(t: dict) -> Tag:
    return Tag(id=t["id"], name=t["name"], slug=t["slug"],
               post_count=tag_post_count(t["id"]))

def make_tag(name: str, slug: str) -> dict:
    global _next_tag
    t = {"id": _next_tag, "name": name, "slug": slug}
    tags[t["id"]] = t
    _next_tag += 1
    return t

def make_series(user_id: int, slug: str, description: str = "",
                intro_post_id: int | None = None) -> dict:
    global _next_sid
    ts = now()
    s = {
        "id": _next_sid, "slug": slug, "description": description,
        "user_id": user_id, "intro_post_id": intro_post_id,
        "created_at": ts, "updated_at": ts,
    }
    series[s["id"]] = s
    _next_sid += 1
    return s

def touch_series(series_id: int | None):
    if series_id and series_id in series:
        series[series_id]["updated_at"] = now()

def series_out(s: dict) -> Series:
    author = users.get(s["user_id"])
    count = sum(1 for p in posts.values() if p.get("series_id") == s["id"])
    intro = posts.get(s.get("intro_post_id")) if s.get("intro_post_id") else None
    title = intro["title"] if intro else "（无标题系列）"
    cover = intro.get("cover") if intro else None
    return Series(
        id=s["id"], title=title, slug=s["slug"],
        description=s.get("description", ""), cover=cover,
        user_id=s["user_id"], intro_post_id=s.get("intro_post_id"),
        author=public_user(author) if author else None,
        post_count=count, created_at=s["created_at"],
        updated_at=s.get("updated_at", s["created_at"]),
    )

def make_post(user_id: int, title: str, content: str,
              tag_ids: list[int] | None = None,
              featured: bool = False,
              series_id: int | None = None,
              series_order: int | None = None,
              cover: str | None = None) -> dict:
    global _next_pid
    ts = now()
    p = {
        "id": _next_pid, "title": title, "content": content,
        "user_id": user_id,
        "series_id": series_id, "series_order": series_order,
        "featured": featured, "cover": cover,
        "created_at": ts, "updated_at": ts,
    }
    posts[p["id"]] = p
    if tag_ids:
        post_tags[p["id"]] = set(tag_ids)
    _next_pid += 1
    return p

def post_out(p: dict) -> Post:
    author = users.get(p["user_id"])
    tids = post_tags.get(p["id"], set())
    s = series.get(p.get("series_id")) if p.get("series_id") else None
    return Post(
        id=p["id"], title=p["title"], content=p["content"], user_id=p["user_id"],
        series_id=p.get("series_id"), series_order=p.get("series_order"),
        series=series_out(s) if s else None,
        tags=[tag_out(tags[t]) for t in tids if t in tags],
        featured=bool(p.get("featured")), cover=p.get("cover"),
        author=public_user(author) if author else None,
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

# ---------- 图片 ----------
def save_image(data: bytes, content_type: str) -> str:
    """只存池，不删旧（清理交给定时任务）"""
    if content_type not in ALLOWED:
        raise HTTPException(400, "仅支持 png/jpeg/webp/gif")
    if not data:
        raise HTTPException(400, "空文件")
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "文件超过 2MB")

    expected = PIL_FORMAT_MAP[content_type]
    try:
        probe = Image.open(io.BytesIO(data))
        probe.verify()
    except Exception:
        raise HTTPException(400, "不是有效图片")

    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:
        raise HTTPException(400, "图片解析失败")

    real_fmt = (img.format or "").upper()
    if real_fmt == "JPG":
        real_fmt = "JPEG"
    if real_fmt != expected:
        raise HTTPException(400, "文件内容与类型不符")

    if expected == "GIF":
        img.close()
        out_bytes = data
        ext = ".gif"
    else:
        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        )
        img = img.convert("RGBA" if has_alpha else "RGB")
        w, h = img.size
        if max(w, h) > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), RESAMPLE)
        buf = io.BytesIO()
        img.save(buf, format=OUTPUT_FORMAT, quality=82, method=6)
        img.close()
        out_bytes = buf.getvalue()
        ext = OUTPUT_EXT

    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(POOL_DIR, name)
    with open(path, "wb") as f:
        f.write(out_bytes)
    return f"/static/pool/{name}"

def ref_count(url: str) -> int:
    n = 0
    for u in users.values():
        if u.get("avatar") == url:
            n += 1
    for p in posts.values():
        if p.get("cover") == url:
            n += 1
        if url in p["content"]:
            n += 1
    return n

def cleanup_uploads():
    """删 24h 以上且引用数为 0 的池文件"""
    cutoff = time.time() - 24 * 3600
    removed = 0
    if not os.path.isdir(POOL_DIR):
        return removed
    for name in os.listdir(POOL_DIR):
        path = os.path.join(POOL_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            if os.path.getmtime(path) > cutoff:
                continue
        except OSError:
            continue
        url = f"/static/pool/{name}"
        if ref_count(url) == 0:
            try:
                os.remove(path)
                removed += 1
            except OSError:
                pass
    return removed

def _seconds_until(hour: int, minute: int = 0) -> float:
    """返回距离下一个 hour:minute 的秒数（本地时区）"""
    now_local = datetime.now()
    target = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now_local:
        target += timedelta(days=1)
    return (target - now_local).total_seconds()

def cleanup_loop():
    while True:
        wait = _seconds_until(4, 0)
        time.sleep(max(1, wait))
        try:
            n = cleanup_uploads()
            print(f"[cleanup] removed {n} unused pool files")
        except Exception as e:
            print("cleanup failed:", e)

threading.Thread(target=cleanup_loop, daemon=True).start()

# ---------- 友链 ----------
def make_friend(d: dict) -> dict:
    global _next_fid
    f = {
        "id": _next_fid, "name": d["name"], "url": d["url"],
        "description": d.get("description", ""),
        "avatar": d.get("avatar"),
        "theme_color": d.get("theme_color", "#3b82f6"),
        "skin": d.get("skin", "minimal"),
        "tags": d.get("tags", []),
        "order": d.get("order", 0),
        "visible": d.get("visible", True),
        "created_at": now(),
    }
    friends[f["id"]] = f
    _next_fid += 1
    return f

def friend_out(f: dict) -> FriendLink:
    return FriendLink(**f)

# ---------- 种子数据 ----------
alice = make_user("alice", "alice123", "alice@example.com", role="admin")
bob = make_user("bob", "bob123")

tag_vue = make_tag("Vue", "vue")
tag_nuxt = make_tag("Nuxt", "nuxt")
tag_note = make_tag("随笔", "note")

p1 = make_post(alice["id"], "Nuxt 从零开始",
               "# 你好\n\n这是**第一篇**文章。\n\n- 支持列表\n- 支持 `code`",
               tag_ids=[tag_vue["id"]], featured=True)

s1 = make_series(alice["id"], "nuxt-from-scratch",
                 "从零写一个 Nuxt 前端，一步步来。",
                 intro_post_id=p1["id"])

p2 = make_post(alice["id"], "Markdown 测试",
               "## 二级标题\n\n```python\nprint('hi')\n```",
               tag_ids=[tag_nuxt["id"]],
               series_id=s1["id"], series_order=1)

p3 = make_post(bob["id"], "Bob 的文章",
               "我是 Bob。\n\n> 引用一段话。",
               tag_ids=[tag_note["id"]])

make_comment(p1["id"], bob["id"], "写得不错！")
make_comment(p1["id"], alice["id"], "谢谢～")

make_friend({"name": "Nuxt", "url": "https://nuxt.com", "description": "The Intuitive Vue Framework",
             "avatar": "https://nuxt.com/icon.png", "theme_color": "#00dc82", "skin": "neon",
             "tags": ["Vue", "框架"], "order": 1})
make_friend({"name": "Vue", "url": "https://vuejs.org", "description": "The Progressive JavaScript Framework",
             "avatar": "https://vuejs.org/logo.svg", "theme_color": "#42b883", "skin": "minimal",
             "tags": ["前端"], "order": 2})
make_friend({"name": "Tailwind", "url": "https://tailwindcss.com", "description": "Rapidly build modern websites",
             "theme_color": "#38bdf8", "skin": "tilt",
             "tags": ["CSS"], "order": 3})

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
app.mount("/static", StaticFiles(directory=UPLOAD_ROOT), name="static")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
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

@app.put("/api/user/me", response_model=User)
def update_me(body: ProfileIn, me: dict = Depends(get_me)):
    if body.username is not None:
        new_name = body.username.strip()
        if not new_name:
            raise HTTPException(400, "用户名不能为空")
        if new_name != me["username"] and new_name in usernames:
            raise HTTPException(409, "用户名已存在")
        usernames.pop(me["username"], None)
        me["username"] = new_name
        usernames[new_name] = me["id"]
    if body.email is not None:
        me["email"] = body.email.strip() or None
    if body.password:
        if len(body.password) < 6:
            raise HTTPException(400, "密码至少 6 位")
        me["password"] = body.password
    # 头像绑定/解绑：null 解绑（不删文件，交给清理）
    if body.avatar is not None or "avatar" in body.model_fields_set:
        if body.avatar and not body.avatar.startswith("/static/pool/"):
            raise HTTPException(400, "头像必须是图片池 URL")
        me["avatar"] = body.avatar or None
    return self_user(me)

# ===== 标签 =====
@app.get("/api/tags", response_model=list[Tag])
def list_tags():
    return [tag_out(t) for t in tags.values()]

@app.post("/api/tags", response_model=Tag, status_code=201)
def create_tag(body: TagIn, me: dict = Depends(get_me)):
    if not body.name.strip() or not body.slug.strip():
        raise HTTPException(400, "名称和 slug 必填")
    if any(t["slug"] == body.slug.strip() for t in tags.values()):
        raise HTTPException(409, "slug 已存在")
    if any(t["name"] == body.name.strip() for t in tags.values()):
        raise HTTPException(409, "标签已存在")
    t = make_tag(body.name.strip(), body.slug.strip())
    return tag_out(t)

@app.put("/api/tags/{tag_id}", response_model=Tag)
def update_tag(tag_id: int, body: TagUpdateIn, me: dict = Depends(get_me)):
    t = tags.get(tag_id)
    if not t:
        raise HTTPException(404, "标签不存在")
    new_name = body.name.strip()
    if not new_name:
        raise HTTPException(400, "名称不能为空")
    if any(x["name"] == new_name and x["id"] != tag_id for x in tags.values()):
        raise HTTPException(409, "标签已存在")
    t["name"] = new_name
    return tag_out(t)

@app.delete("/api/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, me: dict = Depends(get_me)):
    if tag_id not in tags:
        raise HTTPException(404, "标签不存在")
    del tags[tag_id]
    # 级联清 post_tags
    for pid, tids in post_tags.items():
        tids.discard(tag_id)
    return None

# ===== 系列 =====
@app.get("/api/series", response_model=list[Series])
def list_series(
    q: Optional[str] = None,
    sort: str = "updated_at",
    order: str = "desc",
):
    items = list(series.values())

    if q:
        kw = q.strip().lower()
        if kw:
            def matches(s):
                intro = posts.get(s.get("intro_post_id")) if s.get("intro_post_id") else None
                if not intro:
                    return False
                return kw in intro["title"].lower() or kw in intro["content"].lower()
            items = [s for s in items if matches(s)]

    reverse = order == "desc"
    if sort == "title":
        def title_of(s):
            intro = posts.get(s.get("intro_post_id")) if s.get("intro_post_id") else None
            return (intro["title"] if intro else "").lower()
        items.sort(key=title_of, reverse=reverse)
    elif sort == "created_at":
        items.sort(key=lambda s: s["created_at"], reverse=reverse)
    else:
        items.sort(key=lambda s: s.get("updated_at", s["created_at"]), reverse=reverse)

    return [series_out(s) for s in items]

@app.get("/api/series/{slug}")
def get_series(slug: str):
    s = next((s for s in series.values() if s["slug"] == slug), None)
    if not s:
        raise HTTPException(404, "系列不存在")
    intro = posts.get(s.get("intro_post_id")) if s.get("intro_post_id") else None
    posts_in = sorted(
        [p for p in posts.values() if p.get("series_id") == s["id"]],
        key=lambda p: p.get("series_order") or 0,
    )
    return {
        "series": series_out(s),
        "intro": post_out(intro) if intro else None,
        "posts": [post_out(p) for p in posts_in],
    }

@app.post("/api/series", response_model=Series, status_code=201)
def create_series(body: SeriesIn, me: dict = Depends(get_me)):
    if not body.slug.strip():
        raise HTTPException(400, "slug 必填")
    if any(s["slug"] == body.slug for s in series.values()):
        raise HTTPException(409, "slug 已存在")
    if not body.intro_post_id:
        raise HTTPException(400, "必须指定介绍文")
    intro = posts.get(body.intro_post_id)
    if not intro:
        raise HTTPException(400, "介绍文不存在")
    if intro["user_id"] != me["id"] and me["role"] != "admin":
        raise HTTPException(403, "介绍文不是你的文章")
    s = make_series(me["id"], body.slug.strip(), body.description,
                    intro_post_id=body.intro_post_id)
    return series_out(s)

@app.put("/api/series/{series_id}", response_model=Series)
def update_series(series_id: int, body: SeriesIn, me: dict = Depends(get_me)):
    s = series.get(series_id)
    if not s:
        raise HTTPException(404, "系列不存在")
    if s["user_id"] != me["id"] and me["role"] != "admin":
        raise HTTPException(403, "无权修改")
    if body.intro_post_id is not None:
        intro = posts.get(body.intro_post_id)
        if not intro:
            raise HTTPException(400, "介绍文不存在")
        if intro["user_id"] != me["id"] and me["role"] != "admin":
            raise HTTPException(403, "介绍文不是你的文章")
        s["intro_post_id"] = body.intro_post_id
    if body.slug:
        s["slug"] = body.slug.strip()
    s["description"] = body.description
    s["updated_at"] = now()
    return series_out(s)

@app.delete("/api/series/{series_id}", status_code=204)
def delete_series(series_id: int, me: dict = Depends(get_me)):
    s = series.get(series_id)
    if not s:
        raise HTTPException(404, "系列不存在")
    if s["user_id"] != me["id"] and me["role"] != "admin":
        raise HTTPException(403, "无权删除")
    del series[series_id]
    for p in posts.values():
        if p.get("series_id") == series_id:
            p["series_id"] = None
            p["series_order"] = None
    return None

# ===== 博客 =====
@app.get("/api/posts", response_model=PageOut)
def list_posts(
    page: int = 1, limit: int = 10,
    user_id: Optional[int] = None,
    series_id: Optional[int] = None,
    standalone: Optional[bool] = None,
    tag: Optional[str] = None,
    featured: Optional[bool] = None,
    q: Optional[str] = None,
    year: Optional[int] = None,
    sort: str = "created_at",
    order: str = "desc",
):
    items = list(posts.values())

    if q:
        kw = q.strip().lower()
        if kw:
            items = [p for p in items if kw in p["title"].lower() or kw in p["content"].lower()]
    if year:
        items = [p for p in items if p["created_at"][:4] == str(year)]
    if user_id is not None:
        items = [p for p in items if p["user_id"] == user_id]
    if standalone:
        items = [p for p in items if p.get("series_id") is None]
    if series_id is not None:
        items = [p for p in items if p.get("series_id") == series_id]
    if tag:
        t = next((t for t in tags.values() if t["slug"] == tag), None)
        if not t:
            raise HTTPException(404, "标签不存在")
        items = [p for p in items if t["id"] in post_tags.get(p["id"], set())]
    if featured is not None:
        items = [p for p in items if bool(p.get("featured")) == featured]

    reverse = order == "desc"
    if sort == "title":
        items.sort(key=lambda p: p["title"].lower(), reverse=reverse)
    elif sort == "series_order":
        items.sort(key=lambda p: (p.get("series_id") or 0, p.get("series_order") or 0), reverse=reverse)
    else:
        items.sort(key=lambda p: p["created_at"], reverse=reverse)

    total = len(items)
    start = (page - 1) * limit
    return PageOut(data=[post_out(p) for p in items[start:start+limit]],
                   total=total, page=page, limit=limit)

@app.get("/api/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    p = posts.get(post_id)
    if not p:
        raise HTTPException(404, "文章不存在")
    return post_out(p)

@app.get("/api/posts/{post_id}/adjacent", response_model=AdjacentOut)
def get_adjacent(post_id: int):
    p = posts.get(post_id)
    if not p:
        raise HTTPException(404, "文章不存在")

    sid = p.get("series_id")
    if not sid or sid not in series:
        return AdjacentOut(prev=None, next=None, series=None)

    siblings = sorted(
        [x for x in posts.values() if x.get("series_id") == sid],
        key=lambda x: x.get("series_order") or 0,
    )
    idx = next((i for i, x in enumerate(siblings) if x["id"] == post_id), -1)
    if idx < 0:
        return AdjacentOut(prev=None, next=None, series=None)

    s = series[sid]
    intro = posts.get(s.get("intro_post_id")) if s.get("intro_post_id") else None
    return AdjacentOut(
        prev=post_out(siblings[idx - 1]) if idx > 0 else None,
        next=post_out(siblings[idx + 1]) if idx < len(siblings) - 1 else None,
        series={
            "id": s["id"], "slug": s["slug"],
            "title": intro["title"] if intro else "（无标题系列）",
            "index": idx + 1, "total": len(siblings),
        },
    )

@app.post("/api/posts", response_model=Post, status_code=201)
def create_post(body: PostIn, me: dict = Depends(get_me)):
    if not body.title.strip() or not body.content.strip():
        raise HTTPException(400, "标题和内容不能为空")
    if body.featured and me["role"] != "admin":
        raise HTTPException(403, "只有管理员可设精选")
    if body.series_id and body.series_id not in series:
        raise HTTPException(400, "系列不存在")
    p = make_post(me["id"], body.title, body.content,
                  tag_ids=body.tag_ids, featured=body.featured,
                  series_id=body.series_id, series_order=body.series_order,
                  cover=body.cover)
    touch_series(body.series_id)
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
    if body.featured and me["role"] != "admin":
        raise HTTPException(403, "只有管理员可设精选")
    if body.series_id and body.series_id not in series:
        raise HTTPException(400, "系列不存在")

    old_series_id = p.get("series_id")

    p["title"] = body.title
    p["content"] = body.content
    p["featured"] = body.featured
    p["series_id"] = body.series_id
    p["series_order"] = body.series_order
    p["updated_at"] = now()

    if "cover" in body.model_fields_set:
        p["cover"] = body.cover

    post_tags[p["id"]] = set(body.tag_ids)

    touch_series(old_series_id)
    touch_series(body.series_id)
    return post_out(p)

@app.delete("/api/posts/{post_id}", status_code=204)
def delete_post(post_id: int, me: dict = Depends(get_me)):
    p = posts.get(post_id)
    if not p:
        raise HTTPException(404, "文章不存在")
    ensure_can_modify(p, me)
    sid = p.get("series_id")

    used_by = next((s for s in series.values() if s.get("intro_post_id") == post_id), None)
    if used_by:
        raise HTTPException(409, f"该文章是系列《{used_by['slug']}》的介绍文，请先更换介绍文再删除")

    del posts[post_id]
    touch_series(sid)
    post_tags.pop(post_id, None)
    return None

# ===== 图片池上传 =====
@app.post("/api/uploads/images", response_model=PostImageOut)
async def upload_image(file: UploadFile = File(...), me: dict = Depends(get_me)):
    data = await file.read()
    url = save_image(data, file.content_type)
    return PostImageOut(url=url)

@app.get("/api/uploads/images", response_model=list[PoolImage])
def list_pool_images(limit: int = 60, me: dict = Depends(get_me)):
    if not os.path.isdir(POOL_DIR):
        return []
    files = []
    for name in os.listdir(POOL_DIR):
        path = os.path.join(POOL_DIR, name)
        if not os.path.isfile(path):
            continue
        st = os.stat(path)
        files.append(PoolImage(
            url=f"/static/pool/{name}",
            filename=name,
            size=st.st_size,
            mtime=st.st_mtime,
        ))
    files.sort(key=lambda f: f.mtime, reverse=True)
    return files[:limit]

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

# ===== 搜索 =====
@app.get("/api/search", response_model=SearchOut)
def search(q: str = "", type: Optional[str] = None, limit: int = 8):
    kw = q.strip().lower()
    items: list[SearchItem] = []

    if not kw:
        recent = sorted(posts.values(), key=lambda p: p["id"], reverse=True)[:5]
        for p in recent:
            items.append(SearchItem(
                type="post", id=p["id"], title=p["title"],
                subtitle=(users.get(p["user_id"]) or {}).get("username", ""),
                url=f"/posts/{p['id']}", matched="recent",
            ))
        for t in list(tags.values())[:5]:
            items.append(SearchItem(
                type="tag", id=t["id"], title=t["name"],
                subtitle=f"标签 · #{t['slug']}",
                url=f"/posts?tag={t['slug']}", matched="popular",
            ))
        return SearchOut(items=items, post_filters={})

    for p in posts.values():
        if kw in p["title"].lower() or kw in p["content"].lower():
            author = users.get(p["user_id"]) or {}
            items.append(SearchItem(
                type="post", id=p["id"], title=p["title"],
                subtitle=f"作者 {author.get('username','')}",
                url=f"/posts/{p['id']}",
                matched="title" if kw in p["title"].lower() else "content",
            ))

    for s in series.values():
        intro = posts.get(s.get("intro_post_id")) if s.get("intro_post_id") else None
        if not intro:
            continue
        if kw in intro["title"].lower() or kw in intro["content"].lower() or kw in s.get("description", "").lower():
            items.append(SearchItem(
                type="series", id=s["id"], title=intro["title"],
                subtitle=f"系列 · {sum(1 for p in posts.values() if p.get('series_id')==s['id'])} 篇",
                url=f"/series/{s['slug']}", matched="series",
            ))

    for t in tags.values():
        if kw in t["name"].lower() or kw in t["slug"].lower():
            items.append(SearchItem(
                type="tag", id=t["id"], title=t["name"],
                subtitle=f"标签 · #{t['slug']}",
                url=f"/posts?tag={t['slug']}", matched="tag",
            ))

    for u in users.values():
        if kw in u["username"].lower():
            items.append(SearchItem(
                type="user", id=u["id"], title=u["username"],
                subtitle="用户", url=f"/user/{u['id']}", matched="user",
            ))

    if type:
        items = [i for i in items if i.type == type]

    order = {"post": 0, "series": 1, "tag": 2, "user": 3}
    items.sort(key=lambda i: (order[i.type], len(i.title)))

    return SearchOut(items=items[:limit], post_filters={"q": q})

# ===== 友链 =====
@app.get("/api/friends", response_model=list[FriendLink])
def list_friends():
    items = [f for f in friends.values() if f["visible"]]
    items.sort(key=lambda f: (f["order"], f["id"]))
    return [friend_out(f) for f in items]

def _validate_friend(body: FriendLinkIn):
    if not body.name.strip() or not body.url.strip():
        raise HTTPException(400, "名称和链接必填")
    if not HEX_RE.match(body.theme_color):
        raise HTTPException(400, "theme_color 必须是 #rrggbb")
    if body.skin not in ALLOWED_SKINS:
        raise HTTPException(400, f"skin 必须是 {ALLOWED_SKINS}")

@app.post("/api/friends", response_model=FriendLink, status_code=201)
def create_friend(body: FriendLinkIn, me: dict = Depends(get_me)):
    if me["role"] != "admin":
        raise HTTPException(403, "需要管理员")
    _validate_friend(body)
    f = make_friend(body.model_dump())
    return friend_out(f)

@app.put("/api/friends/{fid}", response_model=FriendLink)
def update_friend(fid: int, body: FriendLinkIn, me: dict = Depends(get_me)):
    if me["role"] != "admin":
        raise HTTPException(403, "需要管理员")
    if fid not in friends:
        raise HTTPException(404, "友链不存在")
    _validate_friend(body)
    friends[fid].update(body.model_dump())
    return friend_out(friends[fid])

@app.delete("/api/friends/{fid}", status_code=204)
def delete_friend(fid: int, me: dict = Depends(get_me)):
    if me["role"] != "admin":
        raise HTTPException(403, "需要管理员")
    if fid not in friends:
        raise HTTPException(404, "友链不存在")
    del friends[fid]
    return None