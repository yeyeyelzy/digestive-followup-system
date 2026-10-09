from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApiEnvelope(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Any


class BaseAiRequest(BaseModel):
    patientId: str = Field(..., description="Patient ID in business domain (10/11/12)")
    scene: Optional[str] = Field(default="patient", description="patient/family/doctor")
    source: Optional[str] = Field(default="ruoyi")
    planId: Optional[str] = None
    periodValue: Optional[str] = Field(default="", description="Date/weekStart/month value for report generation")
    periodLabel: Optional[str] = Field(default="", description="Custom report label used in output folder and filename")


class HealthReportSampleRequest(BaseModel):
    patientId: str = Field(..., description="Single patient ID in business domain, e.g. 10")
    scene: Optional[str] = Field(default="doctor", description="patient/family/doctor")
    dailyDate: Optional[str] = Field(default="2016-04-15", description="Daily report date: YYYY-MM-DD")
    weeklyStart: Optional[str] = Field(default="", description="Weekly report start date (Monday): YYYY-MM-DD")
    month: Optional[str] = Field(default="2016-04", description="Monthly report month: YYYY-MM")
    overwrite: Optional[bool] = Field(default=True, description="Clear existing output for this patient before generation")


class RealtimeData(BaseModel):
    patientId: str
    timestamp: str
    heartRate: float
    riskLevel: str
    anomalyFeatures: List[str]


class ForecastItem(BaseModel):
    patientId: str
    monthIndex: int
    monthLabel: str
    heartRate: float
    riskLevel: str
    recoveryTrend: str


class HealthyLifeInputs(BaseModel):
    dietCompleted: Optional[bool] = None
    behaviorCompleted: Optional[bool] = None
    medicineCompleted: Optional[bool] = None
    livingCompleted: Optional[bool] = None
    vitalsNormal: Optional[bool] = None
    notes: Optional[str] = None


class HealthyLifeDecisionRequest(BaseModel):
    patientId: str
    date: str
    inputs: HealthyLifeInputs


class HealthyLifeDecisionData(BaseModel):
    patientId: str
    date: str
    isHealthyLife: bool
    score: float
    reasons: List[str]


class RiskPredictData(BaseModel):
    patientId: str
    riskLevel: str
    heartRateDistribution: Dict[str, int]
    warningDistribution: Dict[str, float]
    description: str


class RehabPlanGenerateRequest(BaseModel):
    patientId: str
    scene: Optional[str] = "doctor"
    source: Optional[str] = "ruoyi"


class RehabPlanReviseRequest(BaseModel):
    patientId: str
    planId: str
    revisedContent: Dict[str, Any]
    revisedBy: str


class RehabPlanViewData(BaseModel):
    planId: str
    patientId: str
    aiPlan: Dict[str, Any]
    doctorRevisedPlan: Optional[Dict[str, Any]] = None
    version: int
    status: str
