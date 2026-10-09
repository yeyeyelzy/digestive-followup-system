# AI 与报告模块配置契约

| 规范变量 | 旧变量 | 必填环境 | 敏感 |
| --- | --- | --- | --- |
| `DFS_AI_BASE_URL` | `AI_SERVICE_BASE_URL` | 全部 | 否 |
| `DFS_AI_REPORT_ROOT` | `AI_REPORT_ROOT` | 全部 | 否 |
| `DFS_FITABASE_DATA_DIR` | `FITABASE_DATA_DIR` | staging/prod | 是 |
| `DFS_APP_OUTPUT_DIR` | `APP_OUTPUT_DIR` | staging/prod | 否 |
| `DFS_PATIENT_CONFIG_PATH` | `PATIENT_CONFIG_PATH` | staging/prod | 是 |

staging/prod 的路径必须为绝对路径，且不得指向 Git 工作树。患者 JSON 文件只允许位于受控本地目录或由数据服务提供。
