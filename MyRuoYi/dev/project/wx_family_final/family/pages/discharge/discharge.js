import request from '../../api/requests'
const app = getApp();
Page({

  /**
   * 页面的初始数据
   */
  data: {
    isLogin: false,
    discharges: [], 
    advice: {}, 
    show: false
  },

  load: function () {
    const patientId = Number(wx.getStorageSync('selectedPatientId'));
    request.getMyDischargeList(patientId).then((res) => {
      if (res.code === 200) {
        this.setData({
          discharges: res.data, 
        })
      } else {
        console.error("加载出院记录失败:", res.msg);
        wx.showToast({ title: res.msg || '加载失败', icon: 'none' });
      }
    }).catch(err => {
      console.error("请求出院记录接口异常:", err);
      wx.showToast({ title: '网络异常', icon: 'none' });
    })
  },

  getAdvice(e) {
    let id = e.currentTarget.dataset.adviceid; // 获取参数id
    if (!id) return;
    console.log(id)
    request.getOne(id, 'advice').then((res) => {
      this.setData({
        advice: res.data,
        show:true
      })
    })

  },
  onClickHide() {
    this.setData({ show: false });
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
    const selectedPatientId = wx.getStorageSync('selectedPatientId');

    if (patientInfo && patientInfo.patientId && selectedPatientId) {
        this.setData({
          isLogin: true,
        });
        this.load();
    } else {
      wx.showToast({ title: '请先绑定并选择患者', icon: 'none', duration: 1500 });
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