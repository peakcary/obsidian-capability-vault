---
type: capability
capability_id: nas-frp-https
domain: deployment
status: draft
trigger_phrases: [NAS外网访问, frp部署, 云服务器转发NAS]
inputs: [授权的云服务器连接配置, NAS应用端口, 域名与DNS]
outputs: [frps服务, frpc部署包, HTTPS入口, 验证结果]
tools: [SSH, Paramiko, frp, Nginx, Certbot, Docker Compose]
success_count: 0
last_verified: 2026-10-25
tags: [capability, frp, NAS]
---

# 通过 frp 与 HTTPS 提供 NAS 应用外网入口

## 交付目标与验证边界

通过自有公网云服务器，为 NAS 的网页应用提供带 HTTPS 和登录认证的外网入口。家中 NAS 主动连接云服务器。

本次已完成云端部署，并用 NAS 临时 frpc 进程验证公网播放与跳转。临时进程已停止；尚未收到用户确认长期 frpc 容器启动的结果，未验收客户端容器持续运行或重启恢复。因此保持 draft，不能视为整套持久化部署已完成。

## 前提与输入

- 用户授权连接云服务器及 NAS，已有应用在内网可用且有登录机制。
- 云端可使用 Nginx、Certbot、systemd，具备配置服务与防火墙的权限。
- 应用域名解析指向云服务器；检查是否已有同名站点。
- 盘点已有端口、站点、证书和架构。本次云端 AMD64，NAS ARM64。
- 从用户指定凭证文件读取配置，不打印密码、令牌和私钥；sudo 密码由用户本机输入。

## 一、规划链路与端口

```text
外网浏览器（HTTPS）
  → 云服务器 Nginx :443
  → 云服务器 127.0.0.1:19866
  → frps ⇄ frpc（主动连接、TLS、独立 token）
  → NAS 局域网地址:9866
  → 应用与只读音乐目录
```

| 用途 | 本次值 | 说明 |
| --- | --- | --- |
| frps 控制端口 | TCP 7000 | NAS 主动连接；主机防火墙和云安全组路径需可达 |
| 云端业务映射 | 127.0.0.1:19866 | 只允许服务器本机反向代理访问 |
| NAS 应用 | NAS_IP:9866 | 使用实际监听地址，不假设绑定回环 |
| 公网入口 | 应用域名:443 | HTTPS，保留应用登录 |
| 后续预留 | 19867 | 仅预留服务器允许范围；不表示看板已部署 |

## 二、准备并验证 frp 程序

本次采用官方 frp 0.71.1，版本与校验时间为 2026-10-25；后续复用应重新确认维护版本。

1. 分别下载 Linux AMD64 与 ARM64 发布包。
2. 对照官方 SHA-256 校验后提取 frps、frpc。
3. 使用同一版本两端程序，上传前确认架构与执行权限。

本次使用的校验值：

```text
frp_0.71.1_linux_amd64.tar.gz
1d9875210972a5d1a62b2dc4c48df45ab0af05d3ca1b5e494a014428259df803

frp_0.71.1_linux_arm64.tar.gz
8edf590b0c396fa42f9c147121a76af83cfc2002b08f5aef0ea1008c43482019
```

校验命令：`shasum -a 256 <安装包>`。下载遇到网络问题时可以显式指定可信的本机代理，但仍要执行校验。

## 三、准备独立令牌和隧道证书

令牌只生成一次，两端使用相同内容；存入受限权限文件，不写进笔记或代码。以下在受控部署目录中执行：

```sh
umask 077
openssl rand -hex 48 > token
openssl req -x509 -newkey ed25519 -nodes \
  -keyout server.key -out server.crt -days 730 \
  -subj '/CN=frps.nas.internal' \
  -addext 'subjectAltName=DNS:frps.nas.internal' \
  -addext 'basicConstraints=critical,CA:TRUE'
```

云端保存 token、server.key、server.crt。NAS 仅接收 token 和公开 server.crt，不需要服务端私钥。客户端校验名与证书 SAN 必须一致。

## 四、部署云服务器 frps

目录：

```text
/usr/local/lib/frp-nas/frps
/etc/frp-nas/frps.toml
/etc/frp-nas/token
/etc/frp-nas/server.crt
/etc/frp-nas/server.key
/etc/systemd/system/frps-nas.service
```

`frps.toml` 示例：

