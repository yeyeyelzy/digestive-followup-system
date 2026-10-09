from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json
import re
from typing import Any, Dict, List

from ...data_processing.fitabase_data_processor import FitabaseDataProcessor
from ...reporting.time_period_reporter import TimePeriodReporter
from ...result_saving.result_saver import ResultSaver
from ...knowledge_base.rag_knowledge_base import RAGKnowledgeBaseInitializer
from .id_mapping_service import PatientIdMappingService


def _parse_datetime_to_str(value: str) -> str:
    if not value:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw = value.strip()
    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%m/%d/%Y %I:%M:%S %p",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _map_risk_level_by_hr(hr_mean: float) -> str:
    if hr_mean < 55 or hr_mean > 95:
        return "high"
    if hr_mean < 60 or hr_mean > 85:
        return "medium"
    return "low"


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


class HeartTwinService:
    def __init__(self):
        self.processor = FitabaseDataProcessor()

    def get_realtime(self, patient_id: str) -> Dict[str, Any]:
        agent_id = PatientIdMappingService.to_agent_id(patient_id)
        biz_id = PatientIdMappingService.to_biz_id(agent_id)
        patient_data = self.processor.get_patient_data(agent_id)
        if not patient_data:
            raise ValueError("Patient data not found")

        hr_stats = patient_data.get("heart_rate", {}).get("stats", {})
        hr_raw = patient_data.get("heart_rate", {}).get("raw_data", [])
        activity_stats = patient_data.get("activity", {}).get("stats", {})

        heart_rate = _safe_float(hr_stats.get("mean", 70.0), 70.0)
        risk_level = _map_risk_level_by_hr(heart_rate)

        anomaly_features: List[str] = []
        if heart_rate > 95:
            anomaly_features.append("心动过速倾向")
        if heart_rate < 55:
            anomaly_features.append("心动过缓倾向")
        if _safe_float(activity_stats.get("mean_steps", 0)) < 1000:
            anomaly_features.append("活动量偏低")
        if not anomaly_features:
            anomaly_features.append("当前未见明显异常")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hr_raw:
            last = hr_raw[-1]
            raw_time = str(last.get("Time") or last.get("time") or "").strip()
            if raw_time:
                timestamp = _parse_datetime_to_str(raw_time)

        return {
            "patientId": biz_id,
            "timestamp": timestamp,
            "heartRate": round(heart_rate, 2),
            "riskLevel": risk_level,
            "anomalyFeatures": anomaly_features,
        }

    def get_forecast(self, patient_id: str) -> List[Dict[str, Any]]:
        realtime = self.get_realtime(patient_id)
        current_hr = _safe_float(realtime["heartRate"], 70)
        current_risk = realtime["riskLevel"]

        # Minimal-change linear trend extrapolation; preserves existing heuristic style.
        if current_risk == "high":
            hr1, hr2, hr3 = current_hr - 2, current_hr - 6, current_hr - 10
        elif current_risk == "medium":
            hr1, hr2, hr3 = current_hr - 2, current_hr - 4, current_hr - 6
        else:
            hr1, hr2, hr3 = current_hr, current_hr - 1, current_hr - 2

        values = [hr1, hr2, hr3]
        output = []
        for idx, hr in enumerate(values, 1):
            risk = _map_risk_level_by_hr(hr)
            trend = "improve"
            if idx > 1 and hr > values[idx - 2]:
                trend = "worse"
            elif idx > 1 and hr == values[idx - 2]:
                trend = "stable"
            output.append(
                {
                    "patientId": realtime["patientId"],
                    "monthIndex": idx,
                    "monthLabel": f"{idx}个月后",
                    "heartRate": round(max(30.0, min(220.0, hr)), 2),
                    "riskLevel": risk,
                    "recoveryTrend": trend,
                }
            )
        return output


