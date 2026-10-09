import {
  request
} from '../utils/request';

function upload(params) {
  return request({
    url : '/file/upload',
    method : 'POST',
    data : params
  })
}

function download(id) {
  return request({
    url : '/file/' + id,
    method : 'GET'
  })
}

export default {
  upload,
  download,
}