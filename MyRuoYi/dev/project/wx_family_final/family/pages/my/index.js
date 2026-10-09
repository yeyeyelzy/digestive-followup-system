// pages/my/index.js
import request from '../../api/requests'
const { getHeartTwinMockPayload, RISK_LABEL_MAP } = require('../../utils/heartTwinMock')
const app = getApp()

Page({
  data: {
    patient: {},
    isLogin: false,
    patientName: '点击登录',
    avatarUrl: '/images/tabs/my-grey.png',
    boundPatients: [],
    selectedPatientId: null,
    selectedPatientName: '未绑定患者',
    msgCount: 0,
    riskMessage: '',
    rehabMessage: '',
    selectedRiskDate: '',
    selectedRehabDate: '',
    heartPreview: {
      heartRate: 72,
      riskLevel: 'low',
      riskLabel: '低风险',
      coronaryHighlight: false,
      tachycardiaHighlight: false
    }
  },

  onShow() {
    const familyInfo = app.globalData.patientInfo
    if (familyInfo && familyInfo.patientId) {
      this.setData({
        isLogin: true,
        patientName: familyInfo.patientName,
        avatarUrl: this.normalizeAvatarUrl(familyInfo.avatarUrl)
      })
      this.load()
      this.loadBoundPatients()
    } else {
      this.setData({
        isLogin: false,
        patientName: '点击登录',
        avatarUrl: '/images/tabs/my-grey.png',
        patient: {},
        boundPatients: [],
        selectedPatientId: null,
        selectedPatientName: '未绑定患者',
        riskMessage: '',
        rehabMessage: '',
        selectedRiskDate: '',
        selectedRehabDate: '',
        heartPreview: {
          heartRate: 72,
          riskLevel: 'low',
          riskLabel: '低风险',
          coronaryHighlight: false,
          tachycardiaHighlight: false
        }
      })
      wx.removeStorageSync('selectedPatientId')
    }
  },

  load() {
    const loginInfo = app.globalData.patientInfo
    if (!loginInfo) return

    this.setData({
      patient: loginInfo,
      patientName: loginInfo.patientName,
      avatarUrl: this.normalizeAvatarUrl(loginInfo.avatarUrl)
    })
  },

  loadBoundPatients() {
    request.getBoundPatients().then((res) => {
      const list = (res && res.data) ? res.data : []
      let selectedPatientId = wx.getStorageSync('selectedPatientId') || null
      if (selectedPatientId !== null && selectedPatientId !== undefined && selectedPatientId !== '') {
        selectedPatientId = Number(selectedPatientId)
      }
      if (!selectedPatientId && list.length > 0) {
        selectedPatientId = Number(list[0].patientId)
      }

      const selected = list.find(item => Number(item.patientId) === Number(selectedPatientId))
      this.setData({
        boundPatients: list,
        selectedPatientId,
        selectedPatientName: selected ? selected.patientName : '未绑定患者'
      })

      if (selectedPatientId) {
        wx.setStorageSync('selectedPatientId', selectedPatientId)
      }
      this.refreshPatientScopedCards(selectedPatientId)
    }).catch(() => {
      this.setData({
        boundPatients: [],
        selectedPatientId: null,
        selectedPatientName: '未绑定患者',
        riskMessage: '',
        rehabMessage: '',
        selectedRiskDate: '',
        selectedRehabDate: ''
      })
    })
  },

  refreshPatientScopedCards(patientId) {
    if (!patientId) {
      this.setData({
        heartPreview: {
          heartRate: 72,
          riskLevel: 'low',
          riskLabel: '低风险',
          coronaryHighlight: false,
          tachycardiaHighlight: false
        },
        riskMessage: '',
        rehabMessage: ''
      })
      return
    }
    this.applyHeartPreview(patientId)
    this.loadInboxHints(patientId)
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

    request.getFamilyHeartTwinRealtime(patientId).then((res) => {
      if (res && res.code === 200 && res.data) {
        this.setData({ heartPreview: this.buildHeartPreview(res.data) })
      } else {
        this.setData({ heartPreview: this.buildHeartPreview(fallbackRealtime) })
      }
    }).catch(() => {
      this.setData({ heartPreview: this.buildHeartPreview(fallbackRealtime) })
    })
  },

  loadInboxHints(patientId) {
    Promise.all([
      request.getFamilyRiskPredictHistory(patientId),
      request.getFamilyRehabPlanHistory(patientId)
    ]).then(([riskRes, rehabRes]) => {
      const riskList = Array.isArray(riskRes && riskRes.data) ? riskRes.data : []
      const rehabList = Array.isArray(rehabRes && rehabRes.data) ? rehabRes.data : []

      const riskLatestDate = riskList.length ? (riskList[0].sourceDate || '') : ''
      const rehabLatestDate = rehabList.length ? (rehabList[0].sourceDate || '') : ''

      const riskSeenKey = `family_risk_seen_${patientId}`
      const rehabSeenKey = `family_rehab_seen_${patientId}`
      const riskSeenDate = wx.getStorageSync(riskSeenKey) || ''
      const rehabSeenDate = wx.getStorageSync(rehabSeenKey) || ''

      this.setData({
        selectedRiskDate: riskLatestDate,
        selectedRehabDate: rehabLatestDate,
        riskMessage: riskLatestDate && riskLatestDate !== riskSeenDate ? '您有新的风险预警，注意查收' : '',
        rehabMessage: rehabLatestDate && rehabLatestDate !== rehabSeenDate ? '您有新的康复方案，注意查收' : ''
      })
    }).catch(() => {
      this.setData({ riskMessage: '', rehabMessage: '', selectedRiskDate: '', selectedRehabDate: '' })
    })
  },

  onPatientChange(e) {
    const index = Number(e.detail.value)
    const target = this.data.boundPatients[index]
    if (!target) return

    this.setData({
      selectedPatientId: Number(target.patientId),
      selectedPatientName: target.patientName
    })
    wx.setStorageSync('selectedPatientId', Number(target.patientId))
    this.refreshPatientScopedCards(Number(target.patientId))
  },

  goToBindManage() {
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    wx.navigateTo({ url: '/pages/familyBind/index' })
  },

  normalizeAvatarUrl(path) {
    if (!path) return '/images/tabs/my-grey.png'
    if (path.startsWith('http://') || path.startsWith('https://')) return path
    return `http://localhost:8080${path}`
  },

  goToProfile() {
    wx.navigateTo({ url: '../profile/profile' })
  },

  closeMsg(e) {
    const type = e.currentTarget.dataset.type
    const patientId = this.data.selectedPatientId
    if (!patientId) return

    if (type === 'risk') {
      const sourceDate = this.data.riskMessage ? (this.data.selectedRiskDate || '') : ''
      if (sourceDate) wx.setStorageSync(`family_risk_seen_${patientId}`, sourceDate)
      this.setData({ riskMessage: '' })
    } else if (type === 'rehab') {
      const sourceDate = this.data.rehabMessage ? (this.data.selectedRehabDate || '') : ''
      if (sourceDate) wx.setStorageSync(`family_rehab_seen_${patientId}`, sourceDate)
      this.setData({ rehabMessage: '' })
    }
  },

  onTapFeature(e) {
    const url = e.currentTarget.dataset.url
    const name = e.currentTarget.dataset.name
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    if (!this.data.selectedPatientId && ['风险预警', '康复方案', '指标变化', '3D心脏孪生体'].includes(name)) {
      wx.showToast({ title: '请先绑定并选择患者', icon: 'none' })
      return
    }

    const routeMap = {
      '风险预警': '../riskAlerts/index',
      '康复方案': '../rehabPlans/index',
      '指标变化': '../visual/visual',
      '3D心脏孪生体': '../heartTwin/index'
    }
    const targetUrl = url || routeMap[name] || ''
    if (targetUrl) {
      if (name === '风险预警' && this.data.selectedPatientId && this.data.selectedRiskDate) {
        wx.setStorageSync(`family_risk_seen_${this.data.selectedPatientId}`, this.data.selectedRiskDate)
        this.setData({ riskMessage: '' })
      }
      if (name === '康复方案' && this.data.selectedPatientId && this.data.selectedRehabDate) {
        wx.setStorageSync(`family_rehab_seen_${this.data.selectedPatientId}`, this.data.selectedRehabDate)
        this.setData({ rehabMessage: '' })
      }
      wx.navigateTo({ url: targetUrl })
    } else {
      wx.showToast({ title: `${name} 功能开发中`, icon: 'none' })
    }
  },

  goToHeartTwin() {
    this.onTapFeature({ currentTarget: { dataset: { name: '3D心脏孪生体', url: '../heartTwin/index' } } })
  },

  handleLoginTap() {
    if (!this.data.isLogin) {
      wx.reLaunch({ url: '/pages/login/login' })
    }
  },

  logout() {
    wx.showModal({
      title: '提示',
      content: '您确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.clearGlobalPatientInfo()
          this.onShow()
          wx.showToast({ title: '已退出登录' })
        }
      }
    })
  }
})
