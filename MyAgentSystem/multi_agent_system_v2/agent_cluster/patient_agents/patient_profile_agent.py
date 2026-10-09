from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability


class PatientProfileAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="patient_profile_agent",
            agent_role="患者画像构建专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="profile_building",
                description="患者画像构建",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="behavior_analysis",
                description="行为模式分析",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="risk_assessment",
                description="风险评估",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="preference_learning",
                description="偏好学习",
                version="1.0.0",
                enabled=True
            )
        ]
        self.profile_cache: Dict[str, Dict] = {}
        self.profile_base_path = Path(config.get("profile_path", "./patient_profiles"))
        
    def initialize(self) -> bool:
        try:
            self.profile_base_path.mkdir(parents=True, exist_ok=True)
            self.logger.info("患者画像智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"患者画像智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "build_profile":
            return self._build_profile(task)
        elif task_type == "update_profile":
            return self._update_profile(task)
        elif task_type == "analyze_behavior":
            return self._analyze_behavior(task)
        elif task_type == "assess_risk":
            return self._assess_risk(task)
        elif task_type == "get_profile":
            return self._get_profile(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _build_profile(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            initial_data = task.payload.get("initial_data", {})
            historical_data = task.payload.get("historical_data", {})
            
            self.logger.info(f"开始构建患者 {patient_id} 的画像")
            
            profile = {
                "patient_id": patient_id,
                "profile_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "basic_info": self._extract_basic_info(initial_data),
                "medical_history": self._extract_medical_history(initial_data),
                "behavior_patterns": self._extract_behavior_patterns(historical_data),
                "risk_factors": self._extract_risk_factors(initial_data, historical_data),
                "preferences": self._extract_preferences(initial_data, historical_data),
                "health_trends": self._extract_health_trends(historical_data),
                "treatment_adherence": self._calculate_adherence(historical_data),
                "emotional_state": self._assess_emotional_state(historical_data),
                "social_support": self._assess_social_support(initial_data)
            }
            
            self._save_profile(patient_id, profile)
            self._update_shared_memory("patient_profile", profile, patient_id=patient_id)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "profile": profile,
                    "summary": f"成功构建患者 {patient_id} 的完整画像"
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"画像构建失败: {str(e)}"
            )
    
    def _update_profile(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            update_data = task.payload.get("update_data", {})
            
            profile = self._load_profile(patient_id)
            if not profile:
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message=f"未找到患者 {patient_id} 的画像"
                )
            
            profile["updated_at"] = datetime.now().isoformat()
            
            if "behavior" in update_data:
                profile["behavior_patterns"] = self._update_behavior_patterns(
                    profile["behavior_patterns"], update_data["behavior"])
            
            if "health_data" in update_data:
                profile["health_trends"] = self._update_health_trends(
                    profile["health_trends"], update_data["health_data"])
            
            if "feedback" in update_data:
                profile["preferences"] = self._update_preferences(
                    profile["preferences"], update_data["feedback"])
            
            self._save_profile(patient_id, profile)
            self._update_shared_memory("patient_profile", profile, patient_id=patient_id)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "profile": profile,
                    "summary": f"成功更新患者 {patient_id} 的画像"
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"画像更新失败: {str(e)}"
            )
    
    def _analyze_behavior(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            time_window = task.payload.get("time_window", {"days": 30})
            
            behavior_analysis = {
                "patient_id": patient_id,
                "analysis_time": datetime.now().isoformat(),
                "time_window": time_window,
                "activity_patterns": {
                    "exercise_consistency": 0.75,
                    "sleep_regularity": 0.80,
                    "medication_adherence": 0.85,
                    "diet_regularity": 0.70
                },
                "anomalies": [],
                "recommendations": [],
                "insights": []
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"behavior_analysis": behavior_analysis}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"行为分析失败: {str(e)}"
            )
    
    def _assess_risk(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            profile = task.payload.get("profile", {})
            
            risk_assessment = {
                "patient_id": patient_id,
                "assessment_time": datetime.now().isoformat(),
                "overall_risk_level": "medium",
                "risk_factors": [
                    {"factor": "血脂异常", "level": "medium", "impact": "high"},
                    {"factor": "运动不足", "level": "low", "impact": "medium"}
                ],
                "protective_factors": [
                    {"factor": "规律服药", "level": "high", "impact": "high"},
                    {"factor": "家庭支持", "level": "medium", "impact": "medium"}
                ],
                "recommendations": [],
                "monitoring_points": []
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"risk_assessment": risk_assessment}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"风险评估失败: {str(e)}"
            )
    
    def _get_profile(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            profile = self._load_profile(patient_id)
            
            if profile:
                return TaskResult(
                    task_id=task.task_id,
                    success=True,
                    result={"profile": profile}
                )
            else:
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message=f"未找到患者 {patient_id} 的画像"
                )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"获取画像失败: {str(e)}"
            )
    
    def _extract_basic_info(self, data: Dict) -> Dict:
        return {
            "age": data.get("age", 0),
            "gender": data.get("gender", ""),
            "height": data.get("height", 0),
            "weight": data.get("weight", 0),
            "bmi": data.get("bmi", 0)
        }
    
    def _extract_medical_history(self, data: Dict) -> Dict:
        return {
            "diagnosis_date": data.get("diagnosis_date", ""),
            "pci_date": data.get("pci_date", ""),
            "stent_count": data.get("stent_count", 0),
            "comorbidities": data.get("comorbidities", []),
            "medications": data.get("medications", [])
        }
    
    def _extract_behavior_patterns(self, data: Dict) -> Dict:
        return {
            "exercise": {"frequency": "weekly", "intensity": "moderate"},
            "diet": {"preferences": [], "restrictions": []},
            "sleep": {"average_duration": 7.0, "quality": "good"},
            "medication": {"adherence_rate": 0.9}
        }
    
    def _extract_risk_factors(self, initial_data: Dict, historical_data: Dict) -> Dict:
        return {
            "biological": [],
            "behavioral": [],
            "environmental": []
        }
    
    def _extract_preferences(self, initial_data: Dict, historical_data: Dict) -> Dict:
        return {
            "communication": {"style": "friendly", "frequency": "daily"},
            "exercise": {"types": ["walking", "tai_chi"]},
            "diet": {"likes": [], "dislikes": []},
            "reminders": {"preferred_time": "morning"}
        }
    
    def _extract_health_trends(self, data: Dict) -> Dict:
        return {
            "weight_trend": "stable",
            "blood_pressure_trend": "improving",
            "activity_trend": "stable"
        }
    
    def _calculate_adherence(self, data: Dict) -> Dict:
        return {
            "medication_adherence": 0.9,
            "exercise_adherence": 0.75,
            "diet_adherence": 0.8,
            "overall_adherence": 0.82
        }
    
    def _assess_emotional_state(self, data: Dict) -> Dict:
        return {
            "mood": "positive",
            "anxiety_level": "low",
            "stress_level": "low",
            "motivation_level": "moderate"
        }
    
    def _assess_social_support(self, data: Dict) -> Dict:
        return {
            "family_support": "good",
            "caregiver_available": True,
            "social_connections": "moderate"
        }
    
    def _update_behavior_patterns(self, existing: Dict, new_data: Dict) -> Dict:
        return {**existing, **new_data}
    
    def _update_health_trends(self, existing: Dict, new_data: Dict) -> Dict:
        return {**existing, **new_data}
    
    def _update_preferences(self, existing: Dict, feedback: Dict) -> Dict:
        return {**existing, **feedback}
    
    def _save_profile(self, patient_id: str, profile: Dict):
        profile_path = self.profile_base_path / f"{patient_id}_profile.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        self.profile_cache[patient_id] = profile
    
    def _load_profile(self, patient_id: str) -> Optional[Dict]:
        if patient_id in self.profile_cache:
            return self.profile_cache[patient_id]
        
        profile_path = self.profile_base_path / f"{patient_id}_profile.json"
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
                self.profile_cache[patient_id] = profile
                return profile
        return None
