import request from '../../api/requests'
const { RISK_LABEL_MAP, TREND_LABEL_MAP } = require('../../utils/heartTwinMock')

const app = getApp()

function toBeatPerSecond(heartRate) {
  if (!heartRate) return 0
  return Number((heartRate / 60).toFixed(2))
}

Page({
  data: {
    loading: false,
    forecastIndex: 0,
    rawRealtime: {},
    rawForecast: [],
    hasCoronaryRisk: false,
    hasTachycardia: false,
    modelHeartRate: 72,
    modelRiskLevel: 'low',
    modelCoronaryHighlight: false,
    modelTachycardiaHighlight: false,
    modelRecoveryProgress: 0,
    modelRhythmStability: 0.6,
    displayRealtime: {
      timestamp: '--',
      heartRate: '--',
      riskLevelLabel: '--',
      beatPerSecond: '--',
      anomalyFeatures: []
    },
    displayForecast: {
      monthLabel: '--',
      heartRate: '--',
      riskLevelLabel: '--',
      recoveryTrendText: '--'
    },
    riskClass: 'risk-low'
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  onUnload() {
    this.clearBeatTimer()
  },

  loadData() {
    const patientId = Number(wx.getStorageSync('selectedPatientId'))

    if (!patientId) {
      wx.showToast({ title: '请先绑定并选择患者', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    Promise.all([
      request.getFamilyHeartTwinRealtime(patientId),
      request.getFamilyHeartTwinForecast(patientId)
    ]).then(([realtimeRes, forecastRes]) => {
      if (realtimeRes && realtimeRes.code === 200 && forecastRes && forecastRes.code === 200) {
        this.applyPayload({
          realtime: realtimeRes.data,
          forecast: forecastRes.data || []
        })
      } else {
        this.setData({
          rawRealtime: {},
          rawForecast: [],
          displayRealtime: {
            timestamp: '--',
            heartRate: '--',
            riskLevelLabel: '--',
            beatPerSecond: '--',
            anomalyFeatures: []
          },
          displayForecast: {
            monthLabel: '--',
            heartRate: '--',
            riskLevelLabel: '--',
            recoveryTrendText: '--'
          }
        })
        wx.showToast({ title: '3D心脏数据加载失败', icon: 'none' })
      }
    }).catch(() => {
      this.setData({
        rawRealtime: {},
        rawForecast: [],
        displayRealtime: {
          timestamp: '--',
          heartRate: '--',
          riskLevelLabel: '--',
          beatPerSecond: '--',
          anomalyFeatures: []
        },
        displayForecast: {
          monthLabel: '--',
          heartRate: '--',
          riskLevelLabel: '--',
          recoveryTrendText: '--'
        }
      })
      wx.showToast({ title: '3D心脏数据加载失败', icon: 'none' })
    }).finally(() => {
      this.setData({ loading: false })
    })
  },

  applyPayload(payload) {
    const realtime = payload.realtime || {}
    const forecast = payload.forecast || []
    const safeForecast = forecast.length ? forecast : []
    const anomalyFeatures = realtime.anomalyFeatures || []
    const hasCoronaryRisk = anomalyFeatures.some((item) => item.indexOf('冠状动脉') > -1)
    const hasTachycardia = anomalyFeatures.some((item) => item.indexOf('心动过速') > -1)

    this.setData({
      rawRealtime: realtime,
      rawForecast: safeForecast,
      forecastIndex: 0,
      hasCoronaryRisk,
      hasTachycardia
    })

    this.updateRealtimeDisplay(realtime)
    this.updateForecastDisplay(0)
    this.syncModelByForecast(0)
    this.triggerHighRiskAlert(realtime.riskLevel)
  },

  syncModelByForecast(index) {
    const forecast = this.data.rawForecast[index] || {}
    const fallbackRealtime = this.data.rawRealtime || {}
    const heartRate = Number(forecast.heartRate || fallbackRealtime.heartRate || 72)
    const riskLevel = forecast.riskLevel || fallbackRealtime.riskLevel || 'low'
    const recoveryTrend = forecast.recoveryTrend || 'stable'

    let modelRecoveryProgress = 0.1
    let modelRhythmStability = 0.55

    if (recoveryTrend === 'improve') {
      modelRecoveryProgress = Math.min(1, 0.4 + index * 0.3)
      modelRhythmStability = Math.min(1, 0.7 + index * 0.12)
    } else if (recoveryTrend === 'stable') {
      modelRecoveryProgress = Math.max(0.1, index * 0.05)
      modelRhythmStability = 0.72
    } else {
      modelRecoveryProgress = 0
      modelRhythmStability = 0.35
    }

    const modelCoronaryHighlight = riskLevel === 'high' || (riskLevel === 'medium' && recoveryTrend !== 'improve')
    const modelTachycardiaHighlight = heartRate >= 110 || riskLevel === 'high'

    this.setData({
      modelHeartRate: heartRate,
      modelRiskLevel: riskLevel,
      modelCoronaryHighlight,
      modelTachycardiaHighlight,
      modelRecoveryProgress,
      modelRhythmStability
    })
  },

  updateRealtimeDisplay(realtime) {
    const riskLevel = realtime.riskLevel || 'low'
    const heartRate = realtime.heartRate || 0

    this.setData({
      displayRealtime: {
        timestamp: realtime.timestamp || '--',
        heartRate: heartRate || '--',
        riskLevelLabel: RISK_LABEL_MAP[riskLevel] || '未知',
        beatPerSecond: toBeatPerSecond(heartRate) || '--',
        anomalyFeatures: realtime.anomalyFeatures || []
      },
      riskClass: `risk-${riskLevel}`
    })
  },

  updateForecastDisplay(index) {
    const item = this.data.rawForecast[index] || {}
    this.setData({
      displayForecast: {
        monthLabel: item.monthLabel || '--',
        heartRate: item.heartRate || '--',
        riskLevelLabel: RISK_LABEL_MAP[item.riskLevel] || '未知',
        recoveryTrendText: TREND_LABEL_MAP[item.recoveryTrend] || '未知'
      }
    })
  },

  onForecastChange(event) {
    const detail = event.detail
    const sliderValue = typeof detail === 'object' ? detail.value : detail
    const index = Number(sliderValue || 0)
    this.setData({
      forecastIndex: index
    })
    this.updateForecastDisplay(index)
    this.syncModelByForecast(index)
  },

  clearBeatTimer() {
    if (this.beatTimer) {
      clearInterval(this.beatTimer)
      this.beatTimer = null
    }
  },

  triggerHighRiskAlert(riskLevel) {
    if (riskLevel !== 'high') return
    wx.vibrateShort({ type: 'heavy' })
    wx.showToast({
      title: '心率异常，请及时休息',
      icon: 'none'
    })
  }
})
