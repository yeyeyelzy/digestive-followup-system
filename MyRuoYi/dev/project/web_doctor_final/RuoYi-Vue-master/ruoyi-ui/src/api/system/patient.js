import request from '@/utils/request'

// 查询患者管理列表
export function listPatient(query) {
  return request({
    url: '/system/patient/list',
    method: 'get',
    params: query
  })
}

// 查询患者管理详细
export function getPatient(patientId) {
  return request({
    url: '/system/patient/' + patientId,
    method: 'get'
  })
}

// 新增患者管理
export function addPatient(data) {
  return request({
    url: '/system/patient',
    method: 'post',
    data: data
  })
}

// 修改患者管理
export function updatePatient(data) {
  return request({
    url: '/system/patient',
    method: 'put',
    data: data
  })
}

// 删除患者管理
export function delPatient(patientId) {
  return request({
    url: '/system/patient/' + patientId,
    method: 'delete'
  })
}
