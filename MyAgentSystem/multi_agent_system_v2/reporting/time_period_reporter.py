from pathlib import Path
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加当前目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from data_processing.fitabase_data_processor import FitabaseDataProcessor
from agent_cluster.nlg_interaction.nlg_generator import MultiEndNLG

class TimePeriodReporter:
    """时间周期报告生成器"""
    
    def __init__(self):
        self.data_processor = FitabaseDataProcessor()
        self.nlg_generator = MultiEndNLG()
        self.patients = ["P_001", "P_002", "P_003"]
    
    def generate_daily_report(self, patient_id: str, date: str = None, end_type: str = "patient") -> Dict[str, Any]:
        """生成日报"""
        # 加载患者数据
        patient_data = self.data_processor.get_patient_data(patient_id)
        if not patient_data:
            return {"error": "患者数据加载失败"}
        
        # 生成基础数据报告
        daily_data = self.data_processor.generate_daily_report(patient_id, date)
        
        # 根据端类型生成不同的报告
        if end_type == "patient":
            return self._generate_patient_daily_report(daily_data, patient_data)
        elif end_type == "family":
            return self._generate_family_daily_report(daily_data, patient_data)
        elif end_type == "doctor":
            return self._generate_doctor_daily_report(daily_data, patient_data)
        else:
            return {"error": "未知的端类型"}
    
    def generate_weekly_report(self, patient_id: str, week_start: str = None, end_type: str = "patient") -> Dict[str, Any]:
        """生成周报"""
        # 加载患者数据
        patient_data = self.data_processor.get_patient_data(patient_id)
        if not patient_data:
            return {"error": "患者数据加载失败"}
        
        # 生成基础数据报告
        weekly_data = self.data_processor.generate_weekly_report(patient_id, week_start)
        
        # 根据端类型生成不同的报告
        if end_type == "patient":
            return self._generate_patient_weekly_report(weekly_data, patient_data)
        elif end_type == "family":
            return self._generate_family_weekly_report(weekly_data, patient_data)
        elif end_type == "doctor":
            return self._generate_doctor_weekly_report(weekly_data, patient_data)
        else:
            return {"error": "未知的端类型"}
    
    def generate_monthly_report(self, patient_id: str, month: str = None, end_type: str = "patient") -> Dict[str, Any]:
        """生成月报"""
        # 加载患者数据
        patient_data = self.data_processor.get_patient_data(patient_id)
        if not patient_data:
            return {"error": "患者数据加载失败"}
        
        # 生成基础数据报告
        monthly_data = self.data_processor.generate_monthly_report(patient_id, month)
        
        # 根据端类型生成不同的报告
        if end_type == "patient":
            return self._generate_patient_monthly_report(monthly_data, patient_data)
        elif end_type == "family":
            return self._generate_family_monthly_report(monthly_data, patient_data)
        elif end_type == "doctor":
            return self._generate_doctor_monthly_report(monthly_data, patient_data)
        else:
            return {"error": "未知的端类型"}
    
    def _generate_patient_daily_report(self, daily_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成患者端日报"""
        heart_rate = daily_data.get("heart_rate", {})
        activity = daily_data.get("activity", {})
        sleep = daily_data.get("sleep", {})
        
        # 构建患者端日报
        report = {
            "report_type": "daily",
            "end_type": "patient",
            "patient_id": daily_data.get("patient_id"),
            "date": daily_data.get("date"),
            "content": "",
            "visuals": [],
            "recommendations": []
        }
        
        # 构建内容
        content_parts = []
        if heart_rate:
            content_parts.append(f"今日平均心率：{heart_rate.get('mean', 0):.1f} 次/分钟")
        if activity:
            content_parts.append(f"今日步数：{activity.get('mean_steps', 0):.0f} 步")
        if sleep:
            content_parts.append(f"今日睡眠：{sleep.get('mean_sleep_duration', 0):.1f} 小时")
        
        report["content"] = "，".join(content_parts)
        
        # 添加可视化
        if heart_rate:
            report["visuals"].append({
                "type": "heart_rate_chart",
                "title": "今日心率",
                "data": heart_rate
            })
        if activity:
            report["visuals"].append({
                "type": "activity_chart",
                "title": "今日活动",
                "data": activity
            })
        if sleep:
            report["visuals"].append({
                "type": "sleep_chart",
                "title": "今日睡眠",
                "data": sleep
            })
        
        # 添加建议
        report["recommendations"] = [
            "继续保持规律的作息时间",
            "按照康复计划进行运动",
            "按时服药，定期监测身体状况"
        ]
        
        return report
    
    def _generate_family_daily_report(self, daily_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成家属端日报"""
        # 构建家属端日报
        report = {
            "report_type": "daily",
            "end_type": "family",
            "patient_id": daily_data.get("patient_id"),
            "date": daily_data.get("date"),
            "content": f"患者 {daily_data.get('patient_id')} 今日情况：",
            "care_advice": [],
            "important_notes": []
        }
        
        # 添加照护建议
        report["care_advice"] = [
            "督促患者按时服药",
            "鼓励患者进行适量的运动",
            "注意观察患者的情绪变化",
            "帮助患者保持规律的作息时间"
        ]
        
        # 添加重要注意事项
        report["important_notes"] = [
            "如发现患者出现不适症状，请及时联系医生",
            "确保患者饮食健康，避免油腻和辛辣食物",
            "保持患者居住环境安静舒适"
        ]
        
        return report
    
    def _generate_doctor_daily_report(self, daily_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成医生端日报"""
        heart_rate = daily_data.get("heart_rate", {})
        activity = daily_data.get("activity", {})
        sleep = daily_data.get("sleep", {})
        
        # 构建医生端日报
        report = {
            "report_type": "daily",
            "end_type": "doctor",
            "patient_id": daily_data.get("patient_id"),
            "date": daily_data.get("date"),
            "patient_info": patient_data.get("basic_info", {}),
            "data_analysis": {
                "heart_rate": {
                    "mean": heart_rate.get("mean", 0),
                    "min": heart_rate.get("min", 0),
                    "max": heart_rate.get("max", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "activity": {
                    "mean_steps": activity.get("mean_steps", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "sleep": {
                    "mean_sleep_duration": sleep.get("mean_sleep_duration", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                }
            },
            "clinical_assessment": {
                "condition_status": "",
                "risk_level": "",
                "recommendations": []
            },
            "visuals": []
        }
        
        # 分析心率数据
        hr_mean = heart_rate.get("mean", 70)
        if 55 <= hr_mean <= 65:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率控制良好，符合术后康复目标"
        elif hr_mean < 55:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率偏低，需关注是否与药物相关"
        else:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率偏高，需调整康复方案"
        
        # 分析活动数据
        mean_steps = activity.get("mean_steps", 0)
        if mean_steps >= 3000:
            report["data_analysis"]["activity"]["analysis"] = "活动量充足，符合康复要求"
        elif mean_steps >= 1000:
            report["data_analysis"]["activity"]["analysis"] = "活动量适中，可适当增加"
        else:
            report["data_analysis"]["activity"]["analysis"] = "活动量不足，需加强运动"
        
        # 分析睡眠数据
        sleep_duration = sleep.get("mean_sleep_duration", 0)
        if sleep_duration >= 7:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠质量良好"
        elif sleep_duration >= 6:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠质量一般"
        else:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠不足，需改善"
        
        # 临床评估
        report["clinical_assessment"]["condition_status"] = "患者术后恢复良好，无明显加重迹象"
        report["clinical_assessment"]["risk_level"] = "低风险"
        report["clinical_assessment"]["recommendations"] = [
            "继续当前康复方案",
            "定期监测心率和血压",
            "保持适量运动",
            "维持健康饮食习惯"
        ]
        
        # 添加可视化
        report["visuals"].append({
            "type": "heart_rate_chart",
            "title": "今日心率",
            "data": heart_rate
        })
        report["visuals"].append({
            "type": "activity_chart",
            "title": "今日活动",
            "data": activity
        })
        report["visuals"].append({
            "type": "sleep_chart",
            "title": "今日睡眠",
            "data": sleep
        })
        
        return report
    
    def _generate_patient_weekly_report(self, weekly_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成患者端周报"""
        # 构建患者端周报
        report = {
            "report_type": "weekly",
            "end_type": "patient",
            "patient_id": weekly_data.get("patient_id"),
            "week_start": weekly_data.get("week_start"),
            "week_end": weekly_data.get("week_end"),
            "content": weekly_data.get("summary", ""),
            "visuals": [],
            "recommendations": []
        }
        
        # 添加可视化
        report["visuals"].append({
            "type": "weekly_trend_chart",
            "title": "本周健康趋势",
            "data": {
                "heart_rate": weekly_data.get("heart_rate", {}),
                "activity": weekly_data.get("activity", {}),
                "sleep": weekly_data.get("sleep", {})
            }
        })
        
        # 添加建议
        report["recommendations"] = [
            "继续保持良好的生活习惯",
            "按照康复计划进行运动",
            "定期监测身体状况",
            "如有不适，及时联系医生"
        ]
        
        return report
    
    def _generate_family_weekly_report(self, weekly_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成家属端周报"""
        # 构建家属端周报
        report = {
            "report_type": "weekly",
            "end_type": "family",
            "patient_id": weekly_data.get("patient_id"),
            "week_start": weekly_data.get("week_start"),
            "week_end": weekly_data.get("week_end"),
            "content": f"患者 {weekly_data.get('patient_id')} 本周情况：",
            "care_advice": [],
            "important_notes": []
        }
        
        # 添加照护建议
        report["care_advice"] = [
            "督促患者按时服药",
            "鼓励患者进行适量的运动",
            "帮助患者保持规律的作息时间",
            "关注患者的情绪变化"
        ]
        
        # 添加重要注意事项
        report["important_notes"] = [
            "如发现患者出现不适症状，请及时联系医生",
            "确保患者饮食健康，避免油腻和辛辣食物",
            "保持患者居住环境安静舒适"
        ]
        
        return report
    
    def _generate_doctor_weekly_report(self, weekly_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成医生端周报"""
        # 构建医生端周报
        report = {
            "report_type": "weekly",
            "end_type": "doctor",
            "patient_id": weekly_data.get("patient_id"),
            "week_start": weekly_data.get("week_start"),
            "week_end": weekly_data.get("week_end"),
            "patient_info": patient_data.get("basic_info", {}),
            "data_analysis": {
                "heart_rate": {
                    "mean": weekly_data.get("heart_rate", {}).get("mean", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "activity": {
                    "mean_steps": weekly_data.get("activity", {}).get("mean_steps", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "sleep": {
                    "mean_sleep_duration": weekly_data.get("sleep", {}).get("mean_sleep_duration", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                }
            },
            "clinical_assessment": {
                "condition_status": "",
                "risk_level": "",
                "recommendations": []
            },
            "visuals": []
        }
        
        # 分析数据
        hr_mean = weekly_data.get("heart_rate", {}).get("mean", 70)
        mean_steps = weekly_data.get("activity", {}).get("mean_steps", 0)
        sleep_duration = weekly_data.get("sleep", {}).get("mean_sleep_duration", 0)
        
        if 55 <= hr_mean <= 65:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率控制良好，符合术后康复目标"
        elif hr_mean < 55:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率偏低，需关注是否与药物相关"
        else:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率偏高，需调整康复方案"
        
        if mean_steps >= 3000:
            report["data_analysis"]["activity"]["analysis"] = "活动量充足，符合康复要求"
        elif mean_steps >= 1000:
            report["data_analysis"]["activity"]["analysis"] = "活动量适中，可适当增加"
        else:
            report["data_analysis"]["activity"]["analysis"] = "活动量不足，需加强运动"
        
        if sleep_duration >= 7:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠质量良好"
        elif sleep_duration >= 6:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠质量一般"
        else:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠不足，需改善"
        
        # 临床评估
        report["clinical_assessment"]["condition_status"] = "患者术后恢复良好，无明显加重迹象"
        report["clinical_assessment"]["risk_level"] = "低风险"
        report["clinical_assessment"]["recommendations"] = [
            "继续当前康复方案",
            "定期监测心率和血压",
            "保持适量运动",
            "维持健康饮食习惯"
        ]
        
        # 添加可视化
        report["visuals"].append({
            "type": "weekly_trend_chart",
            "title": "本周健康趋势",
            "data": {
                "heart_rate": weekly_data.get("heart_rate", {}),
                "activity": weekly_data.get("activity", {}),
                "sleep": weekly_data.get("sleep", {})
            }
        })
        
        return report
    
    def _generate_patient_monthly_report(self, monthly_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成患者端月报"""
        # 构建患者端月报
        report = {
            "report_type": "monthly",
            "end_type": "patient",
            "patient_id": monthly_data.get("patient_id"),
            "month": monthly_data.get("month"),
            "content": monthly_data.get("summary", ""),
            "visuals": [],
            "recommendations": []
        }
        
        # 添加可视化
        report["visuals"].append({
            "type": "monthly_trend_chart",
            "title": "本月健康趋势",
            "data": {
                "heart_rate": monthly_data.get("heart_rate", {}),
                "activity": monthly_data.get("activity", {}),
                "sleep": monthly_data.get("sleep", {})
            }
        })
        
        # 添加建议
        report["recommendations"] = [
            "继续保持良好的生活习惯",
            "按照康复计划进行运动",
            "定期监测身体状况",
            "按时复诊，与医生沟通康复进展"
        ]
        
        return report
    
    def _generate_family_monthly_report(self, monthly_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成家属端月报"""
        # 构建家属端月报
        report = {
            "report_type": "monthly",
            "end_type": "family",
            "patient_id": monthly_data.get("patient_id"),
            "month": monthly_data.get("month"),
            "content": f"患者 {monthly_data.get('patient_id')} 本月情况：",
            "care_advice": [],
            "important_notes": []
        }
        
        # 添加照护建议
        report["care_advice"] = [
            "督促患者按时服药",
            "鼓励患者进行适量的运动",
            "帮助患者保持规律的作息时间",
            "关注患者的情绪变化"
        ]
        
        # 添加重要注意事项
        report["important_notes"] = [
            "如发现患者出现不适症状，请及时联系医生",
            "确保患者饮食健康，避免油腻和辛辣食物",
            "保持患者居住环境安静舒适",
            "提醒患者按时复诊"
        ]
        
        return report
    
    def _generate_doctor_monthly_report(self, monthly_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成医生端月报"""
        # 构建医生端月报
        report = {
            "report_type": "monthly",
            "end_type": "doctor",
            "patient_id": monthly_data.get("patient_id"),
            "month": monthly_data.get("month"),
            "patient_info": patient_data.get("basic_info", {}),
            "data_analysis": {
                "heart_rate": {
                    "mean": monthly_data.get("heart_rate", {}).get("mean", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "activity": {
                    "mean_steps": monthly_data.get("activity", {}).get("mean_steps", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                },
                "sleep": {
                    "mean_sleep_duration": monthly_data.get("sleep", {}).get("mean_sleep_duration", 0),
                    "analysis": "",
                    "evidence": "依据《中国冠心病康复与二级预防指南(2024)》"
                }
            },
            "clinical_assessment": {
                "condition_status": "",
                "risk_level": "",
                "recommendations": []
            },
            "visuals": []
        }
        
        # 分析数据
        hr_mean = monthly_data.get("heart_rate", {}).get("mean", 70)
        mean_steps = monthly_data.get("activity", {}).get("mean_steps", 0)
        sleep_duration = monthly_data.get("sleep", {}).get("mean_sleep_duration", 0)
        
        if 55 <= hr_mean <= 65:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率控制良好，符合术后康复目标"
        elif hr_mean < 55:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率偏低，需关注是否与药物相关"
        else:
            report["data_analysis"]["heart_rate"]["analysis"] = "心率偏高，需调整康复方案"
        
        if mean_steps >= 3000:
            report["data_analysis"]["activity"]["analysis"] = "活动量充足，符合康复要求"
        elif mean_steps >= 1000:
            report["data_analysis"]["activity"]["analysis"] = "活动量适中，可适当增加"
        else:
            report["data_analysis"]["activity"]["analysis"] = "活动量不足，需加强运动"
        
        if sleep_duration >= 7:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠质量良好"
        elif sleep_duration >= 6:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠质量一般"
        else:
            report["data_analysis"]["sleep"]["analysis"] = "睡眠不足，需改善"
        
        # 临床评估
        report["clinical_assessment"]["condition_status"] = "患者术后恢复良好，无明显加重迹象"
        report["clinical_assessment"]["risk_level"] = "低风险"
        report["clinical_assessment"]["recommendations"] = [
            "继续当前康复方案",
            "定期监测心率和血压",
            "保持适量运动",
            "维持健康饮食习惯",
            "按时复诊"
        ]
        
        # 添加可视化
        report["visuals"].append({
            "type": "monthly_trend_chart",
            "title": "本月健康趋势",
            "data": {
                "heart_rate": monthly_data.get("heart_rate", {}),
                "activity": monthly_data.get("activity", {}),
                "sleep": monthly_data.get("sleep", {})
            }
        })
        
        return report
    
    def generate_all_reports(self, patient_id: str, end_type: str = "patient") -> Dict[str, Any]:
        """生成所有时间周期的报告"""
        reports = {
            "daily": self.generate_daily_report(patient_id, end_type=end_type),
            "weekly": self.generate_weekly_report(patient_id, end_type=end_type),
            "monthly": self.generate_monthly_report(patient_id, end_type=end_type)
        }
        return reports


# 测试代码
if __name__ == "__main__":
    reporter = TimePeriodReporter()
    
    # 为每个患者生成报告
    for patient_id in reporter.patients:
        print(f"\n===== 患者 {patient_id} 报告 =====")
        
        # 生成患者端报告
        print("\n患者端日报：")
        daily_report = reporter.generate_daily_report(patient_id, end_type="patient")
        print(json.dumps(daily_report, ensure_ascii=False, indent=2))
        
        print("\n患者端周报：")
        weekly_report = reporter.generate_weekly_report(patient_id, end_type="patient")
        print(json.dumps(weekly_report, ensure_ascii=False, indent=2))
        
        print("\n患者端月报：")
        monthly_report = reporter.generate_monthly_report(patient_id, end_type="patient")
        print(json.dumps(monthly_report, ensure_ascii=False, indent=2))
        
        # 生成医生端报告
        print("\n医生端日报：")
        doctor_daily = reporter.generate_daily_report(patient_id, end_type="doctor")
        print(json.dumps(doctor_daily, ensure_ascii=False, indent=2))
        
        print("\n医生端周报：")
        doctor_weekly = reporter.generate_weekly_report(patient_id, end_type="doctor")
        print(json.dumps(doctor_weekly, ensure_ascii=False, indent=2))
        
        print("\n医生端月报：")
        doctor_monthly = reporter.generate_monthly_report(patient_id, end_type="doctor")
        print(json.dumps(doctor_monthly, ensure_ascii=False, indent=2))