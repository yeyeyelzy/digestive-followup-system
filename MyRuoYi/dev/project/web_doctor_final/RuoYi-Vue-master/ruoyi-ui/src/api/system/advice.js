import request from '@/utils/request'

// 查询医嘱管理列表
export function listAdvice(query) {
  return request({
    url: '/system/advice/list',
    method: 'get',
    params: query
  })
}

// 查询医嘱管理详细
export function getAdvice(doctorsAdviceId) {
  return request({
    url: '/system/advice/' + doctorsAdviceId,
    method: 'get'
  })
}

// 新增医嘱管理
export function addAdvice(data) {
  return request({
    url: '/system/advice',
    method: 'post',
    data: data
  })
}

// 修改医嘱管理
export function updateAdvice(data) {
  return request({
    url: '/system/advice',
    method: 'put',
    data: data
  })
}

// 删除医嘱管理
export function delAdvice(doctorsAdviceId) {
  return request({
    url: '/system/advice/' + doctorsAdviceId,
    method: 'delete'
  })
}
