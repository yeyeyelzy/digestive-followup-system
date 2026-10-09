// 记录同时发送异步请求数量
let ajaxTimes = 0;

export const request = (params) => {
  ajaxTimes++;
  // 显示加载中
  wx.showLoading({
    title: "加载中",
  });

  // 定义公共URL
  // baseUrl: https://api-hmugo-web.itheima.net/api/public/v1/
  const baseUrl = "https://api-hmugo-web.itheima.net/api/public/v1/";
  return new Promise((resolve, reject) => {
    wx.request({
      ...params,
      url: baseUrl + params.url,
      success: (result) => {
        resolve(result.data.message);
      },
      fail: (err) => {
        reject(err);
      },
      complete: () => {
        ajaxTimes--;
        if (ajaxTimes === 0) {
          // 关闭加载中
          wx.hideLoading();
        }
      },
    });
  });
};
