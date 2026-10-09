import {
  request
} from '../utils/request';

// demo
function getTest(data) {
  return request({
    url: '/system/list',
    method: 'GET',
    data: data
  })
}

function addTest(data) {
  return request({
    url: '/system/',
    method: 'POST',
    data: data
  })
}

// 患者信息
function getPatient(patientId) {
  return request({
    url: '/system/patient/' + patientId,
    method: 'GET',
  })
}

function getFlag(patientId) {
  return request({
    url: '/system/medicine/getFlag',
    method: 'GET',
    data: {
      patientName: patientId,
    }
  })
}


// 饮食管理
function getDiet(data) {
  return request({
    url: '/system/diet/my-list',
    method: 'GET',
    data: data
  })
}

function addDiet(data) {
  return request({
    url: '/system/diet',
    method: 'POST',
    data: data
  })
}

// 行为管理
function getBehavior(data) {
  return request({
    url: '/system/behavior/my-list',
    method: 'GET',
    data: data
  })
}

function addBehavior(data) {
  return request({
    url: '/system/behavior',
    method: 'POST',
    data: data
  })
}

// 服药管理
function getMedicine(data) {
  return request({
    url: '/system/medicine/my-list',
    method: 'GET',
    data: data
  })
}

function addMedicine(data) {
  return request({
    url: '/system/medicine',
    method: 'POST',
    data: data
  })
}

// 生活方式管理
function getLiving(data) {
  return request({
    url: '/system/living/my-list',
    method: 'GET',
    data: data
  })
}

function addLiving(data) {
  return request({
    url: '/system/living',
    method: 'POST',
    data: data
  })
}

// 聊天管理
function getChatContent(data) {
  return request({
    url: '/system/chat/list',
    method: 'GET',
    data: data
  })
}

function chat(data) {
  return request({
    url: '/system/chat',
    method: 'POST',
    data: data
  })
}

function get(data, url) {
  return request({
    url: '/system/' + url + '/list',
    method: 'GET',
    data: data
  })
}

function getOne(id, url) {
  return request({
    url: '/system/' + url + '/' + id,
    method: 'GET',
  })
}

function zhexian(id) {
  return request({
    url: '/system/recovery/zhexian/' + id,
    method: 'get'
  })}

function getPatientRiskPredict(patientId) {
  return request({
    url: '/system/risk/predict',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getPatientRiskPredictHistory(patientId) {
  return request({
    url: '/system/risk/predict/history',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getPatientRehabPlanCurrent(patientId, planId) {
  const data = {}
  if (patientId) data.patientId = patientId
  if (planId) data.planId = planId
  return request({
    url: '/api/patient/rehab-plan/current',
    method: 'GET',
    data
  })
}

function getPatientRehabPlanHistory(patientId) {
  return request({
    url: '/api/patient/rehab-plan/history',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getHeartTwinRealtime(patientId) {
  return request({
    url: '/system/heart-twin/realtime',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getHeartTwinForecast(patientId) {
  return request({
    url: '/system/heart-twin/forecast',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getRecoveryAchievement(patientId) {
  return request({
    url: '/system/recovery-achievement/current',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getPatientIndicatorChange(patientId, period = 'daily') {
  const data = { period }
  if (patientId) data.patientId = patientId
  return request({
    url: '/system/indicator/change',
    method: 'GET',
    data
  })
}

function getPatientIndicatorChangeHistory(patientId, period = 'daily') {
  const data = { period }
  if (patientId) data.patientId = patientId
  return request({
    url: '/system/indicator/change/history',
    method: 'GET',
    data
  })
}

function getPatientHealthReportDaily(patientId) {
  return request({
    url: '/system/health-report/daily',
    method: 'GET',
    data: patientId ? { patientId } : undefined
  })
}

function getPatientHealthReportWeekly(patientId) {
  return request({
    url: '/system/health-report/weekly',
    method: 'GET',
    data: patientId ? { patientId } : undefined,
    timeout: 120000
  })
}

function getPatientHealthReportMonthly(patientId) {
  return request({
    url: '/system/health-report/monthly',
    method: 'GET',
    data: patientId ? { patientId } : undefined,
    timeout: 120000
  })
}

  // 【新增】获取个人出院小结列表的专用函数
function getMyDischargeList() {
  return request({
    url: '/system/discharge/my-list',
    method: 'GET'
  })
}

  // 【新增】获取个人复查记录列表的专用函数
  function getMyRecoveryList() {
    return request({
      url: '/system/recovery/my-list',
      method: 'GET'
    })
  }

  // 【新增】获取所有普通用户列表
function getAllNormalUsers() {
  return request({
    url: '/app/user/listAllNormal', // 调用我们新的 API
    method: 'GET'
  })
}

const updatePatientProfile = (formData) => {
  return request({
      url: '/system/patient/profile',
      method: 'PUT',
      data: formData,
      header: {
          'Content-Type': 'application/json' // 明确设置 Content-Type
      }
  });
};

export default {
  getDiet,
  addDiet,
  getBehavior,
  addBehavior,
  getMedicine,
  addMedicine,
  getLiving,
  addLiving,
  getChatContent,
  chat,
  getPatient,
  getFlag,
  get,
  getOne,
  zhexian,
  getPatientRiskPredict,
  getPatientRiskPredictHistory,
  getPatientRehabPlanCurrent,
  getPatientRehabPlanHistory,
  getHeartTwinRealtime,
  getHeartTwinForecast,
  getRecoveryAchievement,
  getPatientIndicatorChange,
  getPatientIndicatorChangeHistory,
  getPatientHealthReportDaily,
  getPatientHealthReportWeekly,
  getPatientHealthReportMonthly,
  getMyDischargeList,
  getMyRecoveryList,
  getAllNormalUsers,
  updatePatientProfile
}
