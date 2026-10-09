import request from '@/utils/request'

// 查询行为日记管理列表
export function listBehavior(query) {
  return request({
    url: '/system/behavior/list',
    method: 'get',
    params: query
  })
}

// 查询行为日记管理详细
export function getBehavior(behaviorId) {
  return request({
    url: '/system/behavior/' + behaviorId,
    method: 'get'
  })
}

// 新增行为日记管理
export function addBehavior(data) {
  return request({
    url: '/system/behavior',
    method: 'post',
    data: data
  })
}

// 修改行为日记管理
export function updateBehavior(data) {
  return request({
    url: '/system/behavior',
    method: 'put',
    data: data
  })
}

// 删除行为日记管理
export function delBehavior(behaviorId) {
  return request({
    url: '/system/behavior/' + behaviorId,
    method: 'delete'
  })
}
