from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability

class DataFusionAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="data_fusion_agent",
            agent_role="多模态数据融合专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="temporal_alignment",
                description="时序数据对齐",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="multimodal_fusion",
                description="多模态数据融合",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="quality_assessment",
                description="数据质量评估",
                version="1.0.0",
                enabled=True
            )
        ]
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.patient_base_path = config.get("patient_data_path", "")
        
    def initialize(self) -> bool:
        try:
            self.logger.info("数据融合智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"数据融合智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "fuse_patient_data":
            return self._fuse_patient_data(task)
        elif task_type == "assess_data_quality":
            return self._assess_data_quality(task)
        elif task_type == "align_temporal_data":
            return self._align_temporal_data(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _fuse_patient_data(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            data_sources = task.payload.get("data_sources", [])
            time_window = task.payload.get("time_window", {"days": 7})
            
            self.logger.info(f"开始融合患者 {patient_id} 的数据")
            
            fused_data = {
                "patient_id": patient_id,
                "fusion_time": datetime.now().isoformat(),
                "time_window": time_window,
                "data_sources": data_sources,
                "physiological": self._load_physiological_data(patient_id, time_window),
                "activity": self._load_activity_data(patient_id, time_window),
                "sleep": self._load_sleep_data(patient_id, time_window),
                "diet": self._load_diet_data(patient_id, time_window),
                "medication": self._load_medication_data(patient_id, time_window),
                "video": self._load_video_data(patient_id, time_window),
                "altitude": self._load_altitude_data(patient_id, time_window)
            }
            
            self._update_shared_memory("fused_data", fused_data, patient_id=patient_id)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "fused_data": fused_data,
                    "summary": f"成功融合患者 {patient_id} 的多模态数据"
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"数据融合失败: {str(e)}"
            )
    
    def _assess_data_quality(self, task: Task) -> TaskResult:
        try:
            data = task.payload.get("data", {})
            
            quality_report = {
                "completeness": self._calculate_completeness(data),
                "consistency": self._check_consistency(data),
                "timeliness": self._check_timeliness(data),
                "overall_score": 0.0
            }
            
            quality_report["overall_score"] = (
                quality_report["completeness"] * 0.4 +
                quality_report["consistency"] * 0.3 +
                quality_report["timeliness"] * 0.3
            )
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"quality_report": quality_report}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"数据质量评估失败: {str(e)}"
            )
    
    def _align_temporal_data(self, task: Task) -> TaskResult:
        try:
            data_sources = task.payload.get("data_sources", {})
            target_frequency = task.payload.get("target_frequency", "1H")
            
            aligned_data = {}
            
            for source_name, data in data_sources.items():
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    if "timestamp" in df.columns:
                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                        df = df.set_index("timestamp")
                        df = df.resample(target_frequency).mean().interpolate()
                        aligned_data[source_name] = df.reset_index().to_dict("records")
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"aligned_data": aligned_data}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"时序对齐失败: {str(e)}"
            )
    
    def _calculate_completeness(self, data: Dict) -> float:
        total_fields = 0
        filled_fields = 0
        
        def count_fields(obj):
            nonlocal total_fields, filled_fields
            if isinstance(obj, dict):
                for v in obj.values():
                    total_fields += 1
                    if v is not None and v != "" and v != []:
                        filled_fields += 1
                    count_fields(v)
            elif isinstance(obj, list):
                for item in obj:
                    count_fields(item)
        
        count_fields(data)
        return filled_fields / max(total_fields, 1)
    
    def _check_consistency(self, data: Dict) -> float:
        score = 1.0
        return score
    
    def _check_timeliness(self, data: Dict) -> float:
        score = 1.0
        return score
    
    def _load_physiological_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        from data_processing.fitabase_data_processor import FitabaseDataProcessor
        processor = FitabaseDataProcessor()
        patient_data = processor.get_patient_data(patient_id)
        return patient_data.get("heart_rate", {}).get("raw_data", [])
    
    def _load_activity_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        from data_processing.fitabase_data_processor import FitabaseDataProcessor
        processor = FitabaseDataProcessor()
        patient_data = processor.get_patient_data(patient_id)
        return patient_data.get("activity", {}).get("raw_data", [])
    
    def _load_sleep_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        from data_processing.fitabase_data_processor import FitabaseDataProcessor
        processor = FitabaseDataProcessor()
        patient_data = processor.get_patient_data(patient_id)
        return patient_data.get("sleep", {}).get("raw_data", [])
    
    def _load_diet_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        from data_processing.fitabase_data_processor import FitabaseDataProcessor
        processor = FitabaseDataProcessor()
        patient_data = processor.get_patient_data(patient_id)
        return patient_data.get("diet", {}).get("raw_data", [])
    
    def _load_medication_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        from data_processing.fitabase_data_processor import FitabaseDataProcessor
        processor = FitabaseDataProcessor()
        patient_data = processor.get_patient_data(patient_id)
        return patient_data.get("medicine", {}).get("raw_data", [])
    
    def _load_video_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        return []
    
    def _load_altitude_data(self, patient_id: str, time_window: Dict) -> List[Dict]:
        return []
