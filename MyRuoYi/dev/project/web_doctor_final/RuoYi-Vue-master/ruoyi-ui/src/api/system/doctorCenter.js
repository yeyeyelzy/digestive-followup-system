import request from '@/utils/request'

const DOCTOR_AI_TIMEOUT = 120000

export function getPatientRiskPredictCurrent(patientId) {
  return request({
    url: '/system/risk/predict',
    method: 'get',
    params: { patientId }
  })
}

export function getPatientRiskPredictHistory(patientId) {
  return request({
    url: '/system/risk/predict/history',
    method: 'get',
    params: { patientId }
  })
}

export function getPatientRehabPlanCurrent(patientId, planId) {
  return request({
    url: '/api/patient/rehab-plan/current',
    method: 'get',
    params: { patientId, planId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function getPatientRehabPlanHistory(patientId) {
  return request({
    url: '/api/patient/rehab-plan/history',
    method: 'get',
    params: { patientId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function getPatientIndicatorChangeCurrent(patientId, period = 'daily') {
  return request({
    url: '/system/indicator/change',
    method: 'get',
    params: { patientId, period },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function getPatientIndicatorChangeHistory(patientId, period = 'daily') {
  return request({
    url: '/system/indicator/change/history',
    method: 'get',
    params: { patientId, period },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function previewPatientIndicatorHistoryPdf(patientId, sourceDate, period = 'daily') {
  return request({
    url: '/system/indicator/change/history/pdf',
    method: 'get',
    params: { patientId, sourceDate, period },
    responseType: 'blob'
  })
}

export function getDoctorRiskPredict(patientId) {
  return request({
    url: '/api/doctor/patient/risk/predict',
    method: 'get',
    params: { patientId }
  })
}

export function listDoctorAiPatients(params) {
  return request({
    url: '/api/doctor/patient/ai-patient/list',
    method: 'get',
    params
  })
}

export function getDoctorIndicatorChange(patientId, period = 'daily') {
  return request({
    url: '/api/doctor/patient/indicator/change',
    method: 'get',
    params: { patientId, period }
  })
}

export function getDoctorIndicatorChangeHistory(patientId, period = 'daily') {
  return request({
    url: '/api/doctor/patient/indicator/change/history',
    method: 'get',
    params: { patientId, period },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function previewDoctorIndicatorHistoryPdf(patientId, sourceDate, period = 'daily') {
  return request({
    url: '/api/doctor/patient/indicator/change/history/pdf',
    method: 'get',
    params: { patientId, sourceDate, period },
    responseType: 'blob'
  })
}

export function getDoctorRehabPlan(patientId, planId) {
  return request({
    url: '/api/doctor/patient/rehab-plan/current',
    method: 'get',
    params: { patientId, planId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function generateDoctorRehabPlan(patientId) {
  return request({
    url: '/api/doctor/patient/rehab-plan/generate',
    method: 'post',
    data: { patientId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function reviseDoctorRehabPlan(data) {
  return request({
    url: '/api/doctor/patient/rehab-plan/revise',
    method: 'post',
    data,
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function dispatchDoctorRehabPlan(patientId, planId) {
  return request({
    url: '/api/doctor/patient/rehab-plan/dispatch',
    method: 'post',
    data: { patientId, planId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function getDoctorRehabPlanTrace(patientId, planId) {
  return request({
    url: '/api/doctor/patient/rehab-plan/dispatch/trace',
    method: 'get',
    params: { patientId, planId }
  })
}

export function getDoctorHealthReportDaily(patientId) {
  return request({
    url: '/api/doctor/patient/health-report/daily',
    method: 'get',
    params: { patientId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function getDoctorHealthReportWeekly(patientId) {
  return request({
    url: '/api/doctor/patient/health-report/weekly',
    method: 'get',
    params: { patientId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function getDoctorHealthReportMonthly(patientId) {
  return request({
    url: '/api/doctor/patient/health-report/monthly',
    method: 'get',
    params: { patientId },
    timeout: DOCTOR_AI_TIMEOUT
  })
}

export function previewDoctorHealthReportPdf(patientId, reportType = 'daily') {
  return request({
    url: '/api/doctor/patient/health-report/pdf/view',
    method: 'get',
    params: { patientId, reportType },
    responseType: 'blob'
  })
}
