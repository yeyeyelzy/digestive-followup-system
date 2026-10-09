import request from '@/utils/request'

// 查询随访记录管理列表
export function listUp(query) {
  return request({
    url: '/system/up/list',
    method: 'get',
    params: query
  })
}

// 查询随访记录管理详细
export function getUp(followUpId) {
  return request({
    url: '/system/up/' + followUpId,
    method: 'get'
  })
}

// 新增随访记录管理
export function addUp(data) {
  return request({
    url: '/system/up',
    method: 'post',
    data: data
  })
}

// 修改随访记录管理
export function updateUp(data) {
  return request({
    url: '/system/up',
    method: 'put',
    data: data
  })
}

// 删除随访记录管理
export function delUp(followUpId) {
  return request({
    url: '/system/up/' + followUpId,
    method: 'delete'
  })
}
