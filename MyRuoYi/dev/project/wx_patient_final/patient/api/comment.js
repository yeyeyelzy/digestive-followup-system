import {
  request
} from '../utils/request';

// 获取页面数据
function findPage(data) {
  return request({
    url: '/comment/page',
    method: 'GET',
    data: data
  })
}

function findTree(id) {
  return request({
    url: '/comment/tree/' + id,
    method: 'GET',
  })
}

function findAll() {
  return request({
    url: '/comment/',
    method: 'GET',
  })
}


// 新增或者更新
function saveComment(data) {
  return request({
    url: '/comment/',
    method: 'POST',
    data: data
  })
}

// 删除
function deleteComment(id) {
  return request({
    url: '/comment/' + id,
    method: 'DELETE',
  })
}

// 删除
function deleteCommentBatch(ids) {
  return request({
    url: '/del/batch',
    method: 'DELETE',
    data: ids
  })
}


function findNotice(id) {
  return request({
    url: '/notice/get/' + id,
    method: 'GET',
  })
}

function readNotice(id) {
  return request({
    url: '/notice/read/' + id,
    method: 'Post',
  })
}

function addNotice(data) {
  return request({
    url: '/notice/save',
    method: 'POST',
    data: data
  })
}

function countNotice(id) {
  return request({
    url: '/notice/count/' + id,
    method: 'GET',
  })
}

//收藏
function col(data) {
  return request({
    url: '/collected',
    method: 'POST',
    data: data
  })
}

function findColPage(id) {
  return request({
    url: '/collected/get/' + id,
    method: 'GET',
  })
}

function countCol(id) {
  return request({
    url: '/collected/count/u/' + id,
    method: 'GET',
  })
}

function countColR(id) {
  return request({
    url: '/collected/count/r/' + id,
    method: 'GET',
  })
}
//点赞
function like(data) {
  return request({
    url: '/liked',
    method: 'POST',
    data: data
  })
}

function findLikePage(id) {
  return request({
    url: '/liked/get/' + id,
    method: 'GET',
  })
}

function countLike(id) {
  return request({
    url: '/liked/count/u/' + id,
    method: 'GET',
  })
}

function countLikeR(id) {
  return request({
    url: '/liked/count/r/' + id,
    method: 'GET',
  })
}
function isCol(data) {
  return request({
    url: '/collected/is',
    method: 'GET',
    data:data
  })
}
function isLike(data) {
  return request({
    url: '/liked/is',
    method: 'GET',
    data:data
  })
}
function delNocite(id){
  return request({
    url:'/notice/'+id,
    method:'DELETE'
  })
}
function delCollection(id){
  return request({
    url:'/collected/'+id,
    method:'DELETE'
  })
}
function delPublished(id){
  return request({
    url:'/recipe/'+id,
    method:'DELETE'
  })
}
export default {
  delNocite,
  delCollection,
  delPublished,
  findPage,
  findTree,
  findAll,
  deleteComment,
  deleteCommentBatch,
  saveComment,
  findNotice,
  addNotice,
  countNotice,
  readNotice,
  col,
  countCol,
  findColPage,
  countColR,
  like,
  countLike,
  findLikePage,
  countLikeR,
  isCol,
  isLike
}