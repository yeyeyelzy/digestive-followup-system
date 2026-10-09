"""
多端差异化NLG生成器V2.0
实现患者/家属端拟人化共情输出，医生端专业结构化输出
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json


@dataclass
class NLGConfig:
    """NLG配置"""
    # 患者端配置
    patient_persona: str = "贴心、专业、有耐心的术后康复专属管家"
    patient_tone: str = "温暖、共情、鼓励"
    
    # 家属端配置
    family_persona: str = "专业、关怀的医疗助手"
    family_tone: str = "关怀、明确、有指导"
    
    # 医生端配置
    doctor_persona: str = "专业严谨的临床决策辅助系统"
    doctor_tone: str = "专业、结构化、循证"


class PatientNLG:
    """患者端NLG生成器 - 拟人化共情输出"""
    
    def __init__(self, config: NLGConfig = None):
        self.config = config or NLGConfig()
        
        # 专业术语替换表
        self.term_replacements = {
            "低密度脂蛋白胆固醇": "坏胆固醇",
            "高密度脂蛋白胆固醇": "好胆固醇",
            "静息心率": "安静时的心跳",
            "运动强度": "运动量大小",
            "METs": "活动量单位",
            "依从性": "听话程度",
            "PCI": "支架手术",
            "心肌梗死": "心梗",
            "心绞痛": "胸痛",
            "β受体阻滞剂": "控制心跳的药物",
            "他汀": "降血脂的药物",
            "抗血小板药物": "防止血液凝固的药物"
        }
        
        # 共情模板
        self.empathy_templates = [
            "我理解您的情况，",
            "我看到您的情况了，",
            "让我看看您的数据，",
            "您最近的情况是这样的，"
        ]
        
        # 鼓励模板
        self.encouragement_templates = [
            "继续保持哦！",
            "做得很好！",
            "继续加油！",
            "很棒，您做得很好！"
        ]
    
    def _replace_terms(self, text: str) -> str:
        """替换专业术语"""
        for term, replacement in self.term_replacements.items():
            text = text.replace(term, replacement)
        return text
    
    def _add_empathy(self, text: str) -> str:
        """添加共情表达"""
        import random
        return random.choice(self.empathy_templates) + text
    
    def _add_encouragement(self, text: str, is_positive: bool = True) -> str:
        """添加鼓励"""
        import random
        if is_positive:
            return text + " " + random.choice(self.encouragement_templates)
        return text
    
    def generate_health_summary(self, health_data: Dict[str, Any]) -> str:
        """
        生成患者端健康总结
        
        Args:
            health_data: 健康数据
            
        Returns:
            患者端自然语言输出
        """
        hr_mean = health_data.get('hr_mean', 70)
        steps_total = health_data.get('steps_total', 0)
        sleep_hours = health_data.get('sleep_hours', 0)
        risk_level = health_data.get('risk_level', 'low')
        
        parts = []
        
        # 心率部分
        if 55 <= hr_mean <= 95:
            parts.append(f"今天您安静时的心跳平均是 {hr_mean:.0f}次，控制得不错")
        elif hr_mean < 55:
            parts.append(f"今天您安静时的心跳稍微有点慢，平均是 {hr_mean:.0f}次")
        else:
            parts.append(f"今天您安静时的心跳有点快，平均是 {hr_mean:.0f}次，要多注意休息哦")
        
        # 步数部分
        if steps_total >= 3000:
            parts.append(f"今天走了 {steps_total:.0f}步，活动量很充足")
        elif steps_total >= 1000:
            parts.append(f"今天走了 {steps_total:.0f}步，还可以再多活动活动")
        else:
            parts.append(f"今天只走了 {steps_total:.0f}步，建议适当增加一些轻度活动")
        
        # 睡眠部分
        if sleep_hours >= 7:
            parts.append(f"今天睡了 {sleep_hours:.1f}小时，睡眠质量不错")
        elif sleep_hours >= 6:
            parts.append(f"今天睡了 {sleep_hours:.1f}小时，还可以")
        else:
            parts.append(f"今天只睡了 {sleep_hours:.1f}小时，要注意保证睡眠哦")
        
        # 组合并添加共情
        summary = "，".join(parts)
        summary = self._add_empathy(summary)
        
        # 替换专业术语
        summary = self._replace_terms(summary)
        
        return summary
    
    def generate_exercise_advice(self, exercise_plan: Dict[str, Any]) -> str:
        """
        生成运动建议"""
        target_hr_low = exercise_plan.get('target_hr_low', 55)
        target_hr_high = exercise_plan.get('target_hr_high', 95)
        max_steps = exercise_plan.get('max_steps', 4500)
        activities = exercise_plan.get('recommended_activities', [])
        
        advice_parts = []
        
        advice_parts.append(f"咱们的目标心跳范围是 {target_hr_low}-{target_hr_high}次/分钟")
        advice_parts.append(f"每天步数控制在 {max_steps}步以内比较合适")
        
        if activities:
            advice_parts.append(f"推荐活动：{'、'.join(activities)}")
        
        advice = "，".join(advice_parts)
        advice = self._replace_terms(advice)
        
        return advice
    
    def generate_medication_reminder(self, medications: list) -> str:
        """
        生成用药提醒"""
        if not medications:
            reminder = "记得按时吃药哦！"
            return reminder
        return ""


class FamilyNLG:
    """家属端NLG生成器 - 兼顾易懂性与专业性"""
    
    def __init__(self, config: NLGConfig = None):
        self.config = config or NLGConfig()
    
    def generate_care_advice(self, patient_data: Dict[str, Any]) -> str:
        """
        生成家属端照护建议
        
        Args:
            patient_data: 患者数据
            
        Returns:
            家属端自然语言输出
        """
        patient_id = patient_data.get('patient_id', '')
        risk_level = patient_data.get('risk_level', 'low')
        
        parts = []
        parts.append(f"患者 {patient_id} 的最新情况：")
        
        if risk_level == 'low':
            parts.append("目前情况稳定，请继续保持")
        elif risk_level == 'medium':
            parts.append("需要关注，建议增加监测频率")
        else:
            parts.append("风险较高，建议及时联系医生")
        
        return "".join(parts)


class DoctorNLG:
    """医生端NLG生成器 - 专业结构化输出"""
    
    def __init__(self, config: NLGConfig = None):
        self.config = config or NLGConfig()
        
        # 循证标注模板
        self.evidence_template = "依据《中国冠心病康复与二级预防指南(2024》"
    
    def generate_structured_report(self, patient_data: Dict[str, Any], 
                               analysis: Dict[str, Any],
                               rehab_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成医生端结构化报告
        
        Args:
            patient_data: 患者数据
            analysis: 分析结果
            rehab_plan: 康复方案
            
        Returns:
            医生端结构化报告
        """
        report = {
            "patient_info": {
                "patient_id": patient_data.get('patient_id', ''),
                "name": patient_data.get('name', ''),
                "age": patient_data.get('age', ''),
                "diagnosis": patient_data.get('diagnosis', ''),
                "days_post_op": patient_data.get('days_post_op', 0),
                "comorbidities": patient_data.get('comorbidities', [])
            },
            "core_data_summary": {
                "period": "2026-04-15至2026-05-12",
                "heart_rate": {
                    "mean": analysis.get('hr_mean', 0),
                    "min": analysis.get('hr_min', 0),
                    "max": analysis.get('hr_max', 0),
                    "trend": "stable"
                },
                "activity": {
                    "steps_total": analysis.get('steps_total', 0),
                    "moderate_high_min": analysis.get('moderate_high_min', 0)
                },
                "sleep": {
                    "sleep_hours": analysis.get('sleep_hours', 0),
                    "sleep_efficiency": analysis.get('sleep_efficiency', 0)
                },
                "medication_adherence": analysis.get('medication_adherence', 'good')
            },
            "risk_analysis": {
                "risk_level": analysis.get('risk_level', 'low'),
                "abnormal_indicators": [],
                "evidence_basis": ""
            },
            "rehab_plan_assessment": {
                "current_plan": rehab_plan,
                "compliance_rate": 0.8,
                "problems": []
            },
            "evidence_based_adjustments": [],
            "key_focus_areas": []
        }
        
        return report
    
    def generate_evidence_annotation(self, content: str, evidence: str) -> str:
        """
        生成循证标注"""
        return f"{content}（{self.evidence_template}）"


