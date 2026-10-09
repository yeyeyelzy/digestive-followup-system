from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability

class RehabDecisionAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="rehab_decision_agent",
            agent_role="康复医学决策专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="rehab_plan_generation",
                description="康复方案生成",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="exercise_prescription",
                description="运动处方",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="diet_advice",
                description="饮食建议",
                version="1.0.0",
                enabled=True
            )
        ]
        
    def initialize(self) -> bool:
        try:
            self.logger.info("康复决策智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"康复决策智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "generate_rehab_plan":
            return self._generate_rehab_plan(task)
        elif task_type == "adjust_rehab_plan":
            return self._adjust_rehab_plan(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _generate_rehab_plan(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            patient_profile = task.payload.get("patient_profile", {})
            fused_data = task.payload.get("fused_data", {})
            intent = task.payload.get("intent", "general_query")
            
            rehab_plan = {
                "plan_id": f"RP_{patient_id}_{datetime.now().strftime('%Y%m%d')}",
                "patient_id": patient_id,
                "generated_at": datetime.now().isoformat(),
                "intent": intent,
                "exercise": {
                    "target_hr_low": 55,
                    "target_hr_high": 95,
                    "max_steps": 4500,
                    "recommended_activities": ["慢走", "太极"]
                },
                "diet": {
                    "recommendations": ["低盐低脂", "控制热量"],
                    "restrictions": []
                },
                "medication": {
                    "reminders": ["按时服药", "监测心率"],
                    "schedule": []
                },
                "risk_alerts": []
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "rehab_plan": rehab_plan,
                    "summary": f"成功为患者 {patient_id} 生成康复方案"
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"康复方案生成失败: {str(e)}"
            )
    
    def _adjust_rehab_plan(self, task: Task) -> TaskResult:
        try:
            original_plan = task.payload.get("original_plan", {})
            adjustment_request = task.payload.get("adjustment", {})
            
            adjusted_plan = original_plan.copy()
            adjusted_plan["adjusted_at"] = datetime.now().isoformat()
            adjusted_plan["adjustment_reason"] = adjustment_request.get("reason", "")
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"adjusted_plan": adjusted_plan}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"康复方案调整失败: {str(e)}"
            )
