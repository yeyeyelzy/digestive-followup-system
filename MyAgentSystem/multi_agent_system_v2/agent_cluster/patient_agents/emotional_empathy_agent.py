from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys
import random

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability


class EmotionalEmpathyAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="emotional_empathy_agent",
            agent_role="情感共情专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="emotion_detection",
                description="情感状态检测",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="empathy_response",
                description="共情回应生成",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="motivation_support",
                description="激励支持",
                version="1.0.0",
                enabled=True
            )
        ]
        self.empathy_templates = {
            "encouragement": [
                "你做得非常棒！继续保持这个势头！",
                "每一步的努力都是值得的，我为你感到骄傲！",
                "坚持就是胜利，相信你一定能做到！",
                "你的进步真的很明显，太棒了！"
            ],
            "comfort": [
                "我理解你的感受，这确实不容易。",
                "别担心，慢慢来，我们一起面对。",
                "有我陪着你，你不是一个人在战斗。",
                "每个人都会有困难的时候，这很正常。"
            ],
            "celebration": [
                "太棒了！这是一个值得庆祝的时刻！",
                "恭喜你！你的努力得到了回报！",
                "真为你高兴！继续加油！"
            ],
            "support": [
                "需要什么帮助随时告诉我，我一直都在。",
                "如果你想聊聊，我随时都愿意倾听。",
                "有什么想法都可以和我说。"
            ]
        }
        
    def initialize(self) -> bool:
        try:
            self.logger.info("情感共情智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"情感共情智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "generate_empathy_response":
            return self._generate_empathy_response(task)
        elif task_type == "detect_emotional_state":
            return self._detect_emotional_state(task)
        elif task_type == "generate_motivation":
            return self._generate_motivation(task)
        elif task_type == "adjust_communication_style":
            return self._adjust_communication_style(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _generate_empathy_response(self, task: Task) -> TaskResult:
        try:
            user_input = task.payload.get("user_input", "")
            emotional_state = task.payload.get("emotional_state", "neutral")
            patient_profile = task.payload.get("patient_profile", {})
            context = task.payload.get("context", {})
            
            response = self._craft_empathy_response(
                user_input, emotional_state, patient_profile, context)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "emotional_response": response,
                    "emotional_state": emotional_state,
                    "response_style": self._determine_response_style(emotional_state)
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"共情回应生成失败: {str(e)}"
            )
    
    def _detect_emotional_state(self, task: Task) -> TaskResult:
        try:
            user_input = task.payload.get("user_input", "")
            conversation_history = task.payload.get("conversation_history", [])
            health_data = task.payload.get("health_data", {})
            
            emotional_analysis = {
                "primary_emotion": "neutral",
                "emotion_intensity": 0.5,
                "secondary_emotions": [],
                "triggers": [],
                "confidence": 0.7,
                "analysis_time": datetime.now().isoformat()
            }
            
            emotional_analysis = self._analyze_text_emotion(user_input, emotional_analysis)
            emotional_analysis = self._analyze_behavior_emotion(health_data, emotional_analysis)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"emotional_analysis": emotional_analysis}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"情感状态检测失败: {str(e)}"
            )
    
    def _generate_motivation(self, task: Task) -> TaskResult:
        try:
            patient_profile = task.payload.get("patient_profile", {})
            recent_progress = task.payload.get("recent_progress", {})
            motivation_type = task.payload.get("motivation_type", "general")
            
            motivation_message = self._create_motivation_message(
                patient_profile, recent_progress, motivation_type)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "motivation_message": motivation_message,
                    "motivation_type": motivation_type
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"激励生成失败: {str(e)}"
            )
    
    def _adjust_communication_style(self, task: Task) -> TaskResult:
        try:
            patient_preferences = task.payload.get("preferences", {})
            emotional_state = task.payload.get("emotional_state", "neutral")
            
            communication_style = {
                "tone": self._get_tone(emotional_state),
                "formality": patient_preferences.get("formality", "casual"),
                "detail_level": patient_preferences.get("detail_level", "medium"),
                "use_empathy": True,
                "use_encouragement": emotional_state in ["sad", "frustrated", "anxious"],
                "response_length": patient_preferences.get("response_length", "medium")
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"communication_style": communication_style}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"沟通风格调整失败: {str(e)}"
            )
    
    def _craft_empathy_response(self, user_input: str, emotional_state: str, 
                                  patient_profile: Dict, context: Dict) -> str:
        name = patient_profile.get("basic_info", {}).get("name", "朋友")
        
        if emotional_state == "frustrated":
            template = random.choice(self.empathy_templates["comfort"])
            return f"{name}，{template} 你愿意和我说说发生了什么吗？"
        elif emotional_state == "happy" or "progress" in context:
            template = random.choice(self.empathy_templates["celebration"])
            return f"{name}，{template}"
        elif emotional_state == "sad" or emotional_state == "anxious":
            template = random.choice(self.empathy_templates["comfort"])
            return f"{name}，{template}"
        elif "努力" in user_input or "坚持" in user_input:
            template = random.choice(self.empathy_templates["encouragement"])
            return f"{name}，{template}"
        else:
            template = random.choice(self.empathy_templates["support"])
            return f"{name}，{template}"
    
    def _analyze_text_emotion(self, text: str, analysis: Dict) -> Dict:
        positive_keywords = ["好", "棒", "开心", "高兴", "不错", "进步", "成功"]
        negative_keywords = ["累", "难", "烦", "担心", "焦虑", "痛苦", "不好"]
        
        for keyword in positive_keywords:
            if keyword in text:
                analysis["primary_emotion"] = "happy"
                analysis["emotion_intensity"] = min(1.0, analysis["emotion_intensity"] + 0.2)
        
        for keyword in negative_keywords:
            if keyword in text:
                analysis["primary_emotion"] = "frustrated"
                analysis["emotion_intensity"] = min(1.0, analysis["emotion_intensity"] + 0.2)
        
        return analysis
    
    def _analyze_behavior_emotion(self, health_data: Dict, analysis: Dict) -> Dict:
        return analysis
    
    def _create_motivation_message(self, profile: Dict, progress: Dict, mtype: str) -> str:
        name = profile.get("basic_info", {}).get("name", "朋友")
        
        if mtype == "progress":
            return f"{name}，看到你的进步真的很开心！每一份努力都会有回报，继续保持！"
        elif mtype == "milestone":
            return f"{name}，恭喜你达成了这个重要的里程碑！这真的很不容易，为你骄傲！"
        elif mtype == "challenge":
            return f"{name}，我知道现在可能有些困难，但相信自己，你有能力克服它！我会一直陪着你。"
        else:
            return f"{name}，新的一天开始了，让我们一起为健康努力吧！你准备好了吗？"
    
    def _determine_response_style(self, emotional_state: str) -> str:
        styles = {
            "happy": "celebratory",
            "frustrated": "supportive",
            "anxious": "calming",
            "sad": "comforting",
            "neutral": "friendly"
        }
        return styles.get(emotional_state, "friendly")
    
    def _get_tone(self, emotional_state: str) -> str:
        tones = {
            "happy": "warm",
            "frustrated": "gentle",
            "anxious": "soothing",
            "sad": "compassionate",
            "neutral": "friendly"
        }
        return tones.get(emotional_state, "friendly")
