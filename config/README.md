# 环境配置协作指南

本目录是消化随访系统的**唯一环境配置入口**。如果你第一次参与本项目，请先阅读本文，再启动后端、AI 服务、知识库或微信小程序。

仓库只提交变量名、默认开发参数和示例数据，绝不提交密码、访问令牌、患者资料、生产地址或本机路径。真实值应由本机环境变量、IDE 运行配置、容器 Secret 或 CI/CD Secret 注入。

## 1. 先了解项目由哪些部分组成

| 部分 | 主要位置 | 需要的配置 |
| --- | --- | --- |
| Java 后端 | `MyRuoYi/dev/project/web_doctor_final/RuoYi-Vue-master` | 数据库、Redis、JWT、文件存储、AI 网关和 Druid 监控 |
| AI 服务 | `MyAgentSystem/Last` | 数据目录、输出目录、患者配置与 AI 网关 |
| 知识库 | `MyKnownlege/knowledge_base_v2` | 知识库目录、Chroma 数据库与嵌入模型 |
| 患者小程序 | `MyRuoYi/dev/project/wx_patient_final/patient` | 对外可访问的后端 API 地址 |

所有新配置优先使用 `DFS_*` 变量。旧变量（如 `DB_MASTER_URL`、`JWT_SECRET`）只为兼容存量部署保留，不应再用于新环境。

## 2. 五分钟完成本地开发配置

在仓库根目录执行：

```powershell
Copy-Item .env.example .env.local
```

然后编辑 `.env.local`，至少填写你准备运行的模块所需字段。`.env.local` 已被 Git 忽略，适合保存你的本机开发值；但应用**不会自动读取**该文件。请把其中变量导入 IDE 的运行配置、服务管理器、容器环境或 CI/CD Secret。

`.env.local` 也可直接用于预检：

```powershell
.\scripts\validate-config.ps1 -Environment dev -Module all -EnvFile .env.local
```

若只启动一个模块，可将 `all` 换为 `backend`、`ai`、`kb` 或 `frontend`。预检成功会显示 `Configuration validation passed`。

> `.env.local` 仅供本地参考和预检；它不是 Java 或 Python 的自动加载机制。不要把真实值写进 `application*.yml`、Python 源码或小程序已跟踪文件。

## 3. 按模块填写变量

建议从这些模块化模板复制变量到 `.env.local`：

| 模块 | 示例文件 | 关键变量 |
| --- | --- | --- |
| 通用 | [`env/common.env.example`](env/common.env.example) | `DFS_APP_ENV`、`DFS_BACKEND_HOST`、`DFS_BACKEND_PORT` |
| 后端 | [`env/backend.env.example`](env/backend.env.example) | `DFS_DB_MASTER_*`、`DFS_REDIS_*`、`DFS_AUTH_JWT_SECRET`、`DFS_STORAGE_*`、`DFS_DRUID_MONITOR_*` |
| AI 服务 | [`env/ai.env.example`](env/ai.env.example) | `DFS_AI_*`、`DFS_APP_OUTPUT_DIR`、`DFS_PATIENT_CONFIG_PATH` |
| 知识库 | [`env/knowledge.env.example`](env/knowledge.env.example) | `DFS_KB_*`、`DFS_CHROMA_*`、`DFS_EMBEDDING_*` |
| 小程序 | [`env/miniprogram.env.example`](env/miniprogram.env.example) | `DFS_MINIPROGRAM_API_BASE_URL`、`DFS_MINIPROGRAM_ENV` |

完整合并示例在仓库根目录的 [`.env.example`](../.env.example)。各模块变量的用途和兼容别名见 [`contracts/`](contracts)。

### 后端最小要求

Java 后端使用 Java 8（由 Maven 项目声明）。启动前至少确认：

