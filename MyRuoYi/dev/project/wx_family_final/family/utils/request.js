const baseURLs = ['http://127.0.0.1:8080', 'http://localhost:8080'];

/**
 *  使用Promise 对wx.request进行封装
 * @param {object} params - 请求参数对象，包含 method, url, data, header
 */
function request(params) {
  wx.showLoading({
    title: "加载中",
    mask: true
  });

  return new Promise(function (resolve, reject) {
    // 在每次请求前，从本地存储动态获取Token
    const token = wx.getStorageSync('token');

    // 动态构建请求头
    const header = {
      // 默认设置为 JSON 类型，但具体API可以覆盖
      'Content-Type': 'application/json',
      ...params.header 
    };

    // 如果Token存在，就把它加到请求头里
    if (token) {
      header['Authorization'] = 'Bearer ' + token;
    }

    const tryRequest = (hostIndex) => {
      wx.request({
        url: baseURLs[hostIndex] + params.url,
        method: params.method,
        data: params.data, // 【注意】这里直接传递原始数据
        header: header,
        timeout: 15000,
        success: (res) => {
          // 我们只关心 HTTP 状态码为 200 的情况
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            // 对于非 200 的情况，都视为请求失败
            wx.showToast({
              title: `请求错误 ${res.statusCode}`,
              icon: 'none'
            });
            reject({
              statusCode: res.statusCode,
              msg: (res.data && (res.data.msg || res.data.message)) || `HTTP ${res.statusCode}`,
              data: res.data
            });
          }
        },
        fail: (err) => {
          const failMsg = (err && err.errMsg) ? err.errMsg : '网络连接失败';
          const isTimeout = failMsg.indexOf('timeout') >= 0;
          if (isTimeout && hostIndex + 1 < baseURLs.length) {
            tryRequest(hostIndex + 1);
            return;
          }
          wx.showToast({ title: '网络请求失败', icon: 'none' });
          reject({
            msg: failMsg,
            errMsg: failMsg,
            detail: err
          });
        },
        // 无论成功失败，都隐藏 Loading
        complete: () => {
          wx.hideLoading();
        }
      });
    };

    tryRequest(0);
  });
}

// 导出
module.exports = {
  request
};

