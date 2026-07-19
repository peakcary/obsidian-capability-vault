---
type: capability
capability_id: manage-reusable-ai-capabilities
domain: knowledge-and-automation
status: stable
trigger_phrases:
  - 沉淀这次能力
  - 复用之前的做法
  - 建立能力知识库
  - 把成熟流程做成 Skill
inputs:
  - 已完成任务的请求、结果、验证和产物
outputs:
  - 执行记录
  - 能力卡
  - 决策记录
  - Skill 候选
tools:
  - Obsidian
  - Dataview
  - Templater
  - Codex Skills
success_count: 2
last_verified: 2026-07-19
skill_path:
tags:
  - capability
  - knowledge-management
---

# 管理并沉淀可复用 AI 能力

## 能力摘要

从一次非简单任务中提取可复用方法、执行证据、决策和知识，并按成熟度管理；稳定且高频的能力再转为 Codex Skill。

## 适用范围

- 新工具或 API 接入
- 重复性故障处理
- 多步骤交付流程
- 用户明确要求保存和复用的方法
- 已验证流程的 Skill 化

## 执行

1. 阅读 [[workflows/能力沉淀与复用流程]]。
2. 按 [[workflows/新能力接入与维护指南]] 完成接入检查清单。
3. 判断是否满足沉淀条件，过滤简单问答和敏感数据。
4. 使用 [[templates/执行记录模板]] 保存实际结果与验证。
5. 搜索现有能力卡，选择更新或新建。
6. 将事实、来源、决策和项目分别归档，不全部塞入能力卡。
7. 更新成功次数、最近验证日期、失败模式和成熟度。
8. 达到 `skill-candidate` 后，确认安装位置并使用 `skill-creator`。

## 验证

- Frontmatter 可解析。
- 能力卡至少链接一个执行记录或来源。
- 输入、输出、工具、验证和失败模式明确。
- 没有密码、令牌、私人原始数据和无用日志。
- Skill 状态必须有验证过的实际 Skill 路径。

## 失败模式

| 失败模式 | 识别方式 | 回退方案 |
| --- | --- | --- |
| 所有任务都记录，形成噪音 | 大量无关联、无复用价值记录 | 只保留满足沉淀条件的任务 |
| 未验证流程被标记为稳定 | 没有 run 或验证结果 | 降级到 `draft` 或 `tested` |
| 知识和流程混在一起 | 能力卡包含大量领域事实 | 拆到 `knowledge/` 和 `sources/` |
| Skill 与 Obsidian 重复维护 | 两处保存相同长文 | Obsidian保留证据，Skill仅保留执行必需内容 |
| 敏感信息进入 Vault | 出现令牌、账号或私人原始数据 | 立即移除并审查相关历史 |

## 证据

- [[runs/2026-07-19 建立通用 AI 能力资产库]]
- [[runs/2026-07-19 新能力维护流程文档化]]
- [[decisions/2026-07-19 Obsidian 管理能力来源并由 Skill 执行]]
