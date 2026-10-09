import request from '@/utils/request'

// 查询医生管理列表
export function listDoctor(query) {
  return request({
    url: '/system/doctor/list',
    method: 'get',
    params: query
  })
}

// 查询医生管理详细
export function getDoctor(doctorId) {
  return request({
    url: '/system/doctor/' + doctorId,
    method: 'get'
  })
}

// 新增医生管理
export function addDoctor(data) {
  return request({
    url: '/system/doctor',
    method: 'post',
    data: data
  })
}

// 修改医生管理
export function updateDoctor(data) {
  return request({
    url: '/system/doctor',
    method: 'put',
    data: data
  })
}

// 删除医生管理
export function delDoctor(doctorId) {
  return request({
    url: '/system/doctor/' + doctorId,
    method: 'delete'
  })
}
