import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from optimized_system.config import OUTPUT_DIR, PATIENTS
from optimized_system.data_processor import DataProcessor
from optimized_system.online_learner import OnlineLearner, OnlinePersonalizedBaseline
from optimized_system.medical_agent import MedicalAgent
from optimized_system.visualizer import Visualizer
from optimized_system.report_generator import ReportGenerator


def process_patient(patient_id):
    print(f"\n{'='*60}")
    print(f"开始处理患者: {patient_id} - {PATIENTS[patient_id]['name']}")
    print(f"{'='*60}")
    
    processor = DataProcessor(patient_id)
    learner = OnlineLearner(processor.patient_baseline)
    baseline_model = OnlinePersonalizedBaseline(
        patient_id, 
        OUTPUT_DIR / patient_id / 'model_cache',
        processor.patient_baseline
    )
    medical_agent = MedicalAgent(processor.patient_baseline)
    visualizer = Visualizer()
    report_gen = ReportGenerator(OUTPUT_DIR)
    
    date_list = processor.get_date_range()
    print(f"找到 {len(date_list)} 天的数据")
    
    if not date_list:
        print(f"警告: 患者 {patient_id} 没有找到数据!")
        return
    
    daily_data = []
    weekly_data = {}
    monthly_data = {}
    
    for i, date_str in enumerate(date_list, 1):
        try:
            print(f"\n处理第 {i}/{len(date_list)} 天: {date_str}")
            
            df = processor.create_minute_level_wide_table(date_str)
            
            if df.empty:
                print(f"  跳过 {date_str}: 数据为空")
                continue
            
            print(f"  数据点数: {len(df)}")
            
            online_result = learner.process_day(df)
            daily_stats = online_result['daily_stats']
            
            if daily_stats:
                print(f"  平均心率: {daily_stats.get('hr_mean', 0):.1f}")
            
            print(f"  健康评分: {online_result['health_score_update']['new_score']:.1f}")
            print(f"  基线μ: {online_result['risk_zones']['mu']:.1f}")
            print(f"  红色预警: {online_result['health_score_update']['red_count']}次")
            print(f"  黄色关注: {online_result['health_score_update']['yellow_count']}次")
            print(f"  病情趋势: {online_result['condition_assessment']}")
            
            daily_features = processor.extract_daily_features(date_str)
            if daily_features:
                baseline_model.update_baseline_daily(date_str, daily_features)
            
            attributed_abnormal = medical_agent.attribute_abnormalities(
                online_result['abnormal_points'], df
            )
            
            alarm_df, alarm_stats = processor.attribute_alarms(df, online_result['risk_zones']['mu'] + 2 * online_result['risk_zones']['sigma'])
            
            abnormal_count = {
                'red': online_result['health_score_update']['red_count'],
                'yellow': online_result['health_score_update']['yellow_count']
            }
            
            qualitative_desc = medical_agent.generate_qualitative_description(
                daily_stats, 
                online_result['condition_assessment']
            )
            
            medical_advice = medical_agent.generate_medical_advice(
                daily_stats, 
                online_result['health_score_update']['new_score'],
                online_result['condition_assessment'],
                abnormal_count
            )
            
            patient_dir = OUTPUT_DIR / patient_id
            figure_paths = {}
            
            for end_type in ['doctor_end', 'patient_end', 'family_end']:
                end_type_short = end_type.replace('_end', '')
                date_dir = patient_dir / end_type / 'daily' / date_str / 'figures'
                date_dir.mkdir(parents=True, exist_ok=True)
                
                hr_fig_path = date_dir / f'{date_str}_hr_trend.png'
                visualizer.plot_daily_hr_trend(
                    date_str, df, online_result['risk_zones'], 
                    online_result['abnormal_points'], str(hr_fig_path), end_type_short
                )
                figure_paths[f'{end_type_short}_hr_trend'] = str(hr_fig_path)
                
                multi_fig_path = date_dir / f'{date_str}_multi_indicator.png'
                visualizer.plot_multi_indicator(
                    date_str, df, online_result['risk_zones'], str(multi_fig_path)
                )
                figure_paths[f'{end_type_short}_multi_indicator'] = str(multi_fig_path)
                
                if end_type == 'doctor_end':
                    activity_fig_path = date_dir / f'{date_str}_activity_distribution.png'
                    visualizer.plot_activity_distribution(df, str(activity_fig_path), date_str)
                    figure_paths['doctor_activity_distribution'] = str(activity_fig_path)
                    
                    alarm_pie_path = date_dir / f'{date_str}_alarm_pie.png'
                    visualizer.plot_alarm_pie(alarm_stats, str(alarm_pie_path), date_str)
                    figure_paths['doctor_alarm_pie'] = str(alarm_pie_path)
            
            print(f"  生成可视化图表完成")
            
            for end_type in ['doctor', 'patient', 'family']:
                end_type_full = f'{end_type}_end'
                report_path = report_gen.generate_daily_report(
                    patient_id, date_str, daily_stats, online_result,
                    medical_advice, attributed_abnormal, figure_paths,
                    end_type_full, alarm_stats, qualitative_desc
                )
                print(f"  生成{end_type}端报告: {report_path.name}")
                
                pdf_content_dict = {
                    'core_summary': {
                        'qualitative_desc': qualitative_desc,
                        'risk_level': report_gen._assess_risk_level(online_result, alarm_stats)
                    },
                    'core_indicators': report_gen._format_core_indicators(daily_stats, online_result, end_type),
                    'health_suggestion': medical_advice,
                    'figure_paths': figure_paths
                }
                date_dir = OUTPUT_DIR / patient_id / end_type_full / 'daily' / date_str
                pdf_path = report_gen.generate_pdf_report(
                    patient_id, date_str, 'daily', end_type,
                    pdf_content_dict, str(date_dir)
                )
                if pdf_path:
                    print(f"  生成{end_type}端PDF报告")
            
            agent_logs = {
                'data_processor': {'input_days': 1, 'output_rows': len(df)},
                'online_learner': {'baseline_updated': online_result['bayesian_update'] is not None},
                'medical_agent': {'abnormalities_attributed': len(attributed_abnormal) if not attributed_abnormal.empty else 0},
                'visualizer': {'figures_generated': len(figure_paths)},
                'report_generator': {'reports_generated': 3}
            }
            
            data_quality = {
                'missing_rate_heart_rate': df['heart_rate'].isna().mean(),
                'total_records': len(df),
                'valid_records': df['heart_rate'].notna().sum()
            }
            
            weight_log = {
                'date': date_str,
                'agent_weights': {
                    'data_processor': 0.15,
                    'online_learner': 0.25,
                    'medical_agent': 0.3,
                    'risk_grading': 0.2,
                    'visualizer': 0.1
                }
            }
            
            system_check_path = report_gen.save_system_check(
                patient_id, date_str, agent_logs, data_quality, weight_log
            )
            print(f"  生成系统自检: {system_check_path.name}")
            
            daily_data.append({
                'date': date_str,
                'daily_stats': daily_stats,
                'online_result': online_result,
                'df': df
            })
            
            week_range, week_start, week_end = processor.get_week_range(date_str)
            if week_range not in weekly_data:
                weekly_data[week_range] = []
            weekly_data[week_range].append({
                'date': date_str,
                'daily_stats': daily_stats,
                'online_result': online_result
            })
            
            month_range, month_start, month_end = processor.get_month_range(date_str)
            if month_range not in monthly_data:
                monthly_data[month_range] = []
            monthly_data[month_range].append({
                'date': date_str,
                'daily_stats': daily_stats
            })
            
        except Exception as e:
            print(f"  错误处理 {date_str}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print(f"开始生成周报")
    print(f"{'='*60}")
    
    for week_range, week_days in weekly_data.items():
        if len(week_days) >= 3:
            try:
                print(f"\n生成周报: {week_range}")
                
                week_date_list = [d['date'] for d in week_days]
                week_stats_list = [d['daily_stats'] for d in week_days]
                week_results_list = [d['online_result'] for d in week_days]
                
                baseline_history = baseline_model.baseline_history
                
                week_figure_paths = {}
                for end_type in ['doctor_end', 'patient_end', 'family_end']:
                    end_type_short = end_type.replace('_end', '')
                    week_dir = patient_dir / end_type / 'weekly' / week_range / 'figures'
                    week_dir.mkdir(parents=True, exist_ok=True)
                    
                    weekly_fig_path = week_dir / f'{week_range}_weekly_summary.png'
                    visualizer.plot_weekly_trend_summary(
                        week_date_list, week_stats_list, str(weekly_fig_path), week_range
                    )
                    week_figure_paths[f'{end_type_short}_weekly_summary'] = str(weekly_fig_path)
                    
                    if end_type == 'doctor_end' and not baseline_history.empty:
                        baseline_fig_path = week_dir / f'{week_range}_baseline_trace.png'
                        visualizer.plot_baseline_update_trace(
                            baseline_history, str(baseline_fig_path), week_range
                        )
                        week_figure_paths['doctor_baseline_trace'] = str(baseline_fig_path)
                
                for end_type in ['doctor', 'patient', 'family']:
                    end_type_full = f'{end_type}_end'
                    report_path = report_gen.generate_weekly_report(
                        patient_id, week_range, week_date_list, week_stats_list,
                        week_results_list, baseline_history, week_figure_paths, end_type_full
                    )
                    print(f"  生成{end_type}端周报: {report_path.name}")
                    
                    weekly_summary = report_gen._calculate_weekly_summary(week_stats_list, week_results_list)
                    pdf_content_dict = {
                        'core_summary': {
                            'qualitative_desc': f'本周共{len(week_date_list)}天数据，平均心率{weekly_summary.get("avg_heart_rate", 0):.1f}次/分，平均步数{weekly_summary.get("avg_steps", 0):.0f}步',
                            'risk_level': '正常'
                        },
                        'core_indicators': {
                            'rest_heart_rate': {
                                'value': weekly_summary.get('avg_heart_rate', 0),
                                'baseline_mean': weekly_summary.get('avg_heart_rate', 0),
                                'status': '正常'
                            },
                            'daily_steps': {
                                'value': weekly_summary.get('avg_steps', 0),
                                'baseline_mean': weekly_summary.get('avg_steps', 0),
                                'status': '达标' if weekly_summary.get('avg_steps', 0) >= 6000 else '未达标'
                            }
                        },
                        'health_suggestion': '保持健康的生活方式，继续坚持运动和规律作息',
                        'figure_paths': week_figure_paths
                    }
                    week_dir = OUTPUT_DIR / patient_id / end_type_full / 'weekly' / week_range
                    pdf_path = report_gen.generate_pdf_report(
                        patient_id, week_range, 'weekly', end_type,
                        pdf_content_dict, str(week_dir)
                    )
                    if pdf_path:
                        print(f"  生成{end_type}端周报PDF")
                
            except Exception as e:
                print(f"  错误生成周报 {week_range}: {str(e)}")
                import traceback
                traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"患者 {patient_id} 处理完成!")
    print(f"{'='*60}")


def main():
    print("\n" + "="*60)
    print("医疗可穿戴数据在线学习系统 - 深度优化版")
    print("="*60)
    
    for patient_id in PATIENTS.keys():
        try:
            process_patient(patient_id)
        except Exception as e:
            print(f"\n处理患者 {patient_id} 时发生严重错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("所有患者处理完成!")
    print(f"结果保存到: {OUTPUT_DIR}")
    print("="*60)


if __name__ == "__main__":
    main()
