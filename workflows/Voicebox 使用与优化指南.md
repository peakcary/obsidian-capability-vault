# Voicebox 使用与优化指南

本文记录当前机器上已经配置好的 Voicebox 音色、历史文化图片讲解流程、常用调用方式和质量优化方法。

## 快速使用

在对话中直接描述文本、音色和用途即可，例如：

```text
使用 voicebox.speak，用“文博讲解 · 温润女声”读出下面这段文字：
“这件青铜器铸造于西周时期……”
生成时不要改写原文，完成后用 Whisper 核对内容。
```

常用工具：

- `voicebox.list_profiles`：查看可用音色档案。
- `voicebox.speak`：生成、保存并播放音频。
- `voicebox.transcribe`：用本地 Whisper 将音频转回文字，用于检查漏字、错读和多余尾音。

## 已配置音色

| 档案 | 类型 | 引擎/音色 | 推荐用途 |
| --- | --- | --- | --- |
| `我的声音` | 克隆声音 | Qwen TTS 1.7B | 个人声音、短通知 |
| `晓晓 · 温柔女声` | 预设女声 | Kokoro / Xiaoxiao | 日常播报、轻柔旁白 |
| `文博讲解 · 沉稳男声` | 预设男声 | Qwen CustomVoice 1.7B / Uncle Fu | 文物、古迹、纪录片式讲解 |
| `文博讲解 · 温润女声` | 预设女声 | Qwen CustomVoice 1.7B / Serena | 绘画、历史故事、细腻文化讲解 |

档案 ID：

```text
我的声音：064677c1-51ba-4a10-8d33-3525e39d52da
晓晓 · 温柔女声：8fb644fc-bd23-4e95-ab00-2c8cdcb1a160
文博讲解 · 沉稳男声：46f92eb8-609e-453a-89e5-3aad79a275c1
文博讲解 · 温润女声：706048fa-9f1d-40cc-8a8a-f0c0c589939f
```

历史文化图片优先使用：

- 温润、细腻：`文博讲解 · 温润女声`
- 成熟、厚重：`文博讲解 · 沉稳男声`

## 图片讲解工作流

1. 先识别图片中能够确认的对象、材质、纹饰、年代标记和文字信息。
2. 将“图片中直接可见的信息”和“外部历史背景”分开。
3. 核对年代、人名、地名、器物名和生僻字，不确定的信息不要写成确定事实。
4. 将讲解稿改成短句，每句尽量控制在 15 至 35 个汉字。
5. 使用文博讲解音色生成，历史事实类内容设置 `personality: false`，避免模型改写原文。
6. 生成后使用 Whisper 回译核对，再播放或导出。

推荐对话模板：

```text
请分析这张图片，并撰写一段 100 字左右的中文文博讲解稿。
要求：区分可见事实和历史背景；不要编造年代或出处；短句表达；
使用“文博讲解 · 温润女声”生成音频；personality 设为 false；
生成后用 Whisper 核对，不得出现漏字、额外尾音或重复声音。
```

已有讲解稿时：

```text
请保持下面文字完全不变，用“文博讲解 · 沉稳男声”生成音频。
长句需要分句生成，以 200 毫秒静音连接，不使用交叉淡化。
生成后进行转写核对。
```

需要比较男女声时：

```text
请用“文博讲解 · 沉稳男声”和“文博讲解 · 温润女声”分别生成同一段文案，
不要改写原文，生成后依次播放并报告时长。
```

## `voicebox.speak` 参数

典型调用数据：

```json
{
  "text": "画面中的青铜器铸造于西周时期。",
  "profile": "文博讲解 · 温润女声",
  "engine": "qwen_custom_voice",
  "language": "zh",
  "personality": false
}
```

参数说明：

| 参数 | 说明 |
| --- | --- |
| `text` | 要朗读的最终文本 |
| `profile` | 音色档案名称 |
| `engine` | 文博音色使用 `qwen_custom_voice`；晓晓使用 `kokoro` |
| `language` | 中文使用 `zh` |
| `personality` | `false` 保持原文；`true` 允许提示词模型调整表达，可能改写内容 |

历史、法律、医疗、产品参数等要求事实准确的内容，应使用 `personality: false`。

## 长文本与重叠处理

当前生成设置：

```text
max_chunk_chars: 100
crossfade_ms: 0
normalize_audio: true
autoplay_on_generate: true
```

说明：

