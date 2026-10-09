# 本地配置说明

所有可变环境值已从源码中移出。仓库只保留 [`.env.example`](../.env.example) 和 `patients.example.json`，其中不包含真实凭据、患者信息或机器路径。

`.env` 仅作本地参考，代码不会自动读取它。请在 IDE 运行配置、Windows 服务、Docker/Kubernetes Secret 或 CI/CD 的环境变量中注入真实值；不要提交 `.env` 或 `patients.local.json`。

Java 服务优先读取 `DFS_*` 变量；`DB_MASTER_URL`、`JWT_SECRET` 等旧变量仅作为临时兼容别名。staging/prod 启动前至少需要设置：`DFS_DB_MASTER_URL`、`DFS_DB_MASTER_USERNAME`、`DFS_DB_MASTER_PASSWORD`、`DFS_AUTH_JWT_SECRET`、`DFS_DRUID_MONITOR_USERNAME` 和 `DFS_DRUID_MONITOR_PASSWORD`。Redis、上传路径和 AI 网关同样使用 `DFS_*` 变量覆盖。

Python 模块会优先读取 `DFS_PROJECT_ROOT`、`DFS_FITABASE_DATA_DIR`、`DFS_APP_DATA_DIR`、`DFS_APP_OUTPUT_DIR`、`DFS_KB_BASE_DIR`、`DFS_CHROMA_DB_DIR` 等变量。staging/prod 必须提供绝对的数据、输出和患者配置路径；旧变量仅作为兼容别名。

如需运行含真实患者数据的流程：复制 `patients.example.json` 为 `patients.local.json`，填写本地允许使用的资料，并将 `PATIENT_CONFIG_PATH` 指向该文件。该文件已被 Git 忽略。

环境分层如下：

- `application.yml`：通用配置和环境变量入口。
- `application-dev.yml`：开发日志与 Swagger。
- `application-prod.yml`：生产日志与默认关闭的 Swagger。
- `application-druid.yml`：数据库和 Druid 的环境变量入口。
