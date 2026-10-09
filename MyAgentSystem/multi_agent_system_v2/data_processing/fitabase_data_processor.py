from pathlib import Path
import sys
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

class FitabaseDataProcessor:
    """Fitabase数据处理器"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or str(Path(__file__).parent.parent.parent / "Fitabase Data 4.12.16-5.12.16")
        self.logger = self._init_logger()
        self.patients = ["P_001", "P_002", "P_003"]
        self.patient_data: Dict[str, Dict[str, Any]] = {}
    
    def _init_logger(self):
        """初始化日志记录器"""
        logger = logging.getLogger("FitabaseDataProcessor")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def load_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """加载单个患者的数据"""
        try:
            patient_dir = Path(self.data_dir) / f"{patient_id}_Wang" if patient_id == "P_001" else \
                        Path(self.data_dir) / f"{patient_id}_Li" if patient_id == "P_002" else \
                        Path(self.data_dir) / f"{patient_id}_Chen"
            
            if not patient_dir.exists():
                self.logger.error(f"患者目录不存在: {patient_dir}")
                return {}
            
            patient_data = {
                "patient_id": patient_id,
                "basic_info": self._load_patient_info(patient_dir),
                "heart_rate": self._load_heart_rate_data(patient_dir),
                "activity": self._load_activity_data(patient_dir),
                "sleep": self._load_sleep_data(patient_dir),
                "diet": self._load_diet_data(patient_dir),
                "medicine": self._load_medicine_data(patient_dir),
                "discharge_summary": self._load_discharge_summary(patient_dir),
                "doctors_advice": self._load_doctors_advice(patient_dir),
                "behavior": self._load_behavior_data(patient_dir),
                "living": self._load_living_data(patient_dir),
                "weight": self._load_weight_data(patient_dir)
            }
            
            self.patient_data[patient_id] = patient_data
            self.logger.info(f"成功加载患者 {patient_id} 的数据")
            return patient_data
        except Exception as e:
            self.logger.error(f"加载患者 {patient_id} 数据失败: {e}")
            return {}
    
    def load_all_patients_data(self) -> Dict[str, Dict[str, Any]]:
        """加载所有患者的数据"""
        for patient_id in self.patients:
            self.load_patient_data(patient_id)
        return self.patient_data
    
    def _load_patient_info(self, patient_dir: Path) -> Dict[str, Any]:
        """加载患者基本信息"""
        info_file = patient_dir / "patient_info.json"
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_heart_rate_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载心率数据"""
        hr_file = patient_dir / "heartrate_seconds_merged.csv"
        if hr_file.exists():
            df = pd.read_csv(hr_file)
            if not df.empty:
                # 计算基本统计信息
                hr_stats = {
                    "mean": float(df["Value"].mean()),
                    "min": float(df["Value"].min()),
                    "max": float(df["Value"].max()),
                    "std": float(df["Value"].std()),
                    "count": int(len(df))
                }
                
                # 按日期分组统计
                df["Time"] = pd.to_datetime(df["Time"])
                df["Date"] = df["Time"].dt.date
                daily_stats = df.groupby("Date").agg({
                    "Value": ["mean", "min", "max"]
                }).round(2).to_dict()

                # 不能只取前1000条，否则会丢失后续日期，导致周/月报图表出现大段0值。
                if len(df) > 120000:
                    step = max(1, len(df) // 120000)
                    sampled_df = df.iloc[::step].copy()
                else:
                    sampled_df = df
                
                return {
                    "raw_data": sampled_df.to_dict('records'),
                    "stats": hr_stats,
                    "daily_stats": daily_stats
                }
        return {}
    
    def _load_activity_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载活动数据"""
        activity_file = patient_dir / "dailyActivity_merged.csv"
        minute_steps_file = patient_dir / "minuteStepsNarrow_merged.csv"
        minute_intensity_file = patient_dir / "minuteIntensitiesNarrow_merged.csv"
        minute_mets_file = patient_dir / "minuteMETsNarrow_merged.csv"

        minute_steps_raw: List[Dict[str, Any]] = []
        minute_intensity_raw: List[Dict[str, Any]] = []
        minute_mets_raw: List[Dict[str, Any]] = []

        if minute_steps_file.exists():
            try:
                ms_df = pd.read_csv(minute_steps_file)
                if not ms_df.empty:
                    minute_steps_raw = ms_df.to_dict('records')
            except Exception as e:
                self.logger.error(f"加载分钟步数数据失败: {e}")

        if minute_intensity_file.exists():
            try:
                mi_df = pd.read_csv(minute_intensity_file)
                if not mi_df.empty:
                    minute_intensity_raw = mi_df.to_dict('records')
            except Exception as e:
                self.logger.error(f"加载分钟强度数据失败: {e}")

        if minute_mets_file.exists():
            try:
                mm_df = pd.read_csv(minute_mets_file)
                if not mm_df.empty:
                    minute_mets_raw = mm_df.to_dict('records')
            except Exception as e:
                self.logger.error(f"加载分钟METs数据失败: {e}")

        if activity_file.exists():
            df = pd.read_csv(activity_file)
            if not df.empty:
                # 计算基本统计信息
                activity_stats = {
                    "total_steps": int(df["TotalSteps"].sum()),
                    "mean_steps": float(df["TotalSteps"].mean()),
                    "total_distance": float(df["TotalDistance"].sum()),
                    "mean_distance": float(df["TotalDistance"].mean()),
                    "total_calories": int(df["Calories"].sum()),
                    "mean_calories": float(df["Calories"].mean()),
                    "active_minutes": int(df["VeryActiveMinutes"].sum() + df["FairlyActiveMinutes"].sum())
                }
                
                return {
                    "raw_data": df.to_dict('records'),
                    "stats": activity_stats,
                    "minute_steps_raw": minute_steps_raw,
                    "minute_intensity_raw": minute_intensity_raw,
                    "minute_mets_raw": minute_mets_raw,
                }
        return {}
    
    def _load_sleep_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载睡眠数据"""
        sleep_file = patient_dir / "sleepDay_merged.csv"
        minute_sleep_file = patient_dir / "minuteSleep_merged.csv"

        minute_sleep_raw: List[Dict[str, Any]] = []
        if minute_sleep_file.exists():
            try:
                ms_df = pd.read_csv(minute_sleep_file)
                if not ms_df.empty:
                    minute_sleep_raw = ms_df.to_dict('records')
            except Exception as e:
                self.logger.error(f"加载分钟睡眠数据失败: {e}")

        if sleep_file.exists():
            df = pd.read_csv(sleep_file)
            if not df.empty:
                # 计算基本统计信息
                sleep_stats = {
                    "total_sleep_days": int(len(df)),
                    "mean_sleep_duration": float(df["TotalMinutesAsleep"].mean() / 60),
                    "mean_time_in_bed": float(df["TotalTimeInBed"].mean() / 60),
                    "total_sleep_hours": float(df["TotalMinutesAsleep"].sum() / 60)
                }
                
                return {
                    "raw_data": df.to_dict('records'),
                    "stats": sleep_stats,
                    "minute_raw": minute_sleep_raw,
                }
        return {}
    
    def _load_diet_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载饮食数据"""
        diet_file = patient_dir / "diet_merged.csv"
        if diet_file.exists():
            try:
                df = pd.read_csv(diet_file)
                if not df.empty:
                    return {
                        "raw_data": df.to_dict('records'),
                        "meal_count": int(len(df))
                    }
            except Exception as e:
                self.logger.error(f"加载饮食数据失败: {e}")
        return {}
    
    def _load_medicine_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载用药数据"""
        medicine_file = patient_dir / "medicine_merged.csv"
        if medicine_file.exists():
            try:
                df = pd.read_csv(medicine_file)
                if not df.empty:
                    return {
                        "raw_data": df.to_dict('records'),
                        "medicine_count": int(len(df))
                    }
            except Exception as e:
                self.logger.error(f"加载用药数据失败: {e}")
        return {}
    
    def _load_discharge_summary(self, patient_dir: Path) -> Dict[str, Any]:
        """加载出院小结"""
        summary_file = patient_dir / "discharge_summary.csv"
        if summary_file.exists():
            try:
                df = pd.read_csv(summary_file)
                if not df.empty:
                    return {
                        "raw_data": df.to_dict('records')[0] if len(df) > 0 else {}
                    }
            except Exception as e:
                self.logger.error(f"加载出院小结失败: {e}")
        return {}
    
    def _load_doctors_advice(self, patient_dir: Path) -> Dict[str, Any]:
        """加载医生建议"""
        advice_file = patient_dir / "doctors_advice_detailed.csv"
        if advice_file.exists():
            try:
                df = pd.read_csv(advice_file)
                if not df.empty:
                    return {
                        "raw_data": df.to_dict('records')
                    }
            except Exception as e:
                self.logger.error(f"加载医生建议失败: {e}")
        return {}
    
    def _load_behavior_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载行为数据"""
        behavior_file = patient_dir / "behavior_merged.csv"
        if behavior_file.exists():
            try:
                df = pd.read_csv(behavior_file)
                if not df.empty:
                    return {
                        "raw_data": df.to_dict('records')
                    }
            except Exception as e:
                self.logger.error(f"加载行为数据失败: {e}")
        return {}
    
    def _load_living_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载生活数据"""
        living_file = patient_dir / "living_merged.csv"
        if living_file.exists():
            try:
                df = pd.read_csv(living_file)
                if not df.empty:
                    return {
                        "raw_data": df.to_dict('records')
                    }
            except Exception as e:
                self.logger.error(f"加载生活数据失败: {e}")
        return {}
    
    def _load_weight_data(self, patient_dir: Path) -> Dict[str, Any]:
        """加载体重数据"""
        weight_file = patient_dir / "weightLogInfo_merged.csv"
        if weight_file.exists():
            try:
                df = pd.read_csv(weight_file)
                if not df.empty:
                    weight_stats = {
                        "mean_weight": float(df["WeightKg"].mean()) if "WeightKg" in df.columns else 0,
                        "min_weight": float(df["WeightKg"].min()) if "WeightKg" in df.columns else 0,
                        "max_weight": float(df["WeightKg"].max()) if "WeightKg" in df.columns else 0
                    }
                    return {
                        "raw_data": df.to_dict('records'),
                        "stats": weight_stats
                    }
            except Exception as e:
                self.logger.error(f"加载体重数据失败: {e}")
        return {}
    
    def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """获取患者数据"""
        if patient_id not in self.patient_data:
            return self.load_patient_data(patient_id)
        return self.patient_data[patient_id]

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except Exception:
                continue
        try:
            return pd.to_datetime(date_str).date()
        except Exception:
            return None

    def _hr_stats_for_date(self, patient_data: Dict[str, Any], target_date) -> Dict[str, Any]:
        hr = patient_data.get("heart_rate", {})
        raw = hr.get("raw_data", [])
        if not raw:
            return hr.get("stats", {})

        values = []
        for row in raw:
            ts = row.get("Time") or row.get("time")
            d = self._parse_date(ts)
            if d == target_date:
                try:
                    values.append(float(row.get("Value")))
                except Exception:
                    continue

        if not values:
            return hr.get("stats", {})

        s = pd.Series(values)
        return {
            "mean": float(s.mean()),
            "min": float(s.min()),
            "max": float(s.max()),
            "std": float(s.std()) if len(values) > 1 else 0.0,
            "count": int(len(values))
        }

    def _activity_stats_for_date(self, patient_data: Dict[str, Any], target_date) -> Dict[str, Any]:
        activity = patient_data.get("activity", {})
        raw = activity.get("raw_data", [])
        if not raw:
            return activity.get("stats", {})

        rows = []
        for row in raw:
            d = self._parse_date(row.get("ActivityDate") or row.get("date"))
            if d == target_date:
                rows.append(row)

        if not rows:
            return activity.get("stats", {})

        df = pd.DataFrame(rows)
        total_steps = float(df["TotalSteps"].sum()) if "TotalSteps" in df.columns else 0.0
        total_distance = float(df["TotalDistance"].sum()) if "TotalDistance" in df.columns else 0.0
        total_calories = float(df["Calories"].sum()) if "Calories" in df.columns else 0.0
        active_minutes = 0.0
        for key in ["VeryActiveMinutes", "FairlyActiveMinutes"]:
            if key in df.columns:
                active_minutes += float(df[key].sum())

        return {
            "total_steps": int(total_steps),
            "mean_steps": float(total_steps),
            "total_distance": total_distance,
            "mean_distance": total_distance,
            "total_calories": int(total_calories),
            "mean_calories": float(total_calories),
            "active_minutes": int(active_minutes)
        }

    def _sleep_stats_for_date(self, patient_data: Dict[str, Any], target_date) -> Dict[str, Any]:
        sleep = patient_data.get("sleep", {})
        raw = sleep.get("raw_data", [])
        if not raw:
            return sleep.get("stats", {})

        rows = []
        for row in raw:
            d = self._parse_date(row.get("SleepDay") or row.get("date"))
            if d == target_date:
                rows.append(row)

        if not rows:
            return sleep.get("stats", {})

        df = pd.DataFrame(rows)
        asleep = float(df["TotalMinutesAsleep"].mean()) if "TotalMinutesAsleep" in df.columns else 0.0
        in_bed = float(df["TotalTimeInBed"].mean()) if "TotalTimeInBed" in df.columns else 0.0
        return {
            "total_sleep_days": int(len(df)),
            "mean_sleep_duration": asleep / 60,
            "mean_time_in_bed": in_bed / 60,
            "total_sleep_hours": asleep / 60
        }

    def _aggregate_daily_reports(self, daily_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid = [r for r in daily_reports if r]
        if not valid:
            return {
                "heart_rate": {},
                "activity": {},
                "sleep": {},
                "medicine": [],
                "diet": []
            }

        hr_values = [r.get("heart_rate", {}).get("mean") for r in valid if r.get("heart_rate", {}).get("mean") is not None]
        step_values = [r.get("activity", {}).get("mean_steps") for r in valid if r.get("activity", {}).get("mean_steps") is not None]
        sleep_values = [r.get("sleep", {}).get("mean_sleep_duration") for r in valid if r.get("sleep", {}).get("mean_sleep_duration") is not None]

        return {
            "heart_rate": {
                "mean": float(pd.Series(hr_values).mean()) if hr_values else 0.0,
                "min": float(pd.Series(hr_values).min()) if hr_values else 0.0,
                "max": float(pd.Series(hr_values).max()) if hr_values else 0.0,
            },
            "activity": {
                "mean_steps": float(pd.Series(step_values).mean()) if step_values else 0.0,
            },
            "sleep": {
                "mean_sleep_duration": float(pd.Series(sleep_values).mean()) if sleep_values else 0.0,
            },
            "medicine": valid[-1].get("medicine", []),
            "diet": valid[-1].get("diet", [])
        }
    
    def generate_daily_report(self, patient_id: str, date: str = None) -> Dict[str, Any]:
        """生成日报"""
        patient_data = self.get_patient_data(patient_id)
        if not patient_data:
            return {}

        target_date = self._parse_date(date) if date else datetime.now().date()
        if target_date is None:
            target_date = datetime.now().date()

        heart_rate_stats = self._hr_stats_for_date(patient_data, target_date)
        activity_stats = self._activity_stats_for_date(patient_data, target_date)
        sleep_stats = self._sleep_stats_for_date(patient_data, target_date)
        
        # 生成日报数据
        daily_report = {
            "patient_id": patient_id,
            "report_type": "daily",
            "date": target_date.strftime("%Y-%m-%d"),
            "heart_rate": heart_rate_stats,
            "activity": activity_stats,
            "sleep": sleep_stats,
            "medicine": patient_data.get("medicine", {}).get("raw_data", []),
            "diet": patient_data.get("diet", {}).get("raw_data", []),
            "summary": self._generate_summary({
                "heart_rate": {"stats": heart_rate_stats},
                "activity": {"stats": activity_stats},
                "sleep": {"stats": sleep_stats}
            }, "daily")
        }
        
        return daily_report
    
    def generate_weekly_report(self, patient_id: str, week_start: str = None) -> Dict[str, Any]:
        """生成周报"""
        patient_data = self.get_patient_data(patient_id)
        if not patient_data:
            return {}

        week_start_date = self._parse_date(week_start) if week_start else (datetime.now().date() - timedelta(days=7))
        if week_start_date is None:
            week_start_date = datetime.now().date() - timedelta(days=7)
        week_end_date = week_start_date + timedelta(days=6)

        daily_reports = []
        current = week_start_date
        while current <= week_end_date:
            daily_reports.append(self.generate_daily_report(patient_id, current.strftime("%Y-%m-%d")))
            current += timedelta(days=1)

        agg = self._aggregate_daily_reports(daily_reports)
        
        # 生成周报数据
        weekly_report = {
            "patient_id": patient_id,
            "report_type": "weekly",
            "week_start": week_start_date.strftime("%Y-%m-%d"),
            "week_end": week_end_date.strftime("%Y-%m-%d"),
            "heart_rate": agg.get("heart_rate", {}),
            "activity": agg.get("activity", {}),
            "sleep": agg.get("sleep", {}),
            "medicine": agg.get("medicine", []),
            "diet": agg.get("diet", []),
            "summary": self._generate_summary({
                "heart_rate": {"stats": agg.get("heart_rate", {})},
                "activity": {"stats": agg.get("activity", {})},
                "sleep": {"stats": agg.get("sleep", {})}
            }, "weekly")
        }
        
        return weekly_report
    
    def generate_monthly_report(self, patient_id: str, month: str = None) -> Dict[str, Any]:
        """生成月报"""
        patient_data = self.get_patient_data(patient_id)
        if not patient_data:
            return {}

        if month:
            try:
                month_start = datetime.strptime(month, "%Y-%m").date().replace(day=1)
            except Exception:
                parsed = self._parse_date(month)
                if parsed:
                    month_start = parsed.replace(day=1)
                else:
                    month_start = datetime.now().date().replace(day=1)
        else:
            month_start = datetime.now().date().replace(day=1)

        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)

        daily_reports = []
        current = month_start
        while current <= month_end:
            daily_reports.append(self.generate_daily_report(patient_id, current.strftime("%Y-%m-%d")))
            current += timedelta(days=1)

        agg = self._aggregate_daily_reports(daily_reports)
        
        # 生成月报数据
        monthly_report = {
            "patient_id": patient_id,
            "report_type": "monthly",
            "month": month_start.strftime("%Y-%m"),
            "month_start": month_start.strftime("%Y-%m-%d"),
            "month_end": month_end.strftime("%Y-%m-%d"),
            "heart_rate": agg.get("heart_rate", {}),
            "activity": agg.get("activity", {}),
            "sleep": agg.get("sleep", {}),
            "medicine": agg.get("medicine", []),
            "diet": agg.get("diet", []),
            "summary": self._generate_summary({
                "heart_rate": {"stats": agg.get("heart_rate", {})},
                "activity": {"stats": agg.get("activity", {})},
                "sleep": {"stats": agg.get("sleep", {})}
            }, "monthly")
        }
        
        return monthly_report
    
    def _generate_summary(self, patient_data: Dict[str, Any], report_type: str) -> str:
        """生成报告摘要"""
        heart_rate = patient_data.get("heart_rate", {}).get("stats", {})
        activity = patient_data.get("activity", {}).get("stats", {})
        sleep = patient_data.get("sleep", {}).get("stats", {})
        
        summary = f"{report_type}报告摘要："
        
        if heart_rate:
            summary += f"平均心率 {heart_rate.get('mean', 0):.1f} 次/分钟，"
        
        if activity:
            summary += f"平均步数 {activity.get('mean_steps', 0):.0f} 步，"
        
        if sleep:
            summary += f"平均睡眠 {sleep.get('mean_sleep_duration', 0):.1f} 小时。"
        
        return summary
    
    def get_data_summary(self, patient_id: str) -> Dict[str, Any]:
        """获取数据摘要"""
        patient_data = self.get_patient_data(patient_id)
        if not patient_data:
            return {}
        
        return {
            "patient_id": patient_id,
            "basic_info": patient_data.get("basic_info", {}),
            "heart_rate_stats": patient_data.get("heart_rate", {}).get("stats", {}),
            "activity_stats": patient_data.get("activity", {}).get("stats", {}),
            "sleep_stats": patient_data.get("sleep", {}).get("stats", {}),
            "medicine_count": patient_data.get("medicine", {}).get("medicine_count", 0),
            "meal_count": patient_data.get("diet", {}).get("meal_count", 0)
        }


# 测试代码
if __name__ == "__main__":
    processor = FitabaseDataProcessor()
    
    # 加载所有患者数据
    all_data = processor.load_all_patients_data()
    
    # 打印每个患者的数据摘要
    for patient_id, data in all_data.items():
        print(f"\n患者 {patient_id} 数据摘要：")
        summary = processor.get_data_summary(patient_id)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        
        # 生成日报
        daily_report = processor.generate_daily_report(patient_id)
        print(f"\n{patient_id} 日报：")
        print(json.dumps(daily_report, ensure_ascii=False, indent=2))
        
        # 生成周报
        weekly_report = processor.generate_weekly_report(patient_id)
        print(f"\n{patient_id} 周报：")
        print(json.dumps(weekly_report, ensure_ascii=False, indent=2))
        
        # 生成月报
        monthly_report = processor.generate_monthly_report(patient_id)
        print(f"\n{patient_id} 月报：")
        print(json.dumps(monthly_report, ensure_ascii=False, indent=2))