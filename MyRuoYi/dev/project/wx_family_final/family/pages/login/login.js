// pages/login/login.js
import { login, getInfo } from '../../api/user.js'; // 引入 API 请求

Page({
  data: {
    patientName: '',
    password: ''
  },

  goMyPage() {
    wx.reLaunch({
      url: '/pages/my/index',
      success: () => {
        console.log('登录后跳转 my 成功(reLaunch)');
      },
      fail: (err) => {
        console.error('reLaunch 跳转 my 失败，尝试 redirectTo', err);
        wx.redirectTo({
          url: '/pages/my/index',
          success: () => {
            console.log('登录后跳转 my 成功(redirectTo)');
          },
          fail: (err2) => {
            console.error('redirectTo 跳转 my 失败', err2);
            wx.showToast({ title: '跳转失败，请重试', icon: 'none' });
          }
        });
      }
    });
  },

  onInput(e) {
    this.setData({
      [e.currentTarget.dataset.field]: e.detail.value
    });
  },

  onInputChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = (e && e.detail) ? (e.detail.value !== undefined ? e.detail.value : e.detail) : '';
    this.setData({ [field]: value });
  },

  handleLogin() {
    const { patientName, password } = this.data;
    if (!patientName || !password) {
      wx.showToast({ title: '请输入用户名和密码', icon: 'none' });
      return;
    }

    // 显示加载提示
    wx.showLoading({ title: '登录中...' });

    login({ username: patientName, password: password }).then(res => {
      if (res.code === 200) {
        // 登录第一步成功：获取并存储Token
        const token = res.data.token;
        wx.setStorageSync('token', token);
        console.log("获取到Token:", token);

        // 【核心修改】登录第二步：使用刚获取的Token去获取用户信息
        return getInfo(); // 返回 getInfo() 的 Promise，形成链式调用
      } else {
        // 如果登录第一步就失败了，直接拒绝Promise
        return Promise.reject(res);
      }
    }).then(infoRes => {
      // getInfo() 成功后的回调
      if (infoRes.code === 200) {
        const patientInfo = infoRes.data; // 这就是完整的用户信息
        console.log("获取到用户信息:", patientInfo);
        console.log("【login.js】准备将用户信息存入全局:", patientInfo);

        // 【核心修改】登录第三步：将用户信息存入全局状态
        const app = getApp();
        if (app && app.setGlobalPatientInfo) {
           app.setGlobalPatientInfo(patientInfo);
           console.log("【login.js】调用setGlobalPatientInfo后, app.globalData.patientInfo 的值为:", app.globalData.patientInfo);
        } else {
           // 兼容处理，如果 app.js 没那个方法
           app.globalData.patientInfo = patientInfo;
        }

        // 所有操作完成，关闭加载提示
        wx.hideLoading();
        wx.showToast({ title: '登录成功', icon: 'success', duration: 600 });
        this.goMyPage();

      } else {
        return Promise.reject(infoRes);
      }
    }).catch(err => {
      // 统一的错误处理
      wx.hideLoading(); // 确保关闭加载提示
      console.error("登录或获取信息失败:", err);
      wx.showToast({
        title: err.msg || '操作失败，请稍后再试',
        icon: 'none'
      });
    });
  },

  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register' // 跳转到注册页面
    });
  }
});
