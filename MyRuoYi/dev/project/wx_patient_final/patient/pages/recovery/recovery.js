import request from '../../api/requests'

const app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    isLogin: false,
    recoveries: [],  
    show: false,
    info: -1,
    loading: false
  },

  load: function () {
    this.setData({ loading: true });
    request.getMyRecoveryList().then((res) => {
      if (res.code === 200) {
        const list = Array.isArray(res.data) ? res.data : (Array.isArray(res.rows) ? res.rows : []);
        this.setData({
          recoveries: list,
        })
      } else {
        return this.loadByPatientId();
      }
    }).catch(err => {
      console.error("请求出院记录接口异常:", err);
      return this.loadByPatientId();
    }).finally(() => {
      this.setData({ loading: false });
    })
  },

  loadByPatientId() {
    const patientInfo = app.globalData.patientInfo || {};
    if (!patientInfo.patientId) {
      wx.showToast({ title: '加载失败', icon: 'none' });
      return Promise.resolve();
    }
    return request.get({ patientId: patientInfo.patientId }, 'recovery').then((res) => {
      if (res.code === 200) {
        const list = Array.isArray(res.rows) ? res.rows : (Array.isArray(res.data) ? res.data : []);
        this.setData({ recoveries: list });
      } else {
        wx.showToast({ title: res.msg || '加载失败', icon: 'none' });
      }
    }).catch(() => {
      wx.showToast({ title: '网络异常', icon: 'none' });
    });
  },

  getInfo(e) {
    this.setData({
      info: e.currentTarget.dataset.info,
      show: true
    })
  },
  onClickHide() {
    this.setData({
      show: false,
      info: -1
    });
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    const patientInfo = app.globalData.patientInfo;
    
    if (patientInfo && patientInfo.patientId) {
        this.setData({
          isLogin: true,
          // 【修改】不再需要设置 form.patientId
        });
        this.load();
    } else {
      wx.showToast({ title: '请先登录', icon: 'none', duration: 1500 });
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/login/login', });
      }, 1500);
    }
  },
  
  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  }
})