// pages/register/register.js
import { register } from '../../api/user.js';

Page({
  /**
   * 页面的初始数据
   */
  data: {
    familyName: '',
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    loading: false // 用于防止重复点击注册按钮
  },

  /**
   * 输入框内容改变时触发，更新data中的数据
   * @param {Object} e 事件对象
   */
  onInput(e) {
    // 使用 dataset.field 来动态设置 data 中的值
    const field = e.currentTarget.dataset.field;
    this.setData({
      [field]: e.detail.value
    });
  },

  /**
   * 处理注册按钮点击事件
   */
  handleRegister() {
    // 如果正在加载中，则直接返回，防止用户重复提交
    if (this.data.loading) {
      return;
    }

    const { familyName, phoneNumber, password, confirmPassword } = this.data;

    // --- 补充完整的表单校验逻辑 ---
    if (!familyName.trim()) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      });
      return;
    }

    if (!/^\d{11}$/.test(phoneNumber)) {
      wx.showToast({
        title: '请输入11位手机号',
        icon: 'none'
      });
      return;
    }
    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }
    if (password.length < 6) {
      wx.showToast({
        title: '密码长度不能少于6位',
        icon: 'none'
      });
      return;
    }
    if (password !== confirmPassword) {
      wx.showToast({
        title: '两次输入的密码不一致',
        icon: 'none'
      });
      return;
    }
    // --- 校验结束 ---

    // 设置加载状态，显示加载提示
    this.setData({ loading: true });
    wx.showLoading({
      title: '注册中...',
    });

    register({ familyName, phoneNumber, password })
      .then(res => {
        // 假设 res 的结构是 { code: 200, msg: '操作成功' }
        // 注意：这里的 res 是 axios 拦截器处理后的，如果你的API返回直接是业务数据，用 res.code
        // 如果是原始的 axios 返回，需要用 res.data.code
        if (res.code === 200) {
          wx.showToast({
            title: '注册成功！',
            icon: 'success'
          });
          // 注册成功后，延时1.5秒引导用户返回登录页
          setTimeout(() => {
            wx.navigateBack(); // 返回上一页（通常是登录页）
          }, 1500);
        } else {
          // 显示后端返回的错误信息，如“用户名已存在”
          wx.showToast({
            title: res.msg || '注册失败，请稍后再试',
            icon: 'none'
          });
        }
      })
      .catch(err => {
        // 处理网络错误、超时与后端业务错误
        const msg = (err && (err.msg || err.errMsg)) || '注册失败，请稍后重试';
        wx.showToast({
          title: msg.length > 18 ? '注册失败，请检查网络' : msg,
          icon: 'none'
        });
        console.error('注册失败:', err);
      })
      .finally(() => {
        // 无论成功失败，都关闭加载提示并恢复按钮状态
        wx.hideLoading();
        this.setData({ loading: false });
      });
  }
});
