import {
  request
} from '../utils/request';

// 获取页面数据
function findPage(params) {
  return request({
    url: '/tag/page',
    method: 'GET',
    params: params
  })
}

function findOne(id) {
  return request({
    url: '/tag/' + id,
    method: 'GET',
  })
}

function findAll() {
  return request({
    url: '/tag/',
    method: 'GET',
  })
}


// 新增或者更新
function saveTag(params) {
  return request({
    url: '/tag/save',
    method: 'POST',
    data: params
  })
}

// 删除
function deleteTag(id) {
  return request({
    url: '/tag/' + id,
    method: 'DELETE',
  })
}

// 删除
function deleteTagBatch(ids) {
  return request({
    url: '/del/batch',
    method: 'DELETE',
    data: ids
  })
}

export default {
  findPage,
  findOne,
  findAll,
  deleteTag,
  deleteTagBatch,
  saveTag,
}