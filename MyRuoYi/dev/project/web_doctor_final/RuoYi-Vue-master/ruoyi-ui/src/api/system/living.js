import request from '@/utils/request'

// 查询生活方式日记管理列表
export function listLiving(query) {
  return request({
    url: '/system/living/list',
    method: 'get',
    params: query
  })
}

// 查询生活方式日记管理详细
export function getLiving(livingId) {
  return request({
    url: '/system/living/' + livingId,
    method: 'get'
  })
}

// 新增生活方式日记管理
export function addLiving(data) {
  return request({
    url: '/system/living',
    method: 'post',
    data: data
  })
}

// 修改生活方式日记管理
export function updateLiving(data) {
  return request({
    url: '/system/living',
    method: 'put',
    data: data
  })
}

// 删除生活方式日记管理
export function delLiving(livingId) {
  return request({
    url: '/system/living/' + livingId,
    method: 'delete'
  })
}
