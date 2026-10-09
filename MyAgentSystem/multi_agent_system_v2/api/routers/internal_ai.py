from fastapi import APIRouter, HTTPException

from ..schemas import (
    ApiEnvelope,
    BaseAiRequest,
    HealthReportSampleRequest,
    HealthyLifeDecisionRequest,
    RehabPlanGenerateRequest,
    RehabPlanReviseRequest,
)
from ..services.health_services import (
    HeartTwinService,
    HealthReportService,
    HealthyLifeDecisionService,
    RehabPlanVersionService,
    RiskPredictService,
)


router = APIRouter(prefix="/ai", tags=["internal-ai"])

heart_twin_service = HeartTwinService()
healthy_service = HealthyLifeDecisionService()
risk_service = RiskPredictService()
rehab_plan_service = RehabPlanVersionService()
health_report_service = HealthReportService()


@router.post("/heart-twin/realtime", response_model=ApiEnvelope)
def heart_twin_realtime(req: BaseAiRequest):
    try:
        data = heart_twin_service.get_realtime(req.patientId)
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/heart-twin/forecast", response_model=ApiEnvelope)
def heart_twin_forecast(req: BaseAiRequest):
    try:
        data = heart_twin_service.get_forecast(req.patientId)
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/recovery/healthy-life-decision", response_model=ApiEnvelope)
def healthy_life_decision(req: HealthyLifeDecisionRequest):
    try:
        data = healthy_service.decide(req.patientId, req.date, req.inputs.model_dump())
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/risk/predict", response_model=ApiEnvelope)
def risk_predict(req: BaseAiRequest):
    try:
        data = risk_service.predict(req.patientId)
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/rehab/plan/generate", response_model=ApiEnvelope)
def rehab_plan_generate(req: RehabPlanGenerateRequest):
    try:
        data = rehab_plan_service.generate_plan(req.patientId)
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/rehab/plan/revise", response_model=ApiEnvelope)
def rehab_plan_revise(req: RehabPlanReviseRequest):
    try:
        data = rehab_plan_service.revise_plan(
            patient_id=req.patientId,
            plan_id=req.planId,
            revised_content=req.revisedContent,
            revised_by=req.revisedBy,
        )
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rehab/plan/view", response_model=ApiEnvelope)
def rehab_plan_view(req: BaseAiRequest):
    try:
        data = rehab_plan_service.view_plan(req.patientId, req.planId or "")
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rehab/plan/dispatch", response_model=ApiEnvelope)
def rehab_plan_dispatch(req: BaseAiRequest):
    try:
        if not req.planId:
            raise ValueError("planId is required")
        data = rehab_plan_service.dispatch_plan(req.patientId, req.planId, "doctor")
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/health-report/daily", response_model=ApiEnvelope)
def health_report_daily(req: BaseAiRequest):
    try:
        data = health_report_service.get_report(
            req.patientId,
            "daily",
            req.scene or "patient",
            req.periodValue or "",
            req.periodLabel or "",
        )
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/health-report/weekly", response_model=ApiEnvelope)
def health_report_weekly(req: BaseAiRequest):
    try:
        data = health_report_service.get_report(
            req.patientId,
            "weekly",
            req.scene or "patient",
            req.periodValue or "",
            req.periodLabel or "",
        )
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/health-report/monthly", response_model=ApiEnvelope)
def health_report_monthly(req: BaseAiRequest):
    try:
        data = health_report_service.get_report(
            req.patientId,
            "monthly",
            req.scene or "patient",
            req.periodValue or "",
            req.periodLabel or "",
        )
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/health-report/debug-sample", response_model=ApiEnvelope)
def health_report_debug_sample(req: HealthReportSampleRequest):
    try:
        data = health_report_service.generate_sample_reports_for_one_patient(
            patient_id=req.patientId,
            scene=req.scene or "doctor",
            daily_date=req.dailyDate or "2016-04-15",
            weekly_start=req.weeklyStart or "",
            month=req.month or "2016-04",
            overwrite=bool(req.overwrite),
        )
        return ApiEnvelope(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
