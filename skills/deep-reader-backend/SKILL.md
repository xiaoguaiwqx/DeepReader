---
name: deep-reader-backend
description: DeepReader 后端开发规范与协作指南。包含 API 设计、数据模型、任务编排、可观测性与交付流程，便于与产品/前端对齐。
---

# DeepReader Backend Skill Guide

面向后端开发与跨角色协作的统一规范。用于需求澄清、接口对齐、数据契约、任务编排与上线检查。

---

## 1. 目标与范围

- 目标: 稳定的论文抓取与摘要服务, 可扩展的 API, 可观测、可测试、可部署。
- 范围: Collector/Storage/Intelligence/Notifier/Server 的设计与实现。
- 不涉及: 前端 UI 细节与用户增长策略。

---

## 2. 架构与模块职责

- Collector: 统一抓取入口, 屏蔽外部 API 差异, 返回标准 `Paper`。
- Storage: 数据落库与查询, 负责 schema 迁移与数据一致性。
- Intelligence: LLM 摘要与关键点抽取, 负责降级策略。
- Notifier: 邮件推送与后续消息通道扩展。
- Server: FastAPI 服务, 提供查询与触发任务的接口。

---

## 3. 设计文档规范 (用于需求对齐)

- 背景与目标: 一句话说明动机与成功指标。
- 需求范围: In/Out of scope。
- 数据契约: 输入/输出字段、类型、必填/可选、示例。
- 关键流程: 顺序图或步骤列表。
- 错误与降级: 失败场景、重试、回退策略。
- 影响评估: DB 变更、API 变更、性能影响。
- 测试策略: 单测/集成/手工验证。

---

## 4. API 设计规范

- 版本: 统一前缀 `/api`，必要时引入 `/api/v1`。
- 分页: `limit` + `offset`，响应包含 `total`。
- 错误: 统一返回 `{"status": "error", "code": "...", "message": "..."}` 与标准 HTTP 状态码。
- 过滤: `topic/start_date/end_date` 等参数可选，避免必填。
- 异步任务: `/api/trigger` 后台任务返回 `accepted`。

示例响应:
```
{
  "items": [...],
  "total": 120,
  "limit": 20,
  "offset": 0
}
```

---

## 5. 项目评审任务记录 (2026-02-06)

- P0: 任务状态追踪系统 (job store, job_id, `/api/jobs/{job_id}` 进度查询)。
- P1: `days` 与 `start_date/end_date` 互斥校验, 冲突时返回 400。
- P2: `/api/trigger` 请求参数重构, 暴露 `max_results`。
- P2: `/api/stats` 统计端点 (总数/最近抓取/分类统计/摘要覆盖率)。
- P2: 查询性能评估与 `published_date` 索引策略。
- P2: topic 查询优先使用 SQLite FTS5, 不可用时回退到 LIKE。

---

## 6. 数据模型与存储规范

- `Paper` 模型字段不可随意删除, 新增字段需写迁移。
- 时间统一 UTC, 持久化为 ISO 格式或 SQLite TIMESTAMP。
- `categories` 使用 JSON 字符串存储, 查询时需注意 LIKE 误匹配。
- 作者表与关联表不可跳过, 便于后期统计与搜索。

---

## 7. 任务编排与调度

- `run_daily_cycle` 作为核心入口, 支持 query/日期范围/主题。
- 失败降级: LLM 失败不应阻断存储与通知。
- 运行模式: CLI 手动触发 + Scheduler 定时。

---

## 8. 可观测性与日志

- 所有关键阶段必须日志化: 抓取、入库、摘要、通知。
- 对外部调用记录耗时与失败原因。
- 后续建议引入结构化日志与 trace id。

---

## 9. 测试与质量

- Collector: 保留集成测试, 需要 API 可用。
- Storage: 使用临时文件数据库。
- Notifier: 使用 mock 验证发送。
- LLM: 仅手工测试, 需要显式 env。

---

## 10. 交付与协作流程

- 需求评审后锁定字段与 API。
- 变更必须更新此文档中的设计规范项。
- 与前端对齐: 提供 OpenAPI 或接口表格。

---

## 11. 常见风险

- SQLite 并发写入受限, 高并发需考虑迁移到 Postgres。
- ArXiv 查询逻辑复杂, 需测试 query 构造。
- LLM 结果不稳定, 需要可回退策略。

