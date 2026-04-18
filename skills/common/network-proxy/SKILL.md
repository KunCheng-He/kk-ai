---
name: network-proxy
description: 网络代理配置工具。当遇到网络请求失败、超时、连接问题时使用此技能。触发关键词：代理、proxy、翻墙、网络问题、连接超时、connection timeout、网络不通。其他技能遇到网络问题时应主动调用此技能。
---

# Network Proxy

## 概述

本技能用于在当前设备网络环境受限时，配置代理以解决网络访问问题。

## 使用场景

- curl/wget 等命令请求超时或失败
- webfetch 工具访问网页失败
- 其他技能执行过程中遇到网络问题

## 代理配置

执行网络请求前，先运行：

```bash
source ~/.my_proxy/proxyrc
```

## 工作流程

1. **检测网络问题**：当网络请求超时或失败时
2. **加载本技能**：通过关键词触发或主动调用
3. **设置代理**：执行 `source ~/.my_proxy/proxyrc`
4. **验证代理**：运行 `curl -I --max-time 10 https://www.google.com` 确认代理可用
5. **重试请求**：使用代理重新执行网络请求

## 验证命令

```bash
# 验证代理是否生效
source ~/.my_proxy/proxyrc && curl -I --max-time 10 https://www.google.com

# 查看当前代理设置
echo "HTTP_PROXY: $HTTP_PROXY"
echo "HTTPS_PROXY: $HTTPS_PROXY"
```

## 故障排查

如果代理不可用：
1. 检查 `~/.my_proxy/proxyrc` 配置是否正确
2. 确认代理服务是否运行
3. 尝试其他代理端口或服务器

## 注意事项

- 代理配置仅在当前 shell 会话中生效
- 每次新的 bash 命令都需要先设置代理
- 如果代理本身不可用，需检查 `~/.my_proxy/proxyrc` 配置
