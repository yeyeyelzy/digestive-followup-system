import sys
from pathlib import Path
from datetime import datetime
import uuid

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

from optimized_system.config import OUTPUT_DIR, BASE_DIR, PATIENTS
from optimized_system.data_processor import DataProcessor
from optimized_system.online_learner import OnlineLearner, OnlinePersonalizedBaseline
from optimized_system.medical_agent import MedicalAgent
from optimized_system.visualizer import Visualizer
from optimized_system.report_generator import ReportGenerator

app = FastAPI(
    title="心脏康复多智能体系统API",
    description="V1.0版本，支持患者健康评估、报告生成、风险预警",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=str(OUTPUT_DIR)), name="static")


class SinglePatientRequest(BaseModel):
    patient_id: str = Field(..., description="患者ID，如P_001")
    data: Optional[Dict[str, Any]] = Field(None, description="患者时序数据与基线数据")
    generate_report: bool = Field(True, description="是否生成报告，默认true")
    export_pdf: bool = Field(False, description="是否导出PDF，默认false")


class ReportGenerateRequest(BaseModel):
    patient_id: str = Field(..., description="患者ID")
    report_date: str = Field(..., description="报告日期，格式YYYY-MM-DD")
    end_type: Optional[str] = Field("all", description="报告端类型，doctor/patient/family/all")
    export_pdf: bool = Field(True, description="是否导出PDF")


class HealthCheckResponse(BaseModel):
    code: int = 200
    msg: str = "服务运行正常"
    version: str = "1.0.0"


class ApiResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Dict[str, Any]] = None
    requestId: Optional[str] = None


def generate_request_id():
    return f"req_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"


@app.get("/health", response_model=HealthCheckResponse, summary="服务健康检查")
async def health_check():
    return HealthCheckResponse()


