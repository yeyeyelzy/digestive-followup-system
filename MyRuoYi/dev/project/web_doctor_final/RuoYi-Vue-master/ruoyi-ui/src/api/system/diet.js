import request from '@/utils/request'

// 查询饮食日记管理列表
export function listDiet(query) {
  return request({
    url: '/system/diet/list',
    method: 'get',
    params: query
  })
}

// 查询饮食日记管理详细
export function getDiet(dietId) {
  return request({
    url: '/system/diet/' + dietId,
    method: 'get'
  })
}

// 新增饮食日记管理
export function addDiet(data) {
  return request({
    url: '/system/diet',
    method: 'post',
    data: data
  })
}

// 修改饮食日记管理
export function updateDiet(data) {
  return request({
    url: '/system/diet',
    method: 'put',
    data: data
  })
}

// 删除饮食日记管理
export function delDiet(dietId) {
  return request({
    url: '/system/diet/' + dietId,
    method: 'delete'
  })
}
