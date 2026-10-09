import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from pathlib import Path
from .config import GLOBAL_CONFIG


matplotlib.rcParams.update(GLOBAL_CONFIG['rc_params'])


class Visualizer:
    def __init__(self):
        self.colors = GLOBAL_CONFIG['colors']
        self.fig_size = GLOBAL_CONFIG['fig_size']
        self.subplot_fig_size = GLOBAL_CONFIG['subplot_fig_size']
        self.dpi = GLOBAL_CONFIG['dpi']
    
    def plot_daily_hr_trend(self, date_str, df, risk_zones, abnormal_df, save_path, end_type='doctor'):
        if df.empty or 'heart_rate' not in df.columns:
            return None
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        if end_type == 'patient':
            normal_low = risk_zones['yellow_low']
            normal_high = risk_zones['yellow_high']
            ax.fill_between(df['time'], normal_low, normal_high, 
                           color=self.colors['green'], alpha=0.2, label='正常区间')
            ax.fill_between(df['time'], risk_zones['red_low'], normal_low, 
                           color=self.colors['red'], alpha=0.2, label='预警区间')
            ax.fill_between(df['time'], normal_high, risk_zones['red_high'], 
                           color=self.colors['red'], alpha=0.2)
        else:
            ax.fill_between(df['time'], risk_zones['blue_low'], risk_zones['blue_high'], 
                           color=self.colors['blue'], alpha=0.2, label='蓝区')
            ax.fill_between(df['time'], risk_zones['yellow_low'], risk_zones['blue_low'], 
                           color=self.colors['yellow'], alpha=0.2, label='黄区')
            ax.fill_between(df['time'], risk_zones['blue_high'], risk_zones['yellow_high'], 
                           color=self.colors['yellow'], alpha=0.2)
            ax.fill_between(df['time'], risk_zones['red_low'], risk_zones['yellow_low'], 
                           color=self.colors['red'], alpha=0.2, label='红区')
            ax.fill_between(df['time'], risk_zones['yellow_high'], risk_zones['red_high'], 
                           color=self.colors['red'], alpha=0.2)
        
        ax.plot(df['time'], df['heart_rate'], color=self.colors['hr_line'], 
               linewidth=1.5, label='心率')
        ax.axhline(y=risk_zones['mu'], color=self.colors['avg_line'], 
                  linestyle='--', linewidth=2, label='基线μ')
        
        if not abnormal_df.empty:
            red_abnormal = abnormal_df[abnormal_df['level'] == 'red']
            yellow_abnormal = abnormal_df[abnormal_df['level'] == 'yellow']
            
            if not red_abnormal.empty:
                ax.scatter(red_abnormal['time'], red_abnormal['heart_rate'], 
                          color=self.colors['red'], s=50, zorder=5, label='红色预警')
            if not yellow_abnormal.empty and end_type != 'patient':
                ax.scatter(yellow_abnormal['time'], yellow_abnormal['heart_rate'], 
                          color=self.colors['yellow'], s=30, zorder=4, label='黄色关注')
        
        ax.set_xlabel('时间', fontsize=12)
        ax.set_ylabel('心率 (次/分)', fontsize=12)
        ax.set_title(f'{date_str} 24小时心率趋势图', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_multi_indicator(self, date_str, df, risk_zones, save_path):
        if df.empty:
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=self.subplot_fig_size)
        axes = axes.flatten()
        
        indicators = [
            ('heart_rate', '心率 (次/分)', axes[0]),
            ('steps', '步数', axes[1]),
            ('METs', 'METs', axes[2]),
            ('sleep_stage', '睡眠分期', axes[3])
        ]
        
        for col_name, y_label, ax in indicators:
            if col_name in df.columns:
                ax.plot(df['time'], df[col_name], color=self.colors['hr_line'], linewidth=1.5)
                ax.set_xlabel('时间', fontsize=10)
                ax.set_ylabel(y_label, fontsize=10)
                ax.set_title(y_label, fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)
        
        fig.suptitle(f'{date_str} 多指标联合趋势', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_alarm_pie(self, alarm_stats, save_path, report_date):
        labels = []
        values = []
        colors = []
        
        if alarm_stats.get('pathological_count', 0) > 0:
            labels.append("病理性预警")
            values.append(alarm_stats['pathological_count'])
            colors.append(self.colors['red'])
        
        if alarm_stats.get('pending_count', 0) > 0:
            labels.append("待排查预警")
            values.append(alarm_stats['pending_count'])
            colors.append(self.colors['yellow'])
        
        if alarm_stats.get('physiological_count', 0) > 0:
            labels.append("生理性预警")
            values.append(alarm_stats['physiological_count'])
            colors.append(self.colors['blue'])
        
        if not values or sum(values) == 0:
            labels = ['无异常预警']
            values = [1]
            colors = [self.colors['green']]
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12}
        )
        
        ax.set_title(f'{report_date} 心率预警分类占比', fontsize=16, fontweight='bold')
        plt.setp(autotexts, size=12, weight='bold', color='white')
        plt.tight_layout()
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_baseline_update_trace(self, baseline_history_df, save_path, week_range):
        if baseline_history_df.empty:
            return None
        
        core_indicators = ["rest_heart_rate", "hrv_sdnn", "deep_sleep_ratio", "daily_steps"]
        indicator_names = ["静息心率", "心率变异性SDNN", "深睡占比", "日均步数"]
        trend_direction = [-1, 1, 1, 1]
        
        fig, axes = plt.subplots(2, 2, figsize=self.subplot_fig_size)
        axes = axes.flatten()
        
        for idx, (indicator, name, direction) in enumerate(zip(core_indicators, indicator_names, trend_direction)):
            ax = axes[idx]
            indicator_data = baseline_history_df[baseline_history_df["indicator"] == indicator].copy()
            
            if len(indicator_data) >= 2:
                try:
                    indicator_data["Date"] = pd.to_datetime(indicator_data["Date"])
                    x_data = range(len(indicator_data))
                    x_labels = [d.strftime("%m-%d") for d in indicator_data["Date"]]
                    
                    ax.plot(x_data, indicator_data["baseline_mean"].values, 
                           color='#1f77b4', linewidth=3, label="个性化基线")
                    
                    lower = pd.to_numeric(indicator_data["baseline_lower"], errors='coerce').fillna(indicator_data["baseline_mean"])
                    upper = pd.to_numeric(indicator_data["baseline_upper"], errors='coerce').fillna(indicator_data["baseline_mean"])
                    
                    ax.fill_between(x_data, 
                                   lower.values, 
                                   upper.values, 
                                   color='#1f77b4', alpha=0.2, label="基线正常区间")
                    
                    start_value = indicator_data["baseline_mean"].iloc[0]
                    end_value = indicator_data["baseline_mean"].iloc[-1]
                    change_ratio = (end_value - start_value) / start_value * 100 * direction if start_value != 0 else 0
                    
                    if change_ratio > 0:
                        trend_text = f"本周改善{abs(change_ratio):.1f}%"
                        color = "#2ecc71"
                    else:
                        trend_text = f"本周变差{abs(change_ratio):.1f}%"
                        color = "#e74c3c"
                    
                    ax.text(0.5, 0.95, trend_text, transform=ax.transAxes, 
                           fontsize=14, fontweight='bold', color=color, ha='center',
                           bbox=dict(facecolor='white', alpha=0.8, edgecolor=color))
                    
                    ax.set_xticks(x_data)
                    ax.set_xticklabels(x_labels, rotation=45)
                except Exception as e:
                    print(f"绘制{name}基线更新轨迹时出错: {e}")
                    continue
            
            ax.set_title(f"{name} 基线更新轨迹", fontsize=14, fontweight='bold')
            ax.set_xlabel("日期", fontsize=12)
            ax.set_ylabel(name, fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
        
        fig.suptitle(f"{week_range} 个性化基线在线更新轨迹", fontsize=18, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_weekly_trend_summary(self, date_list, daily_stats_list, save_path, week_range):
        if not date_list or not daily_stats_list:
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=self.subplot_fig_size)
        axes = axes.flatten()
        
        hr_means = [stats.get('hr_mean', 0) for stats in daily_stats_list if stats]
        steps_totals = [stats.get('steps_total', 0) for stats in daily_stats_list if stats]
        mets_means = [stats.get('METs_mean', 0) for stats in daily_stats_list if stats]
        
        valid_dates = [date for date, stats in zip(date_list, daily_stats_list) if stats]
        
        if hr_means:
            axes[0].plot(valid_dates, hr_means, marker='o', color=self.colors['hr_line'], linewidth=2)
            axes[0].set_title('周度平均心率趋势', fontsize=12, fontweight='bold')
            axes[0].set_xlabel('日期')
            axes[0].set_ylabel('心率 (次/分)')
            axes[0].grid(True, alpha=0.3)
            axes[0].tick_params(axis='x', rotation=45)
        
        if steps_totals:
            axes[1].bar(valid_dates, steps_totals, color=self.colors['blue'], alpha=0.7)
            axes[1].set_title('周度每日步数', fontsize=12, fontweight='bold')
            axes[1].set_xlabel('日期')
            axes[1].set_ylabel('步数')
            axes[1].grid(True, alpha=0.3)
            axes[1].tick_params(axis='x', rotation=45)
        
        if mets_means:
            axes[2].plot(valid_dates, mets_means, marker='s', color=self.colors['green'], linewidth=2)
            axes[2].set_title('周度平均METs趋势', fontsize=12, fontweight='bold')
            axes[2].set_xlabel('日期')
            axes[2].set_ylabel('METs')
            axes[2].grid(True, alpha=0.3)
            axes[2].tick_params(axis='x', rotation=45)
        
        axes[3].text(0.5, 0.5, '更多指标分析', ha='center', va='center', 
                    fontsize=14, fontweight='bold')
        axes[3].axis('off')
        
        fig.suptitle(f'{week_range} 周度健康趋势总结', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_activity_distribution(self, df, save_path, date_str):
        if df.empty or 'METs' not in df.columns:
            return None
        
        sedentary = len(df[df['METs'] < 1.5])
        light = len(df[(df['METs'] >= 1.5) & (df['METs'] < 3)])
        moderate = len(df[(df['METs'] >= 3) & (df['METs'] < 6)])
        vigorous = len(df[df['METs'] >= 6])
        
        labels = ['久坐', '轻强度', '中强度', '高强度']
        values = [sedentary, light, moderate, vigorous]
        colors = [self.colors['blue'], self.colors['yellow'], self.colors['green'], self.colors['red']]
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12}
        )
        
        ax.set_title(f'{date_str} 活动强度分布', fontsize=16, fontweight='bold')
        plt.setp(autotexts, size=12, weight='bold', color='white')
        plt.tight_layout()
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return save_path