class HealthyLifeDecisionService:
    def __init__(self):
        self.processor = FitabaseDataProcessor()

    def decide(self, patient_id: str, date: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = PatientIdMappingService.to_agent_id(patient_id)
        biz_id = PatientIdMappingService.to_biz_id(agent_id)
        patient_data = self.processor.get_patient_data(agent_id)
        if not patient_data:
            raise ValueError("Patient data not found")

        heart_rate = _safe_float(patient_data.get("heart_rate", {}).get("stats", {}).get("mean", 70))
        steps = _safe_float(patient_data.get("activity", {}).get("stats", {}).get("mean_steps", 0))
        sleep_hours = _safe_float(patient_data.get("sleep", {}).get("stats", {}).get("mean_sleep_duration", 0))

        inferred_vitals_normal = 55 <= heart_rate <= 95 and steps >= 1000 and sleep_hours >= 6

        flags = {
            "dietCompleted": bool(inputs.get("dietCompleted")) if inputs.get("dietCompleted") is not None else bool(patient_data.get("diet", {}).get("raw_data")),
            "behaviorCompleted": bool(inputs.get("behaviorCompleted")) if inputs.get("behaviorCompleted") is not None else bool(patient_data.get("behavior", {}).get("raw_data")),
            "medicineCompleted": bool(inputs.get("medicineCompleted")) if inputs.get("medicineCompleted") is not None else bool(patient_data.get("medicine", {}).get("raw_data")),
            "livingCompleted": bool(inputs.get("livingCompleted")) if inputs.get("livingCompleted") is not None else bool(patient_data.get("living", {}).get("raw_data")),
            "vitalsNormal": bool(inputs.get("vitalsNormal")) if inputs.get("vitalsNormal") is not None else inferred_vitals_normal,
        }

        score = sum(1 for v in flags.values() if v) / len(flags)
        is_healthy_life = score >= 0.8

        reasons: List[str] = []
        if flags["dietCompleted"]:
            reasons.append("饮食执行达标")
        if flags["behaviorCompleted"]:
            reasons.append("行为管理达标")
        if flags["medicineCompleted"]:
            reasons.append("按时服药")
        if flags["livingCompleted"]:
            reasons.append("生活方式达标")
        if flags["vitalsNormal"]:
            reasons.append("生命体征总体平稳")

        return {
            "patientId": biz_id,
            "date": date,
            "isHealthyLife": is_healthy_life,
            "score": round(score, 2),
            "reasons": reasons,
        }


class RiskPredictService:
    def __init__(self):
        self.processor = FitabaseDataProcessor()

    def predict(self, patient_id: str) -> Dict[str, Any]:
        agent_id = PatientIdMappingService.to_agent_id(patient_id)
        biz_id = PatientIdMappingService.to_biz_id(agent_id)
        patient_data = self.processor.get_patient_data(agent_id)
        if not patient_data:
            raise ValueError("Patient data not found")

        hr_raw = patient_data.get("heart_rate", {}).get("raw_data", [])
        values = []
        for row in hr_raw:
            value = row.get("Value")
            if value is not None:
                try:
                    values.append(float(value))
                except Exception:
                    continue

        if not values:
            values = [70.0]

        dist = {"lt55": 0, "55to95": 0, "gt95": 0}
        for v in values:
            if v < 55:
                dist["lt55"] += 1
            elif v > 95:
                dist["gt95"] += 1
            else:
                dist["55to95"] += 1

        total = len(values)
        warning_distribution = {
            "high": round((dist["lt55"] + dist["gt95"]) / total, 4),
            "medium": round(max(0.0, dist["55to95"] / total - 0.5), 4),
            "low": round(min(1.0, dist["55to95"] / total), 4),
        }

        hr_mean = sum(values) / total
        risk_level = _map_risk_level_by_hr(hr_mean)
        description = (
            "心率波动总体可控，建议持续监测。"
            if risk_level == "low"
            else "存在一定波动风险，建议增加监测频次。"
            if risk_level == "medium"
            else "高风险波动，建议尽快由医生评估。"
        )

        return {
            "patientId": biz_id,
            "riskLevel": risk_level,
            "heartRateDistribution": dist,
            "warningDistribution": warning_distribution,
            "description": description,
        }


class HealthReportService:
    _shared_kb = None

    def __init__(self):
        self.processor = FitabaseDataProcessor()
        self.period_reporter = TimePeriodReporter()
        self.result_saver = ResultSaver()
        self.heart_twin_service = HeartTwinService()
        self.healthy_service = HealthyLifeDecisionService()
        self.risk_service = RiskPredictService()

        if HealthReportService._shared_kb is None:
            try:
                HealthReportService._shared_kb = RAGKnowledgeBaseInitializer().initialize(force_rebuild=False)
            except Exception:
                HealthReportService._shared_kb = None
        self.knowledge_base = HealthReportService._shared_kb

    def _generate_report_by_type(
        self,
        agent_id: str,
        report_type: str,
        scene: str,
        period_value: str = ""
    ) -> Dict[str, Any]:
        if report_type == "daily":
            return self.period_reporter.generate_daily_report(agent_id, date=period_value or None, end_type=scene)
        if report_type == "weekly":
            return self.period_reporter.generate_weekly_report(agent_id, week_start=period_value or None, end_type=scene)
        if report_type == "monthly":
            return self.period_reporter.generate_monthly_report(agent_id, month=period_value or None, end_type=scene)
        raise ValueError("Unsupported report type")

    def _weekly_label(self, week_start: datetime.date, week_end: datetime.date) -> str:
        week_num = week_start.isocalendar()[1]
        return f"{week_start.year}-W{week_num:02d}({week_start.strftime('%m.%d')}-{week_end.strftime('%m.%d')})"

    def _monthly_label(self, month_start: datetime.date, month_end: datetime.date) -> str:
        return f"{month_start.strftime('%Y-%m')}({month_start.strftime('%m.%d')}-{month_end.strftime('%m.%d')})"

    def _to_date(self, value: Any):
        if not value:
            return None
        text = str(value).strip()
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]:
            try:
                return datetime.strptime(text, fmt).date()
            except Exception:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
        except Exception:
            return None

    def _to_datetime(self, value: Any):
        if not value:
            return None
        text = str(value).strip()
        candidates = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%m/%d/%Y %I:%M:%S %p",
        ]
        for fmt in candidates:
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            return None

    def _resolve_period_range(self, report: Dict[str, Any], report_type: str):
        today = datetime.now().date()
        if report_type == "daily":
            d = self._to_date(report.get("date")) or today
            return d, d
        if report_type == "weekly":
            ws = self._to_date(report.get("week_start")) or (today - timedelta(days=today.weekday()))
            we = self._to_date(report.get("week_end")) or (ws + timedelta(days=6))
            return ws, we

        ms = self._to_date(report.get("month_start"))
        me = self._to_date(report.get("month_end"))
        if ms and me:
            return ms, me

        m = str(report.get("month") or today.strftime("%Y-%m"))
        try:
            ms = datetime.strptime(m + "-01", "%Y-%m-%d").date()
        except Exception:
            ms = today.replace(day=1)
        next_month = (ms.replace(day=28) + timedelta(days=4)).replace(day=1)
        me = next_month - timedelta(days=1)
        return ms, me

    def _build_visualization_payload(
        self,
        agent_id: str,
        report: Dict[str, Any],
        report_type: str,
        period_label: str,
    ) -> Dict[str, Any]:
        start_date, end_date = self._resolve_period_range(report, report_type)
        patient_data = self.processor.get_patient_data(agent_id)

        all_heart_rows = []
        for row in patient_data.get("heart_rate", {}).get("raw_data", []):
            dt = self._to_datetime(row.get("Time") or row.get("time"))
            if not dt:
                continue
            all_heart_rows.append((dt, _safe_float(row.get("Value"), 0.0)))

        all_heart_rows.sort(key=lambda x: x[0])
        heart_rows = [(dt, v) for dt, v in all_heart_rows if start_date <= dt.date() <= end_date]

        # 当目标周期没有心率点时，回退到最近可用的24小时窗口，确保趋势图可生成。
        if not heart_rows and all_heart_rows:
            prev_day = start_date - timedelta(days=1)
            next_day = end_date + timedelta(days=1)
            prev_rows = [(dt, v) for dt, v in all_heart_rows if dt.date() == prev_day]
            next_rows = [(dt, v) for dt, v in all_heart_rows if dt.date() == next_day]
            if prev_rows:
                heart_rows = prev_rows
            elif next_rows:
                heart_rows = next_rows
            else:
                heart_rows = all_heart_rows[-720:]

        if len(heart_rows) > 720:
            step = max(1, len(heart_rows) // 720)
            heart_rows = heart_rows[::step]

        heart_times = [dt.strftime("%m-%d %H:%M") for dt, _ in heart_rows]
        heart_values = [round(v, 2) for _, v in heart_rows]

        if isinstance(report.get("heart_rate"), dict):
            hr_mean = _safe_float(report.get("heart_rate", {}).get("mean", 0.0))
        else:
            hr_mean = _safe_float(report.get("data_analysis", {}).get("heart_rate", {}).get("mean", 0.0))
        if hr_mean == 0.0 and heart_values:
            hr_mean = sum(heart_values) / len(heart_values)

        activity_rows = []
        for row in patient_data.get("activity", {}).get("raw_data", []):
            d = self._to_date(row.get("ActivityDate") or row.get("date"))
            if d and start_date <= d <= end_date:
                activity_rows.append(row)

        light = sum(_safe_float(r.get("LightlyActiveMinutes"), 0.0) for r in activity_rows)
        fairly = sum(_safe_float(r.get("FairlyActiveMinutes"), 0.0) for r in activity_rows)
        very = sum(_safe_float(r.get("VeryActiveMinutes"), 0.0) for r in activity_rows)

        physiological_warning = sum(1 for v in heart_values if v < 55 or v > 110)
        yellow_watch = sum(1 for v in heart_values if (55 <= v < 60) or (95 < v <= 110))
        normal = max(0, len(heart_values) - physiological_warning - yellow_watch)

        day_cursor = start_date
        day_labels: List[str] = []
        day_hr: List[float] = []
        day_steps: List[float] = []
        day_active_minutes: List[float] = []
        day_mets: List[float] = []
        day_sleep_hours: List[float] = []

        hr_by_day: Dict[str, List[float]] = {}
        for dt, v in heart_rows:
            k = dt.strftime("%Y-%m-%d")
            hr_by_day.setdefault(k, []).append(v)

        activity_by_day: Dict[str, Dict[str, float]] = {}
        for row in activity_rows:
            d = self._to_date(row.get("ActivityDate") or row.get("date"))
            if not d:
                continue
            k = d.strftime("%Y-%m-%d")
            cur = activity_by_day.setdefault(k, {"steps": 0.0, "active_minutes": 0.0})
            cur["steps"] += _safe_float(row.get("TotalSteps"), 0.0)
            cur["active_minutes"] += _safe_float(row.get("VeryActiveMinutes"), 0.0) + _safe_float(row.get("FairlyActiveMinutes"), 0.0)

        sleep_by_day: Dict[str, List[float]] = {}
        for row in patient_data.get("sleep", {}).get("raw_data", []):
            d = self._to_date(row.get("SleepDay") or row.get("date"))
            if not d or not (start_date <= d <= end_date):
                continue
            k = d.strftime("%Y-%m-%d")
            sleep_by_day.setdefault(k, []).append(_safe_float(row.get("TotalMinutesAsleep"), 0.0) / 60.0)

        while day_cursor <= end_date:
            key = day_cursor.strftime("%Y-%m-%d")
            day_labels.append(day_cursor.strftime("%m-%d"))
            hr_vals = hr_by_day.get(key, [])
            sl_vals = sleep_by_day.get(key, [])
            day_hr.append(round(sum(hr_vals) / len(hr_vals), 2) if hr_vals else 0.0)
            day_steps.append(round(activity_by_day.get(key, {}).get("steps", 0.0), 2))
            day_active_minutes.append(round(activity_by_day.get(key, {}).get("active_minutes", 0.0), 2))
            day_mets.append(round(activity_by_day.get(key, {}).get("active_minutes", 0.0) / 180.0, 2))
            day_sleep_hours.append(round(sum(sl_vals) / len(sl_vals), 2) if sl_vals else 0.0)
            day_cursor += timedelta(days=1)

        activity_stats = patient_data.get("activity", {}).get("stats", {})
        sleep_stats = patient_data.get("sleep", {}).get("stats", {})
        fallback_steps = _safe_float(activity_stats.get("mean_steps"), 0.0)
        fallback_sleep = _safe_float(sleep_stats.get("mean_sleep_duration"), 0.0)

        bar_steps = round(sum(day_steps) / len(day_steps), 2) if day_steps else 0.0
        bar_sleep = round(sum(day_sleep_hours) / len(day_sleep_hours), 2) if day_sleep_hours else 0.0
        if bar_steps <= 0 and fallback_steps > 0:
            bar_steps = round(fallback_steps, 2)
        if bar_sleep <= 0 and fallback_sleep > 0:
            bar_sleep = round(fallback_sleep, 2)

        baseline_trace = {
            "times": [],
            "resting_heart_rate": [],
            "sdnn": [],
            "deep_sleep_change_pct": [],
            "daily_steps": [],
        }

        if report_type in ("weekly", "monthly"):
            trace_rows = list(heart_rows) if heart_rows else list(all_heart_rows)
            if trace_rows:
                # 先按时间窗口聚合，降低秒级噪声，使基线轨迹更平滑。
                bucket_minutes = 60 if report_type == "weekly" else 360
                bucket_map: Dict[str, List[float]] = {}
                for dt, v in trace_rows:
                    total_minute = dt.hour * 60 + dt.minute
                    slot_start = (total_minute // bucket_minutes) * bucket_minutes
                    slot_hour = slot_start // 60
                    slot_minute = slot_start % 60
                    bucket_dt = dt.replace(hour=slot_hour, minute=slot_minute, second=0, microsecond=0)
                    bucket_key = bucket_dt.strftime("%Y-%m-%d %H:%M")
                    bucket_map.setdefault(bucket_key, []).append(v)

                compact_rows: List[tuple] = []
                for key in sorted(bucket_map.keys()):
                    vals = bucket_map.get(key, [])
                    if not vals:
                        continue
                    avg_v = sum(vals) / len(vals)
                    compact_rows.append((datetime.strptime(key, "%Y-%m-%d %H:%M"), avg_v))

                if compact_rows:
                    trace_rows = compact_rows

            if len(trace_rows) > 520:
                step = max(1, len(trace_rows) // 520)
                trace_rows = trace_rows[::step]

            if trace_rows:
                trace_times = [dt.strftime("%m-%d %H:%M") for dt, _ in trace_rows]
                trace_hr = [round(v, 2) for _, v in trace_rows]

                trace_sdnn: List[float] = []
                window = 12
                for i in range(len(trace_hr)):
                    left = max(0, i - window + 1)
                    seg = trace_hr[left:i + 1]
                    if len(seg) < 2:
                        trace_sdnn.append(0.0)
                    else:
                        mean = sum(seg) / len(seg)
                        var = sum((x - mean) * (x - mean) for x in seg) / (len(seg) - 1)
                        trace_sdnn.append(round(var ** 0.5, 2))

                day_keys = sorted(sleep_by_day.keys())
                day_sleep_mean: Dict[str, float] = {}
                for k in day_keys:
                    vals = sleep_by_day.get(k, [])
                    day_sleep_mean[k] = (sum(vals) / len(vals)) if vals else 0.0

                day_sleep_change: Dict[str, float] = {}
                prev_val = None
                for k in day_keys:
                    cur = day_sleep_mean.get(k, 0.0)
                    if prev_val and prev_val > 0:
                        day_sleep_change[k] = round((cur - prev_val) / prev_val * 100.0, 2)
                    else:
                        day_sleep_change[k] = 0.0
                    if cur > 0:
                        prev_val = cur

                # 如果睡眠数据缺失/常数导致全0，使用活动变化生成温和代理，避免轨迹图退化为直线。
                if day_sleep_change and all(abs(v) < 1e-9 for v in day_sleep_change.values()):
                    step_keys = sorted(activity_by_day.keys())
                    if step_keys:
                        prev_steps = None
                        for k in step_keys:
                            cur_steps = activity_by_day.get(k, {}).get("steps", 0.0)
                            if prev_steps and prev_steps > 0:
                                proxy = ((cur_steps - prev_steps) / prev_steps) * 8.0
                                day_sleep_change[k] = round(max(-8.0, min(8.0, proxy)), 2)
                            else:
                                day_sleep_change[k] = 0.0
                            if cur_steps > 0:
                                prev_steps = cur_steps

                trace_sleep_change: List[float] = []
                trace_steps: List[float] = []
                for dt, _ in trace_rows:
                    day_key = dt.strftime("%Y-%m-%d")
                    trace_sleep_change.append(round(day_sleep_change.get(day_key, 0.0), 2))
                    trace_steps.append(round(activity_by_day.get(day_key, {}).get("steps", 0.0), 2))

                # 若深睡变化仍全0（数据缺失场景），用SDNN波动构造轻微代理，避免图表退化为水平线。
                if trace_sleep_change and all(abs(v) < 1e-9 for v in trace_sleep_change):
                    sdnn_vals = [v for v in trace_sdnn if v > 0]
                    if len(sdnn_vals) >= 2:
                        mean_sdnn = sum(sdnn_vals) / len(sdnn_vals)
                        var_sdnn = sum((x - mean_sdnn) * (x - mean_sdnn) for x in sdnn_vals) / max(1, len(sdnn_vals) - 1)
                        std_sdnn = var_sdnn ** 0.5
                        if std_sdnn > 1e-9:
                            trace_sleep_change = [round(max(-3.0, min(3.0, ((v - mean_sdnn) / std_sdnn) * 0.8)), 2) for v in trace_sdnn]

                baseline_trace = {
                    "times": trace_times,
                    "resting_heart_rate": trace_hr,
                    "sdnn": trace_sdnn,
                    "deep_sleep_change_pct": trace_sleep_change,
                    "daily_steps": trace_steps,
                }

        # 日报按每5分钟生成一条记录，使用真实分钟数据聚合，避免线性伪造趋势。
        if report_type == "daily":
            interval_labels: List[str] = []
            interval_hr: List[float] = []
            interval_steps: List[float] = []
            interval_active_minutes: List[float] = []
            interval_mets: List[float] = []
            interval_sleep_hours: List[float] = []

            bucket_minutes = 5

            hr_by_interval: Dict[str, List[float]] = {}
            for dt, v in heart_rows:
                minute_slot = (dt.minute // bucket_minutes) * bucket_minutes
                bucket_dt = dt.replace(minute=minute_slot, second=0, microsecond=0)
                interval_key = bucket_dt.strftime("%Y-%m-%d %H:%M")
                hr_by_interval.setdefault(interval_key, []).append(v)

            step_by_interval: Dict[str, float] = {}
            minute_steps_rows = patient_data.get("activity", {}).get("minute_steps_raw", [])
            for row in minute_steps_rows:
                dt = self._to_datetime(row.get("ActivityMinute") or row.get("activityMinute") or row.get("date"))
                if not dt or dt.date() != start_date:
                    continue
                minute_slot = (dt.minute // bucket_minutes) * bucket_minutes
                bucket_dt = dt.replace(minute=minute_slot, second=0, microsecond=0)
                interval_key = bucket_dt.strftime("%Y-%m-%d %H:%M")
                step_by_interval[interval_key] = step_by_interval.get(interval_key, 0.0) + _safe_float(row.get("Steps"), 0.0)

            active_by_interval: Dict[str, float] = {}
            minute_intensity_rows = patient_data.get("activity", {}).get("minute_intensity_raw", [])
            for row in minute_intensity_rows:
                dt = self._to_datetime(row.get("ActivityMinute") or row.get("activityMinute") or row.get("date"))
                if not dt or dt.date() != start_date:
                    continue
                intensity = _safe_float(row.get("Intensity"), 0.0)
                if intensity <= 0:
                    continue
                minute_slot = (dt.minute // bucket_minutes) * bucket_minutes
                bucket_dt = dt.replace(minute=minute_slot, second=0, microsecond=0)
                interval_key = bucket_dt.strftime("%Y-%m-%d %H:%M")
                active_by_interval[interval_key] = active_by_interval.get(interval_key, 0.0) + 1.0

            mets_sum_by_interval: Dict[str, float] = {}
            mets_cnt_by_interval: Dict[str, int] = {}
            minute_mets_rows = patient_data.get("activity", {}).get("minute_mets_raw", [])
            for row in minute_mets_rows:
                dt = self._to_datetime(row.get("ActivityMinute") or row.get("activityMinute") or row.get("date"))
                if not dt or dt.date() != start_date:
                    continue
                mets_val = _safe_float(row.get("METs"), 0.0)
                if mets_val <= 0:
                    continue
                minute_slot = (dt.minute // bucket_minutes) * bucket_minutes
                bucket_dt = dt.replace(minute=minute_slot, second=0, microsecond=0)
                interval_key = bucket_dt.strftime("%Y-%m-%d %H:%M")
                mets_sum_by_interval[interval_key] = mets_sum_by_interval.get(interval_key, 0.0) + mets_val
                mets_cnt_by_interval[interval_key] = mets_cnt_by_interval.get(interval_key, 0) + 1

            mets_by_interval: Dict[str, float] = {}
            for k, total in mets_sum_by_interval.items():
                cnt = max(1, mets_cnt_by_interval.get(k, 0))
                mets_by_interval[k] = round(total / cnt, 2)

            sleep_by_interval: Dict[str, float] = {}
            minute_sleep_rows = patient_data.get("sleep", {}).get("minute_raw", [])
            for row in minute_sleep_rows:
                dt = self._to_datetime(row.get("date") or row.get("SleepDay") or row.get("ActivityMinute"))
                if not dt or dt.date() != start_date:
                    continue
                sleep_state = _safe_int(row.get("value"), 0)
                # Fitabase分钟睡眠通常1/2代表睡眠状态，3代表清醒。
                if sleep_state <= 0 or sleep_state >= 3:
                    continue
                minute_slot = (dt.minute // bucket_minutes) * bucket_minutes
                bucket_dt = dt.replace(minute=minute_slot, second=0, microsecond=0)
                interval_key = bucket_dt.strftime("%Y-%m-%d %H:%M")
                sleep_by_interval[interval_key] = sleep_by_interval.get(interval_key, 0.0) + 1.0 / 60.0

            all_interval_keys = sorted(set(hr_by_interval.keys()) | set(step_by_interval.keys()) | set(active_by_interval.keys()) | set(sleep_by_interval.keys()))

            if not all_interval_keys and heart_times and heart_values:
                # 极端情况下至少取若干原始点，避免单点或空图。
                sample = min(len(heart_times), 288)
                interval_labels = heart_times[:sample]
                interval_hr = [round(v, 2) for v in heart_values[:sample]]
                interval_steps = [0.0 for _ in range(sample)]
                interval_active_minutes = [0.0 for _ in range(sample)]
                interval_mets = [0.0 for _ in range(sample)]
                interval_sleep_hours = [0.0 for _ in range(sample)]
            else:
                last_hr = hr_mean if hr_mean > 0 else 0.0
                sleep_total_hours = 0.0
                if day_sleep_hours:
                    sleep_total_hours = day_sleep_hours[0]
                if sleep_total_hours <= 0 and sleep_by_interval:
                    sleep_total_hours = round(sum(sleep_by_interval.values()), 2)
                if sleep_total_hours <= 0 and fallback_sleep > 0:
                    sleep_total_hours = round(fallback_sleep, 2)

                for interval_key in all_interval_keys:
                    label_dt = datetime.strptime(interval_key, "%Y-%m-%d %H:%M")
                    interval_labels.append(label_dt.strftime("%m-%d %H:%M"))

                    hr_vals = hr_by_interval.get(interval_key, [])
                    if hr_vals:
                        cur_hr = round(sum(hr_vals) / len(hr_vals), 2)
                        last_hr = cur_hr
                    else:
                        cur_hr = round(last_hr, 2)
                    interval_hr.append(cur_hr)

                    interval_steps.append(round(step_by_interval.get(interval_key, 0.0), 2))
                    interval_active_minutes.append(round(active_by_interval.get(interval_key, 0.0), 2))
                    interval_mets.append(round(mets_by_interval.get(interval_key, 0.0), 2))
                    interval_sleep_hours.append(round(sleep_total_hours, 2))

            if interval_labels:
                day_labels = interval_labels
                day_hr = interval_hr
                day_steps = interval_steps
                day_active_minutes = interval_active_minutes
                day_mets = interval_mets if interval_mets else [0.0 for _ in interval_labels]
                day_sleep_hours = interval_sleep_hours

        return {
            "reportType": report_type,
            "periodLabel": period_label,
            "range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
            "barChart": {
                "labels": ["heart_rate", "steps", "sleep_hours"],
                "values": [
                    round(hr_mean, 2),
                    bar_steps,
                    bar_sleep,
                ],
                "units": ["bpm", "steps", "hours"],
            },
            "heart_rate_trend": {
                "times": heart_times,
                "values": heart_values,
                "baseline": round(hr_mean if hr_mean else 78.0, 2),
            },
            "activity_distribution": {
                "labels": ["轻强度", "中强度", "高强度"],
                "values": [round(light, 2), round(fairly, 2), round(very, 2)],
            },
            "risk_warning_distribution": {
                "labels": ["生理性预警", "黄色关注", "正常"],
                "values": [physiological_warning, yellow_watch, normal],
            },
            "multi_metric_trend": {
                "times": day_labels,
                "heart_rate": day_hr,
                "steps": day_steps,
                "active_minutes": day_active_minutes,
                "mets": day_mets,
                "sleep_hours": day_sleep_hours,
            },
            "thresholds": {
                "heart_rate": {"min": 55, "max": 95},
                "steps": {"min": 3000},
                "sleep_hours": {"min": 6.0},
            },
            "baseline_trace": baseline_trace,
        }

    def _build_module_outputs(
        self,
        agent_id: str,
        biz_id: str,
        report: Dict[str, Any],
        report_type: str,
        period_label: str,
    ) -> Dict[str, Any]:
        today = datetime.now().strftime("%Y-%m-%d")
        heart_realtime = self.heart_twin_service.get_realtime(biz_id)
        heart_forecast = self.heart_twin_service.get_forecast(biz_id)
        healthy_decision = self.healthy_service.decide(biz_id, today, {})
        risk_prediction = self.risk_service.predict(biz_id)
        visualization_payload = self._build_visualization_payload(agent_id, report, report_type, period_label)

        return {
            "heart_3d": {
                "realtime": heart_realtime,
                "forecast": heart_forecast
            },
            "rehab_achievement": {
                "patientId": healthy_decision.get("patientId", biz_id),
                "date": healthy_decision.get("date", today),
                "healthy_today": bool(healthy_decision.get("isHealthyLife", False)),
                "score": healthy_decision.get("score", 0),
                "reasons": healthy_decision.get("reasons", [])
            },
            "risk_prediction": risk_prediction,
            "report_visualization": visualization_payload,
        }

    def _build_rag_query(self, report: Dict[str, Any], report_type: str, scene: str) -> str:
        heart_rate = _safe_float(report.get("heart_rate", {}).get("mean", 0.0))
        if heart_rate == 0.0:
            heart_rate = _safe_float(report.get("data_analysis", {}).get("heart_rate", {}).get("mean", 0.0))
        steps = _safe_float(report.get("activity", {}).get("mean_steps", 0.0))
        if steps == 0.0:
            steps = _safe_float(report.get("data_analysis", {}).get("activity", {}).get("mean_steps", 0.0))
        sleep_hours = _safe_float(report.get("sleep", {}).get("mean_sleep_duration", 0.0))
        if sleep_hours == 0.0:
            sleep_hours = _safe_float(report.get("data_analysis", {}).get("sleep", {}).get("mean_sleep_duration", 0.0))

        scene_text = {
            "doctor": "医生端",
            "family": "家属端",
            "patient": "患者端",
        }.get(scene, scene)

        lifestyle = report.get("lifestyle_context", {}) if isinstance(report.get("lifestyle_context"), dict) else {}
        med_days = _safe_int(lifestyle.get("medicine_days", 0))
        diet_days = _safe_int(lifestyle.get("diet_days", 0))
        activity_days = _safe_int(lifestyle.get("activity_days", 0))
        sleep_days = _safe_int(lifestyle.get("sleep_days", 0))

        return (
            f"PCI术后康复 {scene_text} {report_type}报告: "
            f"心率{heart_rate:.1f} 步数{steps:.0f} 睡眠{sleep_hours:.1f}。"
            f"服药记录天数{med_days} 饮食记录天数{diet_days} 运动记录天数{activity_days} 睡眠记录天数{sleep_days}。"
            f"请给出循证的深层原因分析、风险提示与分端干预建议。"
        )

    def _extract_metrics(self, report: Dict[str, Any]) -> Dict[str, float]:
        heart_rate = _safe_float(report.get("heart_rate", {}).get("mean", 0.0))
        if heart_rate == 0.0:
            heart_rate = _safe_float(report.get("data_analysis", {}).get("heart_rate", {}).get("mean", 0.0))

        steps = _safe_float(report.get("activity", {}).get("mean_steps", 0.0))
        if steps == 0.0:
            steps = _safe_float(report.get("data_analysis", {}).get("activity", {}).get("mean_steps", 0.0))

        sleep_hours = _safe_float(report.get("sleep", {}).get("mean_sleep_duration", 0.0))
        if sleep_hours == 0.0:
            sleep_hours = _safe_float(report.get("data_analysis", {}).get("sleep", {}).get("mean_sleep_duration", 0.0))

        return {
            "heart_rate": round(heart_rate, 2),
            "steps": round(steps, 2),
            "sleep_hours": round(sleep_hours, 2),
        }

    def _row_in_range(self, row: Dict[str, Any], start_date, end_date) -> bool:
        keys = [
            "date", "Date", "recordDate", "RecordDate", "CreateTime", "createTime",
            "Timestamp", "timestamp", "ActivityDate", "SleepDay", "Time",
        ]
        for key in keys:
            value = row.get(key)
            if value is None:
                continue
            dt = self._to_datetime(value)
            if dt:
                if start_date <= dt.date() <= end_date:
                    return True
                continue
            d = self._to_date(value)
            if d and start_date <= d <= end_date:
                return True
        return False

    def _collect_lifestyle_context(self, agent_id: str, start_date, end_date) -> Dict[str, int]:
        data = self.processor.get_patient_data(agent_id) or {}

        def count_days(rows: List[Dict[str, Any]]) -> int:
            days = set()
            for row in rows:
                keys = [
                    "date", "Date", "recordDate", "RecordDate", "CreateTime", "createTime",
                    "Timestamp", "timestamp", "ActivityDate", "SleepDay", "Time",
                ]
                for key in keys:
                    value = row.get(key)
                    if value is None:
                        continue
                    dt = self._to_datetime(value)
                    if dt and start_date <= dt.date() <= end_date:
                        days.add(dt.date().strftime("%Y-%m-%d"))
                        break
                    d = self._to_date(value)
                    if d and start_date <= d <= end_date:
                        days.add(d.strftime("%Y-%m-%d"))
                        break
            return len(days)

        activity_rows = data.get("activity", {}).get("raw_data", [])
        sleep_rows = data.get("sleep", {}).get("raw_data", [])
        diet_rows = data.get("diet", {}).get("raw_data", [])
        behavior_rows = data.get("behavior", {}).get("raw_data", [])
        medicine_rows = data.get("medicine", {}).get("raw_data", [])
        living_rows = data.get("living", {}).get("raw_data", [])

        hr_values: List[float] = []
        for row in data.get("heart_rate", {}).get("raw_data", []):
            if not self._row_in_range(row, start_date, end_date):
                continue
            v = row.get("Value")
            if v is None:
                continue
            hr_values.append(_safe_float(v, 0.0))

        steps_values: List[float] = []
        for row in activity_rows:
            if not self._row_in_range(row, start_date, end_date):
                continue
            steps_values.append(_safe_float(row.get("TotalSteps"), 0.0))

        sleep_values: List[float] = []
        for row in sleep_rows:
            if not self._row_in_range(row, start_date, end_date):
                continue
            minutes = _safe_float(row.get("TotalMinutesAsleep"), 0.0)
            if minutes > 0:
                sleep_values.append(minutes / 60.0)

        hr_mean = round(sum(hr_values) / len(hr_values), 2) if hr_values else 0.0
        steps_mean = round(sum(steps_values) / len(steps_values), 2) if steps_values else 0.0
        sleep_mean = round(sum(sleep_values) / len(sleep_values), 2) if sleep_values else 0.0

        if hr_mean <= 0:
            hr_mean = round(_safe_float(data.get("heart_rate", {}).get("stats", {}).get("mean"), 0.0), 2)
        if steps_mean <= 0:
            steps_mean = round(_safe_float(data.get("activity", {}).get("stats", {}).get("mean_steps"), 0.0), 2)
        if sleep_mean <= 0:
            sleep_mean = round(_safe_float(data.get("sleep", {}).get("stats", {}).get("mean_sleep_duration"), 0.0), 2)

        return {
            "activity_days": count_days(activity_rows),
            "sleep_days": count_days(sleep_rows),
            "diet_days": count_days(diet_rows),
            "behavior_days": count_days(behavior_rows),
            "medicine_days": count_days(medicine_rows),
            "living_days": count_days(living_rows),
            "heart_rate_mean": hr_mean,
            "steps_mean": steps_mean,
            "sleep_mean": sleep_mean,
        }

    def _infer_deep_medical_insights(
        self,
        metrics: Dict[str, float],
        lifestyle: Dict[str, int],
        report_type: str,
        hits: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        hr = metrics.get("heart_rate", 0.0)
        steps = metrics.get("steps", 0.0)
        sleep_hours = metrics.get("sleep_hours", 0.0)

        observations: List[str] = []
        possible_causes: List[str] = []
        clinical_implications: List[str] = []

        if hr >= 95:
            observations.append(f"{report_type}周期平均心率偏高（{hr:.1f} bpm）")
            possible_causes.append("近期运动负荷恢复节奏偏快或交感神经兴奋增加")
            clinical_implications.append("提示心肌耗氧负担可能增加，需警惕诱发缺血症状")
        elif hr <= 55 and hr > 0:
            observations.append(f"{report_type}周期平均心率偏低（{hr:.1f} bpm）")
            possible_causes.append("药物反应、睡眠紊乱或体力下降可能共同影响心率")
            clinical_implications.append("若伴乏力/头晕需评估窦房结功能与用药耐受")
        else:
            observations.append(f"{report_type}周期平均心率处于相对可控区间（{hr:.1f} bpm）")

        if steps < 2000:
            observations.append(f"活动量偏低（{steps:.0f} 步/日）")
            possible_causes.append("康复训练依从性不足或对活动诱发不适存在担忧")
            clinical_implications.append("去条件化风险上升，可能影响心肺耐力恢复")
        elif steps > 8000:
            observations.append(f"活动量较高（{steps:.0f} 步/日）")
            possible_causes.append("近期可能存在过快恢复行为")
            clinical_implications.append("需结合症状判断是否超出个体化康复阈值")

        if sleep_hours < 6:
            observations.append(f"睡眠时长不足（{sleep_hours:.1f} 小时）")
            possible_causes.append("夜间焦虑、作息不规律或睡眠质量下降")
            clinical_implications.append("睡眠不足可放大炎症反应并增加心血管事件风险")

        if lifestyle.get("medicine_days", 0) == 0:
            possible_causes.append("周期内缺少可识别的服药记录，存在依从性风险")
            clinical_implications.append("抗血小板/他汀等关键治疗链可能中断")
        if lifestyle.get("diet_days", 0) == 0:
            possible_causes.append("饮食管理记录缺失，难以排除高盐高脂摄入")
            clinical_implications.append("代谢负荷可能掩盖在表面指标稳定之下")

        evidence_quotes: List[str] = []
        for hit in hits[:2]:
            text = re.sub(r"\s+", " ", str(hit.get("content", "")).strip())
            if text:
                evidence_quotes.append(text[:120] + ("..." if len(text) > 120 else ""))

        return {
            "observations": observations[:4],
            "possible_causes": possible_causes[:4],
            "clinical_implications": clinical_implications[:4],
            "evidence_quotes": evidence_quotes,
        }

    def _format_scene_recommendations(
        self,
        scene: str,
        report_type: str,
        insights: Dict[str, List[str]],
        hits: List[Dict[str, Any]],
    ) -> List[str]:
        src = "；".join(
            [
                hit.get("file_name") or Path(hit.get("file_path", "")).name
                for hit in hits[:2]
                if (hit.get("file_name") or hit.get("file_path"))
            ]
        )
        source_text = f"（循证来源：{src}）" if src else ""

        obs = insights.get("observations", [])
        causes = insights.get("possible_causes", [])
        implications = insights.get("clinical_implications", [])

        if scene == "doctor":
            recs = [
                f"临床解读：{obs[0] if obs else '当前指标总体平稳'}，建议结合症状谱与生命体征趋势进行分层评估。{source_text}",
                f"潜在机制：{causes[0] if causes else '暂无明确单一诱因'}，建议复核运动处方执行强度、睡眠节律及药物依从性。",
                f"医学提示：{implications[0] if implications else '继续动态监测风险变化'}。必要时评估心电、血压及电解质状态。",
                f"干预建议：按{report_type}周期设定可量化目标（心率区间、步数区间、睡眠下限），并在下周期复评。",
            ]
        elif scene == "family":
            recs = [
                f"照护重点：{obs[0] if obs else '患者总体状态尚可'}，请重点观察患者是否有胸闷、心悸、乏力等不适。{source_text}",
                f"可能原因：{causes[0] if causes else '近期生活节律可能波动'}，家属可协助患者把作息、饮食和活动时间固定下来。",
                f"家庭行动：{implications[0] if implications else '当前以稳定恢复节奏为主'}，若症状持续或加重请及时联系医生。",
                "沟通建议：每天用一句积极反馈强化患者信心，避免因焦虑导致康复执行中断。",
            ]
        else:
            recs = [
                f"你的恢复重点：{obs[0] if obs else '今天整体状态不错'}，这不是简单数字变化，而是身体在给你信号。{source_text}",
                f"背后原因可能是：{causes[0] if causes else '近期节律有点乱'}，建议先把睡眠、活动和饮食节奏稳定下来。",
                f"医学上需要注意：{implications[0] if implications else '继续保持当前节奏'}，一旦出现胸痛、明显气短或头晕要尽快就医。",
                f"可执行计划：未来一个{report_type}周期内，按“规律作息+适量活动+健康饮食”三件事持续打卡。",
            ]

        return [r for r in recs if r]

    def _remove_medication_text_for_non_doctor(self, recs: List[str]) -> List[str]:
        blocked = ["用药", "服药", "药物", "处方", "抗血小板", "他汀", "药"]
        safe = [item for item in recs if item and all(word not in item for word in blocked)]
        if safe:
            return safe
        return [
            "建议以规律作息、适量活动和健康饮食为主线，连续观察恢复趋势。",
            "若出现胸闷、胸痛、明显气短或头晕，请及时就医并联系医生。",
        ]

    def _apply_rag_to_report(self, agent_id: str, report: Dict[str, Any], report_type: str, scene: str) -> List[Dict[str, Any]]:
        kb = self.knowledge_base
        if not kb or not hasattr(kb, "query") or not kb.is_ready():
            return []

        start_date, end_date = self._resolve_period_range(report, report_type)
        lifestyle = self._collect_lifestyle_context(agent_id, start_date, end_date)
        report["lifestyle_context"] = lifestyle

        query = self._build_rag_query(report, report_type, scene)
        hits = kb.query(query, top_k=3)
        if not hits:
            return []

        # 统一将RAG建议映射到 recommendations，保证PDF中可展示。
        base_recs = list(report.get("recommendations", []))
        if not base_recs and isinstance(report.get("care_advice"), list):
            base_recs = list(report.get("care_advice", []))
        if not base_recs and isinstance(report.get("clinical_assessment"), dict):
            base_recs = list(report.get("clinical_assessment", {}).get("recommendations", []))

        metrics = self._extract_metrics(report)
        metrics["heart_rate"] = metrics["heart_rate"] if metrics["heart_rate"] > 0 else _safe_float(lifestyle.get("heart_rate_mean"), 0.0)
        metrics["steps"] = metrics["steps"] if metrics["steps"] > 0 else _safe_float(lifestyle.get("steps_mean"), 0.0)
        metrics["sleep_hours"] = metrics["sleep_hours"] if metrics["sleep_hours"] > 0 else _safe_float(lifestyle.get("sleep_mean"), 0.0)
        insights = self._infer_deep_medical_insights(metrics, lifestyle, report_type, hits)
        scene_recs = self._format_scene_recommendations(scene, report_type, insights, hits)
        merged_recs: List[str] = []
        for rec in scene_recs + base_recs:
            if rec and rec not in merged_recs:
                merged_recs.append(rec)

        for quote in insights.get("evidence_quotes", [])[:1]:
            ref_text = f"证据摘录：{quote}"
            if ref_text not in merged_recs:
                merged_recs.append(ref_text)

        if scene in ("patient", "family"):
            merged_recs = self._remove_medication_text_for_non_doctor(merged_recs)

        report["recommendations"] = merged_recs[:8]
        if scene == "family":
            report["care_advice"] = merged_recs[:4]
        report["clinical_reasoning"] = {
            "observations": insights.get("observations", []),
            "possible_causes": insights.get("possible_causes", []),
            "medical_implications": insights.get("clinical_implications", []),
            "style": scene,
        }
        report["rag_references"] = [
            {
                "file": hit.get("file_name") or Path(hit.get("file_path", "")).name,
                "path": hit.get("file_path", ""),
                "score": hit.get("score", 0.0),
                "evidence_level": hit.get("evidence_level", "C级"),
                "content": hit.get("content", ""),
            }
            for hit in hits
        ]
        return report["rag_references"]

    def get_report(
        self,
        patient_id: str,
        report_type: str,
        scene: str = "patient",
        period_value: str = "",
        period_label: str = "",
    ) -> Dict[str, Any]:
        agent_id = PatientIdMappingService.to_agent_id(patient_id)
        biz_id = PatientIdMappingService.to_biz_id(agent_id)

        report = self._generate_report_by_type(agent_id, report_type, scene, period_value)

        if not report:
            raise ValueError("Patient report not found")

        if "error" in report:
            raise ValueError(str(report.get("error")))

        if not period_label:
            if report_type == "daily":
                period_label = str(report.get("date") or datetime.now().strftime("%Y-%m-%d"))
            elif report_type == "weekly":
                ws = str(report.get("week_start") or datetime.now().strftime("%Y-%m-%d"))
                we = str(report.get("week_end") or datetime.now().strftime("%Y-%m-%d"))
                period_label = f"{ws}_to_{we}"
            else:
                period_label = str(report.get("month") or datetime.now().strftime("%Y-%m"))

        rag_refs = self._apply_rag_to_report(agent_id, report, report_type, scene)

        module_outputs = self._build_module_outputs(agent_id, biz_id, report, report_type, period_label)
        bundle_meta = self.result_saver.save_report_bundle_legacy(
            patient_id=agent_id,
            report=report,
            report_type=report_type,
            end_type=scene,
            period_label=period_label,
            module_outputs=module_outputs,
        )

        report["patient_id"] = biz_id
        report["patientId"] = biz_id
        report["reportType"] = report_type
        report["scene"] = scene
        report["artifacts"] = {
            "json": bundle_meta.get("paths", {}).get("json"),
            "image": bundle_meta.get("paths", {}).get("image"),
            "pdf": bundle_meta.get("paths", {}).get("pdf"),
            "module_files": bundle_meta.get("paths", {}).get("module_files", {})
        }
        report["module_outputs"] = module_outputs
        report["rag_references"] = rag_refs
        return report

    def generate_sample_reports_for_one_patient(
        self,
        patient_id: str,
        scene: str = "doctor",
        daily_date: str = "2016-04-15",
        weekly_start: str = "",
        month: str = "2016-04",
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        agent_id = PatientIdMappingService.to_agent_id(patient_id)

        if overwrite:
            out_dir = Path(self.result_saver.save_dir) / agent_id
            if out_dir.exists():
                import shutil
                shutil.rmtree(out_dir, ignore_errors=True)

        day = datetime.strptime(daily_date, "%Y-%m-%d").date()
        if weekly_start:
            ws = datetime.strptime(weekly_start, "%Y-%m-%d").date()
        else:
            ws = day - timedelta(days=day.weekday())
        we = ws + timedelta(days=6)
        weekly_label = self._weekly_label(ws, we)

        month_start = datetime.strptime(month + "-01", "%Y-%m-%d").date()
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        monthly_label = self._monthly_label(month_start, month_end)

        daily_report = self.get_report(
            patient_id=patient_id,
            report_type="daily",
            scene=scene,
            period_value=daily_date,
            period_label=daily_date,
        )
        weekly_report = self.get_report(
            patient_id=patient_id,
            report_type="weekly",
            scene=scene,
            period_value=ws.strftime("%Y-%m-%d"),
            period_label=weekly_label,
        )
        monthly_report = self.get_report(
            patient_id=patient_id,
            report_type="monthly",
            scene=scene,
            period_value=month,
            period_label=monthly_label,
        )

        return {
            "patient_id": patient_id,
            "agent_patient": agent_id,
            "scene": scene,
            "generated": {
                "daily": daily_report.get("artifacts", {}),
                "weekly": weekly_report.get("artifacts", {}),
                "monthly": monthly_report.get("artifacts", {}),
            },
        }

    def generate_reports_for_date_range(
        self,
        start_date: str,
        end_date: str,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start > end:
            raise ValueError("start_date must be <= end_date")

        patients = ["10", "11", "12"]
        scenes = ["patient", "family", "doctor"]

        if overwrite:
            for pid in patients:
                agent_id = PatientIdMappingService.to_agent_id(pid)
                out_dir = Path(self.result_saver.save_dir) / agent_id
                if out_dir.exists():
                    for item in out_dir.iterdir():
                        if item.is_dir():
                            import shutil
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)

        bundles = []

        # Daily: one report per day in range.
        current = start
        while current <= end:
            date_value = current.strftime("%Y-%m-%d")
            for pid in patients:
                for scene in scenes:
                    bundles.append(
                        self.get_report(
                            patient_id=pid,
                            report_type="daily",
                            scene=scene,
                            period_value=date_value,
                            period_label=date_value,
                        )
                    )
            current += timedelta(days=1)

        # Weekly: align with Last style, full Monday-Sunday weeks only.
        first_monday = start + timedelta(days=(7 - start.weekday()) % 7)
        ws = first_monday
        while ws + timedelta(days=6) <= end:
            we = ws + timedelta(days=6)
            ws_value = ws.strftime("%Y-%m-%d")
            label = self._weekly_label(ws, we)
            for pid in patients:
                for scene in scenes:
                    bundles.append(
                        self.get_report(
                            patient_id=pid,
                            report_type="weekly",
                            scene=scene,
                            period_value=ws_value,
                            period_label=label,
                        )
                    )
            ws += timedelta(days=7)

        # Monthly: one report per month intersecting the range.
        cursor = start.replace(day=1)
        while cursor <= end:
            next_month = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            seg_start = max(cursor, start)
            seg_end = min(month_end, end)
            month_value = cursor.strftime("%Y-%m")
            month_label = self._monthly_label(seg_start, seg_end)
            for pid in patients:
                for scene in scenes:
                    bundles.append(
                        self.get_report(
                            patient_id=pid,
                            report_type="monthly",
                            scene=scene,
                            period_value=month_value,
                            period_label=month_label,
                        )
                    )
            cursor = next_month

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_reports": len(bundles),
            "patients": patients,
            "scenes": scenes,
        }


class RehabPlanVersionService:
    def __init__(self, storage_path: Path | None = None):
        base = Path(__file__).parent.parent.parent / "data" / "output" / "process"
        base.mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path or (base / "rehab_plan_versions.json")

    def _load(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {}
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_plan(self, patient_id: str) -> Dict[str, Any]:
        biz_id = PatientIdMappingService.to_biz_id(PatientIdMappingService.to_agent_id(patient_id))
        now = datetime.now().isoformat()
        plan_id = f"RP_{biz_id}_{datetime.now().strftime('%Y%m%d')}"

        ai_plan = {
            "exercise": {
                "target_hr_low": 55,
                "target_hr_high": 95,
                "max_steps": 4500,
                "recommended_activities": ["慢走", "太极"],
            },
            "diet": {"recommendations": ["低盐低脂", "控制热量"], "restrictions": []},
            "medication": {"reminders": ["按时服药", "监测心率"], "schedule": []},
            "risk_alerts": [],
        }

        plan = {
            "planId": plan_id,
            "patientId": biz_id,
            "aiPlan": ai_plan,
            "doctorRevisedPlan": None,
            "version": 1,
            "status": "ai_generated",
            "createdAt": now,
            "updatedAt": now,
        }

        all_data = self._load()
        all_data[plan_id] = plan
        self._save(all_data)
        return plan

    def revise_plan(self, patient_id: str, plan_id: str, revised_content: Dict[str, Any], revised_by: str) -> Dict[str, Any]:
        biz_id = PatientIdMappingService.to_biz_id(PatientIdMappingService.to_agent_id(patient_id))
        all_data = self._load()
        plan = all_data.get(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        if plan.get("patientId") != biz_id:
            raise ValueError("Plan does not belong to patient")

        plan["doctorRevisedPlan"] = {
            "content": revised_content,
            "revisedBy": revised_by,
            "revisedAt": datetime.now().isoformat(),
        }
        plan["version"] = int(plan.get("version", 1)) + 1
        plan["status"] = "doctor_revised"
        plan["updatedAt"] = datetime.now().isoformat()

        all_data[plan_id] = plan
        self._save(all_data)
        return plan

    def view_plan(self, patient_id: str, plan_id: str = "") -> Dict[str, Any]:
        biz_id = PatientIdMappingService.to_biz_id(PatientIdMappingService.to_agent_id(patient_id))
        all_data = self._load()

        if plan_id:
            plan = all_data.get(plan_id)
            if not plan:
                raise ValueError("Plan not found")
            if plan.get("patientId") != biz_id:
                raise ValueError("Plan does not belong to patient")
            return plan

        candidates = [p for p in all_data.values() if p.get("patientId") == biz_id]
        if not candidates:
            # Auto-generate a plan for first-time query to keep integration simple.
            return self.generate_plan(biz_id)

        candidates.sort(key=lambda x: str(x.get("updatedAt", "")), reverse=True)
        return candidates[0]

    def dispatch_plan(self, patient_id: str, plan_id: str, dispatcher: str = "doctor") -> Dict[str, Any]:
        biz_id = PatientIdMappingService.to_biz_id(PatientIdMappingService.to_agent_id(patient_id))
        all_data = self._load()
        plan = all_data.get(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        if plan.get("patientId") != biz_id:
            raise ValueError("Plan does not belong to patient")

        plan["dispatchInfo"] = {
            "dispatched": True,
            "dispatchedAt": datetime.now().isoformat(),
            "dispatchedBy": dispatcher,
            "targets": ["patient", "family"],
            "sourcePlanId": plan.get("planId"),
            "sourceVersion": plan.get("version", 1),
            "sourceStatus": "doctor_revised" if plan.get("doctorRevisedPlan") else "ai_generated",
        }
        plan["status"] = "dispatched"
        plan["updatedAt"] = datetime.now().isoformat()

        all_data[plan_id] = plan
        self._save(all_data)
        return plan
