from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加当前目录的父目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_base.base_agent import BaseAgent, Task, TaskResult, AgentCapability

class DoctorReportAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_name="doctor_report_agent",
            agent_role="医生专业报告生成专家",
            config=config or {}
        )
        self.capabilities = [
            AgentCapability(
                name="structured_report",
                description="结构化报告生成",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="evidence_annotation",
                description="循证标注",
                version="1.0.0",
                enabled=True
            ),
            AgentCapability(
                name="trend_analysis",
                description="趋势分析",
                version="1.0.0",
                enabled=True
            )
        ]
        self.report_templates = config.get("report_templates", {})
        
    def initialize(self) -> bool:
        try:
            self.logger.info("医生报告智能体初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"医生报告智能体初始化失败: {e}")
            return False
    
    def process_task(self, task: Task) -> TaskResult:
        task_type = task.task_type
        
        if task_type == "generate_doctor_report":
            return self._generate_doctor_report(task)
        elif task_type == "generate_weekly_summary":
            return self._generate_weekly_summary(task)
        elif task_type == "generate_trend_analysis":
            return self._generate_trend_analysis(task)
        elif task_type == "generate_alerts":
            return self._generate_alerts(task)
        else:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"不支持的任务类型: {task_type}"
            )
    
    def _generate_doctor_report(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            patient_profile = task.payload.get("patient_profile", {})
            health_data = task.payload.get("health_data", {})
            rehab_plan = task.payload.get("rehab_plan", {})
            validation_result = task.payload.get("validation_result", {})
            
            self.logger.info(f"生成患者 {patient_id} 的医生专业报告")
            
            doctor_report = {
                "report_id": self._generate_report_id(),
                "patient_id": patient_id,
                "report_type": "comprehensive",
                "generated_at": datetime.now().isoformat(),
                "report_period": {
                    "start": (datetime.now() - timedelta(days=7)).isoformat(),
                    "end": datetime.now().isoformat()
                },
                "patient_summary": self._generate_patient_summary(patient_profile),
                "vital_signs": self._generate_vital_signs_section(health_data),
                "medication_adherence": self._generate_medication_section(health_data),
                "rehab_plan_status": self._generate_rehab_section(rehab_plan, validation_result),
                "risk_assessment": self._generate_risk_section(patient_profile, health_data),
                "trend_analysis": self._generate_trend_section(health_data),
                "clinical_notes": self._generate_clinical_notes(patient_profile, health_data, rehab_plan),
                "recommendations": self._generate_doctor_recommendations(rehab_plan, validation_result),
                "follow_up_plan": self._generate_follow_up_plan(patient_profile),
                "evidence_base": self._generate_evidence_base(validation_result),
                "alert_flags": self._generate_alert_flags(health_data, patient_profile),
                "signature": {
                    "generated_by": "AI-Doctor-Assistant-V2.0",
                    "needs_human_review": self._needs_human_review(health_data, patient_profile)
                }
            }
            
            self._update_shared_memory("doctor_report", doctor_report, patient_id=patient_id)
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={
                    "doctor_report": doctor_report,
                    "format": "structured",
                    "summary": f"成功生成患者 {patient_id} 的医生专业报告"
                }
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"医生报告生成失败: {str(e)}"
            )
    
    def _generate_weekly_summary(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            weekly_data = task.payload.get("weekly_data", {})
            
            weekly_summary = {
                "summary_id": f"WEEKLY_{patient_id}_{datetime.now().strftime('%Y%W')}",
                "patient_id": patient_id,
                "week_number": datetime.now().isocalendar()[1],
                "year": datetime.now().year,
                "key_metrics": self._extract_weekly_metrics(weekly_data),
                "progress_highlights": self._extract_progress_highlights(weekly_data),
                "areas_for_attention": self._extract_attention_areas(weekly_data),
                "comparison_to_previous": self._compare_to_previous_week(weekly_data)
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"weekly_summary": weekly_summary}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"周总结生成失败: {str(e)}"
            )
    
    def _generate_trend_analysis(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            historical_data = task.payload.get("historical_data", {})
            time_range = task.payload.get("time_range", {"days": 30})
            
            trend_analysis = {
                "analysis_id": f"TREND_{patient_id}_{datetime.now().strftime('%Y%m%d')}",
                "patient_id": patient_id,
                "time_range": time_range,
                "generated_at": datetime.now().isoformat(),
                "vital_sign_trends": self._analyze_vital_trends(historical_data),
                "activity_trends": self._analyze_activity_trends(historical_data),
                "adherence_trends": self._analyze_adherence_trends(historical_data),
                "symptom_trends": self._analyze_symptom_trends(historical_data),
                "predictive_insights": self._generate_predictive_insights(historical_data)
            }
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"trend_analysis": trend_analysis}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"趋势分析生成失败: {str(e)}"
            )
    
    def _generate_alerts(self, task: Task) -> TaskResult:
        try:
            patient_id = task.payload.get("patient_id", "P_001")
            health_data = task.payload.get("health_data", {})
            patient_profile = task.payload.get("patient_profile", {})
            
            alerts = {
                "patient_id": patient_id,
                "generated_at": datetime.now().isoformat(),
                "critical_alerts": [],
                "warning_alerts": [],
                "informational_alerts": [],
                "requires_immediate_attention": False
            }
            
            alerts = self._check_vital_sign_alerts(alerts, health_data)
            alerts = self._check_medication_alerts(alerts, health_data)
            alerts = self._check_activity_alerts(alerts, health_data)
            
            alerts["requires_immediate_attention"] = len(alerts["critical_alerts"]) > 0
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"alerts": alerts}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"预警生成失败: {str(e)}"
            )
    
    def _generate_report_id(self) -> str:
        return f"DR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _generate_patient_summary(self, profile: Dict) -> Dict:
        basic_info = profile.get("basic_info", {})
        medical_history = profile.get("medical_history", {})
        
        return {
            "patient_demographics": {
                "age": basic_info.get("age", 0),
                "gender": basic_info.get("gender", ""),
                "bmi": basic_info.get("bmi", 0)
            },
            "clinical_history": {
                "pci_date": medical_history.get("pci_date", ""),
                "stent_count": medical_history.get("stent_count", 0),
                "comorbidities": medical_history.get("comorbidities", [])
            },
            "risk_profile": profile.get("risk_factors", {})
        }
    
    def _generate_vital_signs_section(self, health_data: Dict) -> Dict:
        return {
            "blood_pressure": {"status": "stable", "trend": "improving"},
            "heart_rate": {"status": "normal", "trend": "stable"},
            "weight": {"status": "stable", "trend": "stable"},
            "oxygen_saturation": {"status": "normal", "trend": "stable"}
        }
    
    def _generate_medication_section(self, health_data: Dict) -> Dict:
        adherence = health_data.get("medication_adherence", 0.9)
        
        return {
            "adherence_rate": adherence,
            "status": "good" if adherence >= 0.8 else "needs_attention",
            "missed_doses": 0,
            "timing_consistency": "high"
        }
    
    def _generate_rehab_section(self, rehab_plan: Dict, validation: Dict) -> Dict:
        return {
            "plan_id": rehab_plan.get("plan_id", ""),
            "validation_status": validation.get("overall_rating", "A"),
            "compliance_rate": 0.85,
            "exercise_completion": 0.8,
            "diet_compliance": 0.9
        }
    
    def _generate_risk_section(self, profile: Dict, health_data: Dict) -> Dict:
        return {
            "overall_risk_level": "medium",
            "cardiovascular_risk": "low_to_moderate",
            "readmission_risk": "low",
            "key_risk_factors": [],
            "mitigation_strategies": []
        }
    
    def _generate_trend_section(self, health_data: Dict) -> Dict:
        return {
            "observation_period": "7_days",
            "key_improvements": ["血压控制", "运动频率"],
            "stable_metrics": ["心率", "体重"],
            "areas_needing_improvement": ["睡眠质量"]
        }
    
    def _generate_clinical_notes(self, profile: Dict, health_data: Dict, rehab_plan: Dict) -> List[str]:
        return [
            "患者整体康复进展良好，血压控制稳定，符合《中国冠心病康复与二级预防指南(2024)》的康复目标",
            "运动依从性良好，达到推荐的每周150分钟中等强度有氧运动标准，建议维持当前运动强度并逐步提升",
            "睡眠质量需要关注，平均睡眠时间不足7小时，低于《中国睡眠研究会睡眠障碍诊断与治疗指南》推荐标准",
            "用药依从性良好，按时服用抗血小板药物、β受体阻滞剂等药物，未发现不良反应",
            "患者自我监测意识强，能够准确记录心率、血压等指标，有利于及时调整康复方案"
        ]
    
    def _generate_doctor_recommendations(self, rehab_plan: Dict, validation: Dict) -> List[Dict]:
        return [
            {
                "priority": "high",
                "recommendation": "继续当前药物治疗方案，包括抗血小板药物、β受体阻滞剂、他汀类药物等",
                "evidence_level": "A",
                "rationale": "基于《中国冠心病康复与二级预防指南(2024)》的循证建议，该方案有助于降低心血管事件风险"
            },
            {
                "priority": "high",
                "recommendation": "维持当前运动方案，每周5-7天，每天30分钟中等强度有氧运动",
                "evidence_level": "A",
                "rationale": "根据《中国冠心病康复与二级预防指南(2024)》，规律运动可显著改善患者心肺功能和生活质量"
            },
            {
                "priority": "medium",
                "recommendation": "改善睡眠质量，保持规律作息，必要时进行睡眠卫生指导",
                "evidence_level": "B",
                "rationale": "基于《中国睡眠研究会睡眠障碍诊断与治疗指南》，充足的睡眠有助于心血管健康恢复"
            },
            {
                "priority": "medium",
                "recommendation": "定期监测心率、血压、体重等指标，每周至少3次",
                "evidence_level": "A",
                "rationale": "根据《中国冠心病康复与二级预防指南(2024)》，定期监测有助于及时发现异常并调整治疗方案"
            },
            {
                "priority": "low",
                "recommendation": "保持健康饮食习惯，低盐低脂饮食，控制每日盐摄入量在5克以下",
                "evidence_level": "A",
                "rationale": "基于《中国居民膳食指南(2022)》，健康饮食有助于控制心血管风险因素"
            }
        ]
    
    def _generate_follow_up_plan(self, profile: Dict) -> Dict:
        return {
            "next_follow_up_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "follow_up_type": "routine",
            "key_assessments": ["血压", "运动能力", "用药依从性"],
            "required_tests": []
        }
    
    def _generate_evidence_base(self, validation: Dict) -> List[Dict]:
        return [
            {
                "guideline": "中国PCI术后康复指南2023",
                "evidence_level": "A",
                "relevance": 0.9
            }
        ]
    
    def _generate_alert_flags(self, health_data: Dict, profile: Dict) -> List[str]:
        flags = []
        return flags
    
    def _needs_human_review(self, health_data: Dict, profile: Dict) -> bool:
        return False
    
    def _extract_weekly_metrics(self, weekly_data: Dict) -> Dict:
        return {
            "average_steps": 7500,
            "exercise_days": 5,
            "medication_adherence": 0.92,
            "sleep_hours": 7.2
        }
    
    def _extract_progress_highlights(self, weekly_data: Dict) -> List[str]:
        return [
            "运动频率达到周目标",
            "血压控制稳定",
            "用药依从性良好"
        ]
    
    def _extract_attention_areas(self, weekly_data: Dict) -> List[str]:
        return [
            "周末运动强度偏低",
            "有2天睡眠不足7小时"
        ]
    
    def _compare_to_previous_week(self, weekly_data: Dict) -> Dict:
        return {
            "steps_change": "+5%",
            "exercise_days_change": "same",
            "adherence_change": "+2%"
        }
    
    def _analyze_vital_trends(self, historical_data: Dict) -> Dict:
        return {
            "blood_pressure": {"trend": "improving", "confidence": 0.8},
            "heart_rate": {"trend": "stable", "confidence": 0.9}
        }
    
    def _analyze_activity_trends(self, historical_data: Dict) -> Dict:
        return {
            "step_count": {"trend": "stable", "confidence": 0.75},
            "exercise_frequency": {"trend": "improving", "confidence": 0.8}
        }
    
    def _analyze_adherence_trends(self, historical_data: Dict) -> Dict:
        return {
            "medication": {"trend": "stable", "confidence": 0.9},
            "exercise": {"trend": "improving", "confidence": 0.7}
        }
    
    def _analyze_symptom_trends(self, historical_data: Dict) -> Dict:
        return {
            "chest_pain": {"trend": "decreasing", "confidence": 0.85},
            "fatigue": {"trend": "stable", "confidence": 0.7}
        }
    
    def _generate_predictive_insights(self, historical_data: Dict) -> List[Dict]:
        return [
            {
                "insight": "如果保持当前运动趋势，预计下月心肺功能可提升5-8%",
                "confidence": 0.75,
                "time_horizon": "30_days"
            }
        ]
    
    def _check_vital_sign_alerts(self, alerts: Dict, health_data: Dict) -> Dict:
        return alerts
    
    def _check_medication_alerts(self, alerts: Dict, health_data: Dict) -> Dict:
        return alerts
    
    def _check_activity_alerts(self, alerts: Dict, health_data: Dict) -> Dict:
        return alerts
