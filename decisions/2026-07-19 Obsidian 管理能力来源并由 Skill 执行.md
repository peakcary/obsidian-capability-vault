---
type: decision
date: 2026-07-19
status: accepted
domain: knowledge-and-automation
tags:
  - decision
  - knowledge-management
---

# Obsidian 管理能力来源并由 Skill 执行

## 背景

需要同时保存任务证据、领域知识、决策理由和可复用执行流程，并让 Codex 能快速调用成熟能力。

## 决策

使用 Obsidian 作为能力来源、证据和审计层；使用 Codex Skill 作为成熟能力的精炼执行包。能力未达到晋级门槛前只保存在 Obsidian，不提前创建 Skill。

## 备选方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 所有内容只放 Obsidian | 易查看和编辑 | 执行指令不一定自动触发，内容容易过长 |
| 所有流程直接做 Skill | 调用方便 | 未验证流程会污染能力；缺少执行证据和决策历史 |
| Obsidian + Skill 分层 | 证据完整，执行精炼 | 需要维护晋级与同步规则 |

## 原因

- Obsidian 适合 Markdown、双向链接、属性和查询。
- Skill 需要简洁、明确触发、可验证，不能承载全部历史。
- 分层能够避免把未经验证的笔记直接当作执行规则。

## 后果

- 每项成熟 Skill 必须链接对应能力卡和验证记录。
- Obsidian 与 Skill 不复制相同长文，只共享必要引用和路径。
- 创建 Skill 前必须确认安装位置并运行官方验证工具。
