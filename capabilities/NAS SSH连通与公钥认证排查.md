---
type: capability
capability_id: nas-ssh-diagnostics
domain: infrastructure
status: tested
trigger_phrases: [NAS SSH超时, NAS公钥认证失败, NAS系统巡检]
inputs: [授权主机地址, 登录用户名, 本机网络信息]
outputs: [连通性结论, 认证验证结果, 只读系统状态]
tools: [ssh, nc, route, networksetup]
success_count: 1
last_verified: 2026-10-25
tags: [capability]
---

# NAS SSH连通与公钥认证排查

## 前提与授权
用户授权连接目标 NAS。密码由用户本机输入，私钥不输出、不写入知识库。权限修改应说明用途并由用户执行，考虑共享目录和 ACL 的影响。

## 执行步骤
1. 检查本机地址、掩码及目标路由，用 nc 检查 SSH 端口，用 HTTP 请求辅助验证网络。
2. 超时先查接入网络、路由、隔离策略及服务启用状态；跨子网需要有效双向路由。
3. 网络可达后尝试指定密钥的 BatchMode 登录；失败时查看客户端详细认证信息。
4. 用户本机用密码安装公钥。若仍失败，检查远端实际 HOME、主目录及 .ssh、authorized_keys 的属主、权限和 ACL。
5. .ssh 通常为 700，authorized_keys 为 600；主目录被组或其他用户写入可能触发 StrictModes 拒绝。核实后作最小权限修正，重新验证认证。
6. 只读检查系统版本、uptime、内存、df、lsblk、mdstat、温度及失败服务；明确无权限检查的部分。

## 验证与失败模式
- TCP 成功不等于认证成功，必须执行一条远端只读命令验证。
- 不把单成员 RAID1 视为具备双盘镜像保护。
- Docker 服务在线不等于有权限列出容器；不自行开放 Docker socket 或扩大 sudo 权限。
- 无法确认权限拒绝原因时，由用户检查服务端 SSH 日志，不通过关闭 StrictModes 绕过。

## 证据
- [[runs/2026-10-25-NAS SSH连接与只读巡检]]
