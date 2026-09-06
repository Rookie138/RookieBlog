# 博客管理端（frontend_manage）

个人博客**管理后台**，Vue 3 + JavaScript + Vite + Vue Router + Pinia 实现。

## 快速开始

```sh
npm install
npm run dev        # http://localhost:5174
npm run build      # 产物输出到 dist/
```

## 开发代理

`vite.config.js` 将 `/auth`、`/manage-articles` 代理到后端（默认 `http://127.0.0.1:8000`，可用 `frontend_manage/.env.dev` 的 `VITE_DEV_BACKEND` 覆盖），请求均走相对路径。

## 目录结构

```
src/
  api/          # request.js（Axios + token 注入 + 401 处理）、auth.js、articles.js
  stores/       # Pinia user store（token/localStorage、登录态）
  utils/        # jwt.js（本地解析 payload/过期判断）、markdown.js
  components/   # AppLayout（侧边栏布局）
  views/        # 登录 / 文章列表 / 写文章&编辑 / 404
```

## 登录契约（与后端对接的关键约定）

- 登录端点：`POST /auth/token`（表单编码 `username` / `password`）。
  端点收敛在 `src/api/auth.js` 的 `LOGIN_ENDPOINT` 常量，后端若改路径只改这一处。
- 响应解析**兼容两种形态**：
  - 扁平：`{ access_token, token_type }`
  - 嵌套：`{ user_info: {...}, token: { access_token, token_type } }`
- 用户信息优先取 `user_info`，否则从 JWT 解码（读取 `username` claim）。
- token 存 `localStorage`（key：`manage_access_token`），请求自动带 `Authorization: Bearer <token>`。
- 任意接口返回 **401** 时：清除 token，整页跳转 `/login?redirect=原路径`（已在登录页时只清 token，不重复跳转）。

## 与后端约定的响应形态

| 场景 | 后端返回 |
| --- | --- |
| 管理列表 | `{ data: [...] }`（不含 `deleted`） |
| 创建 / 更新 / 详情 | `{ article: {...} }` |
| 删除 | `{ ok: true }`（软删除） |

## 生产部署提示

路由使用 `createWebHistory`，部署时需 SPA fallback，并将 `/auth`、`/manage-articles` 反向代理到后端。
