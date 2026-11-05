## 一、当前后端接口清单（按你一路加下来的）

### 用户 / 认证

| 方法 | 路径 | 状态 | 说明 |
|---|---|---|---|
| GET | `/api/user/me` | ✅ | 当前用户，含 `role` |
| POST | `/api/user/login` | ✅ | 返回 `{ token, user }` |
| POST | `/api/user/logout` | ✅ | 204 |
| POST | `/api/user/register` | ✅ | 返回 `{ token, user }`，不接受 `role` |
| GET | `/api/user/{id}` | ✅ | 公开用户（`UserPublic`，**不含 role**） |
| PATCH | `/api/user/{id}/role` | ⚠️ | admin 改角色，前端没做 UI |
| POST | `/api/user/me/avatar` | ✅ | 上传头像，返回 `User` |
| DELETE | `/api/user/me/avatar` | ✅ | 删头像，返回 `User` |

### 博客文章

| 方法 | 路径 | 状态 | 说明 |
|---|---|---|---|
| GET | `/api/posts` | ✅ | 分页 + 过滤，见下方 query |
| GET | `/api/posts/{id}` | ✅ | 详情 |
| POST | `/api/posts` | ✅ | 需登录 |
| PUT | `/api/posts/{id}` | ✅ | 作者或 admin |
| DELETE | `/api/posts/{id}` | ✅ | 作者或 admin |

`GET /api/posts` 的 query（**现在支持的一堆，注意是否都接进前端**）：

| 参数 | 状态 | 说明 |
|---|---|---|
| `page` / `limit` | ✅ 前端用 | 分页 |
| `user_id` | ✅ 前端用 | 某用户文章 |
| `category` (slug) | ✅ 前端用 | 分类筛选 |
| `tag` (slug) | ✅ 前端用 | 标签筛选 |
| `featured` | ✅ 前端用 | 首页精选 |
| `series_id` | ⚠️ 后端可能有，前端没接 | 某系列文章 |
| `standalone` | ⚠️ 后端可能有，前端没接 | 只看散篇 |

### 分类 / 标签

| 方法 | 路径 | 状态 | 说明 |
|---|---|---|---|
| GET | `/api/categories` | ✅ | 列表 |
| GET | `/api/tags` | ✅ | 列表 |
| POST | `/api/categories` | ⚠️ | admin 建分类，前端没 UI |
| POST | `/api/tags` | ⚠️ | admin 建标签，前端没 UI |

### 系列（新加，状态要看后端实际写到哪）

| 方法 | 路径 | 状态 | 说明 |
|---|---|---|---|
| GET | `/api/series` | ✅（若后端已写） | 系列列表 + `post_count` |
| GET | `/api/series/{slug}` | ✅（若后端已写） | `{ series, posts }` 有序 |
| POST | `/api/series` | ❌ 多半没写 | 建系列 |
| PUT | `/api/series/{id}` | ❌ 多半没写 | 改系列 |

### 评论

| 方法 | 路径 | 状态 | 说明 |
|---|---|---|---|
| GET | `/api/posts/{id}/comments` | ✅ | 数组，旧→新 |
| POST | `/api/posts/{id}/comments` | ✅ | 需登录 |
| DELETE | `/api/comments/{id}` | ✅ | 评论作者 / 文章作者 / admin |

### 静态

| 路径 | 状态 | 说明 |
|---|---|---|
| `/static/**` | ✅ | 头像文件 |

---

## 二、问题：现在"乱"在哪

1. **`GET /api/posts` 参数太多**：`user_id / category / tag / featured / series_id / standalone` 六个过滤维度混在一个接口里，前端每个页面各传各的，容易传错。
2. **系列接口半成品**：`GET /api/series` 和 `/api/series/{slug}` 前端已调，但后端是否真返回 `post_count`、`series` 内联、`series_order` 排序，需要确认；`POST/PUT /api/series` 没做，意味着**系列没法从 UI 创建**，只能种子数据。
3. **分类/标签的创建接口做了但没 UI**：等于死代码，要么补 admin 页，要么删。
4. **`PATCH /api/user/{id}/role` 死代码**：前端没入口，要么补，要么删。
5. **前端页面职责重叠**：`/posts` 现在既要"系列区"又要"散篇区"又要分类 tab 又要标签筛选，一个页面背太多。
6. **`PostEditor` 同时管**：标题、正文、分类、标签、系列、序号、精选，组件过载。

