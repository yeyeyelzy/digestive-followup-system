import request from '@/utils/request'


    
    //获取图表数据，并显示
export  function  selectStatisics(recoveryName){
        return request({
           //服务端接口地址，因为我后端接收的为3个参数，所以要从页面传来的对象里取出来 
            url: '/system/recovery/showData' + recoveryName,
            method:'get'
        })
    }   





// 查询复查管理列表
export function listRecovery(query) {
  return request({
    url: '/system/recovery/list',
    method: 'get',
    params: query
  })
}

// 查询复查管理详细
export function getRecovery(recoveryId) {
  return request({
    url: '/system/recovery/' + recoveryId,
    method: 'get'
  })
}

// 新增复查管理
export function addRecovery(data) {
  return request({
    url: '/system/recovery',
    method: 'post',
    data: data
  })
}

// 修改复查管理
export function updateRecovery(data) {
  return request({
    url: '/system/recovery',
    method: 'put',
    data: data
  })
}

// 删除复查管理
export function delRecovery(recoveryId) {
  return request({
    url: '/system/recovery/' + recoveryId,
    method: 'delete'
  })
}


export function zhexian(id) {
  return request({
    url: '/system/recovery/zhexian/' + id,
    method: 'get'
  })
}