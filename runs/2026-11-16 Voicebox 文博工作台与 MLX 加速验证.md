---
type: run
date: 2026-11-16
capability: "[[capabilities/生成并质检历史文化图片讲解音频]]"
result: success
reusable: true
validation: partial
tags:
  - run
  - voicebox
  - mlx
---

# 2026-11-16 Voicebox 文博工作台与 MLX 加速验证

## 请求与范围

基于现有 Voicebox 实现文博配音工作台，改善生成等待、分句、恢复和导出体验，并验证 Apple Silicon 加速。

## 环境与前提

- Mac mini，Apple M4，24 GB 内存。
- 源码：`/Users/ompeak/work/peak/voicebox`。
- 前端开发地址：`http://127.0.0.1:5173/narration`；后端：`http://127.0.0.1:17493`。
- Python 3.12 独立环境：`~/.local/share/voicebox-dev/python`。
- 数据沿用 `~/Library/Application Support/sh.voicebox.app`。
- 以上是开发服务地址，不代表开机自启或正式发布；停止后需要重新启动。

## 执行摘要

- 增加参考图片、资料来源、最终稿审核、音色选择与快捷试稿模式。
- 显式传入音色要求的引擎，修复预设音色被默认 `qwen` 拒绝的问题。
- 按标点优先分句，默认每块最多 80 个 Unicode 字符，超长无标点片段才硬切。
- 支持可选转写、单句修改与重生成、进度保存、继续任务、停止等待及完整 WAV 导出。
- CustomVoice 原 PyTorch 设备选择未启用 MPS；新增 MLX 后端，复用原 Qwen 权重，通过专用单线程执行器执行 Metal 操作。
- 源码服务先在 17494 验证，再替换 17493 的打包后端。

## 结果与产物

- [[workflows/Voicebox 使用与优化指南]]
- [[capabilities/生成并质检历史文化图片讲解音频]]
- 实现：`app/src/components/NarrationTab/`、`backend/backends/qwen_custom_voice_mlx_backend.py` 和引擎路由。
- 本次使用同一段中文：“这件青铜器造型庄重，纹饰清晰，展现了古代工匠的精湛技艺。”

## 验证

| 路径 | 首次请求 | 后续请求 | 说明 |
| --- | ---: | ---: | --- |
| 原后端 Kokoro | 23.59 秒 | 2.05 秒 | 音频约 6.2 秒 |
| 原后端 CustomVoice 1.7B | 28.95 秒 | 30.47 秒 | 音频约 5.8–6.2 秒 |
| 独立 MLX 调用 | 推理 11.19 秒 | 推理 7.84 秒 | 模型加载另约 4.74 秒 |
| 源码 MLX HTTP 接口 | 34.34 秒 | 8.64 秒 | 包含加载/请求开销；音频分别约 8.64、5.84 秒 |

测速不包含 Whisper 转写；生成未固定随机种子，音频时长不同，不能作为严格模型质量或吞吐基准。首次请求不保证完全冷缓存。

- 源码接口验证 CustomVoice、Kokoro 生成完成，生成音频可读取。
- Whisper Base 转写接口成功，但出现同音错字及繁体输出；不能据此判定音频逐字正确。
- `test_qwen_runaway_retry.py`：7 项通过。该测试不等于新增 MLX 后端的完整覆盖。
- TypeScript 检查、网页构建、WAV 头/PCM 样本/200 毫秒静音与分句内容保留检查通过。
- 服务切换后健康接口正常、工作台页面返回 200。
- 浏览器完整交互、最终拼接下载和人工听感尚未完成端到端验收。

## 问题与失败

- PyPI 域名解析超时；改用阿里云镜像安装独立环境依赖。
- 初次运行异步测试缺少 pytest-asyncio；安装后 7 项通过。
- 全局健康信息中的 MLX/MPS 不等于每个引擎都用 GPU，应检查引擎实例和实际推理路径。
- 临时测速 JSON、音频和数据库备份存于 `/tmp`，可能被清理；核心数据仍在应用数据目录，临时文件不是长期证据归档。

## 可复用经验

- 快速试稿使用 Kokoro，正式中文讲解使用 CustomVoice；转写可在成稿后补做。
- 失败重试应保留 generation ID，先检查原任务，避免重复配音。
- 严格事实稿使用 `personality: false`，生成后仍需人工试听。

## 后续动作

- [ ] 完成浏览器端编辑、恢复、下载和音频试听验收。
- [ ] 验证长稿、并发加载/卸载、0.6B 及其他平台回归。
- [ ] 完善可重复的依赖安装与服务启动流程；当前独立环境并非完整引擎依赖集。
- [ ] 正式发布前更新打包配置并验证冻结构建；已安装桌面应用不会自动获得源码改动。
