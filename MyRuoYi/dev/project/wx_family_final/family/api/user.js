import {
  request
} from '../utils/request';

// 登录请求
export const login = (data) => {
  return request({
    url: '/api/family/login',
    method: 'POST',
    data: data
  });
};

// 注册请求
export const register = (data) => {
  return request({
    url: '/api/family/register',
    method: 'POST',
    data: data
  });
};

export const getInfo = () => {
  return request({
    url: '/api/family/getInfo', 
    method: 'GET'
  });
};

export const updateInfo = (data) => {
  return request({
    url: '/api/family/profile',
    method: 'POST',
    data
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
  getInfo,
  updateInfo,
  password,
  findOne,
}