# 知识库配置契约

| 规范变量 | 旧变量 | 必填环境 | 敏感 |
| --- | --- | --- | --- |
| `DFS_KB_BASE_DIR` | `KB_BASE_DIR` | staging/prod | 是 |
| `DFS_KB_RAW_DATA_DIR` | `KB_RAW_DATA_DIR` | staging/prod | 是 |
| `DFS_KB_PROCESSED_DATA_DIR` | `KB_PROCESSED_DATA_DIR` | staging/prod | 否 |
| `DFS_CHROMA_DB_DIR` | `CHROMA_DB_DIR` | staging/prod | 否 |
| `DFS_EMBEDDING_MODEL` | `EMBEDDING_MODEL` | 否 | 否 |
| `DFS_EMBEDDING_DEVICE` | `EMBEDDING_DEVICE` | 否 | 否 |

原始文档、向量库和运行时索引均不得提交到 Git。模型名称可以提交，模型令牌和私有模型服务凭据不可提交。
