from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import sys
import asyncio

# 添加当前目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult
from message_bus.message_queue import MessageBus
from memory_system.memory_manager import MemorySystem

from agent_cluster.orchestration_agents.global_orchestrator import GlobalOrchestratorAgent
from agent_cluster.data_agents.data_fusion_agent import DataFusionAgent
from agent_cluster.patient_agents.patient_profile_agent import PatientProfileAgent
from agent_cluster.patient_agents.emotional_empathy_agent import EmotionalEmpathyAgent
from agent_cluster.medical_agents.rehab_decision_agent import RehabDecisionAgent
from agent_cluster.medical_agents.evidence_validation_agent import EvidenceValidationAgent
from agent_cluster.medical_agents.doctor_report_agent import DoctorReportAgent
from agent_cluster.nlg_interaction.nlg_generator import MultiEndNLG
from incremental_learning.online_learner import IncrementalLearner


class AgentOrchestrator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._init_logger()
        
        self.message_bus = MessageBus(config.get("message_bus", {}))
        self.memory_system = MemorySystem(Path(config.get("memory_path", "./memory")))
        
        self.agents: Dict[str, BaseAgent] = {}
        self._register_agents()
        
        self.is_initialized = False
        
    def _init_logger(self):
        import logging
        logger = logging.getLogger("AgentOrchestrator")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _register_agents(self):
        self.logger.info("开始注册智能体...")
        
        agent_classes = [
            ("global_orchestrator", GlobalOrchestratorAgent),
            ("data_fusion", DataFusionAgent),
            ("patient_profile", PatientProfileAgent),
            ("emotional_empathy", EmotionalEmpathyAgent),
            ("rehab_decision", RehabDecisionAgent),
            ("evidence_validation", EvidenceValidationAgent),
            ("doctor_report", DoctorReportAgent),
            ("incremental_learner", IncrementalLearner)
        ]
        
        for agent_name, agent_class in agent_classes:
            try:
                agent = agent_class(self.config.get(agent_name, {}))
                agent.message_bus = self.message_bus
                agent.memory_system = self.memory_system
                self.message_bus.register_agent(agent)
                self.agents[agent_name] = agent
                self.logger.info(f"成功注册智能体: {agent_name}")
            except Exception as e:
                self.logger.error(f"注册智能体失败 {agent_name}: {e}")
        
        self.nlg_generator = MultiEndNLG(self.config.get("nlg", {}))
        
    def initialize(self) -> bool:
        try:
            self.logger.info("开始初始化多智能体系统...")
            
            success = True
            for agent_name, agent in self.agents.items():
                try:
                    agent.initialize()
                    self.logger.info(f"智能体初始化成功: {agent_name}")
                except Exception as e:
                    self.logger.error(f"智能体初始化失败 {agent_name}: {e}")
                    success = False
            
            self.is_initialized = success
            
            if success:
                self.logger.info("多智能体系统初始化完成!")
            else:
                self.logger.warning("多智能体系统部分初始化失败")
            
            return success
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            return False
    
    async def process_user_request_async(self, user_input: str, patient_id: str = "P_001", 
                                         end_type: str = "patient") -> Dict[str, Any]:
        if not self.is_initialized:
            return {
                "success": False,
                "error": "系统未初始化，请先调用 initialize()"
            }
        
        try:
            self.logger.info(f"处理用户请求: patient={patient_id}, end_type={end_type}")
            
            self.memory_system.store(
                memory_type="short_term",
                key=f"session_{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                value={"user_input": user_input, "timestamp": datetime.now().isoformat()},
                patient_id=patient_id
            )
            
            workflow_result = await self._execute_main_workflow_async(user_input, patient_id, end_type)
            
            final_response = self._generate_final_response(workflow_result, end_type)
            
            return {
                "success": True,
                "patient_id": patient_id,
                "end_type": end_type,
                "response": final_response,
                "workflow_trace": workflow_result.get("trace", []),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"处理用户请求失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_user_request(self, user_input: str, patient_id: str = "P_001", 
                            end_type: str = "patient") -> Dict[str, Any]:
        return asyncio.run(self.process_user_request_async(user_input, patient_id, end_type))
    
    async def _execute_main_workflow_async(self, user_input: str, patient_id: str, end_type: str) -> Dict[str, Any]:
        trace = []
        
        try:
            self.logger.info("开始执行主工作流...")
            
            trace.append({"step": 1, "agent": "global_orchestrator", "action": "analyze_request"})
            task = Task.create(
                task_type="analyze_user_request",
                payload={"user_input": user_input, "patient_id": patient_id, "end_type": end_type},
                patient_id=patient_id
            )
            analysis_result = await self._submit_task_async("global_orchestrator", task)
            
            if not analysis_result.success:
                return {"trace": trace, "error": analysis_result.error_message}
            
            intent = analysis_result.result.get("intent", "general_query")
            trace.append({"step": 2, "result": f"intent_detected: {intent}"})
            
            trace.append({"step": 3, "agent": "patient_profile", "action": "get_profile"})
            profile_task = Task.create(
                task_type="get_profile",
                payload={"patient_id": patient_id},
                patient_id=patient_id
            )
            profile_result = await self._submit_task_async("patient_profile", profile_task)
            
            patient_profile = profile_result.result.get("profile", {}) if profile_result.success else {}
            
            trace.append({"step": 4, "agent": "data_fusion", "action": "fuse_data"})
            data_task = Task.create(
                task_type="fuse_patient_data",
                payload={"patient_id": patient_id},
                patient_id=patient_id
            )
            data_result = await self._submit_task_async("data_fusion", data_task)
            
            fused_data = data_result.result.get("fused_data", {}) if data_result.success else {}
            
            trace.append({"step": 5, "agent": "rehab_decision", "action": "generate_plan"})
            rehab_task = Task.create(
                task_type="generate_rehab_plan",
                payload={
                    "patient_id": patient_id,
                    "patient_profile": patient_profile,
                    "fused_data": fused_data,
                    "intent": intent,
                    "user_input": user_input
                },
                patient_id=patient_id
            )
            rehab_result = await self._submit_task_async("rehab_decision", rehab_task)
            
            rehab_plan = rehab_result.result.get("rehab_plan", {}) if rehab_result.success else {}
            
            trace.append({"step": 6, "agent": "evidence_validation", "action": "validate_plan"})
            validation_task = Task.create(
                task_type="validate_rehab_plan",
                payload={
                    "rehab_plan": rehab_plan,
                    "patient_profile": patient_profile
                },
                patient_id=patient_id
            )
            validation_result = await self._submit_task_async("evidence_validation", validation_task)
            
            validation_result_data = validation_result.result.get("validation_result", {}) if validation_result.success else {}
            
            trace.append({"step": 7, "agent": "emotional_empathy", "action": "detect_emotion"})
            emotion_task = Task.create(
                task_type="detect_emotional_state",
                payload={"user_input": user_input, "patient_profile": patient_profile},
                patient_id=patient_id
            )
            emotion_result = await self._submit_task_async("emotional_empathy", emotion_task)
            
            emotional_state = emotion_result.result.get("emotional_analysis", {}).get("primary_emotion", "neutral") if emotion_result.success else "neutral"
            
            trace.append({"step": 8, "agent": "incremental_learner", "action": "process_feedback"})
            
            final_data = {
                "intent": intent,
                "patient_profile": patient_profile,
                "fused_data": fused_data,
                "rehab_plan": rehab_plan,
                "validation_result": validation_result_data,
                "emotional_state": emotional_state,
                "end_type": end_type
            }
            
            trace.append({"step": 9, "status": "completed"})
            
            return {"trace": trace, "data": final_data}
            
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return {"trace": trace, "error": str(e)}
    
    async def _submit_task_async(self, agent_name: str, task: Task) -> TaskResult:
        try:
            if agent_name in self.agents:
                result = await asyncio.to_thread(self.agents[agent_name].process_task, task)
                return result
            else:
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message=f"智能体不存在: {agent_name}"
                )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e)
            )
    
    def _generate_final_response(self, workflow_result: Dict, end_type: str) -> Dict[str, Any]:
        if "error" in workflow_result:
            return {
                "type": "error",
                "content": f"处理出错: {workflow_result['error']}"
            }
        
        data = workflow_result.get("data", {})
        
        if end_type == "patient":
            response = self.nlg_generator.generate_patient_response(data)
        elif end_type == "family":
            response = self.nlg_generator.generate_family_response(data)
        elif end_type == "doctor":
            response = self.nlg_generator.generate_doctor_report(data)
        else:
            response = self.nlg_generator.generate_patient_response(data)
        
        return response
    
    async def submit_feedback_async(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        try:
            task = Task.create(
                task_type="process_feedback",
                payload={"feedback": feedback},
                patient_id=feedback.get("patient_id", "unknown")
            )
            result = await self._submit_task_async("incremental_learner", task)
            
            return {
                "success": result.success,
                "result": result.result if result.success else None,
                "error": result.error_message if not result.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def submit_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self.submit_feedback_async(feedback))
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            "initialized": self.is_initialized,
            "agent_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    def shutdown(self):
        self.logger.info("正在关闭多智能体系统...")
        self.message_bus.shutdown()
        self.is_initialized = False
        self.logger.info("多智能体系统已关闭")
