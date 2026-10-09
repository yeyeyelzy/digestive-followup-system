// app.js (最终正确版本)
import { getInfo } from '/api/user.js'; 

App({
  onLaunch: function () {
    // onLaunch 是小程序启动时唯一一次执行的生命周期
    console.log('App Launch');
    this.checkLoginStatus().catch(() => {});
  },

  // 一个权威的、统一的登录状态检查函数
  checkLoginStatus: function() {
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('token');

      if (token) {
        getInfo().then(res => {
          if (res.code === 200 && res.data) {
            console.log('app.js: Token有效，自动登录成功', res.data);
            this.setGlobalPatientInfo(res.data);
            resolve(res.data);
          } else {
            console.log('app.js: Token无效或过期，清除登录状态');
            this.clearGlobalPatientInfo();
            reject(res);
          }
        }).catch(err => {
          console.error('app.js: getInfo 请求失败', err);
          this.clearGlobalPatientInfo();
          reject(err);
        });
      } else {
        console.log('app.js: 本地无Token，判定为未登录');
        // 无 token 属于正常未登录状态，不作为异常抛出
        resolve(null);
      }
    });
  },

  // 【关键】一个统一的设置全局信息的方法
  setGlobalPatientInfo: function(info) {
    console.log('app.js: setGlobalPatientInfo 被调用, 传入的数据:', info);
    if (info) {
      const normalized = {
        ...info,
        patientId: info.patientId || info.familyId,
        patientName: info.patientName || info.familyName,
        avatarUrl: info.avatarUrl || info.avatar
      };
      this.globalData.patientInfo = normalized;
    } else {
      console.warn('app.js: 尝试设置一个空的 patientInfo');
    }
  },

  // 【关键】一个统一的清空全局信息的方法 (用于退出登录)
  clearGlobalPatientInfo: function() {
    console.log('app.js: clearGlobalPatientInfo 被调用，清除登录状态');
    this.globalData.patientInfo = null;
    wx.removeStorageSync('token');
  },

  // 【关键】globalData 的初始状态
  globalData: {
    patientInfo: null
  }
})

