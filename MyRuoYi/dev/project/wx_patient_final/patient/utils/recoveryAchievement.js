const ACHIEVEMENT_TITLES = [
  '康复萌新',
  '初露锋芒',
  '坚持不懈',
  '渐入佳境',
  '习惯养成',
  '活力焕发',
  '健康卫士',
  '身心自在',
  '铜墙铁壁',
  '康复达人',
  '超越自我',
  '巅峰健康'
]

function getRecoveryAchievementMock() {
  return {
    currentTitleId: 1,
    currentTitleName: '康复萌新',
    currentLevel: 3,
    consecutiveHealthyDays: 4,
    totalHealthyDays: 25,
    healthyToday: true
  }
}

function getAchievementImagePath(titleName) {
  return `/images/recovery/${titleName}.png`
}

function buildAchievementViewModel(raw) {
  const titleId = Number(raw.currentTitleId || 1)
  const titleName = raw.currentTitleName || ACHIEVEMENT_TITLES[Math.max(0, titleId - 1)] || '康复萌新'
  const level = Math.min(5, Math.max(1, Number(raw.currentLevel || 1)))
  const healthyDays = Math.min(7, Math.max(0, Number(raw.consecutiveHealthyDays || 0)))
  const progressPercent = Math.round((healthyDays / 7) * 100)

  return {
    titleId,
    titleName,
    currentLevel: level,
    levelLabel: `Lv.${level}`,
    consecutiveHealthyDays: healthyDays,
    totalHealthyDays: Number(raw.totalHealthyDays || 0),
    healthyToday: !!raw.healthyToday,
    progressText: `${healthyDays}/7`,
    progressPercent,
    badgeImage: getAchievementImagePath(titleName),
    cheerText: `您已坚持健康生活了${Number(raw.totalHealthyDays || 0)}天，请继续保持哦！`
  }
}

module.exports = {
  ACHIEVEMENT_TITLES,
  getRecoveryAchievementMock,
  buildAchievementViewModel
}
