from typing import Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path
import sys

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability

class EvidenceValidationAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="evidence_validation_agent",
            agent_role="循证医学验证专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="evidence_check",
                description="循证医学证据检查",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="conflict_detection",
                description="医学建议冲突检测",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="safety_review",
                description="安全性审查",
                version="1.0.0",
                enabled=True
            )
        ]
        self.evidence_levels = {
            "A": "强推荐",
            "B": "中等推荐",
            "C": "弱推荐",
            "D": "不推荐"
        }
        
    def initialize(self) -> bool:
        try:
            self.logger.info("循证验证智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"循证验证智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "validate_rehab_plan":
            return self._validate_rehab_plan(task)
        elif task_type == "check_evidence":
            return self._check_evidence(task)
        elif task_type == "detect_conflicts":
            return self._detect_conflicts(task)
        elif task_type == "safety_review":
            return self._safety_review(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _validate_rehab_plan(self, task: Task) -> TaskResult:
        try:
            rehab_plan = task.payload.get("rehab_plan", {})
            patient_profile = task.payload.get("patient_profile", {})
            
            validation_result = {
                "plan_id": rehab_plan.get("plan_id", ""),
                "validation_time": datetime.now().isoformat(),
                "overall_rating": "A",
                "components": [],
                "conflicts": [],
                "warnings": [],
                "improvements": []
            }
            
            exercise_plan = rehab_plan.get("exercise", {})
            exercise_validation = self._validate_exercise(exercise_plan, patient_profile)
            validation_result["components"].append(exercise_validation)
            
            diet_plan = rehab_plan.get("diet", {})
            diet_validation = self._validate_diet(diet_plan, patient_profile)
            validation_result["components"].append(diet_validation)
            
            medication_plan = rehab_plan.get("medication", {})
            medication_validation = self._validate_medication(medication_plan, patient_profile)
            validation_result["components"].append(medication_validation)
            
            all_ratings = [c.get("rating", "C") for c in validation_result["components"]]
            validation_result["overall_rating"] = self._combine_ratings(all_ratings)
            
            self._update_shared_memory("validation_result", validation_result, plan_id=rehab_plan.get("plan_id"))
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"validation_result": validation_result}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"康复计划验证失败: {str(e)}"
            )
    
    def _check_evidence(self, task: Task) -> TaskResult:
        try:
            claim = task.payload.get("claim", "")
            context = task.payload.get("context", {})
            
            evidence_check = {
                "claim": claim,
                "evidence_level": "B",
                "sources": [
                    {
                        "title": "中国PCI术后康复指南2023",
                        "evidence_level": "A",
                        "relevance": 0.85
                    }
                ],
                "confidence": 0.75,
                "recommendation": "建议参考现有指南"
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"evidence_check": evidence_check}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"证据检查失败: {str(e)}"
            )
    
    def _detect_conflicts(self, task: Task) -> TaskResult:
        try:
            recommendations = task.payload.get("recommendations", [])
            
            conflicts = []
            warnings = []
            
            for i, rec1 in enumerate(recommendations):
                for j, rec2 in enumerate(recommendations[i+1:], i+1):
                    if self._has_conflict(rec1, rec2):
                        conflicts.append({
                            "type": "recommendation_conflict",
                            "items": [i, j],
                            "description": f"建议 {i+1} 与建议 {j+1} 存在潜在冲突",
                            "severity": "medium"
                        })
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "conflicts": conflicts,
                    "warnings": warnings,
                    "has_conflicts": len(conflicts) > 0
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"冲突检测失败: {str(e)}"
            )
    
    def _safety_review(self, task: Task) -> TaskResult:
        try:
            action = task.payload.get("action", {})
            patient_data = task.payload.get("patient_data", {})
            
            safety_report = {
                "action_type": action.get("type", ""),
                "safe": True,
                "risk_level": "low",
                "risks": [],
                "precautions": [],
                "contraindications": []
            }
            
            contraindications = self._check_contraindications(action, patient_data)
            safety_report["contraindications"] = contraindications
            
            if contraindications:
                safety_report["safe"] = False
                safety_report["risk_level"] = "high"
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"safety_report": safety_report}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"安全性审查失败: {str(e)}"
            )
    
    def _validate_exercise(self, exercise_plan: Dict, patient_profile: Dict) -> Dict:
        return {
            "component": "exercise",
            "rating": "A",
            "issues": [],
            "evidence_sources": ["中国PCI术后康复指南2023"]
        }
    
    def _validate_diet(self, diet_plan: Dict, patient_profile: Dict) -> Dict:
        return {
            "component": "diet",
            "rating": "B",
            "issues": [],
            "evidence_sources": ["心血管疾病营养治疗指南"]
        }
    
    def _validate_medication(self, medication_plan: Dict, patient_profile: Dict) -> Dict:
        return {
            "component": "medication",
            "rating": "A",
            "issues": [],
            "evidence_sources": ["冠心病合理用药指南"]
        }
    
    def _has_conflict(self, rec1: Dict, rec2: Dict) -> bool:
        return False
    
    def _check_contraindications(self, action: Dict, patient_data: Dict) -> List[str]:
        return []
    
    def _combine_ratings(self, ratings: List[str]) -> str:
        rating_order = ["D", "C", "B", "A"]
        if not ratings:
            return "C"
        min_rating = min(ratings, key=lambda x: rating_order.index(x))
        return min_rating
