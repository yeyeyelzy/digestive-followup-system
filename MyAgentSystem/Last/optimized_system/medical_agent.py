import pandas as pd
from .config import MEDICAL_RULES, ATTRIBUTION_RULES, QUALITATIVE_TEMPLATES


class MedicalAgent:
    def __init__(self, patient_baseline=None):
        self.patient_baseline = patient_baseline
    
    def attribute_abnormalities(self, abnormal_df, full_df):
        if abnormal_df.empty:
            return pd.DataFrame()
        
        result_df = abnormal_df.copy()
        
        def get_attribution(row):
            time_point = row['time']
            mets = 0
            steps = 0
            intensity = 0
            
            if not full_df.empty and 'time' in full_df.columns:
                time_match = full_df[full_df['time'] == time_point]
                if not time_match.empty:
                    mets = time_match.iloc[0].get('METs', 0)
                    steps = time_match.iloc[0].get('steps', 0)
                    intensity = time_match.iloc[0].get('intensity', 0)
            
            if (mets >= ATTRIBUTION_RULES['physiological']['mets_threshold'] or 
                steps >= ATTRIBUTION_RULES['physiological']['steps_threshold'] or 
                intensity >= ATTRIBUTION_RULES['physiological']['intensity_threshold']):
                return "生理性预警（运动/活动）"
            elif (mets < ATTRIBUTION_RULES['pathological']['mets_threshold'] and 
                  steps < ATTRIBUTION_RULES['pathological']['steps_threshold'] and 
                  intensity <= ATTRIBUTION_RULES['pathological']['intensity_threshold']):
                return "病理性预警（静息异常）"
            else:
                return "待排查预警（边界值）"
        
        result_df['attribution'] = result_df.apply(get_attribution, axis=1)
        return result_df
    
    def get_alarm_statistics(self, attributed_abnormal_df):
        if attributed_abnormal_df.empty:
            return {
                'total_count': 0,
                'physiological_count': 0,
                'pathological_count': 0,
                'pending_count': 0
            }
        
        stats = {
            'total_count': len(attributed_abnormal_df),
            'physiological_count': len(attributed_abnormal_df[
                attributed_abnormal_df['attribution'] == "生理性预警（运动/活动）"
            ]),
            'pathological_count': len(attributed_abnormal_df[
                attributed_abnormal_df['attribution'] == "病理性预警（静息异常）"
            ]),
            'pending_count': len(attributed_abnormal_df[
                attributed_abnormal_df['attribution'] == "待排查预警（边界值）"
            ])
        }
        
        return stats
    
    def generate_qualitative_description(self, daily_stats, condition_trend, baseline_change=None):
        descriptions = []
        
        if daily_stats and 'hr_mean' in daily_stats:
            hr_mean = daily_stats['hr_mean']
            if condition_trend == 'improving':
                descriptions.append(f"今日静息心率{hr_mean:.0f}次/分，较基线有所改善，心血管状态向好")
            elif condition_trend == 'worsening':
                descriptions.append(f"今日静息心率{hr_mean:.0f}次/分，需关注变化趋势")
            else:
                descriptions.append(f"今日静息心率{hr_mean:.0f}次/分，保持稳定")
        
        if daily_stats and 'steps_total' in daily_stats:
            steps = daily_stats['steps_total']
            if steps >= 10000:
                descriptions.append(f"今日步数{steps:.0f}步，活动量充足")
            elif steps >= 6000:
                descriptions.append(f"今日步数{steps:.0f}步，活动量基本达标")
            else:
                descriptions.append(f"今日步数{steps:.0f}步，建议增加活动量")
        
        return "；".join(descriptions) if descriptions else "今日健康状态稳定"
    
    def generate_medical_advice(self, daily_stats, health_score, condition_trend, abnormal_count):
        advice = []
        
        red_count = abnormal_count.get('red', 0)
        yellow_count = abnormal_count.get('yellow', 0)
        
        if red_count > 0:
            advice.append("⚠️ 今日有红色预警事件，建议关注相关时段的身体状态")
        if yellow_count > 0:
            advice.append("📊 今日有黄色关注事件，建议保持观察")
        
        if condition_trend == 'improving':
            advice.append("✅ 健康趋势向好，继续保持当前的生活习惯")
        elif condition_trend == 'worsening':
            advice.append("⚠️ 健康趋势需要关注，建议调整作息和活动量")
        
        if health_score >= 80:
            advice.append("😊 健康评分优秀，继续保持")
        elif health_score >= 60:
            advice.append("🙂 健康评分良好，可适当增加活动")
        else:
            advice.append("😟 健康评分需关注，建议咨询医生")
        
        advice.append("💤 建议保证7-8小时睡眠，睡前避免剧烈运动")
        advice.append("🚶 建议每日进行适量活动，保持规律作息")
        
        return "\n".join(advice)
    
    def generate_weekly_summary(self, weekly_data, baseline_trends):
        summary = []
        
        hr_trend = baseline_trends.get('rest_heart_rate', 'stable')
        if hr_trend == 'improving':
            summary.append("本周静息心率呈改善趋势，心血管功能持续向好")
        elif hr_trend == 'worsening':
            summary.append("本周静息心率需关注，建议监测变化")
        else:
            summary.append("本周静息心率保持稳定")
        
        steps_avg = weekly_data.get('avg_steps', 0)
        if steps_avg >= 8000:
            summary.append(f"本周平均步数{steps_avg:.0f}步，活动量充足")
        elif steps_avg >= 5000:
            summary.append(f"本周平均步数{steps_avg:.0f}步，活动量基本达标")
        else:
            summary.append(f"本周平均步数{steps_avg:.0f}步，建议增加活动量")
        
        return "；".join(summary)
    
    def get_risk_level(self, health_score, pathological_count):
        if pathological_count > 5:
            return "高风险"
        elif health_score < 50:
            return "中风险"
        elif health_score < 70:
            return "低风险"
        else:
            return "正常"
