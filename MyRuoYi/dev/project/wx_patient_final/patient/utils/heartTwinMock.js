const RISK_LABEL_MAP = {
  low: '低风险',
  medium: '中风险',
  high: '高风险'
}

const TREND_LABEL_MAP = {
  improve: '向好',
  stable: '稳定',
  worse: '波动'
}

function getHeartTwinMockPayload() {
  return {
    realtime: {
      timestamp: '2026-02-28 10:00:00',
      heartRate: 96,
      riskLevel: 'medium',
      anomalyFeatures: ['心动过速倾向', '冠状动脉风险轻度波动']
    },
    forecast: [
      {
        monthIndex: 1,
        monthLabel: '1个月后',
        heartRate: 92,
        riskLevel: 'medium',
        recoveryTrend: 'stable'
      },
      {
        monthIndex: 2,
        monthLabel: '2个月后',
        heartRate: 84,
        riskLevel: 'low',
        recoveryTrend: 'improve'
      },
      {
        monthIndex: 3,
        monthLabel: '3个月后',
        heartRate: 78,
        riskLevel: 'low',
        recoveryTrend: 'improve'
      }
    ]
  }
}

function getHeartTwinHighRiskMockPayload() {
  return {
    realtime: {
      timestamp: '2026-02-28 10:02:10',
      heartRate: 132,
      riskLevel: 'high',
      anomalyFeatures: ['心动过速', '冠状动脉风险']
    },
    forecast: [
      {
        monthIndex: 1,
        monthLabel: '1个月后',
        heartRate: 118,
        riskLevel: 'high',
        recoveryTrend: 'worse'
      },
      {
        monthIndex: 2,
        monthLabel: '2个月后',
        heartRate: 106,
        riskLevel: 'medium',
        recoveryTrend: 'stable'
      },
      {
        monthIndex: 3,
        monthLabel: '3个月后',
        heartRate: 92,
        riskLevel: 'medium',
        recoveryTrend: 'improve'
      }
    ]
  }
}

module.exports = {
  RISK_LABEL_MAP,
  TREND_LABEL_MAP,
  getHeartTwinMockPayload,
  getHeartTwinHighRiskMockPayload
}
