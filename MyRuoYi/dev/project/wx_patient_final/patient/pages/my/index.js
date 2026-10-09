// pages/my/index.js
import request from '../../api/requests'
const { getHeartTwinMockPayload, RISK_LABEL_MAP } = require('../../utils/heartTwinMock')
const { getRecoveryAchievementMock, buildAchievementViewModel } = require('../../utils/recoveryAchievement')
const app = getApp(); // 在Page外部获取app实例

Page({
  /**
   * 页面的初始数据
   */
  data: {
    patient: {}, // 用于存储从服务器获取的详细病人信息
    isLogin: false, // 关键状态：判断是否登录
    patientName: '点击登录', // 用于界面显示的名字
    avatarUrl: '/images/svg/user.svg',
    msgCount: 0,
    // 【新增】消息通知
    riskMessage: '', // 风险预警内容，有值则显示
    rehabMessage: '', // 康复方案提醒，有值则显示
    heartPreview: {
      heartRate: 72,
      riskLevel: 'low',
      riskLabel: '低风险',
      coronaryHighlight: false,
      tachycardiaHighlight: false
    },
    achievement: buildAchievementViewModel(getRecoveryAchievementMock())
  },

  /**
   * 生命周期函数--监听页面显示
   * 每次进入页面都会触发，是管理登录状态的最佳位置
   */
  onShow: function () {
    console.log("--- my/index.js onShow 触发 ---");
    console.log("【my/index.js】当前 app.globalData.patientInfo:", app.globalData.patientInfo);
    const patientInfo = app.globalData.patientInfo;
    
    // 检查全局数据中是否有用户信息，以此判断登录状态
    if (patientInfo && patientInfo.patientId) {
      // 状态一：已登录
      this.setData({
        isLogin: true,
        patientName: patientInfo.patientName, // 先用全局信息快速显示名字
        avatarUrl: this.normalizeAvatarUrl(patientInfo.avatarUrl)
      });
      // 然后调用 load 方法去服务器获取最新、最全的信息
      this.load(); 
      this.applyHeartPreview(patientInfo.patientId);
      this.loadAchievement(patientInfo.patientId);
      // 【模拟】设置消息提醒 (Python后端未接入前做展示用)
      // 实际应根据后端返回数据设置
      // this.setData({
      //   riskMessage: '您有一条新的风险预警，请查看',
      //   rehabMessage: '您有一条新的康复方案，请查收'
      // });
    } else {
      // 状态二：未登录
      this.setData({
        isLogin: false,
        patientName: '点击登录',
        avatarUrl: '/images/svg/user.svg',
        patient: {}, // 清空详细信息，防止退出后还显示旧数据
        riskMessage: '',
        rehabMessage: '',
        heartPreview: {
          heartRate: 72,
          riskLevel: 'low',
          riskLabel: '低风险',
          coronaryHighlight: false,
          tachycardiaHighlight: false
        },
        achievement: buildAchievementViewModel(getRecoveryAchievementMock())
      });
    }
  },

  loadAchievement(patientId) {
    if (!patientId) {
      this.setData({
        achievement: buildAchievementViewModel(getRecoveryAchievementMock())
      })
      return
    }

    request.getRecoveryAchievement(patientId).then((res) => {
      if (res && res.code === 200 && res.data) {
        this.setData({
          achievement: buildAchievementViewModel({
            currentTitleId: res.data.current_title_id,
            currentTitleName: res.data.current_title_name,
            currentLevel: res.data.current_level,
            consecutiveHealthyDays: res.data.consecutive_healthy_days,
            totalHealthyDays: res.data.total_healthy_days,
            healthyToday: res.data.healthy_today
          })
        })
      } else {
        this.setData({
          achievement: buildAchievementViewModel(getRecoveryAchievementMock())
        })
      }
    }).catch(() => {
      this.setData({
        achievement: buildAchievementViewModel(getRecoveryAchievementMock())
      })
    })
  },

  buildHeartPreview(realtime) {
    const riskLevel = realtime.riskLevel || 'low'
    const anomalyFeatures = realtime.anomalyFeatures || []
    const coronaryHighlight = anomalyFeatures.some((item) => item.indexOf('冠状动脉') > -1)
    const tachycardiaHighlight = anomalyFeatures.some((item) => item.indexOf('心动过速') > -1)

    return {
      heartRate: realtime.heartRate || 72,
      riskLevel,
      riskLabel: RISK_LABEL_MAP[riskLevel] || '低风险',
      coronaryHighlight,
      tachycardiaHighlight
    }
  },

  applyHeartPreview(patientId) {
    const fallbackPayload = getHeartTwinMockPayload()
    const fallbackRealtime = fallbackPayload.realtime || {}

    if (!patientId) {
      this.setData({
        heartPreview: this.buildHeartPreview(fallbackRealtime)
      })
      return
    }

    request.getHeartTwinRealtime(patientId).then((res) => {
      if (res && res.code === 200 && res.data) {
        this.setData({
          heartPreview: this.buildHeartPreview(res.data)
        })
      } else {
        this.setData({
          heartPreview: this.buildHeartPreview(fallbackRealtime)
        })
      }
    }).catch(() => {
      this.setData({
        heartPreview: this.buildHeartPreview(fallbackRealtime)
      })
    })
  },

  /**
   * [保留并优化] 从服务器加载用户详细信息的函数
   */
  load() {
    // 从全局获取 patientId，确保 ID 存在
    const patientId = app.globalData.patientInfo.patientId;
    if (!patientId) return;

    // 发起请求获取详细信息
    request.getOne(patientId, 'patient').then((res) => {
      if (res && res.data) {
        this.setData({
          patient: res.data,
          // 用服务器返回的最新数据覆盖，确保信息准确
          patientName: res.data.patientName,
          avatarUrl: this.normalizeAvatarUrl(res.data.avatarUrl)
        });
        console.log("用户详细信息已更新:", this.data.patient);
      }
    }).catch(err => {
      console.error("获取用户详情失败:", err);
      wx.showToast({ title: '信息加载失败', icon: 'none' });
    });

    // 获取消息数量的逻辑 (如果需要)
    // request.getMsgCount(patientId).then(res => { ... });
  },

  normalizeAvatarUrl(path) {
    if (!path) return '/images/svg/user.svg';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    return `http://localhost:8080${path}`;
  },

  /**
   * [新增] 跳转至聊天界面
   */
  goToChat() {
    if (this.data.isLogin) {
      wx.navigateTo({ url: '../chat/chat' });
    } else {
      wx.showToast({ title: '请先登录', icon: 'none' });
    }
  },

  /**
   * [新增] 跳转至个人信息修改
   */
  goToProfile() {
    wx.navigateTo({ url: '../profile/profile' });
  },

  /**
   * [新增] 关闭消息提醒
   */
  closeMsg(e) {
    const type = e.currentTarget.dataset.type;
    if (type === 'risk') {
      this.setData({ riskMessage: '' });
    } else if (type === 'rehab') {
      this.setData({ rehabMessage: '' });
    }
  },

  /**
   * [新增] 通用功能点击处理 (用于未开发功能提示)
   */
  onTapFeature(e) {
    const url = e.currentTarget.dataset.url;
    const name = e.currentTarget.dataset.name;
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    const routeMap = {
      '风险预警': '../riskAlerts/index',
      '康复方案': '../rehabPlans/index',
      '康复成就': '../achievement/index'
    };
    const targetUrl = url || routeMap[name] || '';

    if (targetUrl) {
      wx.navigateTo({ url: targetUrl });
    } else {
      wx.showToast({
        title: name + ' 功能开发中',
        icon: 'none'
      });
    }
  },

  goToHeartTwin() {
    if (this.data.isLogin) {
      wx.navigateTo({ url: '../heartTwin/index' });
    } else {
      wx.showToast({ title: '请先登录', icon: 'none' });
    }
  },

  goAchievement() {
    this.onTapFeature({
      currentTarget: {
        dataset: {
          name: '康复成就',
          url: '../achievement/index'
        }
      }
    });
  },

  /**
   * [新增] 处理登录点击事件
   * 如果未登录，点击头像或名字区域时，跳转到登录页
   */
  handleLoginTap() {
    if (!this.data.isLogin) {
      wx.reLaunch({ // 使用 reLaunch 可以清空页面栈，登录后返回时不会回到“我的”
        url: '/pages/login/login',
      });
    }
    // 如果已登录，则不执行任何操作，或者可以跳转到个人资料编辑页
  },

  /**
   * [新增] 退出登录功能
   */
  logout() {
    wx.showModal({
      title: '提示',
      content: '您确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 关键：调用 app.js 中的全局方法来清空登录信息
          app.clearGlobalPatientInfo(); 
          
          // 页面状态更新：可以直接调用 onShow() 重新判断和渲染页面
          this.onShow(); 
          
          wx.showToast({ title: '已退出登录' });
        }
      }
    });
  },
  
  // 原有的其他生命周期和事件函数可以保留
  onLoad: function (options) {
    // onLoad 只执行一次，不适合处理登录状态，主要逻辑移至 onShow
  },
  onReady: function () {},
  onHide: function () {},
  onUnload: function () {},
  onPullDownRefresh: function () {},
  onReachBottom: function () {},
  onShareAppMessage: function () {}
});