- 每块最多 100 字，避免模型在长段落末尾继续生成无关声音。
- 交叉淡化为 0，避免相邻音频重叠形成回音。
- 音量标准化已开启。
- 自动播放已开启。

对于重要成品，建议主动按句生成。句间加入 150 至 250 毫秒静音，再顺序拼接。不要使用音频重叠。

通过本地 API 修改参数：

```bash
curl -X PUT http://127.0.0.1:17493/settings/generation \
  -H 'Content-Type: application/json' \
  -d '{
    "max_chunk_chars": 100,
    "crossfade_ms": 0,
    "normalize_audio": true,
    "autoplay_on_generate": true
  }'
```

## 音质优化

### 克隆声音

高质量参考录音应满足：

- 8 至 15 秒连续语音。
- 单人、单次朗读，不重复试音。
- 无背景音乐、回音、风噪和明显环境噪声。
- 头尾只保留少量自然静音。
- 参考文本与音频逐字一致，包括停顿和标点。

参考音频中出现“喂喂”、重复句、残句或错误参考文本，会导致音色漂移、重叠、尾音重复和模型幻觉。

### 文博讲解稿

- 首句说明画面主体，不要先堆叠背景知识。
- 一句话只表达一个事实。
- 年代使用完整说法，例如“公元十一世纪”或“北宋中期”。
- 生僻词适当增加停顿，例如“饕餮纹，不仅体现了……”。
- 数字、缩写和外文名称应先改成适合朗读的形式。
- 保持克制，不使用夸张营销语气。

### `personality` 的使用

当前已安装 Qwen3 0.6B 提示词模型，可使用 `personality: true`。

适合开启：

- 氛围旁白、故事表达、非严格逐字内容。
- 希望增加温柔、沉稳或亲切感。

建议关闭：

- 历史事实、年代、引文和专业术语。
- 文案必须逐字一致的场景。
- 字幕与音频需要严格对齐的场景。

## 质量检查

生成后可直接要求：

```text
请用 voicebox.transcribe 和 Whisper Base 回译刚生成的音频，
将转写与原稿比较，检查漏字、错读、重复尾音和额外内容。
```

注意：Whisper Base 对“饕餮”“铸造”“礼制”等专业词可能输出同音错字。判断时应同时检查句子结构和实际听感，不能只看转写用字。

## 常见问题

| 问题 | 处理方法 |
| --- | --- |
| 有回音或声音重叠 | 设置 `crossfade_ms: 0`；按句生成；用静音连接，不重叠音频 |
| 句尾出现重复音节 | 缩短单次文本；关闭 `personality`；分句生成并转写核对 |
| 历史内容被改写 | 使用 `personality: false`，把最终文案直接传给 `voicebox.speak` |
| 专业词读错 | 增加标点停顿；使用更明确的完整表达；单独生成该句测试 |
| 克隆音色不像本人 | 重新录制 8 至 15 秒干净参考音频，并确保参考文本逐字匹配 |
| 请求一直停在 `generating` | 检查 Voicebox 服务、模型是否下载完成以及代理/CDN连接 |
| 没有声音 | 检查生成状态是否为 `completed`、自动播放设置和系统输出设备 |

## 模型与数据位置

当前已使用的本地模型：

- Qwen TTS 1.7B Base：克隆声音。
- Qwen CustomVoice 1.7B：文博预设男女声。
- Kokoro：轻量预设音色。
- Qwen3 0.6B：`personality` 提示词优化。
- Whisper Base：音频转写和质量检查。

本地数据位置：

```text
Voicebox 数据：~/Library/Application Support/sh.voicebox.app
生成音频：~/Library/Application Support/sh.voicebox.app/generations
声音样本：~/Library/Application Support/sh.voicebox.app/profiles
模型缓存：~/.cache/huggingface/hub
```

不要随意删除模型缓存中的大文件或符号链接，否则 Voicebox 可能重新下载数 GB 模型。

## 创建新预设档案

本地 API 示例：

```bash
curl -X POST http://127.0.0.1:17493/profiles \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "新的讲解音色",
    "description": "用于历史文化讲解",
    "language": "zh",
    "voice_type": "preset",
    "preset_engine": "qwen_custom_voice",
    "preset_voice_id": "Serena",
    "default_engine": "qwen_custom_voice",
    "personality": "使用温润、克制、清晰的纪录片讲解语气。"
  }'
```

创建前先调用 `/profiles/presets/{engine}` 检查音色 ID 是否被 Voicebox 支持。不要只根据模型仓库中的文件名创建档案。

