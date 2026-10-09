import numpy as np
import pandas as pd
import os
from pathlib import Path
from .config import ONLINE_LEARNING_CONFIG, MEDICAL_RULES


class OnlinePersonalizedBaseline:
    def __init__(self, patient_id, model_cache_path, patient_baseline=None):
        self.patient_id = patient_id
        self.model_cache_path = Path(model_cache_path)
        self.alpha = ONLINE_LEARNING_CONFIG['alpha']
        self.patient_baseline = patient_baseline
        self.indicators = ONLINE_LEARNING_CONFIG['core_indicators']
        
        self.model_cache_path.mkdir(parents=True, exist_ok=True)
        self.baseline_file = self.model_cache_path / "baseline_history.csv"
        
        self.baseline_history = self._load_baseline_history()
    
    def _load_baseline_history(self):
        if self.baseline_file.exists():
            return pd.read_csv(self.baseline_file, parse_dates=["Date"])
        else:
            return pd.DataFrame(columns=[
                "Date", "patient_id", "indicator", 
                "baseline_mean", "baseline_std", 
                "baseline_upper", "baseline_lower", "daily_value"
            ])
    
    def _get_initial_baseline(self, indicator_data):
        mean = np.mean(indicator_data)
        std = np.std(indicator_data) if len(indicator_data) > 1 else 5.0
        upper = mean + 1.96 * std
        lower = mean - 1.96 * std
        return mean, std, upper, lower
    
    def update_baseline_daily(self, date, daily_indicator_data):
        updated_rows = []
        date = pd.to_datetime(date)
        
        for indicator in self.indicators:
            if indicator not in daily_indicator_data:
                continue
            
            current_value = daily_indicator_data[indicator]
            if pd.isna(current_value):
                continue
            
            indicator_history = self.baseline_history[
                self.baseline_history["indicator"] == indicator
            ]
            
            if len(indicator_history) == 0:
                mean, std, upper, lower = self._get_initial_baseline([current_value])
            else:
                last_mean = indicator_history.iloc[-1]["baseline_mean"]
                last_std = indicator_history.iloc[-1]["baseline_std"]
                mean = self.alpha * current_value + (1 - self.alpha) * last_mean
                std = np.sqrt(
                    self.alpha * (current_value - mean)**2 + (1 - self.alpha) * last_std**2
                )
                upper = mean + 1.96 * std
                lower = mean - 1.96 * std
            
            updated_row = {
                "Date": date,
                "patient_id": self.patient_id,
                "indicator": indicator,
                "baseline_mean": mean,
                "baseline_std": std,
                "baseline_upper": upper,
                "baseline_lower": lower,
                "daily_value": current_value
            }
            updated_rows.append(updated_row)
        
        if updated_rows:
            updated_df = pd.DataFrame(updated_rows)
            self.baseline_history = pd.concat(
                [self.baseline_history, updated_df], 
                axis=0, 
                ignore_index=True
            )
            self.baseline_history.to_csv(self.baseline_file, index=False)
        
        return updated_rows if updated_rows else None
    
    def get_baseline_for_date(self, date):
        date = pd.to_datetime(date)
        return self.baseline_history[
            self.baseline_history["Date"] == date
        ]
    
    def get_trend_for_indicator(self, indicator, window=7):
        indicator_history = self.baseline_history[
            self.baseline_history["indicator"] == indicator
        ]
        if len(indicator_history) < window:
            return "insufficient_data"
        
        recent_data = indicator_history.tail(window)
        trend = np.polyfit(range(len(recent_data)), recent_data["baseline_mean"], 1)[0]
        
        if abs(trend) < 0.5:
            return "stable"
        elif trend < 0:
            if indicator in ["rest_heart_rate", "sedentary_min"]:
                return "improving"
            else:
                return "worsening"
        else:
            if indicator in ["rest_heart_rate", "sedentary_min"]:
                return "worsening"
            else:
                return "improving"
    
    def save_baseline_history(self):
        self.baseline_history.to_csv(self.baseline_file, index=False)


