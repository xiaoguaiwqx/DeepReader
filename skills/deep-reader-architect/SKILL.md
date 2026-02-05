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

### Phase 1: The Core Loop (进行中)
- [ ] **Environment**: Python 3.10+, 虚拟环境, 目录结构。
- [ ] **Collector**: ArXiv API Client (Fetching & Filtering).
- [ ] **Storage**: SQLite Schema (Papers, Authors).
- [ ] **Notifier**: 基础 SMTP 邮件发送。
- [ ] **Integration**: 每日定时任务脚本。

### Phase 2: Intelligence & UI (待定)
- [ ] LLM Summarization (Gemini/OpenAI).
- [ ] Web Dashboard (Next.js).
- [ ] ChromaDB Vector Store.

---

## 3. 🚧 试错记录 (Lessons Learned & Pitfalls)

> **重要**: 每次遇到难以解决的 Bug、配置陷阱或架构失误，解决后**必须**在此处记录，防止重蹈覆辙。

| 日期 | 模块/组件 | 问题描述 (Issue) | 解决方案/预防措施 (Solution) |
| :--- | :--- | :--- | :--- |
| 2026-02-05 | Project Setup | (预留) 初始环境配置可能遇到的依赖冲突 | 建议使用 `venv` 或 `conda` 严格隔离环境，并固定 `requirements.txt` 版本。 |
| - | - | - | - |

---

## 4. 常用命令备忘 (Cheatsheet)

- **运行测试**: `pytest` (建议)
- **格式化代码**: `ruff check .` (如果安装)
