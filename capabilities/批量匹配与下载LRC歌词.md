---
type: capability
capability_id: batch-lrc-download
domain: 本地音乐工具
status: tested
trigger_phrases:
  - 批量下载歌词
  - 为音乐文件夹匹配LRC
inputs:
  - 音乐文件夹
  - 可选输出目录、来源和代理
outputs:
  - 同名UTF-8带时间轴LRC
  - 失败歌曲列表和汇总
tools:
  - Python标准库
success_count: 1
last_verified: 2026-10-16
tags:
  - capability
  - music
---

# 批量匹配与下载LRC歌词

## 能力摘要与前提

使用现有标准库脚本为当前层音频匹配带时间轴歌词；用户需授权处理目标目录。只向来源发送歌手与歌名，不上传音频；API key 不写入知识库。维护入口为 `/Users/peakom/Downloads/download_lyrics.py`，附件为 [[assets/download_lyrics.py]]。

## 执行步骤

1. 阅读 [[knowledge/批量下载音乐歌词脚本]]，确认来源权限、最近验证结果及文件系统限制。
2. 检查目录和文件命名，保留 Live、DJ、语言版本信息；选择默认音频旁保存或 `--output DIR`。
3. 先运行 `/Users/peakom/Downloads/test_download_lyrics.py` 的离线回归，再按需要做少量真实来源验证。
4. 经用户授权后执行批量任务，检查退出码、失败列表与未处理数量。
5. 重跑时跳过已有 LRC；维护脚本后同步附件并校验哈希。

## 验证与失败模式

本次 17 项离线测试及四个来源小样本验证通过；Musixmatch 未做真实权限验证。缺少时间轴、歌手不符或版本不符时换源；429/5xx 有限重试；保存失败不换源反复覆盖；Ctrl+C 后保留已完成结果。硬链接不可用的目标文件系统目前不支持，需先选择 APFS/NTFS 等支持的目录。

## 证据与边界

- [[runs/2026-10-16-歌词下载脚本修复与验证]]
- [[knowledge/批量下载音乐歌词脚本]]

一次成功不代表接口稳定；仅按歌名、歌手匹配，未进行音频时长或声纹校准，不保证全部曲目命中或任意录音版本时间轴一致。
