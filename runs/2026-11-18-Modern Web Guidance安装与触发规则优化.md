---
type: run
date: 2026-11-18
result: success
reusable: true
validation: partial
tags: [run, skills, frontend]
---

# Modern Web Guidance 安装与触发规则优化

## 请求与范围

分析 fork 项目、体验指南检索、安装技能，并减少前端技能重复触发；按用户要求沉淀至 Obsidian。

## 执行与产物

- CLI 帮助和 search 成功，retrieve dialog 成功并读取完整指南。
- 使用官方 skill-installer 从 GoogleChrome/modern-web-guidance 安装技能。
- 调整 frontend-design、modern-web-guidance、ui-ux-pro-max 的描述及正文边界；保留指南内容与自动发现。
- 修改前备份至本机临时目录（临时备份不作为持久恢复保证）。
- [[knowledge/Modern Web Guidance使用与技能触发优化]] 记录最终规则及命令。

## 验证

技能文件基础结构检查通过；后续会话技能清单已显示安装项及三项更新后的中文描述。业务代码未修改，未运行浏览器测试或实际 Token 对比。

## 失败教训与限制

最初仅验证 CLI，不能据此声称技能已安装。应分别验证 CLI、技能发现和实际任务执行。技能更新可能覆盖本机触发定制。

## 后续

- 在真实前端任务中观察触发是否符合分工，再根据证据调整；不批量增加技能。