---

## 三、整理建议：接口分三组，前端按组用

### 组 1：内容读取（公开，无需登录）

```
GET /api/posts                 # 统一列表，query 见下
GET /api/posts/{id}            # 详情（内联 author/category/tags/series）
GET /api/categories            # 分类列表
GET /api/tags                  # 标签列表
GET /api/series                # 系列列表（含 post_count）
GET /api/series/{slug}         # 系列详情 + 有序文章
GET /api/posts/{id}/comments   # 评论列表
GET /api/user/{id}             # 公开用户
```

`GET /api/posts` 的 query **收敛成一张表**，明确每个参数的用途：

| 参数 | 类型 | 用途 | 前端哪用 |
|---|---|---|---|
| `page` / `limit` | int | 分页 | 所有列表 |
| `user_id` | int | 某用户文章 | `/user/[id]`、`/user` |
| `category` | slug | 分类筛选 | `/posts` 分类 tab |
| `tag` | slug | 标签筛选 | `/posts` 标签条 |
| `featured` | bool | 精选 | 首页 |
| `series_id` | int | 某系列文章 | 系列页（但系列页用 `/api/series/{slug}` 更合适） |
| `standalone` | bool | 只看散篇 | `/posts` 散篇区 |

> **建议**：系列页**不要**用 `GET /api/posts?series_id=`，直接用 `GET /api/series/{slug}`（它返回 `{series, posts}`，省一次请求）。`series_id` 参数保留给"后台/管理"场景，前端暂不用。

### 组 2：写入（需登录）

```
POST   /api/posts
PUT    /api/posts/{id}
DELETE /api/posts/{id}
POST   /api/posts/{id}/comments
DELETE /api/comments/{id}
POST   /api/user/me/avatar
DELETE /api/user/me/avatar
```

### 组 3：管理（admin，当前先冻结）

```
POST   /api/categories
POST   /api/tags
POST   /api/series
PUT    /api/series/{id}
PATCH  /api/user/{id}/role
```

> 这组**现在没有 UI**。两种处理：
> - **A（推荐）**：先全部注释/删掉，等真做 admin 页再加，减少死代码；
> - **B**：保留但标 `# TODO: admin UI`，种子数据硬编码分类/标签/系列。
>
> 系列现在只能种子，**如果你要在 UI 里建系列**，至少得做 `POST /api/series` + 一个"建系列"表单，否则系列只能靠手改假后端。

---

## 四、前端页面 ↔ 接口 对照（理清谁调谁）

| 页面 | 调用的接口 |
|---|---|
| `/` 首页 | `GET /api/posts?featured=true&limit=2`、`GET /api/posts?standalone=true&limit=3` |
| `/posts` | `GET /api/posts?standalone=true&page&limit`、`GET /api/series`、`GET /api/categories`、`GET /api/tags`、`POST /api/posts` |
| `/posts/[id]` | `GET /api/posts/{id}`、`GET /api/posts/{id}/comments`、`PUT/DELETE /api/posts/{id}`、评论增删 |
| `/series` | `GET /api/series` |
| `/series/[slug]` | `GET /api/series/{slug}` |
| `/user` | `GET /api/user/me`、`GET /api/posts?user_id=me`、`POST/DELETE /api/user/me/avatar` |
| `/user/[id]` | `GET /api/user/{id}`、`GET /api/posts?user_id=id` |
| `/login` `/register` | `POST /api/user/login`、`POST /api/user/register` |
| 全局 | `GET /api/user/me`（恢复登录态）、`POST /api/user/logout` |

**一眼能看出的冗余**：

