import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from .config import PATIENTS, FONT_DIR, BASE_DIR

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
    
    PDF_DEFAULT_FONT = "Helvetica"
    
    def register_chinese_font():
        import platform
        import os
        
        system = platform.system()
        font_search_paths = []
        
        if system == "Windows":
            font_search_paths = [
                Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts",
                FONT_DIR
            ]
        elif system == "Darwin":
            font_search_paths = [
                Path("/Library/Fonts"),
                Path("~/Library/Fonts").expanduser(),
                FONT_DIR
            ]
        else:
            font_search_paths = [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                FONT_DIR
            ]
        
        font_candidates = []
        
        for font_dir in font_search_paths:
            if font_dir.exists():
                if system == "Windows":
                    font_candidates.extend([
                        font_dir / "simhei.ttf",
                        font_dir / "msyh.ttc",
                        font_dir / "msyhbd.ttc",
                        font_dir / "simsun.ttc",
                        font_dir / "simkai.ttf",
                        font_dir / "simli.ttf"
                    ])
                elif system == "Darwin":
                    font_candidates.extend([
                        font_dir / "PingFang.ttc",
                        font_dir / "STHeiti Light.ttc",
                        font_dir / "STHeiti Medium.ttc"
                    ])
                else:
                    font_candidates.extend([
                        font_dir / "NotoSansCJK-Regular.ttc",
                        font_dir / "wqy-microhei.ttc"
                    ])
        
        font_candidates.extend([
            FONT_DIR / "SourceHanSansCN-Regular.ttf",
            FONT_DIR / "SourceHanSansCN-Bold.ttf",
            FONT_DIR / "SimHei.ttf",
            FONT_DIR / "msyh.ttc"
        ])
        
        for font_path in font_candidates:
            if font_path.exists():
                try:
                    font_name = font_path.stem
                    pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                    global PDF_DEFAULT_FONT
                    PDF_DEFAULT_FONT = font_name
                    print(f"[OK] Font registered: {font_name} ({font_path})")
                    return
                except Exception as e:
                    print(f"[WARN] Font register failed {font_path}: {e}")
                    continue
        
        print("[WARN] No CJK font found; PDF Chinese text may not render correctly.")
        print("[INFO] On Windows, check C:\\Windows\\Fonts for simhei.ttf or msyh.ttc.")
    
    register_chinese_font()
    
except ImportError:
    REPORTLAB_AVAILABLE = False
    PDF_DEFAULT_FONT = "Helvetica"
    print("[WARN] reportlab not installed; PDF generation disabled.")


