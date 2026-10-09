// pages/behavior/behavior.js
import request from '../../api/requests'
import {
  formatTime,
  formatDate
} from '../../utils/util'

const app = getApp(); 
Page({

  /**
   * 页面的初始数据
   */
  data: {
    isLogin: false, // 【新增】
  
    form: {
      patientId: null, // 【修改】初始化为 null
      date: formatDate(new Date()),
      // frequency: null,
      // strength: null,
      // duration: null,
      // type: null,
      // feel: null,
      // replay: null,
      // question: null
    },
    maxDate: new Date().getTime(),
    minDate: new Date().getTime() - 2592000000,
    flag: 0,
    show: false,
    stepList: [],
    stepNum: 0
  },
  onDragFrequency(event) {
    this.setData({
      'form.frequency': event.detail.value,
    });
  },
  onChangeFrequency(event) {
    this.setData({
      'form.frequency': event.detail,
    });
  },
  onDragStrength(event) {
    this.setData({
      'form.strength': event.detail.value,
    });
  },
  onChangeStrength(event) {
    this.setData({
      'form.strength': event.detail,
    });
  },
  iconTip() {
    wx.showToast({
      title: '有氧运动：步行、跑步、骑车、爬楼、椭圆机等；\r\n抗阻运动：弹力绳、杠铃、哑铃等；\r\n柔韧性、综合性运动：太极、瑜伽、拉伸等',
      icon: 'none',
      duration: 5000
    })
  },
  onChangeType(event) {
    this.setData({
      'form.type': event.detail,
    });
  },
  onDisplay() {
    this.setData({
      show: true
    });
  },
  onClose() {
    this.setData({
      show: false
    });
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
    request.addBehavior(this.data.form).then((res) => {
        if(res.code === 200){
          wx.showToast({ title: '保存成功' });
      } else {
          wx.showToast({ title: res.msg || '保存失败', icon: 'none' });
      }
    })
  },
  load: function () {
    request.getBehavior(this.data.form).then((res) => {
      if (res.total == 0) { this.setData({
        form:{},
        'form.date':this.data.form.date
      })} else {
        this.setData({
          form: res.rows[0],
          flag: 1
        })
      }
    })
  },
  onChangeDuration(e) {
    this.setData({
      'form.duration': e.detail
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
  getStepNum() {
    let diff = Math.ceil((new Date().getTime() - new Date(this.data.form.date).getTime())/(1000*60*60*24))
    this.setData({
      stepNum: this.data.stepList[30 - diff].step,
    })
    console.log(this.data.stepNum)
    this.setData({
      'form.feel': '今天行走' + this.data.stepNum + '步，' + (this.data.form.feel==null?"":this.data.form.feel),
      // 'form.strength': Math.round(this.data.stepNum / 5000),
    })

  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    // 【修改】onLoad 不再 load()，主要逻辑移到 onShow
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

  },
  async getWeRunData() {
    let {
      cloudID
    } = await wx.getWeRunData().catch((error) => error);
    if (cloudID) {
      let {
        result
      } = await this.step(cloudID);
      this.setData({
        stepList: result.openData.data.stepInfoList
      })
      console.log(this.data.stepList)
    }
  },
  async step(cloudID) {
    return wx.cloud.callFunction({
      name: "step",
      data: {
        openData: wx.cloud.CloudID(cloudID),
      },
    });
  },
})