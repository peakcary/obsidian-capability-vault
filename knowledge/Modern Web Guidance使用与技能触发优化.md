---
type: knowledge
knowledge_type: 开发工具
verification: partially-verified
created: 2026-11-18
updated: 2026-11-18
tags: [knowledge, Codex, skills, frontend]
---

# Modern Web Guidance 使用与技能触发优化

## 项目定位

Modern Web Guidance 是面向 AI 编程助手的现代 Web 实践知识包，包含浏览器 API、性能、无障碍、兼容性等指南。GoogleChrome/modern-web-guidance 是发布仓库；开发实现位于 modern-web-guidance-src。当前本地项目是 pikecode 的 fork。

使用官方 CLI 不需要将 fork 复制到业务项目。维护 fork 更适合团队规范定制与内容贡献。

## 日常使用

直接提出目标即可，例如：“检查这个弹窗的键盘操作和兼容性”“优化首页图片加载”。需要强制使用时说：“使用 Modern Web Guidance，先读取相关指南再实施”。

手动体验：

```bash
DISABLE_TELEMETRY=1 npx -y modern-web-guidance@latest search "confirmation modal dialog"
DISABLE_TELEMETRY=1 npx -y modern-web-guidance@latest retrieve "dialog"
```

仅在需要扫描旧代码时执行（结果需复核）：

```bash
DISABLE_TELEMETRY=1 npx -y modern-web-guidance@latest legacy-scan /目标项目路径
```

环境变量仅关闭当前命令的遥测。CLI 需要联网，不能将它可用等同于技能已安装或自动加载。

## 本机技能分工（2026-11-18 已调整）

| 技能 | 自动触发范围 | 排除范围 |
| --- | --- | --- |
| frontend-design | 页面制作、美化、布局和组件视觉实现 | 纯逻辑、文案替换、性能或兼容性专项 |
| modern-web-guidance | 浏览器 API、兼容性与降级、性能、无障碍、安全相关浏览器能力、旧代码现代化，或具体平台行为疑问 | 普通页面制作、配色、间距、文案、复用既有组件 |
| ui-ux-pro-max | 明确要求 UX 分析、用户旅程、信息架构、设计系统、设计令牌或系统性体验评审 | 普通页面和单组件制作 |

用户点名仍可使用。按实际需求组合，避免仅因任务涉及前端就加载所有技能。Modern Web Guidance 优先读取直接相关指南，不例行读取多个通用学科指南。

该分工应用 KISS/YAGNI：按需要加载；应用 DRY：避免多套设计规则重复介入。它不是禁用技能，也不是自动匹配准确率的保证。

## Token 与维护成本

技能名称和描述有基础上下文开销；完整说明与检索指南按需增加消耗。技能安装数量与实际调用数量不同，不能认为全部内容每次都会加载。没有测量实际 Token 节省。

本机修改的是技能描述和正文；更新或重新安装可能覆盖定制，届时应对照本笔记复核。

## 验证与限制

- CLI 帮助、搜索成功；dialog 指南已获取并完整阅读（220 行、约 12 KB）。
- 官方技能安装成功，后续会话清单已出现 modern-web-guidance。
- 三个技能描述更新后已在当前会话清单显示，说明描述刷新成功。
- 尚未通过独立真实开发任务验证自动匹配准确率、页面效果或 Token 节省。
- 切换 Codex 配置或其他助手后，不保证共享安装；先检查对应会话技能清单。

## 来源与执行证据

- [[runs/2026-11-18-Modern Web Guidance安装与触发规则优化]]
- https://github.com/GoogleChrome/modern-web-guidance
- https://github.com/GoogleChrome/modern-web-guidance-src
- 本地仓库 README、CONTRIBUTING.md、技能入口及本会话命令结果，核验日期 2026-11-18；以上链接为项目来源，未独立联网复核最新页面。
