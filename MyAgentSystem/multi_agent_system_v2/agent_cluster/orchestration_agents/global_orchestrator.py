from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability

class GlobalOrchestratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="global_orchestrator",
            agent_role="全局编排专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="workflow_orchestration",
                description="工作流编排",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="task_coordination",
                description="任务协调",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="conflict_resolution",
                description="冲突解决",
                version="1.0.0",
                enabled=True
            )
        ]
        
    def initialize(self) -> bool:
        try:
            self.logger.info("全局编排智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"全局编排智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "analyze_user_request":
            return self._analyze_user_request(task)
        elif task_type == "orchestrate_workflow":
            return self._orchestrate_workflow(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _analyze_user_request(self, task: Task) -> TaskResult:
        try:
            user_input = task.payload.get("user_input", "")
            patient_id = task.payload.get("patient_id", "P_001")
            end_type = task.payload.get("end_type", "patient")
            
            intent = "general_query"
            if "累" in user_input or "累" in user_input:
                intent = "fatigue_inquiry"
            elif "运动" in user_input or "exercise" in user_input.lower():
                intent = "exercise_advice"
            elif "医生报告" in user_input:
                intent = "doctor_report"
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "intent": intent,
                    "patient_id": patient_id,
                    "end_type": end_type,
                    "analysis": "用户请求分析完成"
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"请求分析失败: {str(e)}"
            )
    
    def _orchestrate_workflow(self, task: Task) -> TaskResult:
        try:
            workflow_name = task.payload.get("workflow_name", "main")
            workflow_data = task.payload.get("workflow_data", {})
            
            workflow_result = {
                "workflow_name": workflow_name,
                "status": "completed",
                "executed_steps": [],
                "result": workflow_data
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"workflow_result": workflow_result}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"工作流编排失败: {str(e)}"
            )
