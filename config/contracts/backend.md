# 后端配置契约

| 规范变量 | 旧变量 | 必填环境 | 敏感 |
| --- | --- | --- | --- |
| `DFS_APP_ENV` | `SPRING_PROFILES_ACTIVE` | 全部 | 否 |
| `DFS_BACKEND_PORT` | `SERVER_PORT` | 否 | 否 |
| `DFS_DB_MASTER_URL` | `DB_MASTER_URL` | staging/prod | 是 |
| `DFS_DB_MASTER_USERNAME` | `DB_MASTER_USERNAME` | staging/prod | 是 |
| `DFS_DB_MASTER_PASSWORD` | `DB_MASTER_PASSWORD` | staging/prod | 是 |
| `DFS_REDIS_PASSWORD` | `REDIS_PASSWORD` | 按部署启用 | 是 |
| `DFS_AUTH_JWT_SECRET` | `JWT_SECRET` | staging/prod | 是 |
| `DFS_DRUID_MONITOR_USERNAME` | `DRUID_MONITOR_USERNAME` | staging/prod | 是 |
| `DFS_DRUID_MONITOR_PASSWORD` | `DRUID_MONITOR_PASSWORD` | staging/prod | 是 |
| `DFS_STORAGE_UPLOAD_DIR` | `FILE_UPLOAD_PATH` | 全部 | 否 |
| `DFS_STORAGE_PUBLIC_BASE_URL` | `FILES_PUBLIC_BASE_URL` | staging/prod | 否 |

新旧变量同时存在时，后端以 `DFS_*` 为准。生产环境必须通过 `scripts/validate-config.ps1` 校验。
