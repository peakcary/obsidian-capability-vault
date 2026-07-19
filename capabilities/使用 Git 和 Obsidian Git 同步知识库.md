---
type: capability
domain: knowledge-management
status: tested
success_count: 1
last_verified: 2026-07-19
tools:
  - git
  - github
  - obsidian-git
triggers:
  - 同步知识库
  - 备份 Obsidian
  - Git 多账号
tags:
  - capability
  - git
  - obsidian
---

# 使用 Git 和 Obsidian Git 同步知识库

## 目标

将 Obsidian 能力库纳入 Git 版本控制，并在本机存在多个 GitHub 账号时稳定选择正确账号。

## 输入

- Obsidian Vault 本地路径
- 已创建的 GitHub 仓库
- 与目标账号对应的 SSH Host 别名
- 仓库级提交作者姓名和邮箱

## 输出

- 跟踪远程 `main` 的本地仓库
- 可通过终端或 Obsidian Git 拉取、提交和推送
- 明确排除设备状态、缓存和大型生成文件

## 执行方法

按 [[workflows/Git 同步与多账号配置]] 操作。关键点是同时固定两类身份：

1. 使用仓库本地 `user.name`、`user.email` 设置提交作者。
2. 在远程 URL 中使用 SSH Host 别名，让 SSH 选择对应账号的密钥。

## 验证

- `git status --branch` 显示 `main` 跟踪 `origin/main`。
- `git remote -v` 显示预期 SSH 别名。
- `git push` 成功，GitHub 能看到最新提交。
- `.obsidian/workspace.json` 和生成音频没有被跟踪。

## 失败模式

- 远程写成 `github.com`：多账号环境可能选错默认密钥。
- 只修改 `user.email`：提交作者改变，但推送账号不会改变。
- 自动同步间隔过短：产生大量低价值提交，并增加多设备冲突概率。
- 把音频直接提交：仓库体积会快速增长，普通 Git 不适合管理大量二进制产物。

## 回退

先关闭 Obsidian Git 自动操作，使用终端运行 `git status`、`git pull --rebase` 和 `git push` 定位问题。认证问题用 `ssh -T git@github.com-peakcary` 单独验证。

执行证据：[[runs/2026-07-19 为知识库接入 GitHub 同步]]