@app.post("/api/agent/single_patient", response_model=ApiResponse, summary="执行单患者健康评估与报告生成")
async def run_single_patient(request: SinglePatientRequest):
    request_id = generate_request_id()
    try:
        if request.patient_id not in PATIENTS:
            raise HTTPException(status_code=400, detail=f"患者ID {request.patient_id} 不存在")
        
        processor = DataProcessor(request.patient_id)
        learner = OnlineLearner(processor.patient_baseline)
        baseline_model = OnlinePersonalizedBaseline(
            request.patient_id,
            OUTPUT_DIR / request.patient_id / 'model_cache',
            processor.patient_baseline
        )
        medical_agent = MedicalAgent(processor.patient_baseline)
        visualizer = Visualizer()
        report_gen = ReportGenerator(OUTPUT_DIR)
        
        date_list = processor.get_date_range()
        if not date_list:
            raise HTTPException(status_code=400, detail="未找到患者数据")
        
        latest_date = date_list[-1]
        df = processor.create_minute_level_wide_table(latest_date)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="患者最新日期数据为空")
        
        online_result = learner.process_day(df)
        daily_stats = online_result['daily_stats']
        
        daily_features = processor.extract_daily_features(latest_date)
        if daily_features:
            baseline_model.update_baseline_daily(latest_date, daily_features)
        
        attributed_abnormal = medical_agent.attribute_abnormalities(
            online_result['abnormal_points'], df
        )
        
        alarm_df, alarm_stats = processor.attribute_alarms(df, online_result['risk_zones']['mu'] + 2 * online_result['risk_zones']['sigma'])
        
        qualitative_desc = medical_agent.generate_qualitative_description(
            daily_stats,
            online_result['condition_assessment']
        )
        
        medical_advice = medical_agent.generate_medical_advice(
            daily_stats,
            online_result['health_score_update']['new_score'],
            online_result['condition_assessment'],
            {
                'red': online_result['health_score_update']['red_count'],
                'yellow': online_result['health_score_update']['yellow_count']
            }
        )
        
        figure_paths = {}
        report_paths = {}
        
        if request.generate_report:
            patient_dir = OUTPUT_DIR / request.patient_id
            
            for end_type in ['doctor_end', 'patient_end', 'family_end']:
                end_type_short = end_type.replace('_end', '')
                date_dir = patient_dir / end_type / 'daily' / latest_date / 'figures'
                date_dir.mkdir(parents=True, exist_ok=True)
                
                hr_fig_path = date_dir / f'{latest_date}_hr_trend.png'
                visualizer.plot_daily_hr_trend(
                    latest_date, df, online_result['risk_zones'],
                    online_result['abnormal_points'], str(hr_fig_path), end_type_short
                )
                figure_paths[f'{end_type_short}_hr_trend'] = str(hr_fig_path)
                
                multi_fig_path = date_dir / f'{latest_date}_multi_indicator.png'
                visualizer.plot_multi_indicator(
                    latest_date, df, online_result['risk_zones'], str(multi_fig_path)
                )
                figure_paths[f'{end_type_short}_multi_indicator'] = str(multi_fig_path)
                
                if end_type == 'doctor_end':
                    activity_fig_path = date_dir / f'{latest_date}_activity_distribution.png'
                    visualizer.plot_activity_distribution(df, str(activity_fig_path), latest_date)
                    figure_paths['doctor_activity_distribution'] = str(activity_fig_path)
                    
                    alarm_pie_path = date_dir / f'{latest_date}_alarm_pie.png'
                    visualizer.plot_alarm_pie(alarm_stats, str(alarm_pie_path), latest_date)
                    figure_paths['doctor_alarm_pie'] = str(alarm_pie_path)
            
            for end_type in ['doctor', 'patient', 'family']:
                end_type_full = f'{end_type}_end'
                report_path = report_gen.generate_daily_report(
                    request.patient_id, latest_date, daily_stats, online_result,
                    medical_advice, attributed_abnormal, figure_paths,
                    end_type_full, alarm_stats, qualitative_desc
                )
                report_paths[end_type] = str(report_path)
                
                if request.export_pdf:
                    pdf_content_dict = {
                        'core_summary': {
                            'qualitative_desc': qualitative_desc,
                            'risk_level': report_gen._assess_risk_level(online_result, alarm_stats)
                        },
                        'core_indicators': report_gen._format_core_indicators(daily_stats, online_result, end_type),
                        'health_suggestion': medical_advice,
                        'figure_paths': figure_paths
                    }
                    date_dir = OUTPUT_DIR / request.patient_id / end_type_full / 'daily' / latest_date
                    pdf_path = report_gen.generate_pdf_report(
                        request.patient_id, latest_date, 'daily', end_type,
                        pdf_content_dict, str(date_dir)
                    )
                    if pdf_path:
                        report_paths[f'{end_type}_pdf'] = str(pdf_path)
        
        health_score = online_result['health_score_update']['new_score']
        risk_level = "低风险" if health_score >= 70 else ("中风险" if health_score >= 50 else "高风险")
        
        return ApiResponse(
            code=200,
            msg="患者健康评估完成",
            data={
                "patient_id": request.patient_id,
                "health_score": round(health_score, 1),
                "risk_level": risk_level,
                "warning_events": {
                    "red_count": online_result['health_score_update']['red_count'],
                    "yellow_count": online_result['health_score_update']['yellow_count'],
                    "pathological_count": alarm_stats.get('pathological_count', 0) if alarm_stats else 0,
                    "physiological_count": alarm_stats.get('physiological_count', 0) if alarm_stats else 0
                },
                "report_date": latest_date,
                "report_paths": report_paths,
                "figure_paths": figure_paths
            },
            requestId=request_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"接口执行错误: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report/generate_daily", response_model=ApiResponse, summary="生成患者单日报告")
