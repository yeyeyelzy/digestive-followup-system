"""知识库 V2.0 配置：所有可变路径和模型参数均可由环境变量覆盖。"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import yaml


def _env_value(canonical_name: str, legacy_name: Optional[str] = None) -> Optional[str]:
    return os.getenv(canonical_name) or (os.getenv(legacy_name) if legacy_name else None)


def _path_from_env(canonical_name: str, legacy_name: Optional[str], default: Path) -> Path:
    value = _env_value(canonical_name, legacy_name)
    return Path(value).expanduser() if value else default


def _int_from_env(canonical_name: str, legacy_name: Optional[str], default: int) -> int:
    value = _env_value(canonical_name, legacy_name)
    return int(value) if value else default


def _project_root() -> Path:
    return _path_from_env("DFS_PROJECT_ROOT", "PROJECT_ROOT", Path(__file__).resolve().parents[3])


def _kb_base(project_root: Path) -> Path:
    return _path_from_env("DFS_KB_BASE_DIR", "KB_BASE_DIR", project_root / "MyKnownlege" / "knowledge_base")


@dataclass
class KBPathConfig:
    """知识库路径配置。"""

    project_base: Path = field(default_factory=_project_root)
    kb_base: Path = field(init=False)
    raw_data_dir: Path = field(init=False)
    processed_data_dir: Path = field(init=False)
    config_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    chroma_db_dir: Path = field(init=False)
    kb_hash_manifest: Path = field(init=False)
    kb_file_relation_index: Path = field(init=False)
    kb_segment_feature_index: Path = field(init=False)

    def __post_init__(self):
        self.kb_base = _kb_base(self.project_base)
        self.raw_data_dir = _path_from_env("DFS_KB_RAW_DATA_DIR", "KB_RAW_DATA_DIR", self.kb_base / "data" / "raw")
        self.processed_data_dir = _path_from_env("DFS_KB_PROCESSED_DATA_DIR", "KB_PROCESSED_DATA_DIR", self.kb_base / "data" / "processed")
        self.chroma_db_dir = _path_from_env("DFS_CHROMA_DB_DIR", "CHROMA_DB_DIR", self.kb_base / "chroma_db")
        self.kb_hash_manifest = self.config_dir / "kb_hash_manifest.yaml"
        self.kb_file_relation_index = self.config_dir / "kb_file_relation_index.yaml"
        self.kb_segment_feature_index = self.config_dir / "kb_segment_feature_index.yaml"

        # Preserve the previous runtime behavior while keeping these generated paths ignored.
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class HashConfig:
    """哈希检测配置。"""

    hash_algorithm: str = "sha256"
    supported_file_types: List[str] = field(
        default_factory=lambda: ["json", "jsonl", "md", "csv", "xlsx", "pdf", "txt"]
    )
    chunk_size: int = 65536


@dataclass
class FeatureEngineeringConfig:
    """特征工程配置。"""

    chunk_size: int = 500
    chunk_overlap: int = 50
    max_tags_per_file: int = 10
    max_tags_per_segment: int = 5
    relation_threshold: float = 0.3


@dataclass
class RetrievalConfig:
    """检索配置。"""

    enable_tag_filter: bool = True
    enable_relation_recall: bool = True
    enable_vector_search: bool = True
    enable_rerank: bool = True
    top_k_tags: int = 20
    top_k_relations: int = 10
    top_k_vectors: int = 10
    top_k_final: int = 5
    vector_similarity_threshold: float = 0.4
    tag_match_threshold: float = 0.5


@dataclass
class EmbeddingConfig:
    """嵌入模型配置。"""

    model_name: str = field(default_factory=lambda: _env_value("DFS_EMBEDDING_MODEL", "EMBEDDING_MODEL") or "shibing624/text2vec-base-chinese")
    model_path: Optional[str] = field(default_factory=lambda: _env_value("DFS_EMBEDDING_MODEL_PATH", "EMBEDDING_MODEL_PATH"))
    device: str = field(default_factory=lambda: _env_value("DFS_EMBEDDING_DEVICE", "EMBEDDING_DEVICE") or "cpu")
    batch_size: int = field(default_factory=lambda: _int_from_env("DFS_EMBEDDING_BATCH_SIZE", "EMBEDDING_BATCH_SIZE", 32))
    max_length: int = field(default_factory=lambda: _int_from_env("DFS_EMBEDDING_MAX_LENGTH", "EMBEDDING_MAX_LENGTH", 512))


@dataclass
class ChromaConfig:
    """ChromaDB配置。"""

    persist_directory: str = field(
        default_factory=lambda: str(_path_from_env("DFS_CHROMA_DB_DIR", "CHROMA_DB_DIR", _kb_base(_project_root()) / "chroma_db"))
    )
    collection_name: str = field(default_factory=lambda: _env_value("DFS_CHROMA_COLLECTION_NAME", "CHROMA_COLLECTION_NAME") or "medical_guidelines_v2")
    embedding_function: Optional[Any] = None


class KBConfig:
    """统一配置类。"""

    def __init__(self, base_path: Optional[Path] = None):
        self.paths = KBPathConfig(project_base=Path(base_path)) if base_path else KBPathConfig()
        self.hash = HashConfig()
        self.feature = FeatureEngineeringConfig()
        self.retrieval = RetrievalConfig()
        self.embedding = EmbeddingConfig()
        self.chroma = ChromaConfig()

    def save_to_yaml(self, file_path: Optional[Path] = None):
        """保存配置到YAML。"""
        if file_path is None:
            file_path = self.paths.config_dir / "kb_config.yaml"

        config_dict = {
            "paths": {
                "kb_base": str(self.paths.kb_base),
                "raw_data_dir": str(self.paths.raw_data_dir),
                "processed_data_dir": str(self.paths.processed_data_dir),
            },
            "hash": {
                "hash_algorithm": self.hash.hash_algorithm,
                "supported_file_types": self.hash.supported_file_types,
            },
            "feature": {
                "chunk_size": self.feature.chunk_size,
                "chunk_overlap": self.feature.chunk_overlap,
            },
            "retrieval": {
                "top_k_final": self.retrieval.top_k_final,
                "vector_similarity_threshold": self.retrieval.vector_similarity_threshold,
            },
            "embedding": {
                "model_name": self.embedding.model_name,
                "device": self.embedding.device,
            },
        }

        with open(file_path, "w", encoding="utf-8") as handle:
            yaml.dump(config_dict, handle, allow_unicode=True)

        return file_path


class Config(KBConfig):
    """统一配置类（别名）。"""


# 全局配置实例
config = Config()


if __name__ == "__main__":
    print("=" * 60)
    print("知识库V2.0配置")
    print("=" * 60)
    print(f"知识库基础路径: {config.paths.kb_base}")
    print(f"原始数据路径: {config.paths.raw_data_dir}")
    print(f"索引配置路径: {config.paths.config_dir}")
    print()
    print("配置文件已创建，可通过 config.save_to_yaml() 保存")
