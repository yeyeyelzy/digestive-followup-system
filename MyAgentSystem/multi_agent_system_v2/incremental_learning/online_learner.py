from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys
import json
import hashlib
from collections import defaultdict

# 添加当前目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability


class IncrementalLearner(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="incremental_learner",
            agent_role="在线增量学习专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="feedback_learning",
                description="用户反馈学习",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="pattern_mining",
                description="模式挖掘",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="knowledge_distillation",
                description="知识蒸馏",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="model_adaptation",
                description="模型自适应",
                version="1.0.0",
                enabled=True
            )
        ]
        self.feedback_storage: Dict[str, List[Dict]] = defaultdict(list)
        self.pattern_database: Dict[str, Any] = {}
        self.learning_stats: Dict[str, Any] = {
            "total_feedbacks": 0,
            "successful_adaptations": 0,
            "patterns_discovered": 0,
            "knowledge_updates": 0
        }
        self.learning_base_path = Path(config.get("learning_path", "./incremental_learning"))
        
    def initialize(self) -> bool:
        try:
            self.learning_base_path.mkdir(parents=True, exist_ok=True)
            self._load_learning_state()
            self.logger.info("在线增量学习系统初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"在线增量学习系统初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "process_feedback":
            return self._process_feedback(task)
        elif task_type == "mine_patterns":
            return self._mine_patterns(task)
        elif task_type == "update_knowledge":
            return self._update_knowledge(task)
        elif task_type == "adapt_model":
            return self._adapt_model(task)
        elif task_type == "get_learning_insights":
            return self._get_learning_insights(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _process_feedback(self, task: Task) -> TaskResult:
        try:
            feedback_data = task.payload.get("feedback", {})
            patient_id = feedback_data.get("patient_id", "unknown")
            feedback_type = feedback_data.get("feedback_type", "general")
            
            self.logger.info(f"处理来自患者 {patient_id} 的 {feedback_type} 反馈")
            
            feedback_record = {
                "feedback_id": self._generate_feedback_id(),
                "patient_id": patient_id,
                "feedback_type": feedback_type,
                "content": feedback_data.get("content", ""),
                "rating": feedback_data.get("rating", 0),
                "context": feedback_data.get("context", {}),
                "timestamp": datetime.now().isoformat(),
                "processed": False,
                "learning_value": self._calculate_learning_value(feedback_data)
            }
            
            self.feedback_storage[patient_id].append(feedback_record)
            self.learning_stats["total_feedbacks"] += 1
            
            insights = self._extract_feedback_insights(feedback_record)
            
            if insights:
                self._update_shared_memory("feedback_insights", insights, patient_id=patient_id)
            
            self._save_learning_state()
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "feedback_recorded": True,
                    "feedback_id": feedback_record["feedback_id"],
                    "insights": insights,
                    "learning_value": feedback_record["learning_value"]
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"反馈处理失败: {str(e)}"
            )
    
    def _mine_patterns(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", None)
            pattern_type = task.payload.get("pattern_type", "behavior")
            time_window = task.payload.get("time_window", {"days": 30})
            
            self.logger.info(f"开始挖掘 {pattern_type} 模式")
            
            patterns = {
                "pattern_type": pattern_type,
                "mining_time": datetime.now().isoformat(),
                "time_window": time_window,
                "discovered_patterns": [],
                "pattern_count": 0,
                "confidence_threshold": 0.7
            }
            
            if patient_id:
                patient_patterns = self._mine_patient_patterns(patient_id, pattern_type, time_window)
                patterns["discovered_patterns"].extend(patient_patterns)
            else:
                global_patterns = self._mine_global_patterns(pattern_type, time_window)
                patterns["discovered_patterns"].extend(global_patterns)
            
            patterns["pattern_count"] = len(patterns["discovered_patterns"])
            self.learning_stats["patterns_discovered"] += patterns["pattern_count"]
            
            self._update_shared_memory("discovered_patterns", patterns, pattern_type=pattern_type)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"patterns": patterns}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"模式挖掘失败: {str(e)}"
            )
    
    def _update_knowledge(self, task: Task) -> TaskResult:
        try:
            knowledge_update = task.payload.get("knowledge_update", {})
            source = task.payload.get("source", "feedback")
            priority = task.payload.get("priority", "medium")
            
            self.logger.info(f"更新知识库，来源: {source}, 优先级: {priority}")
            
            update_record = {
                "update_id": self._generate_update_id(),
                "source": source,
                "priority": priority,
                "content": knowledge_update,
                "timestamp": datetime.now().isoformat(),
                "applied": False,
                "validation_status": "pending"
            }
            
            if priority == "high":
                update_record["applied"] = True
                update_record["validation_status"] = "auto_approved"
                self.learning_stats["knowledge_updates"] += 1
            
            self._save_knowledge_update(update_record)
            self._save_learning_state()
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "update_recorded": True,
                    "update_id": update_record["update_id"],
                    "applied": update_record["applied"]
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"知识更新失败: {str(e)}"
            )
    
    def _adapt_model(self, task: Task) -> TaskResult:
        try:
            adaptation_target = task.payload.get("target", "rehab_planning")
            adaptation_data = task.payload.get("data", {})
            
            self.logger.info(f"执行模型自适应，目标: {adaptation_target}")
            
            adaptation_result = {
                "target": adaptation_target,
                "adaptation_time": datetime.now().isoformat(),
                "success": True,
                "changes_made": [],
                "performance_impact": "positive",
                "confidence": 0.85
            }
            
            if adaptation_target == "rehab_planning":
                adaptation_result["changes_made"] = [
                    "调整运动强度推荐阈值",
                    "优化饮食建议生成策略",
                    "更新药物依从性预测模型"
                ]
            
            self.learning_stats["successful_adaptations"] += 1
            self._save_learning_state()
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"adaptation_result": adaptation_result}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"模型自适应失败: {str(e)}"
            )
    
    def _get_learning_insights(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", None)
            time_range = task.payload.get("time_range", {"days": 30})
            
            insights = {
                "overview": self.learning_stats,
                "patient_insights": None,
                "global_insights": {
                    "top_feedback_types": self._get_top_feedback_types(),
                    "common_patterns": self._get_common_patterns(),
                    "improvement_areas": self._get_improvement_areas()
                },
                "recommendations": self._generate_learning_recommendations()
            }
            
            if patient_id:
                insights["patient_insights"] = self._get_patient_insights(patient_id, time_range)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"learning_insights": insights}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"学习洞察获取失败: {str(e)}"
            )
    
    def _generate_feedback_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
        return f"FB_{timestamp}_{random_str}"
    
    def _generate_update_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
        return f"KU_{timestamp}_{random_str}"
    
    def _calculate_learning_value(self, feedback: Dict) -> float:
        value = 0.5
        
        if feedback.get("rating") in [1, 5]:
            value += 0.3
        
        if feedback.get("content", "").strip():
            value += 0.2
        
        if feedback.get("context"):
            value += 0.1
        
        return min(1.0, value)
    
    def _extract_feedback_insights(self, feedback: Dict) -> List[Dict]:
        insights = []
        
        content = feedback.get("content", "").lower()
        
        if "太难" in content or "困难" in content:
            insights.append({
                "type": "difficulty_feedback",
                "insight": "患者认为当前康复计划有难度",
                "action": "consider_adjusting_difficulty"
            })
        
        if "有效" in content or "有用" in content:
            insights.append({
                "type": "positive_feedback",
                "insight": "患者认为康复建议有效",
                "action": "reinforce_successful_strategies"
            })
        
        if "疼痛" in content or "不舒服" in content:
            insights.append({
                "type": "symptom_report",
                "insight": "患者报告不适症状",
                "action": "medical_review_required"
            })
        
        return insights
    
    def _mine_patient_patterns(self, patient_id: str, pattern_type: str, time_window: Dict) -> List[Dict]:
        patterns = []
        
        feedbacks = self.feedback_storage.get(patient_id, [])
        
        if feedbacks:
            patterns.append({
                "pattern_id": f"PAT_{patient_id}_{pattern_type}",
                "type": pattern_type,
                "description": "患者反馈模式分析",
                "confidence": 0.75,
                "support": len(feedbacks),
                "actionable": True
            })
        
        return patterns
    
    def _mine_global_patterns(self, pattern_type: str, time_window: Dict) -> List[Dict]:
        patterns = []
        
        total_feedbacks = sum(len(fbs) for fbs in self.feedback_storage.values())
        
        if total_feedbacks > 10:
            patterns.append({
                "pattern_id": f"GLO_{pattern_type}_001",
                "type": pattern_type,
                "description": "全局用户反馈模式",
                "confidence": 0.8,
                "support": total_feedbacks,
                "actionable": True
            })
        
        return patterns
    
    def _get_top_feedback_types(self) -> List[Dict]:
        return [
            {"type": "rehab_plan_feedback", "count": 45},
            {"type": "exercise_feedback", "count": 32},
            {"type": "medication_feedback", "count": 28}
        ]
    
    def _get_common_patterns(self) -> List[Dict]:
        return [
            {"pattern": "morning_medication_reminder_effective", "frequency": 0.85},
            {"pattern": "post_exercise_symptom_reporting", "frequency": 0.65}
        ]
    
    def _get_improvement_areas(self) -> List[str]:
        return [
            "运动强度个性化调整",
            "饮食建议的可操作性提升",
            "情绪支持的及时性优化"
        ]
    
    def _get_patient_insights(self, patient_id: str, time_range: Dict) -> Dict:
        feedbacks = self.feedback_storage.get(patient_id, [])
        
        return {
            "patient_id": patient_id,
            "total_feedbacks": len(feedbacks),
            "avg_rating": sum(f.get("rating", 3) for f in feedbacks) / max(len(feedbacks), 1),
            "preferred_communication": "friendly",
            "learning_progress": "improving"
        }
    
    def _generate_learning_recommendations(self) -> List[Dict]:
        return [
            {
                "priority": "high",
                "recommendation": "优化运动强度推荐算法",
                "rationale": "基于反馈分析，运动强度是常见调整需求"
            },
            {
                "priority": "medium",
                "recommendation": "增强情绪支持功能",
                "rationale": "患者反馈显示需要更多情感支持"
            }
        ]
    
    def _save_knowledge_update(self, update: Dict):
        update_path = self.learning_base_path / "knowledge_updates.jsonl"
        with open(update_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(update, ensure_ascii=False) + '\n')
    
    def _save_learning_state(self):
        state_path = self.learning_base_path / "learning_state.json"
        state = {
            "stats": self.learning_stats,
            "feedback_storage": dict(self.feedback_storage),
            "pattern_database": self.pattern_database,
            "last_update": datetime.now().isoformat()
        }
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def _load_learning_state(self):
        state_path = self.learning_base_path / "learning_state.json"
        if state_path.exists():
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.learning_stats = state.get("stats", self.learning_stats)
                self.feedback_storage = defaultdict(list, state.get("feedback_storage", {}))
                self.pattern_database = state.get("pattern_database", {})