class OnlineLearner:
    def __init__(self, patient_baseline=None):
        self.patient_baseline = patient_baseline
        self.forgetting_factor = ONLINE_LEARNING_CONFIG['forgetting_factor']
        self.health_score = ONLINE_LEARNING_CONFIG['initial_health_score']
        self.max_health_score = ONLINE_LEARNING_CONFIG['max_health_score']
        
        self.hr_params = {
            'mu': 75.0,
            'sigma': 10.0,
            'mu_history': [],
            'sigma_history': [],
            'initialized': False
        }
        
        self.activity_params = {
            'steps_mu': 0,
            'steps_sigma': 0,
            'METs_mu': 1.5,
            'METs_sigma': 0.5
        }
        
        self.history = []
        self.initialized = False
        
        if patient_baseline:
            self._initialize_from_baseline()
    
    def _initialize_from_baseline(self):
        if 'rehab_goals' in self.patient_baseline:
            goals = self.patient_baseline['rehab_goals']
            if 'target_heart_rate_lower' in goals:
                self.hr_params['mu'] = (goals['target_heart_rate_lower'] + goals['target_heart_rate_upper']) / 2
                self.hr_params['sigma'] = (goals['target_heart_rate_upper'] - goals['target_heart_rate_lower']) / 4
        self.hr_params['mu_history'].append(self.hr_params['mu'])
        self.hr_params['sigma_history'].append(self.hr_params['sigma'])
        self.initialized = True
    
    def calculate_daily_stats(self, df):
        if df.empty or 'heart_rate' not in df.columns:
            return None
        
        hr_data = df['heart_rate'].dropna()
        if len(hr_data) < 10:
            return None
        
        stats = {
            'hr_mean': hr_data.mean(),
            'hr_std': hr_data.std(),
            'hr_min': hr_data.min(),
            'hr_max': hr_data.max(),
            'hr_median': hr_data.median(),
            'hr_count': len(hr_data)
        }
        
        if 'steps' in df.columns:
            stats['steps_total'] = df['steps'].sum()
            stats['steps_mean'] = df['steps'].mean()
        
        if 'METs' in df.columns:
            stats['METs_mean'] = df['METs'].mean()
            stats['METs_max'] = df['METs'].max()
        
        return stats
    
    def bayesian_update(self, new_mu, new_sigma):
        alpha = self.forgetting_factor
        
        old_mu = self.hr_params['mu']
        old_sigma = self.hr_params['sigma']
        
        new_mu_combined = alpha * old_mu + (1 - alpha) * new_mu
        new_sigma_sq = alpha * (old_sigma ** 2) + (1 - alpha) * (new_sigma ** 2) + alpha * (1 - alpha) * ((old_mu - new_mu) ** 2)
        new_sigma_combined = np.sqrt(new_sigma_sq)
        
        new_mu_combined = max(MEDICAL_RULES['heart_rate']['rest_min'], 
                              min(MEDICAL_RULES['heart_rate']['rest_max'], new_mu_combined))
        
        self.hr_params['mu'] = new_mu_combined
        self.hr_params['sigma'] = new_sigma_combined
        self.hr_params['mu_history'].append(new_mu_combined)
        self.hr_params['sigma_history'].append(new_sigma_combined)
        
        return {
            'old_mu': old_mu,
            'new_mu': new_mu_combined,
            'old_sigma': old_sigma,
            'new_sigma': new_sigma_combined,
            'change_mu': new_mu_combined - old_mu,
            'change_sigma': new_sigma_combined - old_sigma
        }
    
    def get_risk_zones(self):
        mu = self.hr_params['mu']
        sigma = self.hr_params['sigma']
        
        return {
            'blue_low': mu - sigma,
            'blue_high': mu + sigma,
            'yellow_low': mu - 2 * sigma,
            'yellow_high': mu + 2 * sigma,
            'red_low': max(MEDICAL_RULES['heart_rate']['min'], mu - 3 * sigma),
            'red_high': min(MEDICAL_RULES['heart_rate']['max'], mu + 3 * sigma),
            'mu': mu,
            'sigma': sigma
        }
    
    def detect_abnormal_points(self, df):
        if df.empty or 'heart_rate' not in df.columns:
            return pd.DataFrame()
        
        zones = self.get_risk_zones()
        abnormal_points = []
        
        for _, row in df.iterrows():
            hr = row['heart_rate']
            if pd.isna(hr):
                continue
            
            level = None
            if hr < zones['yellow_low'] or hr > zones['yellow_high']:
                level = 'red'
            elif hr < zones['blue_low'] or hr > zones['blue_high']:
                level = 'yellow'
            
            if level:
                point = {
                    'time': row['time'],
                    'heart_rate': hr,
                    'level': level,
                    'steps': row.get('steps', 0),
                    'METs': row.get('METs', 1.0),
                    'sleep_stage': row.get('sleep_stage', 0),
                    'intensity': row.get('intensity', 0)
                }
                abnormal_points.append(point)
        
        return pd.DataFrame(abnormal_points) if abnormal_points else pd.DataFrame()
    
    def update_health_score(self, daily_stats, abnormal_df):
        old_score = self.health_score
        
        red_count = len(abnormal_df[abnormal_df['level'] == 'red']) if not abnormal_df.empty else 0
        yellow_count = len(abnormal_df[abnormal_df['level'] == 'yellow']) if not abnormal_df.empty else 0
        
        penalty = (red_count * ONLINE_LEARNING_CONFIG['red_warning_penalty'] + 
                  yellow_count * ONLINE_LEARNING_CONFIG['yellow_warning_penalty'])
        
        if daily_stats and 'hr_mean' in daily_stats:
            hr_change = daily_stats['hr_mean'] - self.hr_params['mu']
            if abs(hr_change) < 5:
                bonus = ONLINE_LEARNING_CONFIG['improvement_bonus']
            else:
                bonus = 0
        else:
            bonus = 0
        
        new_score = old_score - penalty + bonus
        new_score = max(0, min(self.max_health_score, new_score))
        
        self.health_score = new_score
        
        return {
            'old_score': old_score,
            'new_score': new_score,
            'change': new_score - old_score,
            'red_count': red_count,
            'yellow_count': yellow_count,
            'penalty': penalty,
            'bonus': bonus
        }
    
    def assess_condition(self):
        if len(self.hr_params['mu_history']) < 3:
            return 'stable'
        
        recent_mu = self.hr_params['mu_history'][-3:]
        trend = np.polyfit(range(3), recent_mu, 1)[0]
        
        if trend < -1:
            return 'improving'
        elif trend > 1:
            return 'worsening'
        else:
            return 'stable'
    
    def predict_next_day(self):
        zones = self.get_risk_zones()
        condition = self.assess_condition()
        
        trend_factor = 0
        if condition == 'improving':
            trend_factor = -0.1
        elif condition == 'worsening':
            trend_factor = 0.1
        
        mu_adjusted = zones['mu'] * (1 + trend_factor)
        sigma_adjusted = zones['sigma']
        
        return {
            'blue_low': mu_adjusted - sigma_adjusted,
            'blue_high': mu_adjusted + sigma_adjusted,
            'yellow_low': mu_adjusted - 2 * sigma_adjusted,
            'yellow_high': mu_adjusted + 2 * sigma_adjusted,
            'red_low': max(MEDICAL_RULES['heart_rate']['min'], mu_adjusted - 3 * sigma_adjusted),
            'red_high': min(MEDICAL_RULES['heart_rate']['max'], mu_adjusted + 3 * sigma_adjusted),
            'condition_trend': condition,
            'mu_predicted': mu_adjusted
        }
    
    def process_day(self, df):
        result = {
            'daily_stats': None,
            'bayesian_update': None,
            'risk_zones': None,
            'abnormal_points': pd.DataFrame(),
            'health_score_update': None,
            'condition_assessment': None,
            'next_day_prediction': None
        }
        
        daily_stats = self.calculate_daily_stats(df)
        result['daily_stats'] = daily_stats
        
        if daily_stats and not self.initialized:
            self.hr_params['mu'] = daily_stats['hr_mean']
            self.hr_params['sigma'] = daily_stats['hr_std']
            self.hr_params['mu_history'].append(self.hr_params['mu'])
            self.hr_params['sigma_history'].append(self.hr_params['sigma'])
            self.initialized = True
        elif daily_stats:
            result['bayesian_update'] = self.bayesian_update(daily_stats['hr_mean'], daily_stats['hr_std'])
        
        result['risk_zones'] = self.get_risk_zones()
        result['abnormal_points'] = self.detect_abnormal_points(df)
        result['health_score_update'] = self.update_health_score(daily_stats, result['abnormal_points'])
        result['condition_assessment'] = self.assess_condition()
        result['next_day_prediction'] = self.predict_next_day()
        
        self.history.append(result)
        
        return result
