import request from '@/utils/request'

// 查询聊天记录管理列表
export function listChat(query) {
  return request({
    url: '/system/chat/list',
    method: 'get',
    params: query
  })
}

// 查询聊天记录管理详细
export function getChat(id) {
  return request({
    url: '/system/chat/' + id,
    method: 'get'
  })
}

// 新增聊天记录管理
export function addChat(data) {
  return request({
    url: '/system/chat',
    method: 'post',
    data: data
  })
}

// 修改聊天记录管理
export function updateChat(data) {
  return request({
    url: '/system/chat',
    method: 'put',
    data: data
  })
}

// 删除聊天记录管理
export function delChat(id) {
  return request({
    url: '/system/chat/' + id,
    method: 'delete'
  })
}
