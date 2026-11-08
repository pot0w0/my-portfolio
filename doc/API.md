# API.md

> 基于 `fake_backend.py` 契约整理，用于实现真后端。  
> 基础路径：`/api`，静态资源：`/static`  
> 鉴权：`Authorization: Bearer <token>`  
> 时间格式：ISO 8601 UTC 字符串，如 `2026-11-08T12:00:00+00:00`  
> 分页：`page` 从 1 开始

---

## 目录

- [通用约定](#通用约定)
- [数据模型](#数据模型)
- [用户 / 鉴权](#用户--鉴权)
- [文章](#文章)
- [系列](#系列)
- [标签](#标签)
- [评论](#评论)
- [图片上传](#图片上传)
- [搜索](#搜索)
- [友链](#友链)
- [错误码](#错误码)
- [实现注意事项](#实现注意事项)

---

## 通用约定

### 请求头

| Header | 说明 |
|---|---|
| `Authorization: Bearer <token>` | 需登录的接口必须携带 |
| `Content-Type: application/json` | JSON 请求体 |
| `Content-Type: multipart/form-data` | 文件上传 |

### 权限角色

| 角色 | 说明 |
|---|---|
| `user` | 普通用户，可写自己的文章/评论，管理自己的资料 |
| `admin` | 管理员，可设精选、管理友链、修改/删除任意文章 |

### 分页响应

```json
{
  "data": [],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

### 删除成功

统一返回 `204 No Content`，无响应体。

---

## 数据模型

### User（私有，仅本人可见）

```json
{
  "id": 1,
  "username": "alice",
  "role": "admin",
  "email": "alice@example.com",
  "avatar": "/static/avatars/xxx.webp",
  "created_at": "2026-11-08T12:00:00+00:00"
}
```

### UserPublic（公开）

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "avatar": "/static/avatars/xxx.webp",
  "created_at": "2026-11-08T12:00:00+00:00"
}
```

> 不含 `role`、`password`。真后端可考虑隐藏 `email`。

### Tag

```json
{ "id": 1, "name": "Vue", "slug": "vue" }
```

### Series

```json
{
  "id": 1,
  "title": "Nuxt 从零开始",
  "slug": "nuxt-from-scratch",
  "description": "从零写一个 Nuxt 前端，一步步来。",
  "cover": "/static/posts/xxx.webp",
  "user_id": 1,
  "intro_post_id": 1,
  "author": { "id": 1, "username": "alice", "...": "..." },
  "post_count": 2,
  "created_at": "2026-11-08T12:00:00+00:00",
  "updated_at": "2026-11-08T12:00:00+00:00"
}
```

> **重要**：Series 无独立 `title` 字段，`title` 与 `cover` 派生自 `intro_post_id` 指向的文章。  
> 无 intro 文章时 `title = "（无标题系列）"`，`cover = null`。

### Post

```json
{
  "id": 1,
  "title": "Nuxt 从零开始",
  "content": "# 你好\n\n这是**第一篇**文章。",
  "user_id": 1,
  "series_id": 1,
  "series_order": 1,
  "series": { "...": "Series 对象或 null" },
  "tags": [{ "id": 1, "name": "Vue", "slug": "vue" }],
  "featured": true,
  "author": { "...": "UserPublic" },
  "created_at": "2026-11-08T12:00:00+00:00",
  "updated_at": "2026-11-08T12:00:00+00:00",
  "cover": "/static/posts/xxx.webp",
  "images": []
}
```

### Comment

```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "content": "写得不错！",
  "author": { "...": "UserPublic" },
  "created_at": "2026-11-08T12:00:00+00:00"
}
```

### FriendLink

```json
{
  "id": 1,
  "name": "Nuxt",
  "url": "https://nuxt.com",
  "description": "The Intuitive Vue Framework",
  "avatar": "https://nuxt.com/icon.png",
  "theme_color": "#00dc82",
  "skin": "neon",
  "tags": ["Vue", "框架"],
  "order": 1,
  "visible": true,
  "created_at": "2026-11-08T12:00:00+00:00"
}
```

### SearchItem / SearchOut

```json
{
  "type": "post",
  "id": 1,
  "title": "Nuxt 从零开始",
  "subtitle": "作者 alice",
  "url": "/posts/1",
  "matched": "title"
}
```

```json
{
  "items": [],
  "post_filters": { "q": "nuxt" }
}
```

`type` 枚举：`post` | `series` | `tag` | `user`  
`matched` 字段：`recent` | `popular` | `title` | `content` | `series` | `tag` | `user`

---

## 用户 / 鉴权

### 1. 获取当前用户

```
GET /api/user/me
```

**鉴权**：必须  
**响应**：`User`

---

### 2. 登录

```
POST /api/user/login
```

**请求体**

```json
{ "username": "alice", "password": "alice123" }
```

**响应** `200`

```json
{
  "token": "a1b2c3d4e5f6...",
  "user": { "id": 1, "username": "alice", "role": "user", "...": "..." }
}
```

**错误**

| 状态码 | 场景 |
|---|---|
| 401 | 用户名或密码错误 |

---

### 3. 登出

```
POST /api/user/logout
```

**鉴权**：可选（有 token 则作废）  
**响应**：`204`

---

### 4. 注册

```
POST /api/user/register
```

**请求体**

```json
{ "username": "bob", "password": "bob123", "email": "bob@example.com" }
```

`email` 可选。

**响应** `200`：同登录（返回 token + user）

**错误**

| 状态码 | 场景 |
|---|---|
| 409 | 用户名已存在 |

---

### 5. 查看用户公开信息

```
GET /api/user/{user_id}
```

**响应**：`UserPublic`  
**错误**：`404` 用户不存在

---

### 6. 更新当前用户资料

```
PUT /api/user/me
```

**鉴权**：必须  
**请求体**（所有字段可选）

```json
{
  "username": "new_name",
  "email": "new@example.com",
  "password": "newpass"
}
```

**响应**：`User`

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | 用户名为空 / 密码少于 6 位 |
| 409 | 新用户名已存在 |

---

### 7. 上传头像

```
POST /api/user/me/avatar
Content-Type: multipart/form-data
```

**字段**：`file`（图片）  
**鉴权**：必须  
**响应**：`User`（含新 `avatar` URL）

---

### 8. 删除头像

```
DELETE /api/user/me/avatar
```

**鉴权**：必须  
**响应**：`User`（`avatar = null`）

---

## 文章

### 1. 文章列表

```
GET /api/posts
```

**Query 参数**

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `page` | int | 1 | 页码，从 1 开始 |
| `limit` | int | 10 | 每页数量 |
| `user_id` | int | - | 按作者筛选 |
| `series_id` | int | - | 按系列筛选 |
| `standalone` | bool | - | true 时只返回不属于系列的文章 |
| `tag` | string | - | 标签 slug |
| `featured` | bool | - | 是否精选 |
| `q` | string | - | 标题或内容模糊匹配 |
| `year` | int | - | 创建年份 |
| `sort` | string | `created_at` | `created_at` \| `title` \| `series_order` |
| `order` | string | `desc` | `asc` \| `desc` |

**响应**：`PageOut`（`data` 为 `Post[]`）

**错误**

| 状态码 | 场景 |
|---|---|
| 404 | `tag` 指定的标签不存在 |

---

### 2. 文章详情

```
GET /api/posts/{post_id}
```

**响应**：`Post`  
**错误**：`404`

---

### 3. 创建文章

```
POST /api/posts
```

**鉴权**：必须  
**请求体**

```json
{
  "title": "标题",
  "content": "Markdown 内容",
  "tag_ids": [1, 2],
  "featured": false,
  "series_id": null,
  "series_order": null,
  "cover": "/static/posts/xxx.webp"
}
```

**响应** `201`：`Post`

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | 标题或内容为空 / 系列不存在 |
| 403 | 非 admin 设置 `featured=true` |

---

### 4. 更新文章

```
PUT /api/posts/{post_id}
```

**鉴权**：必须（作者或 admin）  
**请求体**：同创建  
**响应**：`Post`

**错误**

| 状态码 | 场景 |
|---|---|
| 403 | 无权操作 / 非 admin 设精选 |
| 404 | 文章不存在 |
| 400 | 系列不存在 |

> ⚠️ 假后端此处有 bug（`body_series_id` 未定义），真实现请用 `body.series_id`。

---

### 5. 删除文章

```
DELETE /api/posts/{post_id}
```

**鉴权**：必须（作者或 admin）  
**响应**：`204`

**错误**

| 状态码 | 场景 |
|---|---|
| 403 | 无权操作 |
| 404 | 文章不存在 |
| 409 | 该文章是某系列介绍文，需先更换介绍文 |

---

### 6. 上传文章封面

```
POST /api/posts/{post_id}/cover
Content-Type: multipart/form-data
```

**字段**：`file`  
**鉴权**：必须（作者或 admin）  
**响应**：`Post`

---

### 7. 删除文章封面

```
DELETE /api/posts/{post_id}/cover
```

**鉴权**：必须（作者或 admin）  
**响应**：`Post`

---

### 8. 上传正文图片（绑定文章）

```
POST /api/posts/{post_id}/images
Content-Type: multipart/form-data
```

**字段**：`file`  
**鉴权**：必须（作者或 admin）  
**响应**

```json
{ "url": "/static/posts/xxx.webp" }
```

---

## 系列

### 1. 系列列表

```
GET /api/series
```

**Query 参数**

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `q` | string | - | 匹配介绍文标题/内容 |
| `sort` | string | `updated_at` | `updated_at` \| `created_at` \| `title` |
| `order` | string | `desc` | `asc` \| `desc` |

**响应**：`Series[]`

---

### 2. 系列详情

```
GET /api/series/{slug}
```

**响应**

```json
{
  "series": { "...": "Series" },
  "intro": { "...": "Post 或 null" },
  "posts": [ "...": "按 series_order 升序" ]
}
```

**错误**：`404`

---

### 3. 创建系列

```
POST /api/series
```

**鉴权**：必须  
**请求体**

```json
{
  "slug": "nuxt-from-scratch",
  "description": "系列描述",
  "intro_post_id": 1
}
```

`intro_post_id` **必填**（假后端校验）。

**响应** `201`：`Series`

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | slug 为空 / 未指定介绍文 / 介绍文不存在 |
| 403 | 介绍文不属于当前用户（admin 除外） |
| 409 | slug 已存在 |

---

### 4. 更新系列

```
PUT /api/series/{series_id}
```

**鉴权**：必须（作者或 admin）  
**请求体**：同创建，`intro_post_id` 可选  
**响应**：`Series`

**错误**

| 状态码 | 场景 |
|---|---|
| 403 | 无权修改 / 介绍文不属于当前用户 |
| 404 | 系列不存在 |
| 400 | 介绍文不存在 |

---

### 5. 删除系列

```
DELETE /api/series/{series_id}
```

**鉴权**：必须（作者或 admin）  
**响应**：`204`  
**副作用**：该系列下所有文章的 `series_id` / `series_order` 置 `null`。

**错误**

| 状态码 | 场景 |
|---|---|
| 403 | 无权删除 |
| 404 | 系列不存在 |

---

## 标签

### 1. 标签列表

```
GET /api/tags
```

**响应**：`Tag[]`

---

### 2. 创建标签

```
POST /api/tags
```

**鉴权**：必须  
**请求体**

```json
{ "name": "Vue", "slug": "vue" }
```

**响应** `201`：`Tag`

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | name 或 slug 为空 |
| 409 | slug 已存在 / 标签名已存在 |

> 假后端无更新/删除标签接口，真后端建议补：  
> `PUT /api/tags/{id}`、`DELETE /api/tags/{id}`（admin）。

---

## 评论

### 1. 文章评论列表

```
GET /api/posts/{post_id}/comments
```

**响应**：`Comment[]`（按 id 升序）  
**错误**：`404` 文章不存在

---

### 2. 发表评论

```
POST /api/posts/{post_id}/comments
```

**鉴权**：必须  
**请求体**

```json
{ "content": "写得不错！" }
```

**响应** `201`：`Comment`

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | 内容为空 |
| 404 | 文章不存在 |

---

### 3. 删除评论

```
DELETE /api/comments/{comment_id}
```

**鉴权**：必须（评论作者 / 文章作者 / admin）  
**响应**：`204`

**错误**

| 状态码 | 场景 |
|---|---|
| 403 | 无权删除 |
| 404 | 评论不存在 |

---

## 图片上传

### 通用图片上传

```
POST /api/uploads/images
Content-Type: multipart/form-data
```

**字段**：`file`  
**鉴权**：必须  
**响应**

```json
{ "url": "/static/posts/xxx.webp" }
```

**约束（与假后端一致）**

| 项 | 值 |
|---|---|
| 允许 MIME | `image/png`、`image/jpeg`、`image/webp`、`image/gif` |
| 最大体积 | 2 MB |
| 最长边 | 超过 2048 等比缩小 |
| 输出格式 | 统一 WebP（quality 82，GIF 除外） |
| GIF | 原样保存，扩展名 `.gif` |
| 内容校验 | 真实格式必须与 MIME 一致 |

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | 类型不支持 / 空文件 / 超过 2MB / 非有效图片 / 内容与类型不符 |

### 静态资源

```
GET /static/**
```

由后端静态文件服务提供，目录结构：

```
uploads/
├── avatars/    # 头像
└── posts/      # 封面、正文图、通用图
```

---

## 搜索

```
GET /api/search
```

**Query 参数**

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `q` | string | `""` | 搜索词 |
| `type` | string | - | `post` \| `series` \| `tag` \| `user` |
| `limit` | int | 8 | 返回条数上限 |

**行为**

- `q` 为空：返回最近 5 篇文章（`matched="recent"`）+ 前 5 个标签（`matched="popular"`），`post_filters={}`
- `q` 非空：聚合匹配
  - 文章：标题或内容命中 → `matched=title|content`
  - 系列：介绍文标题/内容或 description 命中 → `matched=series`
  - 标签：name 或 slug 命中 → `matched=tag`
  - 用户：username 命中 → `matched=user`
- 按 `post < series < tag < user` 排序，同类按标题长度升序
- `type` 参数在排序前过滤
- 返回 `post_filters={"q": q}`，供前端跳转 `/posts?q=...`

**响应**：`SearchOut`

---

## 友链

### 1. 友链列表（公开）

```
GET /api/friends
```

**响应**：`FriendLink[]`（仅 `visible=true`，按 `order, id` 升序）

---

### 2. 创建友链

```
POST /api/friends
```

**鉴权**：必须 admin  
**请求体**

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

**响应** `201`：`FriendLink`

**校验**

| 规则 | 说明 |
|---|---|
| `name`、`url` | 非空 |
| `theme_color` | 必须匹配 `^#[0-9a-fA-F]{6}$` |
| `skin` | `minimal` \| `neon` \| `tilt` |

**错误**

| 状态码 | 场景 |
|---|---|
| 400 | 校验失败 |
| 403 | 非 admin |

---

### 3. 更新友链

```
PUT /api/friends/{fid}
```

**鉴权**：必须 admin  
**请求体**：同创建  
**响应**：`FriendLink`

**错误**：`403` / `404` / `400`

---

### 4. 删除友链

```
DELETE /api/friends/{fid}
```

**鉴权**：必须 admin  
**响应**：`204`  
**错误**：`403` / `404`

> 真后端建议补 `GET /api/friends/all`（admin 看全部含隐藏）。

---

## 错误码

| 状态码 | 含义 | 典型场景 |
|---|---|---|
| 400 | 请求参数错误 | 校验失败、文件非法、系列不存在 |
| 401 | 未登录 / token 失效 | 缺少或无效 Bearer |
| 403 | 无权限 | 非作者、非 admin、设精选 |
| 404 | 资源不存在 | 文章/系列/标签/用户/评论/友链 |
| 409 | 冲突 | 用户名、slug、标签重复；介绍文被引用 |
| 204 | 成功无内容 | 所有 DELETE、logout |

错误响应体建议统一：

```json
{ "detail": "错误描述" }
```

（假后端用 FastAPI 默认格式，真后端可沿用）

---

## 实现注意事项

### 假后端的已知 bug（勿照抄）

1. `update_post` 中 `touch_series(body_series_id)` —— `body_series_id` 未定义，应为 `body.series_id`
2. `make_series` 写入 `"update_at"`，但 `series_out` 读取 `"updated_at"`，靠 `.get` 兜底
3. 顶部重复声明 `posts: dict[int, dict]`
4. `Series.title` 完全派生自 intro 文章，系列无法独立命名 —— 真后端可考虑给 Series 加独立 `title` 字段
5. 创建系列时 `intro_post_id` 必填，但更新时可空 —— 语义不一致

### 真后端建议

| 项 | 建议 |
|---|---|
| 密码 | bcrypt / argon2 哈希，禁止明文 |
| Token | JWT（含 `sub`、`exp`）或 DB 存 token 表，支持过期与撤销 |
| 数据库 | Users / Posts / Series / Tags / PostTags / Comments / Friends 七张表 |
| 多对多 | `post_tags(post_id, tag_id)` 联合主键 |
| 系列 | 建议加独立 `title`，`intro_post_id` 可空 |
| 评论 | 建议加 `parent_id` 支持楼中楼、分页 |
| 搜索 | Postgres `tsvector` / SQLite FTS5 / Meilisearch，按相关度排序 |
| 图片 | 对象存储（S3/OSS）+ CDN，或本地 + Pillow 转码 |
| 删除文章 | 级联删除评论、post_tags；检查 intro 引用 |
| 删除系列 | 事务内把 `posts.series_id` 置 null |
| 静态资源 | `/static/*` 加缓存头（`Cache-Control: max-age=31536000, immutable`） |
| CORS | 生产环境限定白名单，勿用 `*` |
| 分页 | 大表建议加 `total` 缓存或 cursor 分页 |
| 友链 | `visible` 公开过滤，admin 另开 `/all` |
| 日志 | 记录写操作审计（谁改了哪篇文章） |
| 限流 | 登录、注册、评论、上传接口加 rate limit |

### 建议补的接口（假后端没有）

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/posts/{id}/adjacent` | 系列内上一篇/下一篇 |
| `GET` | `/api/archives` | 按年月归档 |
| `PUT` / `DELETE` | `/api/tags/{id}` | 标签改删（admin） |
| `PUT` | `/api/comments/{id}` | 编辑评论 |
| `PATCH` | `/api/series/{id}/reorder` | 批量调整 `series_order` |
| `POST` | `/api/user/refresh` | 刷新 token |
| `GET` | `/api/friends/all` | admin 看全部友链 |
| `GET` | `/api/users` | 用户列表（admin） |

### 前端契约要点

- 系列标题永远来自 intro 文章标题，前端不要假设系列有独立 title
- 图片 URL 是相对路径 `/static/...`，前端拼 baseURL
- `401` 触发重新登录，`403` 提示无权限，`409` 提示冲突
- `featured` 只有 admin 能设，普通用户提交会被 403
- 删除系列后文章变成"独立文章"（`series_id=null`）