class MultiEndNLG:
    """多端NLG统一接口"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.patient_nlg = PatientNLG()
        self.family_nlg = FamilyNLG()
        self.doctor_nlg = DoctorNLG()
    
    def generate(self, end_type: str, data: Dict[str, Any], 
                 content_type: str = "health_summary") -> Any:
        """
        生成多端内容
        
        Args:
            end_type: 端类型 (patient/family/doctor)
            data: 数据
            content_type: 内容类型
            
        Returns:
            生成的内容
        """
        if end_type == "patient":
            if content_type == "health_summary":
                return self.patient_nlg.generate_health_summary(data)
            elif content_type == "exercise_advice":
                return self.patient_nlg.generate_exercise_advice(data)
            elif content_type == "medication_reminder":
                return self.patient_nlg.generate_medication_reminder(data)
        
        elif end_type == "family":
            if content_type == "care_advice":
                return self.family_nlg.generate_care_advice(data)
        
        elif end_type == "doctor":
            if content_type == "structured_report":
                return self.doctor_nlg.generate_structured_report(
                    data.get('patient', {}),
                    data.get('analysis', {}),
                    data.get('plan', {})
                )
        
        return None
    
    def generate_patient_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成患者端响应"""
        intent = data.get("intent", "general_query")
        rehab_plan = data.get("rehab_plan", {})
        fused_data = data.get("fused_data", {})
        
        # 构建患者端响应，包含图文并茂的格式
        response = {
            "type": "patient_response",
            "content": "",
            "visuals": [],
            "recommendations": []
        }
        
        if intent == "fatigue_inquiry":
            response["content"] = "我理解您的感受，支架手术后恢复需要时间。根据您的身体数据，我为您准备了一些建议："
            response["recommendations"] = [
                "适当休息，避免过度劳累",
                "保持规律作息，保证充足睡眠",
                "如果疲劳持续加重，请及时联系医生"
            ]
        elif intent == "exercise_advice":
            exercise = rehab_plan.get("exercise_plan", {})
            activities = exercise.get("recommended_activities", [])
            response["content"] = "根据您的身体状况，我为您制定了适合的运动计划："
            response["recommendations"] = [
                f"推荐运动：{'、'.join(activities)}",
                "每次运动时间控制在30分钟内",
                "运动时注意监测心率，保持在目标范围内"
            ]
            response["visuals"].append({
                "type": "chart",
                "title": "运动心率目标范围",
                "data": {
                    "target_low": exercise.get("target_hr_low", 55),
                    "target_high": exercise.get("target_hr_high", 95)
                }
            })
        elif intent == "heart_rate_inquiry":
            hr_stats = fused_data.get("heart_rate", {}).get("stats", {})
            hr_mean = hr_stats.get("mean", 70)
            if 55 <= hr_mean <= 95:
                response["content"] = f"您的平均心率是 {hr_mean:.0f} 次/分钟，控制得不错！"
            elif hr_mean < 55:
                response["content"] = f"您的平均心率是 {hr_mean:.0f} 次/分钟，稍微有点慢，请注意观察。"
            else:
                response["content"] = f"您的平均心率是 {hr_mean:.0f} 次/分钟，有点快，建议多休息。"
            response["visuals"].append({
                "type": "chart",
                "title": "心率趋势",
                "data": hr_stats
            })
        else:
            response["content"] = "您好！我是您的术后康复助手。有什么可以帮您的吗？"
        
        return response
    
    def generate_family_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成家属端响应"""
        patient_id = data.get("patient_id", "P_001")
        fused_data = data.get("fused_data", {})
        rehab_plan = data.get("rehab_plan", {})
        
        # 构建家属端响应
        response = {
            "type": "family_response",
            "content": f"患者 {patient_id} 的当前情况：",
            "care_advice": [],
            "important_notes": []
        }
        
        # 添加照护建议
        response["care_advice"] = [
            "按照康复计划督促患者按时服药",
            "鼓励患者进行适量的运动",
            "注意观察患者的情绪变化",
            "定期监测患者的心率和血压"
        ]
        
        # 添加重要注意事项
        response["important_notes"] = [
            "如发现患者出现胸痛、呼吸困难等症状，请立即就医",
            "保持患者居住环境安静舒适",
            "帮助患者建立规律的作息时间"
        ]
        
        return response
    
    def generate_doctor_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成医生端报告"""
        patient_id = data.get("patient_id", "P_001")
        patient_profile = data.get("patient_profile", {})
        fused_data = data.get("fused_data", {})
        rehab_plan = data.get("rehab_plan", {})
        validation_result = data.get("validation_result", {})
        
        # 提取关键数据
        hr_stats = fused_data.get("heart_rate", {}).get("stats", {})
        activity_stats = fused_data.get("activity", {}).get("stats", {})
        sleep_stats = fused_data.get("sleep", {}).get("stats", {})
        
        # 构建医生端报告，增强专业性
        report = {
            "structured_report": {
                "report_id": f"DR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "patient_id": patient_id,
                "generated_at": datetime.now().isoformat(),
                "patient_info": {
                    "name": patient_profile.get("name", ""),
                    "age": patient_profile.get("age", ""),
                    "diagnosis": patient_profile.get("diagnosis", ""),
                    "days_post_op": patient_profile.get("days_post_op", 0),
                    "comorbidities": patient_profile.get("comorbidities", [])
                },
                "data_analysis": {
                    "heart_rate": {
                        "mean": hr_stats.get("mean", 0),
                        "min": hr_stats.get("min", 0),
                        "max": hr_stats.get("max", 0),
                        "analysis": "",
                        "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                    },
                    "activity": {
                        "mean_steps": activity_stats.get("mean_steps", 0),
                        "total_distance": activity_stats.get("total_distance", 0),
                        "active_minutes": activity_stats.get("active_minutes", 0),
                        "analysis": "",
                        "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                    },
                    "sleep": {
                        "mean_sleep_duration": sleep_stats.get("mean_sleep_duration", 0),
                        "analysis": "",
                        "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                    }
                },
                "clinical_assessment": {
                    "condition_status": "",
                    "complications": [],
                    "risk_level": "",
                    "evidence_basis": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "rehab_plan_evaluation": {
                    "current_plan": rehab_plan,
                    "compliance": "",
                    "recommendations": []
                },
                "visuals": [
                    {
                        "type": "heart_rate_chart",
                        "title": "心率变化趋势",
                        "data": hr_stats
                    },
                    {
                        "type": "activity_chart",
                        "title": "活动量统计",
                        "data": activity_stats
                    },
                    {
                        "type": "sleep_chart",
                        "title": "睡眠质量分析",
                        "data": sleep_stats
                    }
                ]
            }
        }
        
        # 分析心率数据
        hr_mean = hr_stats.get("mean", 70)
        if 55 <= hr_mean <= 65:
            report["structured_report"]["data_analysis"]["heart_rate"]["analysis"] = "心率控制良好，符合术后康复目标"
        elif hr_mean < 55:
            report["structured_report"]["data_analysis"]["heart_rate"]["analysis"] = "心率偏低，需关注是否与药物相关"
        else:
            report["structured_report"]["data_analysis"]["heart_rate"]["analysis"] = "心率偏高，需调整康复方案"
        
        # 分析活动数据
        mean_steps = activity_stats.get("mean_steps", 0)
        if mean_steps >= 3000:
            report["structured_report"]["data_analysis"]["activity"]["analysis"] = "活动量充足，符合康复要求"
        elif mean_steps >= 1000:
            report["structured_report"]["data_analysis"]["activity"]["analysis"] = "活动量适中，可适当增加"
        else:
            report["structured_report"]["data_analysis"]["activity"]["analysis"] = "活动量不足，需加强运动"
        
        # 分析睡眠数据
        sleep_duration = sleep_stats.get("mean_sleep_duration", 0)
        if sleep_duration >= 7:
            report["structured_report"]["data_analysis"]["sleep"]["analysis"] = "睡眠质量良好"
        elif sleep_duration >= 6:
            report["structured_report"]["data_analysis"]["sleep"]["analysis"] = "睡眠质量一般"
        else:
            report["structured_report"]["data_analysis"]["sleep"]["analysis"] = "睡眠不足，需改善"
        
        # 临床评估
        report["structured_report"]["clinical_assessment"]["condition_status"] = "患者术后恢复良好，无明显加重迹象"
        report["structured_report"]["clinical_assessment"]["complications"] = "未发现明显并发症"
        report["structured_report"]["clinical_assessment"]["risk_level"] = "低风险"
        
        # 康复方案评估
        report["structured_report"]["rehab_plan_evaluation"]["compliance"] = "患者依从性良好"
        report["structured_report"]["rehab_plan_evaluation"]["recommendations"] = [
            "继续当前康复方案",
            "定期监测心率和血压",
            "保持适量运动",
            "维持健康饮食习惯"
        ]
        
        return report
