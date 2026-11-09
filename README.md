# 比赛队招募 · 校园招募平台

校园内的比赛队友招募平台：学生用「学号 + 姓名」登录发布招募 / 找队伍，管理员在后台查看运营数据、管理用户与帖子。
界面按设计稿（左侧栏 + 内容区）实现，前端 Vue 3 + Vite，后端 FastAPI + SQLite。

## 目录结构

```
backend/                  FastAPI 服务
  main.py                 入口（建表 / 迁移 / 种子管理员 / 挂载路由）
  models.py               数据模型：User / Post / Token / Admin / Favorite
  schemas.py              入参校验 + 富文本白名单净化
  routes_user.py          注册 / 登录 / 退出 / 当前用户
  routes_post.py          招募帖 CRUD、下架、重新发布、招满、收藏
  routes_stats.py         首页统计概览
  routes_admin.py         管理后台：统计、用户、帖子
  run_tests.py            79 项接口集成测试
  _seed.py                演示数据（可重复执行，会清空 posts / favorites）
  _clean.py               清掉测试账号，跑测试前使用
frontend/                 Vue 3 + Vite 前端
  src/views/              页面（首页 / 招募广场 / 详情 / 发布 / 我的发布 / 收藏 / 登录 / 后台）
  src/components/         通用组件（侧栏、顶栏、图表、富文本编辑器等）
  scripts/shots.mjs       开发用：headless Chrome 逐页截图
  scripts/probe.mjs       开发用：在页面里执行 JS 做样式探针
```

## 启动

后端（默认 8000）：

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

前端（默认 5173，已配置 `/api` 代理到 8000）：

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 （Vite 监听 IPv6，请用 localhost 而非 127.0.0.1）。

## 账号

- 学生：直接输入学号 + 姓名即可登录 / 注册，无需密码。演示数据里可用 `2024413435 / 韩涛`。
- 管理员：`admin / admin123`，入口在登录页右下角「管理员入口」，或直接访问 `/admin/login`。

## 常用命令

```bash
# 重置演示数据（清空招募帖与收藏，重建 4 个演示用户 + 6 条招募）
cd backend && python _seed.py

# 跑接口测试（会创建测试账号，跑完可用 _clean.py 清理）
cd backend && python run_tests.py

# 前端生产构建
cd frontend && npm run build

# 逐页截图（需先启动 dev server 与 headless Chrome，端口 9222）
cd frontend && node scripts/shots.mjs ../.shots
```

## 功能

**学生端**

- 首页：统计概览、最新招募、快捷入口
- 招募广场：按类型筛选（找队友 / 找队伍）、关键词搜索
- 招募详情：倒计时、封面、富文本说明、联系方式打码与一键复制、收藏
- 发布 / 编辑：类型、名称、富文本描述（加粗 / 斜体 / 下划线 / 插图）、需求人数、联系方式、截止日期、封面上传
- 我的发布：状态筛选、编辑、下架、重新发布、招满、删除
- 我的收藏

**管理端**

- 数据概览：近 7 / 30 / 90 天，注册用户 / 发布招募 / 参与人数 / 成功率环比，发布趋势折线图与状态分布环形图
- 用户管理：搜索、状态筛选、分页、改姓名、禁用 / 启用
- 帖子管理：搜索、类型 / 状态筛选、下架违规招募

## 说明

- 招募帖 30 天自动过期（读取时按 `created_at` 计算，不落库）。
- 联系方式仅登录用户可见；未登录时接口直接返回 `contact: null`。
- 富文本描述在服务端做白名单净化：仅保留 `b / i / u / br` 与本站上传的 `img`（`src` 必须是 `/api/uploads/...`），其余标签与属性全部丢弃。
- 上传限制：jpg / png / webp / gif，单张 ≤ 2MB。
