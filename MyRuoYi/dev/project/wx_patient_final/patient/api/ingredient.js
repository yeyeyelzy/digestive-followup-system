import {
  request
} from '../utils/request';

// 获取页面数据
function findPage(params) {
  return request({
    url: '/ingredient/page',
    method: 'GET',
    params: params
  })
}

function findOne(id) {
  return request({
    url: '/ingredient/' + id,
    method: 'GET',
  })
}

function findAll() {
  return request({
    url: '/ingredient/',
    method: 'GET',
  })
}


// 新增或者更新
function saveIngredient(params) {
  return request({
    url: '/ingredient/save',
    method: 'POST',
    data: params
  })
}

// 删除
function deleteIngredient(id) {
  return request({
    url: '/ingredient/' + id,
    method: 'DELETE',
  })
}

// 删除
function deleteIngredientBatch(ids) {
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
  deleteIngredient,
  deleteIngredientBatch,
  saveIngredient,
}