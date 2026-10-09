"""
Fitabase数据处理器
处理患者时序生理数据、临床数据等
"""
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from optimized_system_v2.core.utils.config import config


class FitabaseDataProcessor:
    """Fitabase数据处理器"""
    
    def __init__(self):
        self.base_data_path = config.paths.fitabase_data
        self.patients = ["P_001_Wang", "P_002_Li", "P_003_Chen"]
        self.system_check_log = []
        
    def _log(self, message: str):
        """记录系统自检日志"""
        print(message)
        self.system_check_log.append(message)
        
    def get_patient_data_path(self, patient_id: str) -> Path:
        """获取患者数据路径"""
        patient_folder_map = {
            "P_001": "P_001_Wang",
            "P_002": "P_002_Li",
            "P_003": "P_003_Chen"
        }
        folder_name = patient_folder_map.get(patient_id, patient_id)
        return self.base_data_path / folder_name
        
    def load_patient_info(self, patient_id: str) -> Dict[str, Any]:
        """加载患者基本信息"""
        data_path = self.get_patient_data_path(patient_id)
        info_file = data_path / "patient_info.json"
        
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def load_heartrate_data(self, patient_id: str) -> Optional[pd.DataFrame]:
        """加载心率数据"""
        data_path = self.get_patient_data_path(patient_id)
        hr_file = data_path / "heartrate_seconds_merged.csv"
        
        if hr_file.exists():
            df = pd.read_csv(hr_file)
            return df
        return None
        
    def load_daily_activity(self, patient_id: str) -> Optional[pd.DataFrame]:
        """加载日常活动数据"""
        data_path = self.get_patient_data_path(patient_id)
        activity_file = data_path / "dailyActivity_merged.csv"
        
        if activity_file.exists():
            df = pd.read_csv(activity_file)
            return df
        return None
        
    def load_sleep_data(self, patient_id: str) -> Optional[pd.DataFrame]:
        """加载睡眠数据"""
        data_path = self.get_patient_data_path(patient_id)
        sleep_file = data_path / "sleepDay_merged.csv"
        
        if sleep_file.exists():
            df = pd.read_csv(sleep_file)
            return df
        return None
        
    def load_medicine_data(self, patient_id: str) -> Optional[pd.DataFrame]:
        """加载用药数据"""
        data_path = self.get_patient_data_path(patient_id)
        med_file = data_path / "medicine_merged.csv"
        
        if med_file.exists():
            df = pd.read_csv(med_file)
            return df
        return None
        
    def load_diet_data(self, patient_id: str) -> Optional[pd.DataFrame]:
        """加载饮食数据"""
        data_path = self.get_patient_data_path(patient_id)
        diet_file = data_path / "diet_merged.csv"
        
        if diet_file.exists():
            df = pd.read_csv(diet_file)
            return df
        return None
        
    def analyze_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """综合分析患者数据"""
        self._log(f"\n📊 分析患者 {patient_id} 数据")
        self._log("-" * 80)
        
        analysis_result = {
            "patient_id": patient_id,
            "basic_info": {},
            "heartrate": {},
            "activity": {},
            "sleep": {},
            "medicine": {},
            "diet": {}
        }
        
        # 加载基本信息
        basic_info = self.load_patient_info(patient_id)
        analysis_result["basic_info"] = basic_info
        self._log(f"✅ 加载患者基本信息: {basic_info.get('name', '未知')}")
        
        # 分析心率数据
        hr_df = self.load_heartrate_data(patient_id)
        if hr_df is not None and 'Value' in hr_df.columns:
            analysis_result["heartrate"] = {
                "mean": hr_df['Value'].mean(),
                "min": hr_df['Value'].min(),
                "max": hr_df['Value'].max(),
                "count": len(hr_df)
            }
            self._log(f"✅ 心率分析: 平均 {analysis_result['heartrate']['mean']:.1f} bpm, "
                     f"范围 {analysis_result['heartrate']['min']}-{analysis_result['heartrate']['max']} bpm")
        
        # 分析活动数据
        activity_df = self.load_daily_activity(patient_id)
        if activity_df is not None:
            if 'TotalSteps' in activity_df.columns:
                analysis_result["activity"]["total_steps_mean"] = activity_df['TotalSteps'].mean()
            if 'Calories' in activity_df.columns:
                analysis_result["activity"]["calories_mean"] = activity_df['Calories'].mean()
            self._log(f"✅ 活动分析: 平均步数 {analysis_result['activity'].get('total_steps_mean', 0):.0f}")
        
        # 分析睡眠数据
        sleep_df = self.load_sleep_data(patient_id)
        if sleep_df is not None:
            if 'TotalMinutesAsleep' in sleep_df.columns:
                analysis_result["sleep"]["minutes_asleep_mean"] = sleep_df['TotalMinutesAsleep'].mean()
            self._log(f"✅ 睡眠分析: 平均睡眠 {analysis_result['sleep'].get('minutes_asleep_mean', 0)/60:.1f} 小时")
        
        # 加载用药数据
        med_df = self.load_medicine_data(patient_id)
        if med_df is not None:
            analysis_result["medicine"]["record_count"] = len(med_df)
            self._log(f"✅ 用药数据: {len(med_df)} 条记录")
        
        # 加载饮食数据
        diet_df = self.load_diet_data(patient_id)
        if diet_df is not None:
            analysis_result["diet"]["record_count"] = len(diet_df)
            self._log(f"✅ 饮食数据: {len(diet_df)} 条记录")
        
        return analysis_result
        
    def get_system_check_log(self) -> List[str]:
        """获取系统自检日志"""
        return self.system_check_log
