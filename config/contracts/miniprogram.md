# 微信小程序配置契约

小程序只读取非敏感的 API 公共地址和环境名：

| 配置项 | 来源 | 限制 |
| --- | --- | --- |
| `apiBaseUrl` | `patient/config/environment.js` | 只能是公开 HTTPS 地址；dev 可使用本机地址 |
| `environment` | 同上 | `dev/test/staging/prod` |

构建或发布生产包前，由 CI 生成或覆盖 `environment.prod.js`；数据库连接、JWT 签名密钥、AI 内部地址和任何 Secret 禁止进入小程序包。
