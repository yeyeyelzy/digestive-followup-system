"""系统配置：路径可由环境变量覆盖，避免依赖开发机器目录结构。"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


def _env_value(canonical_name: str, legacy_name: str = None) -> str:
    return os.getenv(canonical_name) or (os.getenv(legacy_name) if legacy_name else None)


def _path_from_env(canonical_name: str, legacy_name: str, default: Path) -> Path:
    value = _env_value(canonical_name, legacy_name)
    return Path(value).expanduser() if value else default


def _project_root() -> Path:
    return _path_from_env("DFS_PROJECT_ROOT", "PROJECT_ROOT", Path(__file__).resolve().parents[5])


@dataclass
class PathConfig:
    """路径配置。"""

    project_root: Path = field(default_factory=_project_root)
    myagent_system: Path = field(init=False)
    fitabase_data: Path = field(init=False)
    myknowledge: Path = field(init=False)
    kb_raw_data: Path = field(init=False)
    kb_processed_data: Path = field(init=False)
    kb_config: Path = field(init=False)
    kb_chroma_db: Path = field(init=False)
    output_dir: Path = field(init=False)
    patient_output: Path = field(init=False)
    family_output: Path = field(init=False)
    doctor_output: Path = field(init=False)
    system_check_output: Path = field(init=False)

    def __post_init__(self):
        self.myagent_system = _path_from_env("DFS_MYAGENT_SYSTEM_DIR", "MYAGENT_SYSTEM_DIR", self.project_root / "MyAgentSystem")
        self.fitabase_data = _path_from_env(
            "DFS_FITABASE_DATA_DIR", "FITABASE_DATA_DIR", self.myagent_system / "Fitabase Data 4.12.16-5.12.16"
        )
        self.myknowledge = _path_from_env("DFS_MYKNOWLEDGE_DIR", "MYKNOWLEDGE_DIR", self.project_root / "MyKnownlege")
        kb_base = _path_from_env("DFS_KB_BASE_DIR", "KB_BASE_DIR", self.myknowledge / "knowledge_base")
        self.kb_raw_data = _path_from_env("DFS_KB_RAW_DATA_DIR", "KB_RAW_DATA_DIR", kb_base / "data" / "raw")
        self.kb_processed_data = _path_from_env("DFS_KB_PROCESSED_DATA_DIR", "KB_PROCESSED_DATA_DIR", kb_base / "data" / "processed")
        self.kb_config = _path_from_env("DFS_KB_CONFIG_DIR", "KB_CONFIG_DIR", self.myknowledge / "knowledge_base_v2" / "config")
        self.kb_chroma_db = _path_from_env("DFS_CHROMA_DB_DIR", "CHROMA_DB_DIR", kb_base / "chroma_db")
        self.output_dir = _path_from_env(
            "DFS_V2_OUTPUT_DIR", "V2_OUTPUT_DIR", self.myagent_system / "Last" / "optimized_system_v2" / "output"
        )
        self.patient_output = _path_from_env("DFS_V2_PATIENT_OUTPUT_DIR", "V2_PATIENT_OUTPUT_DIR", self.output_dir / "患者端")
        self.family_output = _path_from_env("DFS_V2_FAMILY_OUTPUT_DIR", "V2_FAMILY_OUTPUT_DIR", self.output_dir / "家属端")
        self.doctor_output = _path_from_env("DFS_V2_DOCTOR_OUTPUT_DIR", "V2_DOCTOR_OUTPUT_DIR", self.output_dir / "医生端")
        self.system_check_output = _path_from_env("DFS_V2_SYSTEM_CHECK_OUTPUT_DIR", "V2_SYSTEM_CHECK_OUTPUT_DIR", self.output_dir / "系统自检")


@dataclass
class KBConfig:
    """知识库配置。"""

    paths: PathConfig
    hash_manifest: Path = field(init=False)
    file_relation_index: Path = field(init=False)
    segment_feature_index: Path = field(init=False)
    supported_file_types: List[str] = field(
        default_factory=lambda: ["json", "jsonl", "md", "csv", "xlsx", "pdf", "txt"]
    )
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_tags_per_file: int = 10
    max_tags_per_segment: int = 5

    def __post_init__(self):
        self.hash_manifest = self.paths.kb_config / "kb_hash_manifest.yaml"
        self.file_relation_index = self.paths.kb_config / "kb_file_relation_index.yaml"
        self.segment_feature_index = self.paths.kb_config / "kb_segment_feature_index.yaml"


@dataclass
class MultiAgentConfig:
    """多智能体配置。"""

    max_iterations: int = 3
    patient_tone: str = "friendly"
    doctor_format: str = "structured"


@dataclass
class SystemConfig:
    """系统配置。"""

    paths: PathConfig = field(default_factory=PathConfig)
    kb: KBConfig = field(init=False)
    mas: MultiAgentConfig = field(default_factory=MultiAgentConfig)

    def __post_init__(self):
        self.kb = KBConfig(self.paths)


config = SystemConfig()
