import {
  request
} from '../utils/request';

// 获取页面数据
function findPage(data) {
  return request({
    url: '/recipe/page',
    method: 'GET',
    data: data
  })
}

function findOne(id) {
  return request({
    url: '/recipe/' + id,
    method: 'GET',
  })
}

function findAll() {
  return request({
    url: '/recipe/',
    method: 'GET',
  })
}

function findRand() {
  return request({
    url: '/recipe/rand',
    method: 'GET',
  })
}

// 新增或者更新
function saveRecipe(data) {
  return request({
    url: '/recipe',
    method: 'POST',
    data: data
  })
}

// 删除
function deleteRecipe(id) {
  return request({
    url: '/recipe/' + id,
    method: 'DELETE',
  })
}

// 删除
function deleteRecipeBatch(ids) {
  return request({
    url: '/del/batch',
    method: 'DELETE',
    data: ids
  })
}

function selectByIngredientId(data) {
  return request({
    url: '/recipe/ingredient',
    method: 'GET',
    data: data
  })
}

function selectByTagId(data) {
  return request({
    url: '/recipe/tag',
    method: 'GET',
    data: data
  })
}

function selectById(data) {
  return request({
    url: '/recipe/'+data.type,
    method: 'GET',
    data: data
  })
}

function getFile(id){
  return request({
    url: '/recipe/file/'+id,
    method: 'GET',
  })
}

function countRecipe(id){
  return request({
    url: '/recipe/count/'+id,
    method: 'GET',
  })
}
export default {
  findPage,
  findOne,
  findAll,
  deleteRecipe,
  deleteRecipeBatch,
  saveRecipe,
  selectByIngredientId,
  selectByTagId,
  selectById,
  getFile,
  findRand,
  countRecipe
}