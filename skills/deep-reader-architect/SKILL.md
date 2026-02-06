---
name: deep-reader-architect
description: DeepReader 项目的官方开发指南。包含架构决策、编码规范、开发路线图以及试错记录（坑）。在进行任何代码修改或规划前请查阅此技能。
---

# DeepReader Architect Guide

此 Skill 是 DeepReader (ScholarFlow) 项目的“核心大脑”。它记录了项目的开发规范、当前进度以及至关重要的“试错记录”。

**当你要进行以下操作时，请参考此文档：**
1. 开始一个新的 Feature 开发。
2. 提交代码或 Pull Request。
3. 遇到技术决策困难或奇怪的 Bug。

---

## 1. 🛑 核心规范 (Conventions)

### 代码风格 (Code Style)
- **Python**:
  - 遵循 **PEP 8**。
  - 使用 **Type Hints** (Python 3.10+)。
  - Docstrings 采用 **Google Style**。
  - 使用 `ruff` 或 `black` 进行格式化（如果已配置）。
- **Frontend (Next.js/React)**:
  - 使用 Functional Components 和 Hooks。
  - 使用 TypeScript。

### Git 工作流 (Git Flow)
- **主分支**: `main` (仅限稳定代码)。
- **开发分支**: 从 `main` 切出。
  - 功能: `feature/add-arxiv-collector`
  - 修复: `fix/email-encoding-error`
  - 文档: `docs/update-readme`
- **提交信息 (Commit Messages)**:
  - 格式: `[Module] Type: Description`
  - 类型: `Feat`, `Fix`, `Refactor`, `Docs`, `Chore`
  - 示例: `[Collector] Feat: Add support for filtering by date`

---

## 2. 📅 项目路线图 (Roadmap Status)

**当前阶段**: Phase 1 (MVP) - 核心循环搭建

### Phase 1: The Core Loop (已完成)
- [x] **Environment**: Python 3.10+, 虚拟环境, 目录结构。
- [x] **Collector**: ArXiv API Client (Fetching & Filtering).
  - **增强**: 现在通过 `run_daily_cycle` 中的 `query` 参数和 `/api/trigger` 端点支持基于用户定义关键词的论文获取。
- [x] **Storage**: SQLite Schema (Papers, Authors).
- [x] **Notifier**: 基础 SMTP 邮件发送。
- [x] **Integration**: 每日定时任务脚本。

### Phase 2: Intelligence & UI (进行中)

**目标**: 将项目升级为 Client-Server 架构，集成 LLM 摘要功能，并提供 Web 界面。

**Step 1: Intelligence Engine (智能引擎)**
- [x] **Dependency**: 添加 `google-generativeai` (Gemini) 或 `openai` (Custom/Compatible) 依赖。
- [x] **Schema Update**: 数据库 `papers` 表新增字段:
    - `llm_summary` (TEXT): AI 生成的中文摘要。
    - `key_insights` (JSON/TEXT): 关键点提取。
- [x] **LLM Client**: 实现 `src/deep_reader/intelligence/llm_client.py`。
    - 支持配置 `LLM_PROVIDER` (google/custom)。
    - 支持自定义 `LLM_BASE_URL` 和 `LLM_API_KEY`。
- [x] **Integration**: 更新 `core_loop`，在抓取后自动触发摘要生成。

**Step 2: Backend API (后端服务)**
- [x] **Dependency**: 添加 `fastapi`, `uvicorn`。
- [x] **API Logic**: 实现 `src/deep_reader/server/app.py`。
    - `GET /api/papers`: 获取论文列表（分页、筛选）。
    - `GET /api/papers/{id}`: 获取详情。
    - `POST /api/trigger`: 手动触发抓取任务。

**Step 3: Web Dashboard (前端界面)**
- [x] **Setup**: 初始化 Next.js 项目 (`web/` 目录)。
- [x] **UI Components**: PaperCard, SummaryView, Filters.
- [x] **Integration**: 对接 FastAPI 后端。

### Phase 3: Advanced Features (未来规划)
- [ ] ChromaDB Vector Store (RAG).
- [ ] Chat with Paper.

---

## 3. 🚧 试错记录 (Lessons Learned & Pitfalls)

> **重要**: 每次遇到难以解决的 Bug、配置陷阱或架构失误，解决后**必须**在此处记录，防止重蹈覆辙。

| 日期 | 模块/组件 | 问题描述 (Issue) | 解决方案/预防措施 (Solution) |
| :--- | :--- | :--- | :--- |
| 2026-02-05 | Project Setup | (预留) 初始环境配置可能遇到的依赖冲突 | 建议使用 `venv` 或 `conda` 严格隔离环境，并固定 `requirements.txt` 版本。 |
| 2026-02-05 | Storage/Test | `sqlite3` `:memory:` DB isolation causing "no such table" errors in tests | `sqlite3.connect(":memory:")` creates a fresh DB every time. For tests requiring shared connection logic (like our Manager), use a temp file via `tmp_path` instead. |
| - | - | - | - |

---

## 4. 常用命令备忘 (Cheatsheet)

- **运行测试**: `pytest` (建议)
- **格式化代码**: `ruff check .` (如果安装)