- `/posts` 调了 `categories` + `tags` 但**如果系列成了主轴，分类/标签筛选可以砍掉或降级**，否则这页太重；
- 首页的"精选"和"散篇最新"是两次 `GET /api/posts`，可以合并成一次拉 5 条前端拆，但语义不同（featured 和 standalone 是不同过滤），保持两次也合理。

---

## 五、整理后的"目标接口契约"（建议以此为准）

### 1. 统一响应格式

- 列表：`{ data, total, page, limit }`（已有）
- 详情：对象本身（已有）
- 错误：`{ message }` + HTTP 状态码（已有）
- 头像上传/删除：返回 `User`（已有）

### 2. 字段命名

- 全部 snake_case（`user_id`、`series_id`、`created_at`、`post_count`）
- 内联对象：`author`、`category`、`tags[]`、`series`（详情/系列页返回）
- 公开用户 `UserPublic` **不含 `role`**（已有，保持）

### 3. 权限规则（统一写在一处文档）

| 操作 | 谁能做 |
|---|---|
| 读文章/评论/用户/系列 | 所有人 |
| 写文章 | 登录用户 |
| 改/删文章 | 作者 或 admin |
| 发评论 | 登录用户 |
| 删评论 | 评论作者 或 文章作者 或 admin |
| 上传/删自己头像 | 登录用户 |
| 设精选 | admin |
| 建分类/标签/系列 | admin（**当前无 UI，种子数据代替**） |
| 改用户角色 | admin（**当前无 UI**） |

### 4. `Post` 最终字段

```
id, title, content, user_id,
series_id, series_order,        # 系列归属（可空）
category_id,                    # 分类（可空）
featured,                       # 精选
created_at, updated_at,
author?, category?, tags[]?, series?   # 内联
```

### 5. `Series` 最终字段

```
id, title, slug, description, cover, user_id,
post_count, created_at,
author?
```

---

## 六、建议的整理动作（按顺序）

1. **后端**：确认 `GET /api/series`、`GET /api/series/{slug}` 真的返回 `post_count`、`series` 内联、按 `series_order` 排序；没有就补。
2. **后端**：把 `POST /api/categories`、`POST /api/tags`、`POST /api/series`、`PATCH /api/user/{id}/role` **要么注释掉，要么加 `# 暂无 UI` 注释**，避免"以为有其实没接"的混乱。系列如果要在 UI 建，就补 `POST /api/series` + 建系列表单。
3. **前端 `types/api.ts`**：按上面"最终字段"对齐，`Series`、`Post`、`PostPayload`、`PostListQuery` 一次写全（上轮给过）。
4. **前端页面职责收敛**：
   - `/posts`：**系列区 + 散篇区**，分类/标签筛选**移到散篇区内部**或先砍掉（系列成主轴后，分类 tab 和标签条会让首页过载）；
   - `/series/[slug]`：只用 `GET /api/series/{slug}`，不额外调 `posts?series_id`；
   - `PostEditor`：拆成"基础信息（标题/正文）+ 归属（分类/标签/系列/序号）+ 高级（精选，admin）"三段，避免一个组件 7 个字段平铺。
5. **删死代码**：`PATCH role`、`POST categories/tags` 如果短期不做 admin，先删，减少干扰。

---

## 七、一句话

你现在乱的根源是**接口只加不减、页面职责膨胀**。整理就两步：

1. **接口分三组**（读 / 写 / 管理），管理组暂时冻结或删，别让"有接口没 UI"的假象干扰；
2. **页面职责收敛**：`/posts` 只管"系列入口 + 散篇列表"，分类/标签降级为散篇区内的次级筛选或详情页展示，别再让一个页面背全部维度。

要我先做哪一件？
- **A**：给一份**统一的 `types/api.ts` 完整版**（对齐上面最终字段）；
- **B**：给**后端 `GET /api/series` / `GET /api/series/{slug}` 的确认/补全代码**（含 `post_count`、`series` 内联、排序）；
- **C**：给**`/posts` 页面收敛版**（系列区 + 散篇区，砍掉顶部分类 tab/标签条，或把它们收进散篇区）。

建议顺序 **A → B → C**，先对齐类型，再保证数据对，最后改页面。