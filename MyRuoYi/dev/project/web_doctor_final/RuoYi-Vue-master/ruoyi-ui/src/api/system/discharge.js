import request from '@/utils/request'

// 查询出院小结管理列表
export function listDischarge(query) {
  return request({
    url: '/system/discharge/list',
    method: 'get',
    params: query
  })
}

// 查询出院小结管理详细
export function getDischarge(admissionNumber) {
  return request({
    url: '/system/discharge/' + admissionNumber,
    method: 'get'
  })
}

// 新增出院小结管理
export function addDischarge(data) {
  return request({
    url: '/system/discharge',
    method: 'post',
    data: data
  })
}

// 修改出院小结管理
export function updateDischarge(data) {
  return request({
    url: '/system/discharge',
    method: 'put',
    data: data
  })
}

// 删除出院小结管理
export function delDischarge(admissionNumber) {
  return request({
    url: '/system/discharge/' + admissionNumber,
    method: 'delete'
  })
}
