import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
from .config import DATA_DIR, PATIENTS, MEDICAL_RULES, ATTRIBUTION_RULES


class DataProcessor:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.patient_info = PATIENTS[patient_id]
        self.data_dir = DATA_DIR / self.patient_info['folder']
        self.patient_baseline = self._load_patient_baseline()
        self.all_data_cache = None

    def _load_patient_baseline(self):
        baseline_path = self.data_dir / 'patient_info.json'
        if baseline_path.exists():
            with open(baseline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def load_heart_rate_data(self):
        file_path = self.data_dir / 'heartrate_seconds_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = df.dropna(subset=['time'])
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df[(df['Value'] >= MEDICAL_RULES['heart_rate']['min']) & 
                (df['Value'] <= MEDICAL_RULES['heart_rate']['max'])]
        
        df = df.rename(columns={'Value': 'heart_rate'})
        return df[['time', 'heart_rate']]

    def load_steps_data(self):
        file_path = self.data_dir / 'minuteStepsNarrow_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['time'] = pd.to_datetime(df['ActivityMinute'], errors='coerce')
        df = df.dropna(subset=['time'])
        df['Steps'] = pd.to_numeric(df['Steps'], errors='coerce').fillna(0)
        df = df[df['Steps'] >= 0]
        df = df.rename(columns={'Steps': 'steps'})
        return df[['time', 'steps']]

    def load_mets_data(self):
        file_path = self.data_dir / 'minuteMETsNarrow_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['time'] = pd.to_datetime(df['ActivityMinute'], errors='coerce')
        df = df.dropna(subset=['time'])
        df['METs'] = pd.to_numeric(df['METs'], errors='coerce').fillna(1.0)
        df = df[(df['METs'] >= 0)]
        df = df.rename(columns={'METs': 'METs'})
        return df[['time', 'METs']]

    def load_sleep_data(self):
        file_path = self.data_dir / 'minuteSleep_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['time'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['time'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)
        df = df.rename(columns={'value': 'sleep_stage'})
        return df[['time', 'sleep_stage']]

    def load_intensity_data(self):
        file_path = self.data_dir / 'minuteIntensitiesNarrow_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['time'] = pd.to_datetime(df['ActivityMinute'], errors='coerce')
        df = df.dropna(subset=['time'])
        df['Intensity'] = pd.to_numeric(df['Intensity'], errors='coerce').fillna(0)
        df = df.rename(columns={'Intensity': 'intensity'})
        return df[['time', 'intensity']]

    def load_daily_activity(self):
        file_path = self.data_dir / 'dailyActivity_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['date'] = pd.to_datetime(df['ActivityDate'])
        return df

    def load_sleep_day(self):
        file_path = self.data_dir / 'sleepDay_merged.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df = df[df['Id'] == self.patient_info['id']].copy()
        df['date'] = pd.to_datetime(df['SleepDay']).dt.date
        return df

    def load_all_data(self):
        if self.all_data_cache is not None:
            return self.all_data_cache
        
        hr_df = self.load_heart_rate_data()
        steps_df = self.load_steps_data()
        mets_df = self.load_mets_data()
        sleep_df = self.load_sleep_data()
        intensity_df = self.load_intensity_data()
        
        if hr_df.empty:
            self.all_data_cache = pd.DataFrame()
            return self.all_data_cache
        
        hr_df['time'] = hr_df['time'].dt.floor('min')
        hr_df = hr_df.groupby('time')['heart_rate'].mean().reset_index()
        
        df = hr_df.copy()
        
        if not steps_df.empty:
            df = pd.merge(df, steps_df, on='time', how='left')
        if not mets_df.empty:
            df = pd.merge(df, mets_df, on='time', how='left')
        if not sleep_df.empty:
            df = pd.merge(df, sleep_df, on='time', how='left')
        if not intensity_df.empty:
            df = pd.merge(df, intensity_df, on='time', how='left')
        
        df['steps'] = df['steps'].fillna(0)
        df['METs'] = df['METs'].fillna(1.0)
        df['sleep_stage'] = df['sleep_stage'].fillna(0)
        df['intensity'] = df['intensity'].fillna(0)
        
        df['date'] = df['time'].dt.date
        
        self.all_data_cache = df
        return df

    def create_minute_level_wide_table(self, date_str=None):
        df = self.load_all_data()
        
        if df.empty:
            return pd.DataFrame()
        
        if date_str:
            target_date = pd.to_datetime(date_str).date()
            df = df[df['date'] == target_date].copy()
        
        return df

    def get_date_range(self):
        df = self.load_all_data()
        if df.empty:
            return []
        
        min_date = df['time'].min().date()
        max_date = df['time'].max().date()
        
        date_list = []
        current_date = min_date
        while current_date <= max_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        return date_list

    def extract_daily_features(self, date_str):
        df = self.create_minute_level_wide_table(date_str)
        if df.empty:
            return None
        
        features = {}
        
        hr_data = df['heart_rate'].dropna()
        if len(hr_data) > 0:
            features['rest_heart_rate'] = hr_data.mean()
            features['hrv_sdnn'] = hr_data.std()
            features['hrv_rmssd'] = np.sqrt(np.mean(np.square(np.diff(hr_data))))
        
        if 'steps' in df.columns:
            features['daily_steps'] = df['steps'].sum()
        
        if 'METs' in df.columns:
            moderate_high = len(df[(df['METs'] >= 3)])
            features['moderate_high_activity_min'] = moderate_high
            sedentary = len(df[(df['METs'] < 1.5)])
            features['sedentary_min'] = sedentary
        
        if 'sleep_stage' in df.columns:
            sleep_data = df[df['sleep_stage'] > 0]
            if len(sleep_data) > 0:
                deep_sleep = len(sleep_data[sleep_data['sleep_stage'] == 2])
                total_sleep = len(sleep_data)
                features['deep_sleep_ratio'] = deep_sleep / total_sleep if total_sleep > 0 else 0
                features['sleep_efficiency'] = 0.85 + (features['deep_sleep_ratio'] * 0.15)
        
        return features

    def attribute_alarms(self, df, rest_hr_threshold=100):
        if df.empty or 'heart_rate' not in df.columns:
            return pd.DataFrame(), {}
        
        alarm_df = df[df['heart_rate'] >= rest_hr_threshold].copy()
        
        if alarm_df.empty:
            return pd.DataFrame(), {'total_count': 0, 'physiological_count': 0, 'pathological_count': 0, 'pending_count': 0}
        
        def attribution_label(row):
            mets = row.get('METs', 0)
            steps = row.get('steps', 0)
            intensity = row.get('intensity', 0)
            
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
        
        alarm_df['attribution'] = alarm_df.apply(attribution_label, axis=1)
        
        alarm_stats = alarm_df['attribution'].value_counts()
        total_alarm = len(alarm_df)
        
        stats = {
            'total_count': total_alarm,
            'physiological_count': int(alarm_stats.get("生理性预警（运动/活动）", 0)),
            'pathological_count': int(alarm_stats.get("病理性预警（静息异常）", 0)),
            'pending_count': int(alarm_stats.get("待排查预警（边界值）", 0))
        }
        
        return alarm_df, stats

    def get_week_range(self, date_str):
        date = pd.to_datetime(date_str)
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        week_num = date.isocalendar()[1]
        return f"{date.year}-W{week_num:02d}({week_start.strftime('%m.%d')}-{week_end.strftime('%m.%d')})", week_start.date(), week_end.date()

    def get_month_range(self, date_str):
        date = pd.to_datetime(date_str)
        month_start = date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        return f"{date.year}-{date.month:02d}", month_start.date(), month_end.date()
