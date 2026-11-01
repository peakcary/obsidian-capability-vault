---
type: source
source_type: official-documentation
publisher: Nginx 与 Fail2ban
accessed: 2026-10-25
reliability: primary
tags: [source, security]
---

# Nginx 限流与 Fail2ban 防护官方文档

- [Nginx 请求速率限制](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)：来源键、速率、突发、状态码及配置继承。
- [Nginx 并发限制](https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html)：按来源或站点限制活跃请求；HTTP/2 中并发请求分别计数。
- [Fail2ban 官方 Nginx 认证过滤示例](https://github.com/fail2ban/fail2ban/blob/master/config/filter.d/nginx-http-auth.conf)：官方示例针对 Nginx 自身认证错误日志；后端应用的 401 需要独立日志与匹配器，不能直接假定适用。

## 关联
- [[runs/2026-10-25-NAS外网音乐入口安全加固]]
- [[capabilities/公网个人应用的SSH与登录防护加固]]
