# Amo的博客 · 前台（frontend）

个人博客**用户访问端**，Vue 3 + JavaScript + Vite + Vue Router 实现。

## 快速开始

```sh
npm install
npm run dev        # http://localhost:5173
npm run build      # 产物输出到 dist/
npm run lint       # oxlint + eslint
npm run format     # prettier
```

## 开发代理

`vite.config.js` 将 `/common-articles` 代理到后端（默认 `http://127.0.0.1:8000`，可用 `frontend/.env.dev` 的 `VITE_DEV_BACKEND` 覆盖），因此代码内请求使用相对路径，无跨域问题。

## 目录结构

```
src/
  api/          # Axios 封装（request.js）与按模块 API（articles.js）
  assets/       # 全局样式
  components/   # AppHeader 等公共组件
  router/       # 路由与标题守卫
  utils/        # markdown 渲染（marked + DOMPurify 消毒）
  views/        # 首页 / 文章列表 / 文章详情 / 关于 / 404
  config.js     # 站点级常量（SITE_NAME 等）
```

## 与后端约定的响应形态（勿随意改动）

| 场景 | 后端返回 |
| --- | --- |
| 文章列表 | `{ articles: [...] }` |
| 文章详情 | `{ article: {...} }`（含 `context` 正文、`created_at`） |

> 注意：正文字段在后端模型中叫 `context`（拼写与需求文档一致沿用），前端表单与渲染均使用该字段名。
> 站点名称统一从 `src/config.js` 的 `SITE_NAME` 读取，请勿在组件里写死。

## 生产部署提示

路由使用 `createWebHistory`，部署时需在 Web 服务器配置 SPA fallback（如 nginx `try_files $uri $uri/ /index.html;`），并将 `/common-articles` 反向代理到后端。
