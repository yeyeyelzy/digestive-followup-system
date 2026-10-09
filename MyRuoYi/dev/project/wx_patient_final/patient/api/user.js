import {
  request
} from '../utils/request';

// 登录请求
export const login = (data) => {
  return request({
    url: '/api/patient/login',
    method: 'POST',
    data: data
  });
};

// 注册请求
export const register = (data) => {
  return request({
    url: '/api/patient/register',
    method: 'POST',
    data: data
  });
};

export const getInfo = () => {
  return request({
    url: '/api/patient/getInfo', 
    method: 'GET'
  });
};

// 修改密码
function password(params) {
  return request({
    url: '/user/password',
    method: 'POST',
    data: params
  })
}

function findOne(id) {
  return request({
    url: '/user/' + id,
    method: 'GET',
  })
}


export default {
  login,
  register,
  password,
  findOne,
}