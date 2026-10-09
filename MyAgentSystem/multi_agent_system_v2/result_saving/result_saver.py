from pathlib import Path
import sys
import json
import importlib
from datetime import datetime
from typing import Dict, Any, List

try:
    A4 = importlib.import_module("reportlab.lib.pagesizes").A4
    colors = importlib.import_module("reportlab.lib.colors")
    cm = importlib.import_module("reportlab.lib.units").cm
    styles_mod = importlib.import_module("reportlab.lib.styles")
    getSampleStyleSheet = styles_mod.getSampleStyleSheet
    ParagraphStyle = styles_mod.ParagraphStyle
    platypus = importlib.import_module("reportlab.platypus")
    SimpleDocTemplate = platypus.SimpleDocTemplate
    Paragraph = platypus.Paragraph
    Spacer = platypus.Spacer
    Table = platypus.Table
    TableStyle = platypus.TableStyle
    ReportLabImage = platypus.Image
    PageBreak = platypus.PageBreak
    pdfmetrics = importlib.import_module("reportlab.pdfbase.pdfmetrics")
    UnicodeCIDFont = importlib.import_module("reportlab.pdfbase.cidfonts").UnicodeCIDFont
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

try:
    plt = importlib.import_module("matplotlib.pyplot")
    font_manager = importlib.import_module("matplotlib.font_manager")
    MATPLOTLIB_AVAILABLE = True
except Exception:
    plt = None
    font_manager = None
    MATPLOTLIB_AVAILABLE = False

# 添加当前目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