```toml
bindAddr = "0.0.0.0"
bindPort = 7000
proxyBindAddr = "127.0.0.1"
allowPorts = [{ single = 19866 }, { single = 19867 }]
maxPortsPerClient = 2

auth.method = "token"
auth.additionalScopes = ["HeartBeats", "NewWorkConns"]
auth.tokenSource.type = "file"
auth.tokenSource.file.path = "/etc/frp-nas/token"

transport.tls.force = true
transport.tls.certFile = "/etc/frp-nas/server.crt"
transport.tls.keyFile = "/etc/frp-nas/server.key"

log.to = "console"
log.level = "info"
log.disablePrintColor = true
```

创建独立系统用户 frp-nas；配置目录可用 root:frp-nas、750，token、key 与配置为 640，公开证书为 644。frps 不以 root 运行。

systemd 服务：

```ini
[Unit]
Description=FRP server for NAS applications
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=frp-nas
Group=frp-nas
ExecStart=/usr/local/lib/frp-nas/frps -c /etc/frp-nas/frps.toml
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
UMask=0077
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

验证并启动：

```sh
/usr/local/lib/frp-nas/frps verify -c /etc/frp-nas/frps.toml
systemctl daemon-reload
systemctl enable --now frps-nas.service
systemctl is-active frps-nas.service
```

放行实际使用的 TCP 控制端口，并确认云安全组；业务端口无需开放公网。本次使用 UFW 放行 7000/tcp，公网 80/443 已有规则。

## 五、部署 NAS frpc

```text
/volume1/docker/frpc/
├── Dockerfile
├── compose.yaml
├── bin/frpc
└── config/
    ├── frpc.toml
    ├── token
    └── server.crt
```

`frpc.toml` 示例，替换 CLOUD_PUBLIC_IP 与 NAS_IP：

```toml
serverAddr = "CLOUD_PUBLIC_IP"
serverPort = 7000
loginFailExit = false

auth.method = "token"
auth.additionalScopes = ["HeartBeats", "NewWorkConns"]
auth.tokenSource.type = "file"
auth.tokenSource.file.path = "/etc/frp/token"

transport.tls.enable = true
transport.tls.trustedCaFile = "/etc/frp/server.crt"
transport.tls.serverName = "frps.nas.internal"

log.to = "console"
log.level = "info"
log.disablePrintColor = true

[[proxies]]
name = "verse-music"
type = "tcp"
localIP = "NAS_IP"
localPort = 9866
remotePort = 19866
```

Dockerfile，使用已经下载校验过的静态 ARM64 程序，NAS 构建无需下载基础镜像：

```dockerfile
FROM scratch
COPY bin/frpc /frpc
USER 1000:10
ENTRYPOINT ["/frpc", "-c", "/etc/frp/frpc.toml"]
```

Compose：

```yaml
services:
  frpc:
    build: .
    image: peak-frpc:0.71.1-arm64
    container_name: peak-frpc
    user: "1000:10"
    network_mode: host
    volumes:
      - ./config:/etc/frp:ro
    restart: unless-stopped
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
```

UID/GID 使用本次目标设备的值，迁移设备前重新检查。配置目录为 700、敏感文件为 600，确保运行用户可读。通过 `.dockerignore` 将 config 排除出镜像构建上下文，只包含 Dockerfile 与 bin/frpc；配置始终通过卷挂载。

在 NAS 终端执行：

```sh
cd /volume1/docker/frpc
sudo docker compose config --quiet
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs --tail=30
```

从本次 Mac 连接执行的命令：

```sh
ssh -t -i ~/.ssh/ugreen_peak_ed25519 peak@192.168.31.48 \
  'cd /volume1/docker/frpc && sudo docker compose up -d --build'
```

提示 sudo 密码时输入 NAS 的用户密码；它不是播放器密码，也不是云服务器密码。

## 六、配置 Nginx 与公网 HTTPS

1. 检查应用域名的公网解析指向目标云服务器。
2. 新建独立站点与 ACME webroot，保留已有站点。
3. 先使用 HTTP challenge 配置，`nginx -t` 成功后 reload。
4. 使用现有 Certbot 账户获取域名证书，例如：

```sh
certbot certonly --webroot -w /var/www/frp-nas-acme \
  -d APP_DOMAIN --non-interactive --keep-until-expiring
