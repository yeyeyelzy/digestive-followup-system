import { request } from '../utils/request';

function getSelectedPatientId() {
  return wx.getStorageSync('selectedPatientId') || null;
}

function getDiet(data) {
  const patientId = (data && data.patientId) || getSelectedPatientId();
  return request({
    url: '/api/family/patient/diet',
    method: 'GET',
    data: {
      ...(data || {}),
      patientId
    }
  });
}

function getBehavior(data) {
  const patientId = (data && data.patientId) || getSelectedPatientId();
  return request({
    url: '/api/family/patient/behavior',
    method: 'GET',
    data: {
      ...(data || {}),
      patientId
    }
  });
}

function getMedicine(data) {
  const patientId = (data && data.patientId) || getSelectedPatientId();
  return request({
    url: '/api/family/patient/medicine',
    method: 'GET',
    data: {
      ...(data || {}),
      patientId
    }
  });
}

function getLiving(data) {
  const patientId = (data && data.patientId) || getSelectedPatientId();
  return request({
    url: '/api/family/patient/living',
    method: 'GET',
    data: {
      ...(data || {}),
      patientId
    }
  });
}

function getOne(id, url) {
  return request({
    url: '/system/' + url + '/' + id,
    method: 'GET'
  });
}

function zhexian(id) {
  const patientId = id || getSelectedPatientId();
  return request({
    url: '/api/family/patient/visual/' + patientId,
    method: 'GET'
  });
}

function getMyDischargeList(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/discharge',
    method: 'GET',
    data: { patientId }
  });
}

function getMyRecoveryList(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/recovery',
    method: 'GET',
    data: { patientId }
  });
}

function updateFamilyProfile(formData) {
  return request({
    url: '/api/family/profile',
    method: 'POST',
    data: formData
  });
}

function getBoundPatients() {
  return request({
    url: '/api/family/patients',
    method: 'GET'
  });
}

function getFamilyRiskPredict(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/risk/predict',
    method: 'GET',
    data: { patientId }
  });
}

function getFamilyRiskPredictHistory(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/risk/predict/history',
    method: 'GET',
    data: { patientId }
  });
}

function getFamilyRehabPlanCurrent(patientIdParam, planId) {
  const patientId = patientIdParam || getSelectedPatientId();
  const data = { patientId };
  if (planId) data.planId = planId;
  return request({
    url: '/api/family/patient/rehab-plan/current',
    method: 'GET',
    data
  });
}

function getFamilyRehabPlanHistory(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/rehab-plan/history',
    method: 'GET',
    data: { patientId }
  });
}

function getFamilyHeartTwinRealtime(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/heart-twin/realtime',
    method: 'GET',
    data: { patientId }
  });
}

function getFamilyHeartTwinForecast(patientIdParam) {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/heart-twin/forecast',
    method: 'GET',
    data: { patientId }
  });
}

function getFamilyIndicatorChange(patientIdParam, period = 'daily') {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/indicator/change',
    method: 'GET',
    data: { patientId, period }
  });
}

function getFamilyIndicatorChangeHistory(patientIdParam, period = 'daily') {
  const patientId = patientIdParam || getSelectedPatientId();
  return request({
    url: '/api/family/patient/indicator/change/history',
    method: 'GET',
    data: { patientId, period }
  });
}

function bindPatient(data) {
  return request({
    url: '/api/family/bind',
    method: 'POST',
    data
  });
}

function unbindPatient(patientId) {
  return request({
    url: '/api/family/unbind',
    method: 'POST',
    data: { patientId }
  });
}

export default {
  getDiet,
  getBehavior,
  getMedicine,
  getLiving,
  getOne,
  zhexian,
  getMyDischargeList,
  getMyRecoveryList,
  updateFamilyProfile,
  getBoundPatients,
  bindPatient,
  unbindPatient,
  getFamilyRiskPredict,
  getFamilyRiskPredictHistory,
  getFamilyRehabPlanCurrent,
  getFamilyRehabPlanHistory,
  getFamilyHeartTwinRealtime,
  getFamilyHeartTwinForecast,
  getFamilyIndicatorChange,
  getFamilyIndicatorChangeHistory
};