- `DFS_APP_ENV=dev`
- `DFS_DB_MASTER_URL`、`DFS_DB_MASTER_USERNAME`、`DFS_DB_MASTER_PASSWORD`
- `DFS_AUTH_JWT_SECRET`
- `DFS_DRUID_MONITOR_USERNAME`、`DFS_DRUID_MONITOR_PASSWORD`
- 如启用 Redis：`DFS_REDIS_HOST`、`DFS_REDIS_PORT`、`DFS_REDIS_DATABASE`，并按需设置 `DFS_REDIS_PASSWORD`

后端按 `application.yml` 读取通用入口，再叠加 `application-dev.yml`、`application-test.yml`、`application-staging.yml` 或 `application-prod.yml`。`application-druid.yml` 专门处理数据源与 Druid 监控。

### AI 服务和知识库最小要求

开发环境可先使用本机的测试数据目录；staging/prod 必须使用仓库外的绝对路径，并且患者配置不应位于 Git 工作区内。

- AI 服务：配置数据输入、输出目录及 `DFS_PATIENT_CONFIG_PATH`。
- 知识库：配置 `DFS_KB_BASE_DIR` 和 `DFS_CHROMA_DB_DIR`，再按设备填写嵌入模型、设备类型和批大小。
- 如需要本地患者示例，请复制 [`patients.example.json`](patients.example.json) 为 `patients.local.json`，填入获准使用的数据，并把路径赋给 `DFS_PATIENT_CONFIG_PATH`。该文件已被 Git 忽略。

### 微信小程序最小要求

小程序当前读取 `patient/config/environment.js` 中的公开 API 地址。仓库中的该文件只保留安全的本地开发地址；部署时应由 CI/CD 根据 `DFS_MINIPROGRAM_API_BASE_URL` 生成或替换目标环境地址。

`environment.local.js` 已被 Git 忽略，但当前代码不会自动加载它。因此不要把真实服务器地址提交到 `environment.js`；请通过构建/发布流程注入，或在本机临时修改后确认不会提交。

## 4. 环境分层与上线门槛

| 环境 | 用途 | 校验要求 |
| --- | --- | --- |
| `dev` | 本机开发 | 可使用本机 HTTP 地址与测试数据 |
| `test` | 自动化/联调测试 | 使用隔离测试资源 |
| `staging` | 上线前验证 | 数据库、JWT、Druid 凭据必填；外部路径必须是绝对路径；公开地址必须为 HTTPS |
| `prod` | 生产 | 满足 staging 全部要求；Swagger 必须关闭，Druid 白名单不能对全网开放 |

在准备发布时运行：

```powershell
.\scripts\validate-config.ps1 -Environment staging -Module all -EnvFile .env.local
.\scripts\validate-config.ps1 -Environment prod -Module all -EnvFile .env.local
```

校验会拒绝空值、`change_me`、`example`、`todo` 和 `replace-with-*` 等占位符，也会拒绝生产环境中的 HTTP 公开地址、仓库内数据路径、开放的 Druid 白名单或开启的 Swagger。

## 5. 提交前检查清单

- [ ] 只使用 `DFS_*` 新变量；没有新增硬编码地址、密码、Token 或机器路径。
- [ ] `.env.local`、`patients.local.json`、真实数据和模型输出均未进入 `git status`。
- [ ] 已运行与改动模块对应的 `validate-config.ps1` 校验。
- [ ] staging/prod 已由 Secret 管理系统注入真实值，未依赖示例文件。
- [ ] 小程序目标 API 使用 HTTPS，且发布产物不含私密配置。

## 6. 常见问题

**校验报“Missing or placeholder configuration”**：在 `.env.local` 或运行环境中补齐对应的 `DFS_*` 值；不要用示例占位符上线。

**修改 `.env.local` 后服务配置没有变化**：这是预期行为。将变量配置到 IDE、进程环境、容器或发布平台，然后重启服务。

**不知道某个变量属于哪里**：先查看 [`contracts/`](contracts) 中对应模块的契约文档，再查同名 `*.env.example`。仍不明确时，请在协作讨论中说明“模块 + 环境 + 变量名”，不要粘贴真实凭据。
