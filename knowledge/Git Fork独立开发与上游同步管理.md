---
type: knowledge
knowledge_type: 软件工程
verification: 配置与抓取已验证，合并发布流程待验证
status: draft
created: 2026-11-16
tags:
  - Git
  - fork
  - 软件维护
---

# Git Fork 独立开发与上游同步管理

维护 Fork 时，用 origin 指向自己的仓库，用 upstream 指向原作者；自己的稳定分支保留产品修改，功能分支负责开发，同步分支负责整合上游。上游更新通过 fetch 查看，通过显式 merge 整合。配置、抓取和本地提交已在 OlibTauri 执行，完整上游冲突合并与远程推送尚未验收。

## 为什么选择合并上游

| 方案 | 适用场景 | 取舍 |
| --- | --- | --- |
| merge，推荐 | 长期独立开发、共享分支、自己的改动较多 | 保留双方提交历史；需要处理冲突 |
| rebase | 少量本地补丁、仅个人使用的未共享分支 | 历史更线性；重写提交，后续协作成本较高 |

OlibTauri 已补齐公开兼容客户端，与上游私有依赖存在持续差异，因此选 merge。KISS/YAGNI：沿用标准 Git，不增加自动同步服务；DRY：复用项目验证命令；SOLID：开发、整合与发布分别完成。

## 远程与本地配置

```sh
# 只在尚无 upstream 时执行，地址替换为真实原作者仓库
git remote add upstream https://github.com/shiyi-0x7f/OlibTauri.git
git config remote.pushDefault origin
git config pull.ff only
git remote -v
```

remote.pushDefault 控制默认推送远程，不是禁止推送上游的权限机制；明确指定 git push upstream 仍可能触发上游推送。pull.ff=only 让普通 pull 在历史分叉时停止；它不阻止显式 merge。

本例默认分支名为 master，无需为了统一命名改成 main。复用于其他仓库时，先确认真实默认分支名、远程地址和当前分支跟踪关系。

## 日常开发

先确认 git status，保存现有改动，再切分支。不要 reset、clean 或整份覆盖来处理已有成果。

```sh
git switch master
git switch -c feat/任务名称
# 修改并验证，按独立目的提交
git add 文件路径
git commit -m "说明本次修改"
git switch master
git merge --no-ff feat/任务名称
```

提交代码与研究档案可以分开，方便后续定位冲突与回退。研究原始证据保留字节，不因格式工具提示而批量重排。

## 查看原作者更新

```sh
git fetch upstream --no-tags
git log --oneline master..upstream/master
git diff --stat master...upstream/master
git rev-list --left-right --count master...upstream/master
```

fetch 不合并到当前分支，也不覆盖工作区。log 列出上游尚未进入自己分支的提交；三点 diff 展示共同祖先到上游的变化，不能当成双方当前树的完整差异。rev-list 两个计数依次是本地独有和上游独有提交数。

## 独立分支整合上游

仅在上游有新提交且工作区干净时执行；以下步骤为维护方案，本次未发生实际整合。

```sh
git switch master
git switch -c sync/upstream-YYYYMMDD
git merge upstream/master
# 处理冲突，检查差异，完成项目验证
git switch master
git merge --no-ff sync/upstream-YYYYMMDD
# 确认需要推送时执行
git push origin master
```

冲突要按行为处理，不能统一选择 ours 或 theirs。对 OlibTauri，重点检查 Cargo 私有依赖、API 调用、下载逻辑和 CI；上游可能仍需要私有模块，本地兼容实现不能被直接覆盖。只有目标平台构建与相应测试支持，才能宣称该平台可用。

## 本次项目记录

项目路径：`/Users/peakom/peak/OlibTauri`。

- origin：`git@github.com:pikecode/OlibTauri.git`。
- upstream：`https://github.com/shiyi-0x7f/OlibTauri.git`。
- 抓取时上游 master 与本地原始基线同为 e5754f5，没有新更新需要合并。
- 本地代码提交：92eb8ea；文档与研究归档提交：5614951。
- Rust 单元测试 87 项通过、1 项真实会话诊断忽略；另 1 项 LAN/OPDS 集成测试通过。
- 未推送、未重新打包；研究归档自身存在原有空白格式提示，保留原始字节。

私有模块是基于逆向证据的兼容实现，尚未完整还原。历史 3.4.0 原指令证据、当前 3.5.0 实现、本地模拟测试、真实服务验收必须分开表述。

## 来源与验证边界

- [[runs/2026-11-16-OlibTauri-Fork维护配置与验证]]：本次实际配置、提交与检查证据。
- 项目文档：`/Users/peakom/peak/OlibTauri/docs/fork维护.md`。
- 项目交接：`/Users/peakom/peak/OlibTauri/docs/交接与接续.md`。
- GitHub Fork 元数据：<https://api.github.com/repos/pikecode/OlibTauri>，2026-11-16 查询，parent 为 shiyi-0x7f/OlibTauri。

这是一份经本项目配置与抓取验证的维护知识，不代表合并冲突、远程推送、云端 CI、真实账号与多平台发布均已通过。
