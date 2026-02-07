---
name: deep-reader-frontend
description: DeepReader 前端开发指南。包含 Next.js 最佳实践、组件设计规范、API 集成模式以及 UI/UX 标准。
---

# DeepReader Frontend Guide

此 Skill 专为 DeepReader 的前端开发设计，基于 **Next.js 16 (App Router)** 和 **React 19**。

**当你要进行以下操作时，请参考此文档：**
1. 开发新的前端页面或组件。
2. 对接后端 API。
3. 优化 UI/UX 或重构前端代码。

---

## 1. 🛠️ 技术栈 (Tech Stack)

- **Framework**: [Next.js 16](https://nextjs.org/) (App Router)
- **Library**: [React 19](https://react.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
- **Icons**: (建议) Lucide React or Heroicons
- **State Management**: React Hooks / Context API (暂不需要 Redux/Zustand)

---

## 2. 📂 目录结构 (Directory Structure)

我们遵循 Next.js App Router 的推荐结构，并进行适当的模块化分离：

```text
web/
├── app/                 # Next.js App Router 页面路由
│   ├── layout.tsx       # 全局布局
│   ├── page.tsx         # 首页
│   └── globals.css      # 全局样式
├── components/          # 可复用的 UI 组件
│   ├── common/          # 通用组件 (Button, Input, Card)
│   └── papers/          # 业务相关组件 (PaperCard, PaperList)
├── hooks/               # 自定义 React Hooks
│   └── usePapers.ts     # 示例: 论文数据获取逻辑
├── services/            # API 请求服务层
│   └── api.ts           # 封装 fetch 请求
├── types/               # TypeScript 类型定义
│   └── paper.ts         # 核心数据模型
└── utils/               # 工具函数
    └── date.ts          # 日期格式化
```

---

## 3. 📝 编码规范 (Coding Conventions)

### 组件 (Components)
- **函数式组件**: 必须使用 Functional Components。
- **命名**: PascalCase (e.g., `PaperCard.tsx`).
- **Props**: 必须定义 Interface，并在组件参数中解构。
- **Server vs Client**:
  - 默认优先使用 Server Components (RSC) 进行数据获取。
  - 仅在需要交互 (onClick, useState, useEffect) 时添加 `'use client'` 指令。

```tsx
// 示例: components/papers/PaperCard.tsx
import { Paper } from '@/types/paper';

interface PaperCardProps {
  paper: Paper;
  onBookmark?: (id: string) => void;
}

export function PaperCard({ paper, onBookmark }: PaperCardProps) {
  return (
    <div className="border p-4 rounded-lg">
      <h2 className="text-xl font-bold">{paper.title}</h2>
      {/* ... */}
    </div>
  );
}
```

### 数据获取与 API (Data Fetching)
- **Service Layer**: 所有的 API 请求**不要**直接写在组件里，必须封装在 `services/` 目录中。
- **Environment Variables**: API Base URL 应从 `process.env.NEXT_PUBLIC_API_URL` 读取。

```ts
// 示例: services/paperService.ts
import { Paper, PaperListResponse } from '@/types/paper';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchPapers(params: Record<string, string>): Promise<PaperListResponse> {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_URL}/papers?${query}`);
  if (!res.ok) throw new Error('Failed to fetch papers');
  return res.json();
}
```

### 样式 (Styling)
- **Tailwind First**: 优先使用 Utility Classes。
- **一致性**: 遵循项目现有的颜色和间距系统。
  - Primary Color: Indigo (`bg-indigo-600`, `text-indigo-600`)
  - Background: Gray 50 (`bg-gray-50`)
  - Card: White (`bg-white`)

---

## 4. 🚀 开发流程 (Workflow)

1. **理解需求**: 阅读 `README.md` 和后端 API 文档（或代码）。
2. **定义类型**: 在 `web/types/` 中更新或创建 TypeScript 接口，确保与后端 Pydantic 模型一致。
3. **实现 Service**: 在 `web/services/` 中添加 API 方法。
4. **开发组件**: 创建 UI 组件，使用 Mock 数据先行调试（可选）。
5. **集成页面**: 在 `app/` 页面中组合组件并调用 Service。
6. **Lint & Build**: 运行 `npm run lint` 和 `npm run build` 确保无报错。

---

## 5. 📅 前端开发计划与路线图 (Development Plan & Roadmap)

**Objective**: 将“抓取”与“浏览”逻辑彻底解耦，通过任务追踪改善用户反馈，并提升阅读体验。

### Phase 1: 架构与职责分离 (Architecture & Separation) - **Priority P0**
**Goal**: 解决 `page.tsx` 中的职责混乱问题。
- [x] **Refactor**: 将 `page.tsx` 拆分为 `DashboardLayout`，包含两个独立区域：
    - **Main Area**: 论文列表与浏览筛选。
    - **Sidebar/Drawer**: “抓取控制中心”（初始隐藏或可折叠）。
- [x] **Component**: 创建 `BrowseFilterBar` 用于本地搜索（主题、日期范围）。
- [x] **Component**: 创建 `FetchPanel` 用于 ArXiv 抓取（分类、日期/天数、关键词）。
- [x] **State**: 实现“浏览”与“抓取”表单的独立状态管理。
- [x] **UX**: 将 "Days to Fetch" 严格移至 `FetchPanel`，并实现互斥逻辑（日期范围 vs 天数）。

### Phase 2: 导航与体验优化 (Navigation & Experience) - **Priority P1/P2**
**Goal**: 提升列表的导航性和可读性。
- [x] **Pagination**: 利用 `GET /api/papers` 返回的 `total` 和 `offset` 字段实现完整分页控件。
    - 显示: "Showing 1-20 of 145 papers".
    - 控件: 上一页 / 下一页 / 跳转。
- [x] **PaperCard**: 实现 AI 摘要的“展开/折叠”功能，减少视觉干扰。
- [x] **Loading States**: 将论文列表的简单 Spinner 替换为 Skeleton Screen（骨架屏）。

### Phase 3: 异步任务集成 (Async Task Integration) - **Priority P0**
**Goal**: 为长时间运行的抓取任务提供实时反馈（依赖后端支持）。
- [x] **Service**: 更新 `api.ts` 处理 `POST /api/trigger` 返回的新 `job_id`（初期可 Mock）。
- [x] **Polling**: 实现 `useJobStatus(jobId)` Hook 轮询 `GET /api/jobs/{jobId}`。
- [x] **UI**: 在顶部或抓取面板添加全局“任务状态横幅”或“进度条”。
- [x] **Auto-Refresh**: 任务状态变为 `completed` 时自动触发列表刷新。

### Phase 4: 完善与标准化 (Polish & Standardization)
**Goal**: 健壮的错误处理与配置。
- [x] **Error Handling**: 将 `alert()` 替换为 Toast 通知系统 (e.g., `sonner` or `react-hot-toast`)。
- [x] **Dynamic Configuration**: 从后端获取可用的 ArXiv 分类列表，替代硬编码（等待后端接口）。

---

## 6. 🎨 UI/UX 优化建议 (Current Focus)

- **Loading States**: 所有异步操作（加载列表、触发抓取）必须有明确的 Loading 指示器。
- **Error Handling**: API 请求失败时，必须在 UI 上给予用户友好的提示（Toast 或 Error Message）。
- **Responsive**: 确保在移动端和桌面端都有良好的显示效果。
- **Filters**: 搜索和筛选栏应清晰易用。