class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
    
    def _generate_standard_directory_structure(self, patient_id):
        patient_dir = self.output_dir / patient_id
        
        dirs_to_create = [
            patient_dir / 'patient_end' / 'daily',
            patient_dir / 'patient_end' / 'weekly',
            patient_dir / 'patient_end' / 'monthly',
            patient_dir / 'family_end' / 'daily',
            patient_dir / 'family_end' / 'weekly',
            patient_dir / 'family_end' / 'monthly',
            patient_dir / 'doctor_end' / 'daily',
            patient_dir / 'doctor_end' / 'weekly',
            patient_dir / 'doctor_end' / 'monthly',
            patient_dir / 'system_check' / 'daily',
            patient_dir / 'system_check' / 'weekly',
            patient_dir / 'system_check' / 'monthly',
            patient_dir / 'model_cache'
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return patient_dir
    
    def generate_daily_report(self, patient_id, date_str, daily_stats, online_result, 
                             medical_advice, attributed_abnormal, figure_paths, 
                             end_type='doctor', alarm_stats=None, qualitative_desc=""):
        patient_dir = self._generate_standard_directory_structure(patient_id)
        
        date_dir = patient_dir / end_type / 'daily' / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        
        figures_dir = date_dir / 'figures'
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "report_base_info": {
                "patient_id": patient_id,
                "patient_name": PATIENTS[patient_id]['name'],
                "report_date": date_str,
                "report_type": "daily",
                "end_type": end_type,
                "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_time_range": f"{date_str} 00:00:00 - {date_str} 23:59:59"
            },
            "core_summary": {
                "qualitative_desc": qualitative_desc,
                "risk_level": self._assess_risk_level(online_result, alarm_stats),
                "abnormal_event_count": alarm_stats.get('total_count', 0) if alarm_stats else 0
            },
            "core_indicators": self._format_core_indicators(daily_stats, online_result, end_type),
            "abnormal_event": self._format_abnormal_events(attributed_abnormal, alarm_stats, end_type),
            "baseline_update_info": self._format_baseline_update(online_result),
            "health_suggestion": medical_advice,
            "figure_paths": figure_paths
        }
        
        json_path = date_dir / f"{date_str}_{end_type}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        return json_path
    
    def generate_weekly_report(self, patient_id, week_range, date_list, daily_stats_list, 
                              online_results_list, baseline_history, figure_paths, end_type='doctor'):
        patient_dir = self._generate_standard_directory_structure(patient_id)
        
        week_dir = patient_dir / end_type / 'weekly' / week_range
        week_dir.mkdir(parents=True, exist_ok=True)
        
        figures_dir = week_dir / 'figures'
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        weekly_summary = self._calculate_weekly_summary(daily_stats_list, online_results_list)
        
        report_data = {
            "report_base_info": {
                "patient_id": patient_id,
                "patient_name": PATIENTS[patient_id]['name'],
                "report_date": week_range,
                "report_type": "weekly",
                "end_type": end_type,
                "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_time_range": week_range
            },
            "weekly_summary": weekly_summary,
            "daily_details": self._format_weekly_daily_details(date_list, daily_stats_list, online_results_list),
            "baseline_update_trace": self._format_baseline_trace(baseline_history),
            "figure_paths": figure_paths
        }
        
        json_path = week_dir / f"{week_range}_{end_type}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        return json_path
    
    def generate_monthly_report(self, patient_id, month_range, date_list, daily_stats_list, 
                               figure_paths, end_type='doctor'):
        patient_dir = self._generate_standard_directory_structure(patient_id)
        
        month_dir = patient_dir / end_type / 'monthly' / month_range
        month_dir.mkdir(parents=True, exist_ok=True)
        
        figures_dir = month_dir / 'figures'
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        monthly_summary = self._calculate_monthly_summary(daily_stats_list)
        
        report_data = {
            "report_base_info": {
                "patient_id": patient_id,
                "patient_name": PATIENTS[patient_id]['name'],
                "report_date": month_range,
                "report_type": "monthly",
                "end_type": end_type,
                "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_time_range": month_range
            },
            "monthly_summary": monthly_summary,
            "figure_paths": figure_paths
        }
        
        json_path = month_dir / f"{month_range}_{end_type}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        return json_path
    
    def save_system_check(self, patient_id, date_str, agent_logs, data_quality, weight_log, report_type='daily'):
        patient_dir = self._generate_standard_directory_structure(patient_id)
        
        check_dir = patient_dir / 'system_check' / report_type
        check_dir.mkdir(parents=True, exist_ok=True)
        
        system_check_data = {
            "check_info": {
                "patient_id": patient_id,
                "check_date": date_str,
                "report_type": report_type,
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent_logs": agent_logs,
            "data_quality": data_quality,
            "weight_log": weight_log
        }
        
        json_path = check_dir / f"{date_str}_system_check.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(system_check_data, f, ensure_ascii=False, indent=2, default=str)
        
        return json_path
    
    def _assess_risk_level(self, online_result, alarm_stats):
        health_score = online_result.get('health_score_update', {}).get('new_score', 50)
        pathological_count = alarm_stats.get('pathological_count', 0) if alarm_stats else 0
        
        if pathological_count > 5:
            return "高风险"
        elif health_score < 50:
            return "中风险"
        elif health_score < 70:
            return "低风险"
        else:
            return "正常"
    
    def _format_core_indicators(self, daily_stats, online_result, end_type):
        indicators = {}
        
        if daily_stats and 'hr_mean' in daily_stats:
            hr_mean = daily_stats['hr_mean']
            risk_zones = online_result.get('risk_zones', {})
            baseline_mu = risk_zones.get('mu', hr_mean)
            change_ratio = (hr_mean - baseline_mu) / baseline_mu * 100 if baseline_mu != 0 else 0
            
            status = "正常"
            if hr_mean < risk_zones.get('yellow_low', hr_mean - 20) or hr_mean > risk_zones.get('yellow_high', hr_mean + 20):
                status = "异常"
            elif hr_mean < risk_zones.get('blue_low', hr_mean - 10) or hr_mean > risk_zones.get('blue_high', hr_mean + 10):
                status = "关注"
            
            qualitative_desc = "较昨日改善" if change_ratio < -2 else ("较昨日变差" if change_ratio > 2 else "保持稳定")
            
            indicators['rest_heart_rate'] = {
                "value": round(hr_mean, 1),
                "baseline_mean": round(baseline_mu, 1),
                "change_ratio": round(change_ratio, 2),
                "status": status,
                "qualitative_desc": qualitative_desc
            }
        
        if daily_stats and 'steps_total' in daily_stats:
            steps = daily_stats['steps_total']
            status = "达标" if steps >= 6000 else "未达标"
            indicators['daily_steps'] = {
                "value": int(steps),
                "baseline_mean": 7000,
                "change_ratio": round((steps - 7000) / 7000 * 100, 2) if 7000 != 0 else 0,
                "status": status,
                "qualitative_desc": "活动量充足" if steps >= 8000 else "建议增加活动"
            }
        
        return indicators
    
    def _format_abnormal_events(self, attributed_abnormal, alarm_stats, end_type):
        if attributed_abnormal is None or attributed_abnormal.empty:
            return {
                "total_count": 0,
                "physiological_count": 0,
                "pathological_count": 0,
                "pending_count": 0,
                "event_list": []
            }
        
        event_list = []
        for _, row in attributed_abnormal.iterrows():
            event = {
                "time": row['time'].strftime("%H:%M:%S") if hasattr(row['time'], 'strftime') else str(row['time']),
                "heart_rate": int(row['heart_rate']),
                "level": row['level'],
                "attribution": row.get('attribution', '未知')
            }
            event_list.append(event)
        
        return {
            "total_count": alarm_stats.get('total_count', 0) if alarm_stats else len(attributed_abnormal),
            "physiological_count": alarm_stats.get('physiological_count', 0) if alarm_stats else 0,
            "pathological_count": alarm_stats.get('pathological_count', 0) if alarm_stats else 0,
            "pending_count": alarm_stats.get('pending_count', 0) if alarm_stats else 0,
            "event_list": event_list[:10]
        }
    
    def _format_baseline_update(self, online_result):
        bayesian_update = online_result.get('bayesian_update')
        
        if bayesian_update:
            return {
                "update_indicator_count": 1,
                "update_details": [
                    {
                        "indicator": "rest_heart_rate",
                        "old_mu": round(bayesian_update['old_mu'], 1),
                        "new_mu": round(bayesian_update['new_mu'], 1),
                        "change_mu": round(bayesian_update['change_mu'], 2)
                    }
                ]
            }
        else:
            return {
                "update_indicator_count": 0,
                "update_details": []
            }
    
    def _calculate_weekly_summary(self, daily_stats_list, online_results_list):
        valid_stats = [s for s in daily_stats_list if s]
        if not valid_stats:
            return {}
        
        hr_means = [s.get('hr_mean', 0) for s in valid_stats]
        steps_totals = [s.get('steps_total', 0) for s in valid_stats]
        
        return {
            "avg_heart_rate": round(np.mean(hr_means), 1) if hr_means else 0,
            "avg_steps": round(np.mean(steps_totals), 0) if steps_totals else 0,
            "total_days": len(valid_stats)
        }
    
    def _calculate_monthly_summary(self, daily_stats_list):
        valid_stats = [s for s in daily_stats_list if s]
        if not valid_stats:
            return {}
        
        hr_means = [s.get('hr_mean', 0) for s in valid_stats]
        steps_totals = [s.get('steps_total', 0) for s in valid_stats]
        
        return {
            "avg_heart_rate": round(np.mean(hr_means), 1) if hr_means else 0,
            "avg_steps": round(np.mean(steps_totals), 0) if steps_totals else 0,
            "total_days": len(valid_stats)
        }
    
    def _format_weekly_daily_details(self, date_list, daily_stats_list, online_results_list):
        details = []
        for date, stats, result in zip(date_list, daily_stats_list, online_results_list):
            if stats:
                detail = {
                    "date": date,
                    "hr_mean": round(stats.get('hr_mean', 0), 1),
                    "steps_total": int(stats.get('steps_total', 0)),
                    "health_score": round(result.get('health_score_update', {}).get('new_score', 0), 1)
                }
                details.append(detail)
        return details
    
    def _format_baseline_trace(self, baseline_history):
        if baseline_history is None or baseline_history.empty:
            return []
        
        trace_list = []
        for _, row in baseline_history.iterrows():
            trace = {
                "date": row['Date'].strftime("%Y-%m-%d") if hasattr(row['Date'], 'strftime') else str(row['Date']),
                "indicator": row['indicator'],
                "baseline_mean": round(row['baseline_mean'], 2)
            }
            trace_list.append(trace)
        
        return trace_list
    
    def generate_pdf_report(self, patient_id, report_date, report_type, end_type, content_dict, save_path):
        if not REPORTLAB_AVAILABLE:
            print("PDF生成功能不可用，请先安装reportlab库")
            return None
        
        try:
            doc_file = str(Path(save_path) / f"{report_date}_{end_type}.pdf")
            doc = SimpleDocTemplate(doc_file, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            story = []
            
            title_style = ParagraphStyle(
                "title", parent=styles["Heading1"], fontName=PDF_DEFAULT_FONT, fontSize=18, textColor=colors.HexColor("#2c3e50"), alignment=1, spaceAfter=0.5*cm
            )
            subtitle_style = ParagraphStyle(
                "subtitle", parent=styles["Heading2"], fontName=PDF_DEFAULT_FONT, fontSize=14, textColor=colors.HexColor("#34495e"), spaceAfter=0.3*cm
            )
            normal_style = ParagraphStyle(
                "normal", parent=styles["Normal"], fontName=PDF_DEFAULT_FONT, fontSize=10, spaceAfter=0.2*cm, leading=16
            )
            highlight_style = ParagraphStyle(
                "highlight", parent=styles["Normal"], fontName=PDF_DEFAULT_FONT, fontSize=12, textColor=colors.HexColor("#e74c3c"), spaceAfter=0.3*cm, leading=16
            )
            
            report_title_map = {
                "daily": "每日健康监测报告",
                "weekly": "每周健康评估报告",
                "monthly": "每月健康管理报告"
            }
            end_title_map = {
                "patient": "患者版",
                "family": "家属版",
                "doctor": "医生专业版"
            }
            patient_name = PATIENTS.get(patient_id, {}).get('name', patient_id)
            title = Paragraph(f"患者{patient_name} {report_date} {report_title_map.get(report_type, '健康报告')}({end_title_map.get(end_type, '')})", title_style)
            story.append(title)
            story.append(Spacer(1, 0.5*cm))
            
            core_summary = content_dict.get('core_summary', {})
            story.append(Paragraph("一、核心健康总结", subtitle_style))
            qualitative_desc = core_summary.get('qualitative_desc', '暂无总结')
            story.append(Paragraph(qualitative_desc, normal_style))
            story.append(Spacer(1, 0.3*cm))
            
            story.append(Paragraph("二、核心健康指标", subtitle_style))
            core_indicators = content_dict.get('core_indicators', {})
            indicator_table_data = [["指标名称", "当前数值", "状态"]]
            for indicator_key, indicator_data in core_indicators.items():
                indicator_name_map = {
                    'rest_heart_rate': '静息心率',
                    'daily_steps': '日均步数'
                }
                name = indicator_name_map.get(indicator_key, indicator_key)
                value = str(indicator_data.get('value', '-'))
                status = indicator_data.get('status', '-')
                indicator_table_data.append([name, value, status])
            
            if len(indicator_table_data) > 1:
                table = Table(indicator_table_data, colWidths=[4*cm, 3*cm, 4*cm])
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                    ("ALIGN", (0,0), (-1,-1), "CENTER"),
                    ("FONTNAME", (0,0), (-1,-1), PDF_DEFAULT_FONT),
                    ("FONTSIZE", (0,0), (-1,-1), 10),
                    ("BOTTOMPADDING", (0,0), (-1,0), 12),
                    ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f8f9fa")),
                    ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#dee2e6"))
                ]))
                story.append(table)
                story.append(Spacer(1, 0.5*cm))
            
            story.append(Paragraph("三、健康建议", subtitle_style))
            health_suggestion = content_dict.get('health_suggestion', '保持良好的生活习惯')
            story.append(Paragraph(health_suggestion, normal_style))
            
            figure_paths = content_dict.get('figure_paths', {})
            if figure_paths:
                story.append(Paragraph("四、健康趋势可视化", subtitle_style))
                for fig_key, fig_path in figure_paths.items():
                    try:
                        if Path(fig_path).exists():
                            img = Image(fig_path, width=16*cm, height=10*cm)
                            story.append(img)
                            story.append(Spacer(1, 0.3*cm))
                    except Exception as img_e:
                        print(f"添加图片失败 {fig_path}: {img_e}")
            
            doc.build(story)
            print(f"{end_type}端PDF报告已生成：{doc_file}")
            return doc_file
            
        except Exception as e:
            print(f"生成PDF失败: {e}")
            import traceback
            traceback.print_exc()
            return None