```

5. 证书生成后启用 HTTPS 站点，示例中 APP_DOMAIN 均替换为实际域名：

```nginx
server {
    listen 80;
    server_name APP_DOMAIN;
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/frp-nas-acme;
    }
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 443 ssl;
    server_name APP_DOMAIN;
    ssl_certificate /etc/letsencrypt/live/APP_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/APP_DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    client_max_body_size 2m;

    location / {
        proxy_pass http://127.0.0.1:19866;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
```

保持 Host 与网页 Origin 一致，保留应用的 Authorization 认证头；支持媒体 Range。启用站点前后均执行 `nginx -t`，成功后才 reload。

确认 Certbot 的续期计划，并在成功续期后校验和 reload Nginx。公网证书与 frp 自建隧道证书是两套生命周期；后者不由 Certbot 自动更新，需在到期前协调服务端证书及客户端信任更新。

## 七、分层验收

| 层级 | 检查 | 通过标准 |
| --- | --- | --- |
| 内网应用 | NAS 原地址访问 | 登录、API、音频均可用 |
| 控制通道 | frpc 日志 | TLS 登录成功、代理注册成功 |
| 云端映射 | 回环端口请求 | 19866 监听在回环，未认证请求得到应用 401 |
| 公网证书 | HTTPS 访问 | 证书可信且域名匹配 |
| 用户认证 | 不登录与登录分别访问 | 未认证拒绝，登录后成功 |
| API | 前端实际发起请求 | 无 Origin/Host 拒绝 |
| 媒体 | Range 请求和浏览器播放 | 206、实际播放和进度跳转成功 |
| 持久化 | 停止临时进程后检查容器 | frpc 容器持续运行；需另外验证重启恢复 |

不要只因端口可连就宣布部署完成，也不能用临时进程结果代替持久化验收。

## 八、维护与故障排查

云服务器：

```sh
systemctl status frps-nas --no-pager
journalctl -u frps-nas -n 30 --no-pager
nginx -t
ss -ltn '( sport = :7000 or sport = :19866 )'
```

NAS：

```sh
cd /volume1/docker/frpc
sudo docker compose ps
sudo docker compose logs --tail=30
```

| 现象 | 优先检查 |
| --- | --- |
| SSH 连接被拒绝 | NAS SSH 是否到期自动关闭；与容器是否运行分别判断 |
| frpc 连接超时 | 云 IP、控制端口、主机防火墙及云安全组 |
| TLS 校验失败 | 可信证书、SAN、serverName、系统时间与证书有效期 |
| 认证失败 | 两端 token 是否一致、文件权限是否可读 |
| 代理启动失败 | 映射端口是否冲突、是否在 allowPorts 内、旧测试进程是否仍占用 |
| HTTPS 502 | frpc 是否在线、云端回环映射是否监听、NAS 应用是否运行 |
| 反复要求登录 | 区分网页密码、NAS sudo 密码与 frp token；检查认证头转发 |
| 页面打开但歌曲不播放 | NAS 音乐权限、浏览器编码、Range、同源策略与应用媒体路径 |
| 域名正常但重启后失效 | frps enabled、Docker restart 策略及实际容器状态 |

## 九、新增项目看板或其他应用

先部署并验证新应用的内网访问，再增加一个客户端代理与独立 HTTPS 站点。确认 frps 允许对应回环映射端口，配置新域名后重新验收。项目看板在本次未部署，不能仅增加 frp 配置就认为看板已就绪。

## 回退

- NAS：在客户端目录运行 `sudo docker compose down`，不删除播放器或音乐文件。
- 云端：停用新增 frps 服务或新增 Nginx 站点前，确认没有其他应用依赖；不覆盖或删除原站点配置。
- 保留应用数据与部署记录；密码、令牌、私钥和实际凭证配置不进入 Vault 或 Git。

## 本次产物与证据

- [[capabilities/公网个人应用的SSH与登录防护加固]]：后续已验证的管理密钥、限流与失败登录封禁流程。
- [[runs/2026-10-25-NAS外网音乐入口安全加固]]：后续复核时隧道在线且公网播放通过；仍未独立检查 NAS 客户端容器身份与重启恢复。
- [本机部署目录](/Users/ompeak/work/peak/frp-deploy/README.md)：实际脚本、配置位置及维护说明。
- [[runs/2026-10-25-frp连接NAS与云服务器]]：本次实际执行和验证边界。
- [[sources/frp官方部署与认证文档]]：官方发布及配置依据。
- [[knowledge/NAS通过云服务器与frp外网访问的架构]]：组件关系与访问说明。
