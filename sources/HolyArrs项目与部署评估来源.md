---
type: source
created: 2026-11-18
accessed: 2026-11-17
verification: 本地源码静态阅读与官方文档检索，未实机部署
tags: [source, HolyArrs, NAS]
---

# HolyArrs 项目与部署评估来源

## 本地项目

路径：`/Users/ompeak/work/peak/HolyArrs`。2026-11-17 阅读 README、go.mod、前端 package.json、入口与装配代码、Dockerfile，以及 docs/dev 下 architecture、modules、setup、testing。未固定源码提交号，后续复用须按实际版本重新核对。

- [项目说明](/Users/ompeak/work/peak/HolyArrs/README.md)
- [架构说明](/Users/ompeak/work/peak/HolyArrs/docs/dev/architecture.md)
- [模块边界](/Users/ompeak/work/peak/HolyArrs/docs/dev/modules.md)
- [构建运行](/Users/ompeak/work/peak/HolyArrs/docs/dev/setup.md)
- [Dockerfile](/Users/ompeak/work/peak/HolyArrs/deploy/Dockerfile)

## 官方在线来源

2026-11-17 检索官方文档；以下为后续核对入口，未进行下载器兼容实测。

- [Downloaders](https://docs.holyarrs.com/downloads/downloaders/)：外部下载器要求与路径映射。
- [Architecture](https://docs.holyarrs.com/dev/architecture/)：单程序、数据库和外部服务关系。
- [Environment variables](https://docs.holyarrs.com/reference/env-vars/)：部署配置与元数据服务参数。

## NAS 环境依据

- [[knowledge/NAS个人应用平台建设全流程与知识总览]]：历史硬件、系统及部署条件。
- [[projects/NAS个人应用平台建设]]：项目待办与未验收事项。
- [[runs/2026-11-11-家庭媒体中心HTTPS与Docker交付]]：截至 2026-11-15 的相关部署增量。

汇总分析：[[knowledge/HolyArrs项目架构与绿联NAS部署价值评估]]。
