---
type: run
date: 2026-09-10
status: completed
tags:
  - codex
  - plugin
  - ponytail
---

# 安装 Ponytail Codex 插件

## 请求

查看并安装使用 `DietrichGebert/ponytail`。

## 结果

- Codex `0.154.0`、Node `v22.22.0` 可用。
- `ponytail@ponytail` `4.9.0` 已安装并启用。
- 6 个命令可见：`ponytail`、`ponytail-audit`、`ponytail-debt`、`ponytail-gain`、`ponytail-help`、`ponytail-review`。
- 安装路径：`~/.codex/plugins/cache/ponytail/ponytail/4.9.0`。

## 验证

- 官方仓库 codeload 快照下载成功。
- 项目测试：83 项通过；1 项 CSV 测试因本机缺少 `pandas` 未通过。尝试补装 pandas 时下载无进度，已取消；不影响插件安装。

## 故障与回退

Codex 默认 Git clone GitHub 长时间无响应。改用 GitHub 官方 codeload 下载 `main` 快照，建立临时本地 Git 源，再添加本地 marketplace 并安装，最终插件状态为 `installed, enabled`。
