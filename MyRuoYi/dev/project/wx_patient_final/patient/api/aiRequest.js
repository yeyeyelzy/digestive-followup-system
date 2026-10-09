const aiBaseURL = 'http://127.0.0.1:8081';

function getAIAnswer(question) {
  wx.showLoading({
    title: "思考中...",
    mask: true
  });

  return new Promise((resolve, reject) => {
    wx.request({
      url: aiBaseURL + '/get_answer',
      method: 'GET',
      data: {
        questions: question
      },
      timeout: 15000,
      success: (res) => {
        // 【核心修改】检查返回的数据是否是字符串
        if (res.statusCode === 200 && typeof res.data === 'string') {
          // 如果是字符串，直接将它 resolve 出去
          resolve(res.data);
        } else {
          // 如果不是字符串或状态码不为200，视为失败
          reject(res);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: 'AI服务连接失败',
          icon: 'none'
        });
        reject(err);
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  });
}

module.exports = {
  getAIAnswer
};