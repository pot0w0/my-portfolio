# API.md

# API 文档

假后端：FastAPI + 内存存储。默认运行在 `http://localhost:3000`。

- 交互式文档：`/docs`、`/openapi.json`
- 静态资源：`/static/*` → `uploads/` 目录，图片池在 `uploads/pool/`
- 前端地址（用于 RSS/分享链接）：`http://localhost:3001`

## 目录

- [通用约定](#通用约定)
- [鉴权与用户](#鉴权与用户)
- [文章 Posts](#文章-posts)
- [标签 Tags](#标签-tags)
- [系列 Series](#系列-series)
- [评论 Comments](#评论-comments)
- [图片池 Uploads](#图片池-uploads)
- [搜索 Search](#搜索-search)
- [友链 Friends](#友链-friends)
- [RSS](#rss)
- [数据结构](#数据结构)
- [错误码](#错误码)
- [业务规则与坑点](#业务规则与坑点)

---

## 通用约定

### Base URL

http://localhost:3000
```

### 鉴权
需要登录的接口在请求头带：
```
Authorization: Bearer <token>
```
- token 由登录/注册返回，服务端内存存储，**重启即失效**，无过期时间。
- 缺失或无效 → `401`。

### 分页响应
列表类接口（目前仅 `/api/posts`）统一返回：
```json
{ "data": [...], "total": 100, "page": 1, "limit": 10 }
```

### 时间格式
所有 `created_at` / `updated_at` 为 ISO 8601 UTC 字符串，例如 `2024-01-01T00:00:00+00:00`。

### CORS
全开：`allow_origins=["*"]`，允许 credentials、所有方法和头。

---

## 鉴权与用户

### POST `/api/user/login`
登录。

**Body**
```json
{ "username": "alice", "password": "alice123" }
```
**200**
```json
{
  "token": "a1b2c3...",
  "user": {
    "id": 1, "username": "alice", "role": "admin",
    "email": "alice@example.com", "avatar": null,
    "created_at": "2024-01-01T00:00:00+00:00"
  }
}
```
**错误**：`401` 用户名或密码错误。

---

### POST `/api/user/register`
注册并直接返回 token。

**Body**
```json
{ "username": "carol", "password": "secret", "email": "c@example.com" }
```
`email` 可选。**200** 同登录返回结构。

**错误**：`409` 用户名已存在。

---

### POST `/api/user/logout`
登出，从 Header 取 token 并从内存移除。

**Header**：`Authorization: Bearer <token>`（可选）
**204** 无 body。

---

### GET `/api/user/me`
当前登录用户（含 `role`）。

**需登录**。**200** 返回 `User`。

---

### PUT `/api/user/me`
更新当前用户资料，所有字段可选。

**需登录**。

**Body**
```json
{
  "username": "newname",
  "email": "new@example.com",
  "password": "newpass",
  "avatar": "/static/pool/xxx.webp"
}
```
字段语义：
- `username`：去空格后非空；与他人重名 → `409`；会同步更新用户名索引。
- `email`：去空格，空串视为 `null`。
- `password`：长度 < 6 → `400`。
- `avatar`：三态语义
  - **不传字段** → 不改
  - **传 `null`** → 解绑
  - **传值** → 必须是 `/static/pool/` 前缀，否则 `400`

**200** 返回更新后的 `User`。

---

### GET `/api/user/{user_id}`
用户公开信息（不含 role、password）。

**200** 返回 `UserPublic`；**404** 不存在。

---

## 文章 Posts

### GET `/api/posts`
分页文章列表。

**Query**
| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `page` | int | 1 | 页码 |
| `limit` | int | 10 | 每页数量 |
| `user_id` | int | - | 按作者过滤 |
| `series_id` | int | - | 按系列过滤 |
| `standalone` | bool | - | true 仅非系列文章 |
| `tag` | str | - | **标签 slug**（不是 id）；不存在 → `404` |
| `featured` | bool | - | 精选过滤 |
| `q` | str | - | 标题/内容关键字（不区分大小写） |
| `year` | int | - | 按创建年份 |
| `sort` | str | `created_at` | `created_at` / `title` / `series_order` |
| `order` | str | `desc` | `asc` / `desc` |

**200** 返回 `PageOut`，`data` 为 `Post[]`（内嵌 `author`、`series`、`tags`）。

---

### GET `/api/posts/{post_id}`
文章详情。**404** 不存在。返回 `Post`。

---

### GET `/api/posts/{post_id}/adjacent`
系列内前后篇导航。

**200**
```json
{
  "prev": { ...Post } | null,
  "next": { ...Post } | null,
  "series": {
    "id": 1, "slug": "nuxt-from-scratch",
    "title": "Nuxt 从零开始", "index": 2, "total": 5
  } | null
}
```
非系列文章：三者全为 `null`。

---

### POST `/api/posts`
新建文章。**需登录**。

**Body**
```json
{
  "title": "标题",
  "content": "Markdown 内容",
  "tag_ids": [1, 2],
  "featured": false,
  "series_id": 1,
  "series_order": 2,
  "cover": "/static/pool/xxx.webp"
}
```
规则：
- `title`、`content` 非空否则 `400`
- `featured=true` 仅 `admin`，否则 `403`
- `series_id` 必须存在，否则 `400`

**201** 返回 `Post`。

---

### PUT `/api/posts/{post_id}`
更新文章。**需登录**，作者本人或 `admin`。

**Body** 同 `POST /api/posts`。

**注意**：`cover` 使用 `model_fields_set` 判断——
- **不传 `cover` 字段** → 不修改
- **传 `cover: null`** → 清空封面
- **传值** → 更新

**200** 返回 `Post`；`404` 不存在；`403` 无权。

---

### DELETE `/api/posts/{post_id}`
删除文章。**需登录**，作者本人或 `admin`。

- 若该文章是某系列的介绍文 → `409`，需先更换介绍文。
- 删除会级联移除其标签关联，并 touch 所属系列。

**204** 无 body。

---

## 标签 Tags

### GET `/api/tags`
全部标签，含动态 `post_count`。

**200** `Tag[]`。

---

### POST `/api/tags`
新建标签。**需登录**。

**Body**
```json
{ "name": "Vue", "slug": "vue" }
```
- `name`、`slug` 均需非空 → 否则 `400`
- `slug` 已存在 → `409`
- `name` 已存在 → `409`

**201** 返回 `Tag`。

---

### PUT `/api/tags/{tag_id}`
只允许改 `name`。**需登录**。

**Body**
```json
{ "name": "Vue.js" }
```
- 空名 → `400`
- 重名（排除自身）→ `409`
- 不存在 → `404`

**200** 返回 `Tag`。

---

### DELETE `/api/tags/{tag_id}`
删除标签。**需登录**。级联从所有文章的 `post_tags` 中移除。

**204**；`404` 不存在。

---

## 系列 Series

> 系列没有独立标题和封面字段：**标题 = 介绍文的 title，封面 = 介绍文的 cover**。因此每个系列必须指定 `intro_post_id`。

### GET `/api/series`
系列列表。

**Query**
| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `q` | str | - | 匹配介绍文标题/内容 |
| `sort` | str | `updated_at` | `updated_at` / `created_at` / `title` |
| `order` | str | `desc` | `asc` / `desc` |

**200** `Series[]`。

---

### GET `/api/series/{slug}`
按 **slug** 取系列详情（注意不是 id）。

**200**
```json
{
  "series": { ...Series },
  "intro": { ...Post } | null,
  "posts": [ { ...Post } ]
}
```
`posts` 按 `series_order` 升序（`None` 视为 0）。

**404** 不存在。

---

### POST `/api/series`
新建系列。**需登录**。

**Body**
```json
{
  "slug": "nuxt-from-scratch",
  "description": "从零写一个 Nuxt 前端。",
  "intro_post_id": 1
}
```
规则：
- `slug` 非空且唯一，否则 `400`/`409`
- `intro_post_id` 必填且文章存在，否则 `400`
- 介绍文必须是自己（或 admin），否则 `403`

**201** 返回 `Series`。

---

### PUT `/api/series/{series_id}`
更新系列。**需登录**，作者本人或 `admin`。

**Body** 同创建（`intro_post_id` 可选，传则校验归属）。会更新 `updated_at`。

**200** 返回 `Series`。

---

### DELETE `/api/series/{series_id}`
删除系列。**需登录**，作者本人或 `admin`。

系列内所有文章的 `series_id` / `series_order` 置为 `null`（文章保留）。

**204**。

---

## 评论 Comments

### GET `/api/posts/{post_id}/comments`
某文章的全部评论，按 `id` 升序。

**404** 文章不存在。**200** `Comment[]`。

---

### POST `/api/posts/{post_id}/comments`
发表评论。**需登录**。

**Body**
```json
{ "content": "写得不错！" }
```
内容去空格后为空 → `400`；文章不存在 → `404`。

**201** 返回 `Comment`。

---

### DELETE `/api/comments/{comment_id}`
删除评论。**需登录**。允许：评论作者 / 文章作者 / admin。

**204**；`404` 不存在；`403` 无权。

---

## 图片池 Uploads

图片池用于文章封面、正文图片、用户头像等。文件只增不删，服务端每天 **04:00（本地时区）** 清理 **mtime > 24h 且引用数为 0** 的文件。

### POST `/api/uploads/images`
上传图片。**需登录**。`multipart/form-data`，字段名 `file`。

限制：
- MIME：`image/png`、`image/jpeg`、`image/webp`、`image/gif`
- 大小 ≤ 2MB
- 文件内容格式必须与 MIME 一致（魔数校验）
- 非 GIF 统一转 `WEBP`（quality=82），最大边 2048，保留透明通道
- GIF 原样保存

**200**
```json
{ "url": "/static/pool/xxxxxxxx.webp" }
```
**400** 类型/大小/格式不符。

---

### GET `/api/uploads/images`
列出图片池文件。**需登录**。

**Query**：`limit`（默认 60）
**200** 按 mtime 倒序的 `PoolImage[]`：
```json
[{ "url": "/static/pool/a.webp", "filename": "a.webp", "size": 12345, "mtime": 1700000000.0 }]
```

---

## 搜索 Search

### GET `/api/search`
聚合搜索文章、系列、标签、用户。

**Query**
| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `q` | str | `""` | 关键字 |
| `type` | str | - | 过滤：`post` / `series` / `tag` / `user` |
| `limit` | int | 8 | 返回条数 |

**行为**
- `q` 为空：返回最近 5 篇文章（`matched: "recent"`）+ 前 5 个标签（`matched: "popular"`）。
- `q` 非空：在文章标题/正文、系列介绍文/描述、标签名/slug、用户名中匹配。
- 排序优先级：`post > series > tag > user`，同级按标题长度升序。

**200**
```json
{
  "items": [
    {
      "type": "post", "id": 1, "title": "Nuxt 从零开始",
      "subtitle": "作者 alice", "url": "/posts/1", "matched": "title"
    }
  ],
  "post_filters": { "q": "nuxt" }
}
```

---

## 友链 Friends

### GET `/api/friends`
公开友链列表，仅返回 `visible=true`，按 `order, id` 升序。**无需登录**。

**200** `FriendLink[]`。

---

### POST `/api/friends`
新建友链。**需登录且 admin**，否则 `403`。

**Body**
```json
{
  "name": "Nuxt",
  "url": "https://nuxt.com",
  "description": "The Intuitive Vue Framework",
  "avatar": "https://nuxt.com/icon.png",
  "theme_color": "#00dc82",
  "skin": "neon",
  "tags": ["Vue", "框架"],
  "order": 1,
  "visible": true
}
```
校验：
- `name`、`url` 非空
- `theme_color` 必须匹配 `^#[0-9a-fA-F]{6}$`
- `skin` ∈ `{minimal, neon, tilt}`

**201** 返回 `FriendLink`。

---

### PUT `/api/friends/{fid}`
更新友链。**需登录且 admin**。Body 同创建，整体覆盖。

**200** 返回 `FriendLink`；`404` 不存在。

---

### DELETE `/api/friends/{fid}`
删除友链。**需登录且 admin**。**204**。

---

## RSS

### GET `/rss.xml`
RSS 2.0 订阅，最新 20 篇文章。

- `Cache-Control: public, max-age=600`
- 正文取 `content` 前 500 字符并转义
- `pubDate` 为 RFC 822 格式

---

## 数据结构

### User（登录/注册/me 返回，含 role）
```ts
{
  id: number;
  username: string;
  role: "user" | "admin";
  email: string | null;
  avatar: string | null;
  created_at: string;
}
```

### UserPublic（公开信息，无 role）
```ts
{
  id: number;
  username: string;
  email: string | null;
  avatar: string | null;
  created_at: string;
}
```

### Tag
```ts
{ id: number; name: string; slug: string; post_count: number; }
```

### Series
```ts
{
  id: number;
  title: string;          // 来自介绍文 title，无介绍文时为 "（无标题系列）"
  slug: string;
  description: string;
  cover: string | null;   // 来自介绍文 cover
  user_id: number;
  intro_post_id: number | null;
  author: UserPublic | null;
  post_count: number;
  created_at: string;
  updated_at: string;
}
```

### Post
```ts
{
  id: number;
  title: string;
  content: string;        // Markdown
  user_id: number;
  series_id: number | null;
  series_order: number | null;
  series: Series | null;
  tags: Tag[];
  featured: boolean;
  author: UserPublic | null;
  created_at: string;
  updated_at: string;
  cover: string | null;
}
```

### Comment
```ts
{
  id: number;
  post_id: number;
  user_id: number;
  content: string;
  author: UserPublic | null;
  created_at: string;
}
```

### FriendLink
```ts
{
  id: number;
  name: string;
  url: string;
  description: string;
  avatar: string | null;
  theme_color: string;    // #rrggbb
  skin: "minimal" | "neon" | "tilt";
  tags: string[];
  order: number;
  visible: boolean;
  created_at: string;
}
```

### PoolImage
```ts
{ url: string; filename: string; size: number; mtime: number; }
```

### SearchItem / SearchOut
```ts
type SearchItem = {
  type: "post" | "series" | "tag" | "user";
  id: number;
  title: string;
  subtitle: string;
  url: string;
  matched: string;        // "title" | "content" | "recent" | "popular" | ...
};
type SearchOut = { items: SearchItem[]; post_filters: Record<string, unknown> };
```

---

## 错误码

| 状态码 | 含义 | 典型场景 |
|---|---|---|
| 400 | 参数错误 | 标题/内容为空、图片格式不符、密码过短、theme_color 非法 |
| 401 | 未登录 / token 失效 | 缺 Bearer、token 不在内存 |
| 403 | 无权限 | 非 admin 设 featured、改他人文章、非 admin 管友链 |
| 404 | 资源不存在 | 文章/标签/系列/评论/用户不存在 |
| 409 | 冲突 | 用户名/slug/标签重名、删除系列介绍文 |
| 204 | 成功无内容 | 删除类接口 |

错误响应体为 FastAPI 默认：
```json
{ "detail": "错误说明" }
```

---

## 业务规则与坑点

1. **系列标题/封面来自介绍文**：没有独立字段。改介绍文标题或封面会同步改变系列展示。删除介绍文前必须先更换（否则 409）。
2. **`GET /api/series/{slug}` 用 slug**，而 `PUT/DELETE /api/series/{id}` 用 id，别混。
3. **`?tag=` 参数用 slug**，不是 tag id；slug 不存在返回 404。
4. **三态字段**：`PUT /api/user/me` 的 `avatar`、`PUT /api/posts/{id}` 的 `cover` 使用 `model_fields_set` 判断——
   - 不传字段 = 不改
   - 传 `null` = 解绑/清空
   - 传值 = 更新
5. **头像必须是图片池 URL**：`/static/pool/` 前缀，否则 400。
6. **精选仅 admin**：`featured=true` 时非 admin 会 403（更新时同）。
7. **评论删除权限**：评论作者、文章作者、admin 三者任一即可。
8. **图片池清理**：每天 04:00 删除 mtime > 24h 且无引用的文件。引用检查覆盖 `user.avatar`、`post.cover`、`post.content` 中的 URL 子串。**刚上传但未发布/未引用的图 24h 后会被清理**，前端如需长期保存请及时引用。
9. **上传即转 WEBP**（GIF 除外），前端回显 URL 后缀会是 `.webp`。
10. **token 永不过期**（内存存储），服务重启后需重新登录。
11. **种子数据**：`alice / alice123`（admin）、`bob / bob123`；种子文章、系列 `nuxt-from-scratch`、3 条友链、2 条评论。
12. **搜索空 q** 返回 recent + popular，适合首页搜索框下拉默认数据。
13. **列表接口统一分页结构** `{data,total,page,limit}`，前端可直接按此解构。
14. **`/openapi.json`** 可用于自动生成 TS 类型。

---

## 附：完整接口一览

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| POST | `/api/user/login` | - | 登录 |
| POST | `/api/user/register` | - | 注册 |
| POST | `/api/user/logout` | 可选 | 登出 |
| GET | `/api/user/me` | ✅ | 当前用户 |
| PUT | `/api/user/me` | ✅ | 更新资料 |
| GET | `/api/user/{user_id}` | - | 用户公开信息 |
| GET | `/api/posts` | - | 文章列表 |
| GET | `/api/posts/{id}` | - | 文章详情 |
| GET | `/api/posts/{id}/adjacent` | - | 系列前后篇 |
| POST | `/api/posts` | ✅ | 新建文章 |
| PUT | `/api/posts/{id}` | ✅ | 更新文章 |
| DELETE | `/api/posts/{id}` | ✅ | 删除文章 |
| GET | `/api/tags` | - | 标签列表 |
| POST | `/api/tags` | ✅ | 新建标签 |
| PUT | `/api/tags/{id}` | ✅ | 重命名标签 |
| DELETE | `/api/tags/{id}` | ✅ | 删除标签 |
| GET | `/api/series` | - | 系列列表 |
| GET | `/api/series/{slug}` | - | 系列详情（按 slug） |
| POST | `/api/series` | ✅ | 新建系列 |
| PUT | `/api/series/{id}` | ✅ | 更新系列 |
| DELETE | `/api/series/{id}` | ✅ | 删除系列 |
| GET | `/api/posts/{id}/comments` | - | 评论列表 |
| POST | `/api/posts/{id}/comments` | ✅ | 发表评论 |
| DELETE | `/api/comments/{id}` | ✅ | 删除评论 |
| POST | `/api/uploads/images` | ✅ | 上传图片 |
| GET | `/api/uploads/images` | ✅ | 图片池列表 |
| GET | `/api/search` | - | 聚合搜索 |
| GET | `/api/friends` | - | 友链列表 |
| POST | `/api/friends` | ✅ admin | 新建友链 |
| PUT | `/api/friends/{id}` | ✅ admin | 更新友链 |
| DELETE | `/api/friends/{id}` | ✅ admin | 删除友链 |
| GET | `/rss.xml` | - | RSS 订阅 |
| GET | `/static/pool/{filename}` | - | 图片静态访问 |
```