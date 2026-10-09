// pages/diet/diet.js
import request from '../../api/requests'
import {
  formatTime,
  formatDate
} from '../../utils/util'

const app = getApp(); // 在Page外部获取app实例

Page({
  /**
   * 页面的初始数据 (重构后)
   */
  data: {
    isLogin: false, // 【新增】登录状态标志
  
    form: {
      patientId: null, // 初始化为 null
      date: formatDate(new Date()),
      dietDescription: null,
      dietPictureUrl: null,
      // ... 其他表单字段 ...
    },
    
    maxDate: new Date().getTime(),
    minDate: new Date().getTime() - 2592000000,
    flag: 0,
    show: false,
    fileList: [],
  },

  /**
   * 生命周期函数--监听页面加载
   * onLoad 只执行一次，适合做一些初始化的设置
   */
  onLoad: function (options) {
    // 这里可以保持为空，或者做一些不依赖登录状态的初始化
  },
  
  /**
   * 生命周期函数--监听页面显示
   * onShow 每次页面显示都会触发，是处理登录状态和刷新数据的最佳位置
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
   * 加载当天饮食数据的函数 (保持不变，但现在由 onShow 触发)
   */
  load: function () {
    if (!this.data.form.patientId) {
      console.error("加载失败，patientId 为空！");
      return;
    }
    
    request.getDiet(this.data.form).then((res) => {
      console.log('饮食记录查询结果:', res)
      if (!res || !res.rows || res.rows.length === 0) {
        this.setData({
          form: {
            ...this.data.form, // 保留 patientId 和 date
            dietDescription: null,
            dietPictureUrl: null,
            // ... 清空其他字段 ...
          },
          fileList: [],
          flag: 0 // 标记为新增状态
        })
      } else {
        this.setData({
          form: res.rows[0],
          flag: 1, // 标记为修改状态
          fileList: res.rows[0].dietPictureUrl ? [{ url: res.rows[0].dietPictureUrl }] : []
        })
      }
    })
  },
  
  // 保存函数，需要确保 patientId 正确
  save: function () {
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    console.log('准备保存的饮食数据:', this.data.form)
    request.addDiet(this.data.form).then((res) => {
        if(res.code === 200){
            wx.showToast({ title: '保存成功' });
        } else {
            wx.showToast({ title: res.msg || '保存失败', icon: 'none' });
        }
    })
  },
  
  onConfirm(event) {
    this.setData({
      show: false,
      'form.date': formatDate(event.detail),
    });
    // 日期改变后，重新加载该日期的数据
    this.load();
  },

  // ... 你其他的函数如 afterRead, delPicture, onDisplay, onClose, onChange... 保持原样即可 ...

  afterRead(event) {
    const {
      file
    } = event.detail;
    // 当设置 mutiple 为 true 时, file 为数组格式，否则为对象格式
    wx.uploadFile({
      url: 'http://localhost:8080/common/upload',
      filePath: file.url,
      name: 'file',
      success: (res) => {
        // 上传完成需要更新 fileList
        const {
          fileList = []
        } = this.data;
        const responseData = JSON.parse(res.data); // 后端返回的是JSON字符串，需要解析
        
        fileList.push({
          ...file,
          url: responseData.url // 假设后端返回 { url: '...' }
        });
        this.setData({
          fileList,
          'form.dietPictureUrl': responseData.url
        });
        console.log(this.data.fileList)
      },
    });
  },
  delPicture(event) {
    this.data.fileList.splice(event.detail.index, 1);
    //渲染数据
    this.setData({
      fileList: this.data.fileList,
      'form.dietPictureUrl': '' // 同时清空表单中的图片URL
    })
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
  onChangeDietDescription(e) { // 对应三餐/描述
    this.setData({
      'form.dietDescription': e.detail
    })
  },
  onChangeKcal(e) { // 对应热量
    this.setData({
      'form.kcal': e.detail
    })
  },
  onChangeFeel(e) { // 对应感受
    this.setData({
      'form.feel': e.detail
    })
  },
  onChangeReplay(e) { // 对应复盘
    this.setData({
      'form.replay': e.detail
    })
  },
  onChangeConfusion(e) { // 对应困惑
    this.setData({
      'form.confusion': e.detail
    })
  },

});
