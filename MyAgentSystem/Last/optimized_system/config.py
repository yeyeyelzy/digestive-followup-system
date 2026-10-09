import json
import os
from pathlib import Path
from typing import Optional


def _env_value(canonical_name: str, legacy_name: Optional[str] = None) -> Optional[str]:
    """Read the canonical name first, then the temporary legacy alias."""
    return os.getenv(canonical_name) or (os.getenv(legacy_name) if legacy_name else None)


APP_ENV = _env_value("DFS_APP_ENV", "SPRING_PROFILES_ACTIVE") or "dev"
if APP_ENV not in {"dev", "test", "staging", "prod"}:
    raise ValueError("DFS_APP_ENV must be one of: dev, test, staging, prod")


def _path_from_env(canonical_name: str, legacy_name: str, default: Path) -> Path:
    """Return a configured local path without embedding a machine-specific path."""
    value = _env_value(canonical_name, legacy_name)
    return Path(value).expanduser() if value else default


def _load_patients() -> dict:
    """Load patient metadata from an explicitly configured local JSON file."""
    path_value = _env_value("DFS_PATIENT_CONFIG_PATH", "PATIENT_CONFIG_PATH")
    if not path_value:
        if APP_ENV in {"staging", "prod"}:
            raise RuntimeError("DFS_PATIENT_CONFIG_PATH is required outside dev/test")
        return DEFAULT_PATIENTS

    patient_file = Path(path_value).expanduser()
    if APP_ENV in {"staging", "prod"} and not patient_file.is_absolute():
        raise ValueError("DFS_PATIENT_CONFIG_PATH must be an absolute path outside dev/test")
    if not patient_file.is_file():
        raise FileNotFoundError(f"Patient configuration does not exist: {patient_file}")

    with patient_file.open("r", encoding="utf-8") as handle:
        patients = json.load(handle)

    if not isinstance(patients, dict):
        raise ValueError("PATIENT_CONFIG_PATH must contain a JSON object keyed by patient ID")
    return patients


DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = _path_from_env("DFS_OPTIMIZED_SYSTEM_BASE_DIR", "OPTIMIZED_SYSTEM_BASE_DIR", DEFAULT_BASE_DIR)
INPUT_DIR = _path_from_env("DFS_APP_DATA_DIR", "APP_DATA_DIR", BASE_DIR / "data" / "input")
DATA_DIR = _path_from_env("DFS_FITABASE_DATA_DIR", "FITABASE_DATA_DIR", INPUT_DIR)
OUTPUT_DIR = _path_from_env("DFS_APP_OUTPUT_DIR", "APP_OUTPUT_DIR", BASE_DIR / "data" / "output")
FONT_DIR = _path_from_env("DFS_APP_FONT_DIR", "APP_FONT_DIR", BASE_DIR / "assets" / "fonts")
INPUT_RAW_DIR = _path_from_env("DFS_APP_INPUT_RAW_DIR", "APP_INPUT_RAW_DIR", INPUT_DIR / "raw")
OUTPUT_PATIENTS_DIR = _path_from_env("DFS_APP_PATIENT_OUTPUT_DIR", "APP_PATIENT_OUTPUT_DIR", OUTPUT_DIR / "patients")

if APP_ENV in {"staging", "prod"}:
    required_paths = {
        "DFS_FITABASE_DATA_DIR": _env_value("DFS_FITABASE_DATA_DIR", "FITABASE_DATA_DIR"),
        "DFS_APP_OUTPUT_DIR": _env_value("DFS_APP_OUTPUT_DIR", "APP_OUTPUT_DIR"),
    }
    missing = [name for name, value in required_paths.items() if not value]
    if missing:
        raise RuntimeError(f"Required environment paths are missing: {', '.join(missing)}")
    if not DATA_DIR.is_absolute() or not OUTPUT_DIR.is_absolute():
        raise ValueError("Data and output paths must be absolute outside dev/test")

# Production patient metadata stays in an ignored local JSON file.
DEFAULT_PATIENTS = {
    "P_001": {"name": "Sample patient 001", "folder": "P_001", "id": "P_001"},
    "P_002": {"name": "Sample patient 002", "folder": "P_002", "id": "P_002"},
    "P_003": {"name": "Sample patient 003", "folder": "P_003", "id": "P_003"},
}
PATIENTS = _load_patients()

DATE_START = "2016-04-12"
DATE_END = "2016-05-12"

END_TYPES = ["patient_end", "family_end", "doctor_end", "system_check"]
REPORT_TYPES = ["daily", "weekly", "monthly"]

GLOBAL_CONFIG = {
    "fig_size": (16, 6),
    "subplot_fig_size": (16, 12),
    "dpi": 300,
    "rc_params": {
        "font.family": ["SimHei", "Microsoft YaHei", "Arial"],
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.unicode_minus": False,
    },
    "colors": {
        "blue": "#1E88E5",
        "yellow": "#FFB300",
        "red": "#E53935",
        "green": "#43A047",
        "hr_line": "#212121",
        "avg_line": "#43A047",
        "rest_line": "#7B1FA2",
        "grid": "#EEEEEE",
    },
}

ONLINE_LEARNING_CONFIG = {
    "alpha": 0.3,
    "forgetting_factor": 0.8,
    "initial_health_score": 50.0,
    "max_health_score": 100.0,
    "red_warning_penalty": 5,
    "yellow_warning_penalty": 2,
    "improvement_bonus": 2,
    "core_indicators": [
        "rest_heart_rate", "hrv_sdnn", "hrv_rmssd",
        "deep_sleep_ratio", "daily_steps", "moderate_high_activity_min",
        "sedentary_min", "sleep_efficiency",
    ],
}

MEDICAL_RULES = {
    "heart_rate": {"min": 30, "max": 220, "rest_min": 50, "rest_max": 100},
    "steps": {"min": 0, "max": 200},
    "METs": {"min": 0.8, "max": 20},
    "sleep_stages": {0: "醒觉", 1: "浅睡", 2: "深睡", 3: "入睡期"},
    "activity_intensity": {0: "久坐", 1: "轻强度", 2: "中强度", 3: "高强度"},
}

ATTRIBUTION_RULES = {
    "physiological": {
        "mets_threshold": 3.0,
        "steps_threshold": 50,
        "intensity_threshold": 2,
    },
    "pathological": {
        "mets_threshold": 1.5,
        "steps_threshold": 10,
        "intensity_threshold": 1,
    },
}

QUALITATIVE_TEMPLATES = {
    "improving": ["较昨日改善", "持续向好", "明显好转", "稳步提升"],
    "worsening": ["较昨日变差", "有恶化趋势", "需要关注", "有所下降"],
    "stable": ["保持稳定", "无明显变化", "维持现状"],
}
