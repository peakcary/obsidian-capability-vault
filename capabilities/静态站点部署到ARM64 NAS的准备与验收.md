---
type: capability
capability_id: static-site-arm64-nas
domain: deployment
status: draft
trigger_phrases: [静态网站部署NAS, ARM64网页部署, 纯前端Docker部署]
inputs: [本机代码, 授权NAS, HTTPS入口]
outputs: [最小部署包, 静态服务, 代理配置, 验收证据]
tools: [Go, Docker Compose, SSH, frp, Nginx, Playwright]
success_count: 0
last_verified: 2026-10-25
tags: [capability, NAS]
---

# 静态站点部署到 ARM64 NAS 的准备与验收

## 步骤
1. 检查页面、数据、外部请求、localStorage、Service Worker 与现有部署脚本，明确是否真正不需要后端。
2. 只打包运行必需资源，排除 .git、凭证、生成批次和截图，保留署名与许可证。
3. 私有部署关闭不需要的外部统计，分享链接跟随部署域名；明确浏览器本地记录不会自动跨设备同步。
4. 使用可交叉编译静态服务或支持目标架构的服务器。认证覆盖页面和数据；拒绝私密路径、目录列表及不需要的写入方法。
5. 数据较大且经家庭上行转发时，预压缩 JSON/JS 等资源，协商 Content-Encoding/Vary；保留未压缩与 q=0 行为。特别检查首次 PWA 预缓存与页面并发下载。
6. 新增独立 NAS 服务与 HTTPS 域名，备份并追加现有 frpc 配置，复用受限回环代理；不要覆盖已运行的其他应用。
7. 临时试运行后验证真实浏览器与离线缓存，再停止测试进程并切换持久容器。sudo 需要交互时，准备完成后提供具体启动命令。

## 验证边界
已验证原生临时进程、公网浏览器、压缩、PWA 与数据隐私配置；实际长期容器待验收，保持 draft。既有测试失败应记录并定位，不应为了宣布部署通过而直接改动测试期望。

## 证据
- [[runs/2026-10-25-知识图谱部署到NAS与HTTPS入口]]
- [[capabilities/通过frp与HTTPS提供NAS应用外网入口]]
