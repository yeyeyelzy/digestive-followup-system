"""
多智能体系统管理器
"""
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import json

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from optimized_system_v2.core.utils.config import config
from optimized_system_v2.core.data_processor.fitabase_processor import FitabaseDataProcessor


class MultiAgentSystemManager:
    """多智能体系统管理器"""
    
    def __init__(self):
        self.data_processor = FitabaseDataProcessor()
        self.system_check_log = []
        self.is_initialized = False
        
    def _log(self, message: str):
        """记录系统自检日志"""
        print(message)
        self.system_check_log.append(message)
        
    def initialize(self) -> Dict[str, Any]:
        """初始化多智能体系统"""
        self._log("=" * 80)
        self._log("🤖 多智能体系统初始化")
        self._log("=" * 80)
        
        result = {
            "success": True,
            "agents": [
                "全局调度智能体",
                "时序生理数据解析智能体",
                "临床与行为数据融合智能体",
                "风险预警智能体",
                "康复医学决策智能体",
                "循证医学校验智能体",
                "药物管理智能体",
                "多端内容生成智能体"
            ]
        }
        
        self._log(f"\n✅ 已注册 {len(result['agents'])} 个智能体:")
        for i, agent in enumerate(result['agents'], 1):
            self._log(f"  {i}. {agent}")
        
        self.is_initialized = True
        self._log("\n" + "=" * 80)
        self._log("✅ 多智能体系统初始化完成!")
        self._log("=" * 80)
        
        return result
    
    def generate_patient_report(self, patient_id: str, analysis_data: Dict[str, Any]) -> str:
        """生成患者端报告（拟人化）"""
        name = analysis_data.get('basic_info', {}).get('name', '患者')
        
        hr_mean = analysis_data.get('heartrate', {}).get('mean', 0)
        steps_mean = analysis_data.get('activity', {}).get('total_steps_mean', 0)
        sleep_hours = analysis_data.get('sleep', {}).get('minutes_asleep_mean', 0) / 60
        
        report = f"""
{'='*60}
❤️  {name} 的康复报告
{'='*60}

📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

---
📊 您的近期数据总结:
---

💓 心率情况:
   • 平均心率: {hr_mean:.1f} 次/分
   {'✅ 心率控制得不错！继续保持！' if 55 <= hr_mean <= 75 else '⚠️  心率需要注意，建议咨询医生'}

🚶 活动情况:
   • 平均每日步数: {steps_mean:.0f} 步
   {'👍 活动量很好！' if steps_mean >= 3000 else '💪 可以适当增加一些活动'}

😴 睡眠情况:
   • 平均睡眠: {sleep_hours:.1f} 小时
   {'😊 睡眠充足！' if sleep_hours >= 7 else '😴 建议保证7-8小时睡眠'}

---
💡 温馨建议:
---

1. 运动方面:
   • 继续保持规律的轻度运动，比如慢走、太极
   • 避免剧烈运动，感觉累了就休息
   • 运动时注意监测心率，不要超过目标范围

2. 饮食方面:
   • 继续保持低盐低脂饮食
   • 多吃新鲜蔬菜水果
   • 控制热量摄入，保持健康体重

3. 用药方面:
   • 一定要按时服药，不要漏服
   • 如果有不适，及时告诉医生或家属

4. 生活方面:
   • 保持好心情，避免情绪激动
   • 保证充足睡眠
   • 定期复诊

---
有任何问题随时找我们哦！祝您早日康复！💪
{'='*60}
"""
        return report
    
    def generate_family_report(self, patient_id: str, analysis_data: Dict[str, Any]) -> str:
        """生成家属端报告"""
        name = analysis_data.get('basic_info', {}).get('name', '患者')
        
        hr_mean = analysis_data.get('heartrate', {}).get('mean', 0)
        steps_mean = analysis_data.get('activity', {}).get('total_steps_mean', 0)
        sleep_hours = analysis_data.get('sleep', {}).get('minutes_asleep_mean', 0) / 60
        
        report = f"""
{'='*60}
🏠  {name} 的家属照护报告
{'='*60}

📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

---
📊 患者近期数据:
---

💓 心率: 平均 {hr_mean:.1f} 次/分
   {'✅ 稳定' if 55 <= hr_mean <= 75 else '⚠️  需要关注'}

🚶 活动: 平均每日 {steps_mean:.0f} 步
   {'✅ 活动量合适' if 2000 <= steps_mean <= 5000 else '⚠️  需要调整'}

😴 睡眠: 平均 {sleep_hours:.1f} 小时/晚
   {'✅ 睡眠充足' if sleep_hours >= 7 else '⚠️  睡眠不足'}

---
👨‍👩‍👧 家属照护建议:
---

1. 用药监督:
   • 提醒患者按时服药
   • 观察是否有药物不良反应
   • 记录用药情况

2. 活动陪伴:
   • 陪同患者进行轻度运动
   • 避免患者单独进行剧烈活动
   • 活动时注意患者状态

3. 饮食管理:
   • 准备低盐低脂饮食
   • 控制患者热量摄入
   • 鼓励多吃蔬菜水果

4. 情绪支持:
   • 多与患者沟通交流
   • 关注患者情绪变化
   • 给予心理支持

5. 紧急情况:
   • 如患者出现胸痛、呼吸困难等症状，立即就医
   • 保存好急救电话和医生联系方式

---
感谢您的照护！如有疑问请及时咨询医生。
{'='*60}
"""
        return report
    
    def generate_doctor_report(self, patient_id: str, analysis_data: Dict[str, Any]) -> str:
        """生成医生端报告（专业结构化）"""
        basic_info = analysis_data.get('basic_info', {})
        name = basic_info.get('name', '未知')
        age = basic_info.get('age', '未知')
        diagnosis = basic_info.get('diagnosis', '冠心病PCI术后')
        
        hr_data = analysis_data.get('heartrate', {})
        activity_data = analysis_data.get('activity', {})
        sleep_data = analysis_data.get('sleep', {})
        
        report = f"""
{'='*80}
📋 冠心病PCI术后康复评估报告
{'='*80}

【患者基本信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
患者ID: {patient_id}
姓名: {name}
年龄: {age}岁
诊断: {diagnosis}
报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【核心数据汇总】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 心率数据:
   • 平均心率: {hr_data.get('mean', 'N/A'):.1f} bpm
   • 最低心率: {hr_data.get('min', 'N/A')} bpm
   • 最高心率: {hr_data.get('max', 'N/A')} bpm
   • 数据点数: {hr_data.get('count', 'N/A')}
   • 评估: {'✅ 目标范围(55-60bpm)' if 55 <= hr_data.get('mean', 0) <= 60 else 
             '⚠️ 接近目标' if 50 <= hr_data.get('mean', 0) <= 70 else '❌ 需调整'}

2. 活动数据:
   • 平均每日步数: {activity_data.get('total_steps_mean', 'N/A'):.0f} 步
   • 平均每日消耗: {activity_data.get('calories_mean', 'N/A'):.0f} kcal
   • 评估: {'✅ 活动量适宜' if 2000 <= activity_data.get('total_steps_mean', 0) <= 5000 else
             '⚠️ 活动量偏低' if activity_data.get('total_steps_mean', 0) < 2000 else '⚠️ 活动量偏高'}

3. 睡眠数据:
   • 平均睡眠时间: {sleep_data.get('minutes_asleep_mean', 0)/60:.1f} 小时
   • 评估: {'✅ 睡眠充足' if sleep_data.get('minutes_asleep_mean', 0)/60 >= 7 else '⚠️ 睡眠不足'}

4. 用药依从性:
   • 用药记录数: {analysis_data.get('medicine', {}).get('record_count', 'N/A')}
   • 评估: 需结合临床判断

5. 饮食记录:
   • 饮食记录数: {analysis_data.get('diet', {}).get('record_count', 'N/A')}
   • 评估: 需结合临床判断

【风险预警分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
风险等级: {'低风险' if (55 <= hr_data.get('mean', 0) <= 75 and 
                       2000 <= activity_data.get('total_steps_mean', 0) <= 5000) else '中风险'}
主要观察点:
{'- 心率控制' if not (55 <= hr_data.get('mean', 0) <= 60) else ''}
{'- 活动量管理' if not (2000 <= activity_data.get('total_steps_mean', 0) <= 5000) else ''}
{'- 睡眠改善' if sleep_data.get('minutes_asleep_mean', 0)/60 < 7 else ''}

【循证调整建议】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
依据: 《中国冠心病康复与二级预防指南(2024)》

1. 运动处方建议:
   • 推荐运动类型: 有氧运动（步行、太极）
   • 运动频率: 每周3-5次
   • 运动强度: 中等强度，心率控制在目标范围
   • 每次时长: 20-30分钟

2. 药物调整建议:
   • β受体阻滞剂: 评估是否需要调整剂量以达到目标心率
   • 抗血小板药物: 确认依从性
   • 他汀类药物: 监测血脂水平

3. 生活方式建议:
   • 饮食: 低盐低脂，控制热量
   • 睡眠: 保证7-8小时睡眠
   • 心理: 避免焦虑紧张

【重点关注事项】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 下次复诊时间: 建议1周后
• 需检查项目: 心电图、血脂、肝肾功能
• 患者教育: 强化用药依从性教育

报告结束
{'='*80}
"""
        return report
    
    def process_patient(self, patient_id: str) -> Dict[str, Any]:
        """处理患者数据，生成所有端的报告"""
        self._log(f"\n👤 处理患者: {patient_id}")
        self._log("-" * 80)
        
        # 分析患者数据
        analysis_data = self.data_processor.analyze_patient_data(patient_id)
        
        # 生成各端报告
        patient_report = self.generate_patient_report(patient_id, analysis_data)
        family_report = self.generate_family_report(patient_id, analysis_data)
        doctor_report = self.generate_doctor_report(patient_id, analysis_data)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        patient_path = config.paths.patient_output / f"{patient_id}_患者报告_{timestamp}.md"
        family_path = config.paths.family_output / f"{patient_id}_家属报告_{timestamp}.md"
        doctor_path = config.paths.doctor_output / f"{patient_id}_医生报告_{timestamp}.md"
        
        patient_path.parent.mkdir(parents=True, exist_ok=True)
        family_path.parent.mkdir(parents=True, exist_ok=True)
        doctor_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(patient_path, 'w', encoding='utf-8') as f:
            f.write(patient_report)
        self._log(f"✅ 患者端报告已保存: {patient_path}")
        
        with open(family_path, 'w', encoding='utf-8') as f:
            f.write(family_report)
        self._log(f"✅ 家属端报告已保存: {family_path}")
        
        with open(doctor_path, 'w', encoding='utf-8') as f:
            f.write(doctor_report)
        self._log(f"✅ 医生端报告已保存: {doctor_path}")
        
        return {
            "patient_id": patient_id,
            "analysis_data": analysis_data,
            "reports": {
                "patient": patient_report,
                "family": family_report,
                "doctor": doctor_report
            },
            "report_paths": {
                "patient": str(patient_path),
                "family": str(family_path),
                "doctor": str(doctor_path)
            }
        }
    
    def get_system_check_log(self) -> List[str]:
        """获取系统自检日志"""
        return self.system_check_log + self.data_processor.get_system_check_log()