class ResultSaver:
    """结果保存模块"""
    
    def __init__(self, save_dir: str = None):
        self.save_dir = save_dir or str(Path(__file__).parent.parent / "results")
        self.report_font_name = "Helvetica"
        self._init_reportlab_cjk_font()
        self._configure_matplotlib_fonts()
        self._ensure_save_dir_exists()

    def _init_reportlab_cjk_font(self):
        """初始化 ReportLab 中文字体。"""
        if not REPORTLAB_AVAILABLE:
            return
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
            self.report_font_name = "STSong-Light"
        except Exception:
            self.report_font_name = "Helvetica"

    def _configure_matplotlib_fonts(self):
        """配置 matplotlib 中文字体，避免图表中文缺字。"""
        if not MATPLOTLIB_AVAILABLE or font_manager is None:
            return

        preferred_fonts = [
            "Microsoft YaHei",
            "SimHei",
            "Noto Sans CJK SC",
            "WenQuanYi Micro Hei",
            "Arial Unicode MS",
        ]

        selected = None
        for name in preferred_fonts:
            try:
                font_manager.findfont(name, fallback_to_default=False)
                selected = name
                break
            except Exception:
                continue

        if selected:
            plt.rcParams["font.sans-serif"] = [selected, "DejaVu Sans"]
        else:
            plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
    
    def _ensure_save_dir_exists(self):
        """确保保存目录存在"""
        save_path = Path(self.save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

    def _safe_get(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return default

    def _extract_indicator_values(self, report: Dict[str, Any], module_outputs: Dict[str, Any] = None) -> Dict[str, float]:
        """兼容不同报告结构提取核心指标。"""
        heart_rate = 0.0
        steps = 0.0
        sleep_hours = 0.0

        if isinstance(report.get("heart_rate"), dict):
            heart_rate = self._safe_get(report["heart_rate"].get("mean"), 0.0)
        if isinstance(report.get("activity"), dict):
            steps = self._safe_get(report["activity"].get("mean_steps"), 0.0)
        if isinstance(report.get("sleep"), dict):
            sleep_hours = self._safe_get(report["sleep"].get("mean_sleep_duration"), 0.0)

        data_analysis = report.get("data_analysis", {})
        if isinstance(data_analysis, dict):
            hr_analysis = data_analysis.get("heart_rate", {})
            activity_analysis = data_analysis.get("activity", {})
            sleep_analysis = data_analysis.get("sleep", {})
            if isinstance(hr_analysis, dict) and heart_rate == 0.0:
                heart_rate = self._safe_get(hr_analysis.get("mean"), 0.0)
            if isinstance(activity_analysis, dict) and steps == 0.0:
                steps = self._safe_get(activity_analysis.get("mean_steps"), 0.0)
            if isinstance(sleep_analysis, dict) and sleep_hours == 0.0:
                sleep_hours = self._safe_get(sleep_analysis.get("mean_sleep_duration"), 0.0)

        # 优先从模块可视化载荷回填，避免 patient/family 场景出现 0 值。
        rv = (module_outputs or {}).get("report_visualization", {}) if isinstance(module_outputs, dict) else {}
        bar = rv.get("barChart", {}) if isinstance(rv, dict) else {}
        labels = bar.get("labels", []) if isinstance(bar, dict) else []
        values = bar.get("values", []) if isinstance(bar, dict) else []
        if labels and values and len(labels) == len(values):
            label_map = {str(k): self._safe_get(v, 0.0) for k, v in zip(labels, values)}
            if heart_rate == 0.0 and label_map.get("heart_rate", 0.0) > 0:
                heart_rate = label_map.get("heart_rate", 0.0)
            if steps == 0.0 and label_map.get("steps", 0.0) > 0:
                steps = label_map.get("steps", 0.0)
            if sleep_hours == 0.0 and label_map.get("sleep_hours", 0.0) > 0:
                sleep_hours = label_map.get("sleep_hours", 0.0)

        return {
            "heart_rate": round(heart_rate, 2),
            "steps": round(steps, 2),
            "sleep_hours": round(sleep_hours, 2)
        }

    def _metric_status(self, metric: str, value: float, module_outputs: Dict[str, Any] = None) -> str:
        rv = (module_outputs or {}).get("report_visualization", {}) if isinstance(module_outputs, dict) else {}
        thresholds = rv.get("thresholds", {}) if isinstance(rv, dict) else {}

        if metric == "heart_rate":
            t = thresholds.get("heart_rate", {}) if isinstance(thresholds, dict) else {}
            low = self._safe_get(t.get("min"), 55.0)
            high = self._safe_get(t.get("max"), 95.0)
            if value <= 0:
                return "数据不足"
            return "正常" if low <= value <= high else "需关注"
        if metric == "steps":
            t = thresholds.get("steps", {}) if isinstance(thresholds, dict) else {}
            min_steps = self._safe_get(t.get("min"), 3000.0)
            if value <= 0:
                return "数据不足"
            return "达标" if value >= min_steps else "未达标"
        if metric == "sleep_hours":
            t = thresholds.get("sleep_hours", {}) if isinstance(thresholds, dict) else {}
            min_sleep = self._safe_get(t.get("min"), 6.0)
            if value <= 0:
                return "数据不足"
            return "正常" if value >= min_sleep else "偏低"
        return "-"

    def _build_report_figure(self, report: Dict[str, Any]):
        if not MATPLOTLIB_AVAILABLE:
            return None

        metrics = self._extract_indicator_values(report)
        report_type = str(report.get("report_type", "unknown")).lower()
        patient_id = report.get("patient_id") or report.get("patientId", "unknown")

        fig, axes = plt.subplots(2, 1, figsize=(8.27, 11.69))

        labels = ["Heart Rate", "Steps", "Sleep Hours"]
        values = [metrics["heart_rate"], metrics["steps"], metrics["sleep_hours"]]
        colors = ["#1f77b4", "#2ca02c", "#ff7f0e"]

        axes[0].bar(labels, values, color=colors)
        axes[0].set_title(f"{report_type.title()} Report Summary Metrics")
        axes[0].set_ylabel("Value")
        axes[0].grid(axis="y", alpha=0.3)

        summary_lines = [
            f"Patient: {patient_id}",
            f"Report Type: {report_type}",
            f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Heart Rate: {metrics['heart_rate']} bpm",
            f"Steps: {metrics['steps']}",
            f"Sleep: {metrics['sleep_hours']} hours"
        ]
        axes[1].axis("off")
        axes[1].text(0.02, 0.98, "\n".join(summary_lines), va="top", fontsize=11)

        fig.tight_layout()
        return fig

    def _save_scene_visualization_assets(
        self,
        report: Dict[str, Any],
        module_outputs: Dict[str, Any],
        output_dir: Path,
        period_label: str,
    ) -> List[str]:
        if not MATPLOTLIB_AVAILABLE:
            return []

        payload = (module_outputs or {}).get("report_visualization", {})
        if not isinstance(payload, dict):
            return []
        report_type = str(payload.get("reportType", "")).lower()

        saved_paths: List[str] = []

        heart = payload.get("heart_rate_trend", {})
        heart_times = heart.get("times", [])
        heart_values = [self._safe_get(v, 0.0) for v in heart.get("values", [])]
        if heart_times and heart_values and len(heart_times) == len(heart_values):
            try:
                fig, ax = plt.subplots(figsize=(11.0, 6.2))
                x = list(range(len(heart_values)))
                ax.plot(x, heart_values, color="#2d3436", linewidth=1.1, marker="o", markersize=2.5, label="心率")
                baseline = self._safe_get(heart.get("baseline", 78.0), 78.0)
                ax.axhline(baseline, color="#27ae60", linestyle="--", linewidth=1.4, label="基线")

                # 按示例图风格：蓝区(66-91)、黄区(53-66/91-104)、红区(<53/>104)
                blue_low, blue_high = 66.0, 91.0
                yellow_low, yellow_high = 53.0, 104.0
                red_low, red_high = 40.0, 117.0

                ax.axhspan(blue_low, blue_high, color="#5b8db8", alpha=0.42, label="蓝区")
                ax.axhspan(yellow_low, blue_low, color="#f2d694", alpha=0.55, label="黄区")
                ax.axhspan(blue_high, yellow_high, color="#f2d694", alpha=0.55)
                ax.axhspan(red_low, yellow_low, color="#e8a1a1", alpha=0.45, label="红区")
                ax.axhspan(yellow_high, red_high, color="#e8a1a1", alpha=0.45)

                red_idx = [i for i, v in enumerate(heart_values) if v < yellow_low or v > yellow_high]
                yellow_idx = [i for i, v in enumerate(heart_values) if (yellow_low <= v < blue_low) or (blue_high < v <= yellow_high)]
                if red_idx:
                    red_values = [heart_values[i] for i in red_idx]
                    ax.scatter(red_idx, red_values, color="#e53935", s=20, zorder=3, label="红色预警")
                if yellow_idx:
                    yellow_values = [heart_values[i] for i in yellow_idx]
                    ax.scatter(yellow_idx, yellow_values, color="#f2a900", s=18, zorder=3, label="黄色关注")

                tick_count = min(8, len(x))
                if tick_count > 1:
                    tick_positions = [int(i * (len(x) - 1) / (tick_count - 1)) for i in range(tick_count)]
                    tick_labels = [heart_times[i] for i in tick_positions]
                    ax.set_xticks(tick_positions)
                    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
                elif len(heart_values) == 1:
                    ax.set_xticks([0])
                    ax.set_xticklabels([heart_times[0]], rotation=35, ha="right", fontsize=8)

                if len(heart_values) == 1:
                    v = heart_values[0]
                    delta = max(3.0, abs(v) * 0.08)
                    ax.set_ylim(v - delta, v + delta)

                ax.set_title(f"{period_label} 24小时心率趋势图")
                ax.set_xlabel("时间")
                ax.set_ylabel("心率（次/分钟）")
                ax.grid(alpha=0.25)
                ax.legend(loc="best", fontsize=8)
                fig.tight_layout()

                out = output_dir / "chart_heart_rate_trend.png"
                fig.savefig(out, dpi=160, bbox_inches="tight")
                plt.close(fig)
                saved_paths.append(str(out))
            except Exception:
                pass

        activity = payload.get("activity_distribution", {})
        activity_labels = activity.get("labels", [])
        activity_values = [self._safe_get(v, 0.0) for v in activity.get("values", [])]
        if activity_labels and activity_values and len(activity_labels) == len(activity_values):
            try:
                fig, ax = plt.subplots(figsize=(8.8, 6.0))
                total = sum(activity_values)
                if total > 0:
                    ax.pie(
                        activity_values,
                        labels=activity_labels,
                        autopct="%1.1f%%",
                        startangle=90,
                        colors=["#f4d03f", "#f39c12", "#e74c3c", "#27ae60"][: len(activity_values)],
                    )
                else:
                    ax.text(0.5, 0.5, "无有效活动强度数据", ha="center", va="center")
                ax.set_title(f"{period_label} 活动强度分布")
                fig.tight_layout()

                out = output_dir / "chart_activity_intensity_distribution.png"
                fig.savefig(out, dpi=160, bbox_inches="tight")
                plt.close(fig)
                saved_paths.append(str(out))
            except Exception:
                pass

        risk = payload.get("risk_warning_distribution", {})
        risk_labels = risk.get("labels", [])
        risk_values = [self._safe_get(v, 0.0) for v in risk.get("values", [])]
        if risk_labels and risk_values and len(risk_labels) == len(risk_values):
            try:
                fig, ax = plt.subplots(figsize=(8.8, 6.0))
                total = sum(risk_values)
                if total > 0:
                    ax.pie(
                        risk_values,
                        labels=risk_labels,
                        autopct="%1.1f%%",
                        startangle=90,
                        colors=["#2e86de", "#f39c12", "#e74c3c"][: len(risk_values)],
                    )
                else:
                    ax.text(0.5, 0.5, "无有效预警分布数据", ha="center", va="center")
                ax.set_title(f"{period_label} 心率预警分类占比")
                fig.tight_layout()

                out = output_dir / "chart_risk_warning_distribution.png"
                fig.savefig(out, dpi=160, bbox_inches="tight")
                plt.close(fig)
                saved_paths.append(str(out))
            except Exception:
                pass

        multi = payload.get("multi_metric_trend", {})
        multi_times = multi.get("times", [])
        if multi_times:
            try:
                fig, axs = plt.subplots(2, 2, figsize=(11.0, 8.0))
                x = list(range(len(multi_times)))
                tick_count = min(6, len(x))
                tick_positions = [int(i * (len(x) - 1) / (tick_count - 1)) for i in range(tick_count)] if tick_count > 1 else [0]
                tick_labels = [multi_times[i] for i in tick_positions] if tick_positions and multi_times else []

                chart_defs = [
                    ("heart_rate", "心率（次/分）", "#2d3436"),
                    ("steps", "步数", "#1f77b4"),
                    ("mets", "METs", "#d35400"),
                    ("sleep_hours", "睡眠总时长（小时）" if report_type == "daily" else "睡眠时长（小时）", "#8e44ad"),
                ]

                for ax, (key, title, color) in zip(axs.flatten(), chart_defs):
                    if key == "mets":
                        raw_vals = multi.get("mets", [])
                        if not raw_vals:
                            raw_vals = [round(self._safe_get(v, 0.0) / 180.0, 2) for v in multi.get("active_minutes", [])]
                    else:
                        raw_vals = multi.get(key, [])
                    vals = [self._safe_get(v, 0.0) for v in raw_vals]
                    if vals and len(vals) == len(x):
                        if len(vals) == 1:
                            ax.plot(x, vals, color=color, linewidth=1.3, marker="o", markersize=4)
                            v = vals[0]
                            delta = max(1.0, abs(v) * 0.08)
                            ax.set_ylim(v - delta, v + delta)
                        else:
                            ax.plot(x, vals, color=color, linewidth=1.3, marker="o", markersize=2.5)
                    ax.set_title(title, fontsize=10)
                    ax.grid(alpha=0.25)
                    if tick_labels:
                        ax.set_xticks(tick_positions)
                        ax.set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=8)

                fig.suptitle(f"{period_label} 多指标联合趋势", fontsize=12)
                fig.tight_layout(rect=[0, 0, 1, 0.96])

                out = output_dir / "chart_multi_metric_trend.png"
                fig.savefig(out, dpi=160, bbox_inches="tight")
                plt.close(fig)
                saved_paths.append(str(out))
            except Exception:
                pass

        # 周报/月报补充更完整的趋势版式，尽量贴近“核心总结 + 趋势图 + 更多指标分析”的展示。
        if report_type in ("weekly", "monthly"):
            times = multi.get("times", []) if isinstance(multi, dict) else []
            hr_vals = [self._safe_get(v, 0.0) for v in multi.get("heart_rate", [])] if isinstance(multi, dict) else []
            steps_vals = [self._safe_get(v, 0.0) for v in multi.get("steps", [])] if isinstance(multi, dict) else []
            mets_source = multi.get("mets", []) if isinstance(multi, dict) else []
            if mets_source:
                mets_vals = [self._safe_get(v, 0.0) for v in mets_source]
            else:
                mets_vals = [round(self._safe_get(v, 0.0) / 180.0, 2) for v in (multi.get("active_minutes", []) if isinstance(multi, dict) else [])]
            sleep_vals = [self._safe_get(v, 0.0) for v in multi.get("sleep_hours", [])] if isinstance(multi, dict) else []

            if times and hr_vals and len(times) == len(hr_vals):
                try:
                    x = list(range(len(times)))
                    tick_count = min(7, len(x))
                    tick_positions = [int(i * (len(x) - 1) / (tick_count - 1)) for i in range(tick_count)] if tick_count > 1 else [0]
                    tick_labels = [times[i] for i in tick_positions]

                    fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.6))
                    axs[0].plot(x, hr_vals, color="#2d3436", linewidth=1.5, marker="o", markersize=3)
                    axs[0].set_title("周度平均心率趋势" if report_type == "weekly" else "月度平均心率趋势", fontsize=11)
                    axs[0].set_ylabel("心率(次/分)")
                    axs[0].grid(alpha=0.25)
                    axs[0].set_xticks(tick_positions)
                    axs[0].set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=8)

                    if steps_vals and len(steps_vals) == len(x):
                        axs[1].bar(x, steps_vals, color="#5b9bd5", alpha=0.95)
                    axs[1].set_title("周度每日步数" if report_type == "weekly" else "月度每日步数", fontsize=11)
                    axs[1].set_ylabel("步数")
                    axs[1].grid(alpha=0.25)
                    axs[1].set_xticks(tick_positions)
                    axs[1].set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=8)

                    fig.suptitle(f"{period_label} {'周度健康趋势总结' if report_type == 'weekly' else '月度健康趋势总结'}", fontsize=12)
                    fig.tight_layout(rect=[0, 0, 1, 0.95])

                    out = output_dir / "chart_period_overview.png"
                    fig.savefig(out, dpi=160, bbox_inches="tight")
                    plt.close(fig)
                    saved_paths.append(str(out))
                except Exception:
                    pass

            baseline_trace = payload.get("baseline_trace", {}) if isinstance(payload, dict) else {}
            bt_times = baseline_trace.get("times", []) if isinstance(baseline_trace, dict) else []
            bt_hr = [self._safe_get(v, 0.0) for v in baseline_trace.get("resting_heart_rate", [])] if isinstance(baseline_trace, dict) else []
            bt_sdnn = [self._safe_get(v, 0.0) for v in baseline_trace.get("sdnn", [])] if isinstance(baseline_trace, dict) else []
            bt_sleep_change = [self._safe_get(v, 0.0) for v in baseline_trace.get("deep_sleep_change_pct", [])] if isinstance(baseline_trace, dict) else []
            bt_steps = [self._safe_get(v, 0.0) for v in baseline_trace.get("daily_steps", [])] if isinstance(baseline_trace, dict) else []

            use_real_trace = (
                bt_times and bt_hr and bt_sdnn and bt_sleep_change and bt_steps and
                len(bt_times) == len(bt_hr) == len(bt_sdnn) == len(bt_sleep_change) == len(bt_steps)
            )

            if use_real_trace or (times and len(times) >= 2 and hr_vals and sleep_vals and steps_vals):
                try:
                    if use_real_trace:
                        trace_times = bt_times
                        trace_hr = bt_hr
                        trace_sdnn_vals = bt_sdnn
                        trace_sleep_vals = bt_sleep_change
                        trace_step_vals = bt_steps
                    else:
                        trace_times = times
                        trace_hr = hr_vals
                        trace_sdnn_vals = [max(1.0, abs((hr_vals[i] - hr_vals[i - 1]) if i > 0 else 8.0) * 3.2) for i in range(len(hr_vals))]
                        trace_sleep_vals = [max(0.0, min(100.0, (sleep_vals[i] / 8.0) * 100.0)) for i in range(len(sleep_vals))]
                        trace_step_vals = steps_vals

                    x = list(range(len(trace_times)))
                    tick_count = min(8, len(x))
                    tick_positions = [int(i * (len(x) - 1) / (tick_count - 1)) for i in range(tick_count)] if tick_count > 1 else [0]
                    tick_labels = [trace_times[i] for i in tick_positions]

                    # 用简化的滑动均值 + 方差带，表达“个性化基线在线更新轨迹”。
                    def _rolling_center(vals):
                        out = []
                        for i in range(len(vals)):
                            left = max(0, i - 2)
                            right = min(len(vals), i + 3)
                            seg = vals[left:right]
                            out.append(sum(seg) / max(1, len(seg)))
                        return out

                    def _band(vals, rate=0.15):
                        center = _rolling_center(vals)
                        low = [c - max(0.8, abs(c) * rate) for c in center]
                        high = [c + max(0.8, abs(c) * rate) for c in center]
                        return center, low, high

                    fig, axs = plt.subplots(2, 2, figsize=(11.2, 8.0))
                    chart_defs = [
                        (trace_hr, "静息心率", "静息心率"),
                        (trace_sdnn_vals, "心率变异性SDNN", "心率变异性SDNN"),
                        (trace_sleep_vals, "深睡占比", "深睡占比变化(%)"),
                        (trace_step_vals, "日均步数", "日均步数"),
                    ]

                    # 指标方向定义：True=越大越好，False=越小越好。
                    better_when_higher = {
                        "静息心率": False,
                        "心率变异性SDNN": True,
                        "深睡占比": True,
                        "日均步数": True,
                    }

                    def _smooth_series(vals, window=15):
                        src = [self._safe_get(v, 0.0) for v in vals]
                        n = len(src)
                        if n <= 2:
                            return src
                        w = max(3, min(window, n if n % 2 == 1 else n - 1))
                        half = w // 2
                        out = []
                        for i in range(n):
                            left = max(0, i - half)
                            right = min(n, i + half + 1)
                            seg = src[left:right]
                            out.append(sum(seg) / max(1, len(seg)))
                        return out

                    def _calc_trend_change(vals):
                        series = _smooth_series(vals, window=15)
                        n = len(series)
                        if n < 2:
                            return 0.0
                        k = max(2, min(12, n // 6))
                        start = sum(series[:k]) / k
                        end = sum(series[-k:]) / k
                        if abs(start) < 1e-9:
                            return 0.0
                        return ((end - start) / abs(start)) * 100.0

                    for ax, (vals, title, ylabel) in zip(axs.flatten(), chart_defs):
                        smoothed_vals = _smooth_series(vals, window=15)
                        center, low, high = _band(smoothed_vals, rate=0.14)
                        ax.fill_between(x, low, high, color="#5dade2", alpha=0.25, label="基线正常区间")
                        ax.plot(x, center, color="#1f77b4", linewidth=2.0, label="个性化基线")
                        ax.set_title(f"{title} 基线更新轨迹", fontsize=10)
                        ax.set_ylabel(ylabel)
                        ax.grid(alpha=0.25)
                        ax.set_xticks(tick_positions)
                        ax.set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=7)
                        ax.legend(loc="upper right", fontsize=7)

                        change_pct = _calc_trend_change(vals)
                        abs_change = abs(change_pct)
                        direction_higher = better_when_higher.get(title, True)

                        change_text = f"{abs_change:.1f}%"
                        if abs_change < 0.6:
                            tag_text = f"本周持平{change_text}"
                            tag_fc = "#f4f6f7"
                            tag_ec = "#95a5a6"
                            tag_color = "#7f8c8d"
                        else:
                            improved = (change_pct > 0 and direction_higher) or (change_pct < 0 and not direction_higher)
                            if improved:
                                tag_text = f"本周改善{change_text}"
                                tag_fc = "#e8f8f0"
                                tag_ec = "#27ae60"
                                tag_color = "#1e8449"
                            else:
                                tag_text = f"本周变差{change_text}"
                                tag_fc = "#fdecea"
                                tag_ec = "#e74c3c"
                                tag_color = "#c0392b"

                        ax.text(
                            0.5,
                            0.98,
                            tag_text,
                            transform=ax.transAxes,
                            ha="center",
                            va="top",
                            fontsize=10,
                            color=tag_color,
                            bbox={"boxstyle": "round,pad=0.2", "facecolor": tag_fc, "edgecolor": tag_ec, "linewidth": 0.9},
                        )

                    fig.suptitle(f"{period_label} 个性化基线在线更新轨迹", fontsize=12)
                    fig.tight_layout(rect=[0, 0, 1, 0.95])

                    out = output_dir / "chart_baseline_update_trace.png"
                    fig.savefig(out, dpi=160, bbox_inches="tight")
                    plt.close(fig)
                    saved_paths.append(str(out))
                except Exception:
                    pass

            if times and mets_vals and len(times) == len(mets_vals):
                try:
                    x = list(range(len(times)))
                    tick_count = min(7, len(x))
                    tick_positions = [int(i * (len(x) - 1) / (tick_count - 1)) for i in range(tick_count)] if tick_count > 1 else [0]
                    tick_labels = [times[i] for i in tick_positions]

                    fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.5))
                    axs[0].plot(x, mets_vals, color="#3fa34d", linewidth=1.8, marker="s", markersize=4)
                    axs[0].set_title("周度平均METs趋势" if report_type == "weekly" else "月度平均METs趋势", fontsize=11)
                    axs[0].set_ylabel("METs")
                    axs[0].grid(alpha=0.25)
                    axs[0].set_xticks(tick_positions)
                    axs[0].set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=8)

                    axs[1].axis("off")
                    axs[1].text(0.5, 0.5, "更多指标分析", ha="center", va="center", fontsize=13)

                    fig.tight_layout()
                    out = output_dir / "chart_mets_and_more.png"
                    fig.savefig(out, dpi=160, bbox_inches="tight")
                    plt.close(fig)
                    saved_paths.append(str(out))
                except Exception:
                    pass

        return saved_paths

    def _save_visual_assets(self, report: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        assets: Dict[str, str] = {}
        fig = self._build_report_figure(report)
        if fig is None:
            return assets

        png_path = output_dir / "report_summary.png"
        pdf_path = output_dir / "report_summary.pdf"

        fig.savefig(png_path, dpi=150, bbox_inches="tight")
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
        plt.close(fig)

        assets["image"] = str(png_path)
        assets["pdf"] = str(pdf_path)
        return assets

    def _json_default(self, obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    def _end_dir_name(self, end_type: str) -> str:
        mapping = {
            "patient": "patient_end",
            "family": "family_end",
            "doctor": "doctor_end"
        }
        return mapping.get(end_type, f"{end_type}_end")

    def _legacy_paths(self, patient_id: str, report_type: str, end_type: str, period_label: str) -> Dict[str, Path]:
        end_dir = self._end_dir_name(end_type)
        folder = Path(self.save_dir) / patient_id / end_dir / report_type / period_label
        folder.mkdir(parents=True, exist_ok=True)

        if report_type == "daily":
            json_name = f"{period_label}_{end_dir}.json"
            pdf_name = f"{period_label}_{end_type}.pdf"
            png_name = f"{period_label}_{end_type}.png"
        elif report_type == "weekly":
            json_name = f"{period_label}_{end_dir}.json"
            pdf_name = f"{period_label}_{end_type}.pdf"
            png_name = f"{period_label}_{end_type}.png"
        else:
            json_name = f"{period_label}_{end_dir}.json"
            pdf_name = f"{period_label}_{end_type}.pdf"
            png_name = f"{period_label}_{end_type}.png"

        return {
            "dir": folder,
            "json": folder / json_name,
            "pdf": folder / pdf_name,
            "image": folder / png_name,
            "modules": folder / "module_outputs"
        }

    def _save_pdf_with_reportlab(
        self,
        report: Dict[str, Any],
        pdf_path: Path,
        report_type: str,
        end_type: str,
        period_label: str,
        chart_image_path: Path = None,
        extra_chart_paths: List[str] = None,
        module_outputs: Dict[str, Any] = None,
    ):
        if not REPORTLAB_AVAILABLE:
            return False

        title_map = {
            "daily": "每日健康监测报告",
            "weekly": "每周健康评估报告",
            "monthly": "每月健康管理报告"
        }
        end_title_map = {
            "patient": "患者版",
            "family": "家属版",
            "doctor": "医生专业版"
        }

        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "title",
            parent=styles["Heading1"],
            fontName=self.report_font_name,
            fontSize=16,
            textColor=colors.HexColor("#2c3e50"),
            alignment=1,
            spaceAfter=0.5 * cm,
        )
        subtitle_style = ParagraphStyle(
            "subtitle",
            parent=styles["Heading2"],
            fontName=self.report_font_name,
            fontSize=12,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=0.25 * cm,
        )
        normal_style = ParagraphStyle(
            "normal",
            parent=styles["Normal"],
            fontName=self.report_font_name,
            fontSize=10,
            leading=15,
            spaceAfter=0.2 * cm,
        )

        patient_id = report.get("patient_id") or report.get("patientId") or "unknown"
        title = f"患者{patient_id} {period_label} {title_map.get(report_type, '健康报告')} ({end_title_map.get(end_type, end_type)})"

        story = [Paragraph(title, title_style), Spacer(1, 0.2 * cm)]
        story.append(Paragraph("一、核心健康总结", subtitle_style))
        story.append(Paragraph(report.get("content", "暂无内容"), normal_style))

        metrics = self._extract_indicator_values(report, module_outputs)
        table_data = [
            ["指标名称", "当前数值", "状态"],
            ["静息心率", f"{metrics['heart_rate']:.2f}", self._metric_status("heart_rate", metrics["heart_rate"], module_outputs)],
            ["日均步数", f"{metrics['steps']:.2f}", self._metric_status("steps", metrics["steps"], module_outputs)],
            ["睡眠时长(小时)", f"{metrics['sleep_hours']:.2f}", self._metric_status("sleep_hours", metrics["sleep_hours"], module_outputs)],
        ]
        story.append(Paragraph("二、核心健康指标", subtitle_style))
        table = Table(table_data, colWidths=[5.2 * cm, 4.2 * cm, 3.6 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#dcdcdc")),
                    ("FONTNAME", (0, 0), (-1, -1), self.report_font_name),
                ]
            )
        )
        story.append(table)

        story.append(Spacer(1, 0.3 * cm))
        recommendations = report.get("recommendations", [])
        if recommendations:
            story.append(Paragraph("三、健康建议", subtitle_style))
            for idx, item in enumerate(recommendations, 1):
                story.append(Paragraph(f"{idx}. {item}", normal_style))

        story.append(Spacer(1, 0.3 * cm))
        visual_title = "四、健康趋势可视化" if report_type in ("weekly", "monthly") else "四、健康数据可视化图表"
        story.append(Paragraph(visual_title, subtitle_style))
        charts = []
        for p in extra_chart_paths or []:
            path_obj = Path(p)
            if path_obj.exists() and str(path_obj) not in charts:
                charts.append(str(path_obj))

        if charts:
            for idx, chart_file in enumerate(charts, 1):
                chart = ReportLabImage(chart_file)
                max_width = 16 * cm
                width = float(getattr(chart, "imageWidth", 0) or 0)
                height = float(getattr(chart, "imageHeight", 0) or 0)
                ratio = (height / width) if width > 0 else 0.62
                chart.drawWidth = max_width
                chart.drawHeight = max_width * ratio
                story.append(Paragraph(f"图{idx}: {Path(chart_file).stem}", normal_style))
                story.append(chart)
                if idx < len(charts):
                    story.append(PageBreak())
                    story.append(Paragraph(f"{visual_title}（续）", subtitle_style))
        else:
            story.append(Paragraph("暂未生成图表，建议检查可视化数据输出。", normal_style))

        doc.build(story)
        return True

    def save_report_bundle_legacy(
        self,
        patient_id: str,
        report: Dict[str, Any],
        report_type: str,
        end_type: str,
        period_label: str,
        module_outputs: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        paths = self._legacy_paths(patient_id, report_type, end_type, period_label)

        assets: Dict[str, str] = {}
        extra_charts: List[str] = []
        if MATPLOTLIB_AVAILABLE:
            try:
                fig = self._build_report_figure(report)
                if fig is not None:
                    fig.savefig(paths["image"], dpi=150, bbox_inches="tight")
                    plt.close(fig)
                    assets["image"] = str(paths["image"])
            except Exception as e:
                print(f"生成图片失败: {e}")

            try:
                extra_charts = self._save_scene_visualization_assets(
                    report,
                    module_outputs or {},
                    paths["dir"],
                    period_label,
                )
            except Exception as e:
                print(f"生成扩展图表失败: {e}")

        pdf_ok = False
        try:
            pdf_ok = self._save_pdf_with_reportlab(
                report,
                paths["pdf"],
                report_type,
                end_type,
                period_label,
                paths["image"] if paths["image"].exists() else None,
                extra_charts,
                module_outputs,
            )
        except Exception as e:
            print(f"ReportLab生成PDF失败: {e}")

        if not pdf_ok and MATPLOTLIB_AVAILABLE:
            try:
                fig = self._build_report_figure(report)
                if fig is not None:
                    fig.savefig(paths["pdf"], format="pdf", bbox_inches="tight")
                    plt.close(fig)
                    pdf_ok = True
            except Exception as e:
                print(f"回退PDF生成失败: {e}")

        if pdf_ok:
            assets["pdf"] = str(paths["pdf"])

        report_with_assets = dict(report)
        report_with_assets.setdefault("artifacts", {})
        report_with_assets["artifacts"].update({
            "json": str(paths["json"]),
            "image": assets.get("image"),
            "pdf": assets.get("pdf"),
            "charts": extra_charts,
        })

        if module_outputs:
            report_with_assets["module_outputs"] = module_outputs

        with open(paths["json"], "w", encoding="utf-8") as f:
            json.dump(report_with_assets, f, ensure_ascii=False, indent=2, default=self._json_default)

        module_files: Dict[str, str] = {}
        if module_outputs:
            paths["modules"].mkdir(parents=True, exist_ok=True)
            for name, payload in module_outputs.items():
                p = paths["modules"] / f"{name}.json"
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2, default=self._json_default)
                module_files[name] = str(p)

        bundle_meta = {
            "patient_id": patient_id,
            "end_type": end_type,
            "report_type": report_type,
            "period_label": period_label,
            "generated_at": datetime.now().isoformat(),
            "paths": {
                "json": str(paths["json"]),
                "image": assets.get("image"),
                "pdf": assets.get("pdf"),
                "charts": extra_charts,
                "module_files": module_files
            },
            "capabilities": {
                "matplotlib_available": MATPLOTLIB_AVAILABLE,
                "reportlab_available": REPORTLAB_AVAILABLE
            }
        }

        meta_path = paths["dir"] / "bundle_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(bundle_meta, f, ensure_ascii=False, indent=2)

        print(f"患者 {patient_id} 的 {report_type} 报告已生成(兼容目录): {paths['dir']}")
        return bundle_meta
    
    def save_patient_report(self, patient_id: str, report: Dict[str, Any], report_type: str, end_type: str):
        """保存患者报告"""
        # 创建患者目录
        patient_dir = Path(self.save_dir) / patient_id
        patient_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建报告文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{report_type}_{end_type}_{timestamp}.json"
        file_path = patient_dir / file_name
        
        # 保存报告
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"患者 {patient_id} 的 {report_type} 报告已保存到: {file_path}")
        return str(file_path)

    def save_report_bundle(
        self,
        patient_id: str,
        report: Dict[str, Any],
        report_type: str,
        end_type: str,
        module_outputs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """保存报告及其衍生产物（json/png/pdf + 模块接口输出）。"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_dir = Path(self.save_dir) / patient_id / end_type / report_type / timestamp
        bundle_dir.mkdir(parents=True, exist_ok=True)

        assets = {}
        if MATPLOTLIB_AVAILABLE:
            try:
                assets = self._save_visual_assets(report, bundle_dir)
            except Exception as e:
                print(f"生成图片/PDF产物失败: {e}")

        report_with_assets = dict(report)
        report_with_assets.setdefault("artifacts", {})
        report_with_assets["artifacts"].update({
            "json": str(bundle_dir / "report.json"),
            "image": assets.get("image"),
            "pdf": assets.get("pdf")
        })

        if module_outputs:
            report_with_assets["module_outputs"] = module_outputs

        report_json_path = bundle_dir / "report.json"
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report_with_assets, f, ensure_ascii=False, indent=2, default=self._json_default)

        module_files: Dict[str, str] = {}
        if module_outputs:
            modules_dir = bundle_dir / "module_outputs"
            modules_dir.mkdir(parents=True, exist_ok=True)
            for name, payload in module_outputs.items():
                module_path = modules_dir / f"{name}.json"
                with open(module_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2, default=self._json_default)
                module_files[name] = str(module_path)

        bundle_meta = {
            "patient_id": patient_id,
            "end_type": end_type,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "paths": {
                "json": str(report_json_path),
                "image": assets.get("image"),
                "pdf": assets.get("pdf"),
                "module_files": module_files
            },
            "capabilities": {
                "matplotlib_available": MATPLOTLIB_AVAILABLE
            }
        }

        meta_path = bundle_dir / "bundle_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(bundle_meta, f, ensure_ascii=False, indent=2)

        print(f"患者 {patient_id} 的 {report_type} 报告产物已生成: {bundle_dir}")
        return bundle_meta
    
    def save_all_reports(self, patient_id: str, reports: Dict[str, Dict[str, Any]], end_type: str):
        """保存所有报告"""
        saved_files = []
        for report_type, report in reports.items():
            file_path = self.save_patient_report(patient_id, report, report_type, end_type)
            saved_files.append(file_path)
        return saved_files
    
    def save_system_report(self, report: Dict[str, Any]):
        """保存系统报告"""
        # 创建系统报告目录
        system_dir = Path(self.save_dir) / "system"
        system_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建报告文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"system_report_{timestamp}.json"
        file_path = system_dir / file_name
        
        # 保存报告
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"系统报告已保存到: {file_path}")
        return str(file_path)
    
    def save_agent_interactions(self, interactions: List[Dict[str, Any]]):
        """保存智能体交互记录"""
        # 创建交互记录目录
        interaction_dir = Path(self.save_dir) / "agent_interactions"
        interaction_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建报告文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"agent_interactions_{timestamp}.json"
        file_path = interaction_dir / file_name
        
        # 保存交互记录
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, ensure_ascii=False, indent=2)
        
        print(f"智能体交互记录已保存到: {file_path}")
        return str(file_path)
    
    def load_report(self, file_path: str) -> Dict[str, Any]:
        """加载报告"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载报告失败: {e}")
            return {}
    
    def get_patient_reports(self, patient_id: str) -> List[str]:
        """获取患者的所有报告"""
        patient_dir = Path(self.save_dir) / patient_id
        if not patient_dir.exists():
            return []
        
        reports = []
        for file in patient_dir.rglob("*.json"):
            reports.append(str(file))
        
        return reports
    
    def get_system_reports(self) -> List[str]:
        """获取系统报告"""
        system_dir = Path(self.save_dir) / "system"
        if not system_dir.exists():
            return []
        
        reports = []
        for file in system_dir.glob("*.json"):
            reports.append(str(file))
        
        return reports
    
    def get_agent_interactions(self) -> List[str]:
        """获取智能体交互记录"""
        interaction_dir = Path(self.save_dir) / "agent_interactions"
        if not interaction_dir.exists():
            return []
        
        interactions = []
        for file in interaction_dir.glob("*.json"):
            interactions.append(str(file))
        
        return interactions
    
    def generate_report_summary(self, patient_id: str) -> Dict[str, Any]:
        """生成患者报告摘要"""
        reports = self.get_patient_reports(patient_id)
        summary = {
            "patient_id": patient_id,
            "report_count": len(reports),
            "reports": [],
            "last_updated": datetime.now().isoformat()
        }
        
        for report_path in reports:
            report = self.load_report(report_path)
            if report:
                summary["reports"].append({
                    "file_path": report_path,
                    "report_type": report.get("report_type", ""),
                    "end_type": report.get("end_type", ""),
                    "generated_at": report.get("generated_at", "")
                })
        
        return summary


# 全局结果保存实例
result_saver = ResultSaver()

# 测试代码
if __name__ == "__main__":
    # 模拟报告数据
    test_report = {
        "patient_id": "P_001",
        "report_type": "daily",
        "end_type": "patient",
        "generated_at": datetime.now().isoformat(),
        "content": "测试报告内容",
        "visuals": [],
        "recommendations": []
    }
    
    # 保存报告
    saved_path = result_saver.save_patient_report("P_001", test_report, "daily", "patient")
    print(f"保存的报告路径: {saved_path}")
    
    # 加载报告
    loaded_report = result_saver.load_report(saved_path)
    print(f"加载的报告: {loaded_report}")
    
    # 获取患者报告
    patient_reports = result_saver.get_patient_reports("P_001")
    print(f"患者 P_001 的报告数量: {len(patient_reports)}")
    
    # 生成报告摘要
    summary = result_saver.generate_report_summary("P_001")
    print(f"报告摘要: {summary}")