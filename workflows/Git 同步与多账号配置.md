---
type: workflow
workflow: vault-git-sync
status: active
tags:
  - workflow
  - git
  - obsidian
---

# Git 同步与多账号配置

## 当前仓库

| 项目 | 值 |
| --- | --- |
| 分支 | `main` |
| 远程 | `git@github.com-peakcary:peakcary/obsidian-capability-vault.git` |
| 提交作者 | `ompeak <peakcary@163.com>` |
| 认证密钥 | SSH 配置别名 `github.com-peakcary` 指定的密钥 |

远程地址必须使用 SSH 别名 `github.com-peakcary`，不要改回 `github.com`。本机存在多个 GitHub 账号时，别名决定推送使用哪个 SSH 密钥；仓库本地的 `user.name` 和 `user.email` 只决定提交作者。

## 日常同步

开始编辑前：

1. 打开 Obsidian 命令面板。
2. 运行 `Git: Pull`。
3. 确认没有冲突后开始编辑。

完成一批有意义的修改后：

1. 运行 `Git: Commit-and-sync`。
2. 查看通知，确认提交、拉取和推送都成功。
3. 在 GitHub 仓库确认最新提交已经出现。

不要为每个字词修改单独提交。一次提交应对应一项完整的知识整理、能力更新或项目进展。

## 终端操作

在 Vault 根目录执行：

```bash
git status
git pull --rebase
git add -A
git commit -m "docs: 更新能力库"
git push
```

检查当前仓库实际使用的身份和远程：

```bash
git config --local --get user.name
git config --local --get user.email
git remote -v
ssh -T git@github.com-peakcary
```

## 新设备恢复

```bash
git clone git@github.com-peakcary:peakcary/obsidian-capability-vault.git
```

克隆后用 Obsidian 的“打开本地仓库”选择该目录，并确认社区插件处于启用状态。新设备也必须在 `~/.ssh/config` 中配置同名 SSH 别名和对应密钥。

## 冲突处理

- 不要在冲突未处理时继续自动同步。
- 先阅读 Obsidian Git 生成的冲突列表，再逐个合并 Markdown 内容。
- 不确定哪份内容应保留时，同时保留两侧内容并记录待确认项，不要直接覆盖。
- 解决后运行 `git add -A`、`git commit`、`git push`。

## 仓库边界

Git 会保存笔记、模板、能力卡、执行记录和插件配置。`.gitignore` 排除工作区布局、缓存、系统临时文件和 `assets/audio/` 下的生成音频。音频需要长期保存时，应使用对象存储或 Git LFS，并在相关记录中保留地址、生成参数和校验信息。

关联能力：[[capabilities/使用 Git 和 Obsidian Git 同步知识库]]

## 实例：Voicebox 推送账号不匹配（2026-11-18）

Voicebox 远程仓库归属 `pikecode`，但本机 `github.com` 默认 SSH 身份是 `peakcary`。直接推送时提示 `Permission to pikecode/voicebox.git denied to peakcary`。

先检查 `git remote -v` 和已配置的 SSH Host 别名。确认存在 `github.com-pikecode` 后，在 **Voicebox 仓库目录**执行：

```bash
git remote set-url origin git@github.com-pikecode:pikecode/voicebox.git
git push origin main
```

该操作只修改当前仓库的 origin，不修改本 Vault 的远程，也不改变全局 `github.com` 身份。不要为了修复认证失败更改提交作者，或使用强制推送。

成功证据：Voicebox 提交 `16716e8` 已推送，详见 [[runs/2026-11-16 Voicebox 文博工作台与 MLX 加速验证]]。此例说明账号选择方式，不能据此假定新设备已经具备相同 SSH 配置。