async def generate_daily_report(request: ReportGenerateRequest):
    request_id = generate_request_id()
    try:
        if request.patient_id not in PATIENTS:
            raise HTTPException(status_code=400, detail=f"患者ID {request.patient_id} 不存在")
        
        processor = DataProcessor(request.patient_id)
        learner = OnlineLearner(processor.patient_baseline)
        baseline_model = OnlinePersonalizedBaseline(
            request.patient_id,
            OUTPUT_DIR / request.patient_id / 'model_cache',
            processor.patient_baseline
        )
        medical_agent = MedicalAgent(processor.patient_baseline)
        visualizer = Visualizer()
        report_gen = ReportGenerator(OUTPUT_DIR)
        
        df = processor.create_minute_level_wide_table(request.report_date)
        
        if df.empty:
            raise HTTPException(status_code=400, detail=f"日期 {request.report_date} 数据为空")
        
        online_result = learner.process_day(df)
        daily_stats = online_result['daily_stats']
        
        daily_features = processor.extract_daily_features(request.report_date)
        if daily_features:
            baseline_model.update_baseline_daily(request.report_date, daily_features)
        
        attributed_abnormal = medical_agent.attribute_abnormalities(
            online_result['abnormal_points'], df
        )
        
        alarm_df, alarm_stats = processor.attribute_alarms(df, online_result['risk_zones']['mu'] + 2 * online_result['risk_zones']['sigma'])
        
        qualitative_desc = medical_agent.generate_qualitative_description(
            daily_stats,
            online_result['condition_assessment']
        )
        
        medical_advice = medical_agent.generate_medical_advice(
            daily_stats,
            online_result['health_score_update']['new_score'],
            online_result['condition_assessment'],
            {
                'red': online_result['health_score_update']['red_count'],
                'yellow': online_result['health_score_update']['yellow_count']
            }
        )
        
        figure_paths = {}
        report_paths = {}
        end_types = ['doctor', 'patient', 'family'] if request.end_type == 'all' else [request.end_type]
        
        for end_type in end_types:
            end_type_full = f'{end_type}_end'
            date_dir = OUTPUT_DIR / request.patient_id / end_type_full / 'daily' / request.report_date / 'figures'
            date_dir.mkdir(parents=True, exist_ok=True)
            
            hr_fig_path = date_dir / f'{request.report_date}_hr_trend.png'
            visualizer.plot_daily_hr_trend(
                request.report_date, df, online_result['risk_zones'],
                online_result['abnormal_points'], str(hr_fig_path), end_type
            )
            figure_paths[f'{end_type}_hr_trend'] = str(hr_fig_path)
            
            multi_fig_path = date_dir / f'{request.report_date}_multi_indicator.png'
            visualizer.plot_multi_indicator(
                request.report_date, df, online_result['risk_zones'], str(multi_fig_path)
            )
            figure_paths[f'{end_type}_multi_indicator'] = str(multi_fig_path)
            
            if end_type == 'doctor':
                activity_fig_path = date_dir / f'{request.report_date}_activity_distribution.png'
                visualizer.plot_activity_distribution(df, str(activity_fig_path), request.report_date)
                figure_paths['doctor_activity_distribution'] = str(activity_fig_path)
                
                alarm_pie_path = date_dir / f'{request.report_date}_alarm_pie.png'
                visualizer.plot_alarm_pie(alarm_stats, str(alarm_pie_path), request.report_date)
                figure_paths['doctor_alarm_pie'] = str(alarm_pie_path)
        
        for end_type in end_types:
            end_type_full = f'{end_type}_end'
            report_path = report_gen.generate_daily_report(
                request.patient_id, request.report_date, daily_stats, online_result,
                medical_advice, attributed_abnormal, figure_paths,
                end_type_full, alarm_stats, qualitative_desc
            )
            report_paths[end_type] = str(report_path)
            
            if request.export_pdf:
                pdf_content_dict = {
                    'core_summary': {
                        'qualitative_desc': qualitative_desc,
                        'risk_level': report_gen._assess_risk_level(online_result, alarm_stats)
                    },
                    'core_indicators': report_gen._format_core_indicators(daily_stats, online_result, end_type),
                    'health_suggestion': medical_advice,
                    'figure_paths': figure_paths
                }
                date_dir = OUTPUT_DIR / request.patient_id / end_type_full / 'daily' / request.report_date
                pdf_path = report_gen.generate_pdf_report(
                    request.patient_id, request.report_date, 'daily', end_type,
                    pdf_content_dict, str(date_dir)
                )
                if pdf_path:
                    report_paths[f'{end_type}_pdf'] = str(pdf_path)
        
        return ApiResponse(
            code=200,
            msg="报告生成完成",
            data={
                "patient_id": request.patient_id,
                "report_date": request.report_date,
                "report_paths": report_paths,
                "figure_paths": figure_paths
            },
            requestId=request_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"接口执行错误: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/get_pdf_url", response_model=ApiResponse, summary="获取报告PDF下载链接")
async def get_pdf_url(patient_id: str, report_date: str, end_type: str = "doctor"):
    request_id = generate_request_id()
    try:
        end_type_full = f'{end_type}_end'
        pdf_path = OUTPUT_DIR / patient_id / end_type_full / 'daily' / report_date / f'{report_date}_{end_type}.pdf'
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF文件不存在")
        
        relative_path = pdf_path.relative_to(OUTPUT_DIR)
        pdf_url = f"/static/{relative_path.as_posix()}"
        
        return ApiResponse(
            code=200,
            msg="获取PDF链接成功",
            data={
                "pdf_url": pdf_url,
                "pdf_path": str(pdf_path),
                "expire_time": None
            },
            requestId=request_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patient/list", response_model=ApiResponse, summary="获取患者列表")
async def get_patient_list():
    request_id = generate_request_id()
    patient_list = []
    for patient_id, patient_info in PATIENTS.items():
        patient_list.append({
            "patient_id": patient_id,
            "patient_name": patient_info['name'],
            "folder": patient_info['folder']
        })
    
    return ApiResponse(
        code=200,
        msg="获取患者列表成功",
        data={"patient_list": patient_list},
        requestId=request_id
    )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("心脏康复多智能体系统 API服务")
    print("="*60)
    print("服务地址: http://127.0.0.1:8000")
    print("接口文档: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
