// pages/science/science.js
import Dialog from '../../miniprogram_npm/@vant/weapp/dialog/dialog';
import request from '../../api/requests'

Page({

  /**
   * 页面的初始数据
   */
  data: {
    files: [{
        name: '心肌梗死患者住院期间注意事项（沈珑）.pdf',
        type: 'pdf',
        size: 16214,
        url: ''
      },
      {
        name: '戒烟.pdf',
        type: 'pdf',
        size: 7161,
        url: ''
      },
      {
        name: '药物宣教.pptx',
        type: 'pptx',
        size: 19656,
        url: ''
      },
      {
        name: '心血管患者饮食指导-上海交通大学医学院附属仁济医院-张晨、陈晓涵、严佳丽、许莉.mp4',
        type: 'mp4',
        size: 246577,
        url: ''
      },
      {
        name: 'Meet METs—邂逅梅脱-CCU 陈晓涵、许莉.pdf',
        type: 'pdf',
        size: 658,
        url: ''
      },


    ],
    recipes: [],
    src: '',
  },

  doit(e) {
    let index = e.currentTarget.dataset.id;
    console.log(this.data.files[index]);
    let that = this;
    let type = this.data.files[index].type;
    let fileName = this.data.files[index].name;
    let url = 'http://localhost:8080/system/files/' + encodeURIComponent(fileName);

    if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf'].indexOf(type) != -1) {
      wx.downloadFile({
        url: url,
        success(res) {
          console.log(res)
          let data = res.tempFilePath;
          wx.openDocument({
            filePath: data,
            fileType: that.data.files[index].type,
            showMenu: true //表示右上角是否有转发按钮
          })
        }
      })
    } else if (type == 'mp4') {
      this.setData({
        src: url,
      })
      Dialog.alert({
        confirmButtonText: '了解！',
      });
    }

  },
  close() {
    this.setData({
      src: ''
    })
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    request.get({},'recipe').then((res)=>{
      this.setData({
        recipes:res.rows
      })
    })
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