// pages/living/living.js
import request from '../../api/requests'
import {formatTime,formatDate} from '../../utils/util'

const app = getApp(); 
Page({

  /**
   * 页面的初始数据
   */
  data: {
    isLogin: false, // 【新增】

    form: {
      patientId: null,
      date: formatDate(new Date()),
      // neededChange: null,
      // isImproved: null,
      // feel: null,
      // question: null
    },
    maxDate: new Date().getTime(),
    minDate: new Date().getTime()-2592000000,
    flag:0,
    show: false,
    checked:false,
    fileList: [],
  },

  onChangeRadio(event) {
    this.setData({
      'form.isImproved': event.detail,
    });
  },
  
  iconTip() {
    wx.showToast({
      title: '戒烟、限酒、久坐改变、减少熬夜、减少加班、调整情绪等',
      icon: 'none',
      duration: 2500
    })
  },

  onDisplay() {
    this.setData({ show: true });
  },
  onClose() {
    this.setData({ show: false });
  },
  onConfirm(event) {
    this.setData({
      show: false,
      'form.date': formatDate(event.detail),
    });
    this.load()
  },
  save: function () {
    if (!this.data.isLogin) { // 【新增】检查登录状态
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    console.log(this.data.form)
    request.addLiving(this.data.form).then((res) => {
        if(res.code === 200){
          wx.showToast({ title: '保存成功' });
      } else {
          wx.showToast({ title: res.msg || '保存失败', icon: 'none' });
      }
    })
  },
  load: function () {
    if (!this.data.form.patientId) {
      console.error("加载失败，patientId 为空！");
      return;
    }
    
    request.getLiving(this.data.form).then((res) => {
      console.log('生活方式记录查询结果:', res)
      if (!res || !res.rows || res.rows.length === 0) {
        this.setData({
          form: {
            ...this.data.form,
            neededChange: null,
            isImproved: null,
            feel: null,
            replay: null,
            question: null
          },
          flag: 0 // 标记为新增状态
        })
      } else {
        this.setData({
          form: res.rows[0],
          flag: 1
        })
      }
    })
  },
  onChangeNeededChange(e) {
    this.setData({
      'form.neededChange': e.detail
    })
  },
  onChangeFeel(e) {
    this.setData({
      'form.feel': e.detail
    })
  },
  onChangeReplay(e) {
    this.setData({
      'form.replay': e.detail
    })
  },
  onChangeQuestion(e) {
    this.setData({
      'form.question': e.detail
    })
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
    
    // 只用 patientId (Long) 来判断登录状态
    if (patientInfo && patientInfo.patientId) {
      
        this.setData({
          isLogin: true,
          'form.patientId': patientInfo.patientId, 
        });
        this.load();
      
    } else {
      // 未登录
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