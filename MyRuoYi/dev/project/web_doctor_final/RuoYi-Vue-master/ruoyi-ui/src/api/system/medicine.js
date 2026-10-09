import request from '@/utils/request'

// 查询服药日记管理列表
export function listMedicine(query) {
  return request({
    url: '/system/medicine/list',
    method: 'get',
    params: query
  })
}

// 查询服药日记管理详细
export function getMedicine(medicineId) {
  return request({
    url: '/system/medicine/' + medicineId,
    method: 'get'
  })
}

// 新增服药日记管理
export function addMedicine(data) {
  return request({
    url: '/system/medicine',
    method: 'post',
    data: data
  })
}

// 修改服药日记管理
export function updateMedicine(data) {
  return request({
    url: '/system/medicine',
    method: 'put',
    data: data
  })
}

// 删除服药日记管理
export function delMedicine(medicineId) {
  return request({
    url: '/system/medicine/' + medicineId,
    method: 'delete'
  })
}
