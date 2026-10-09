import request from '../../api/requests'

const app = getApp();

Page({
  data: {
    loading: false,
    achievement: null,
    progressPercent: 0
  },

  onShow() {
    this.loadData();
  },

  getPatientId() {
    const info = app.globalData.patientInfo || {};
    return info.patientId || null;
  },

  async loadData() {
    const patientId = this.getPatientId();
    if (!patientId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => wx.reLaunch({ url: '/pages/login/login' }), 1200);
      return;
    }

    this.setData({ loading: true });
    try {
      const res = await request.getRecoveryAchievement(patientId);
      const data = (res && res.data) || {};
      const consecutive = Number(data.consecutive_healthy_days || 0);
      const percent = Math.max(0, Math.min(100, Math.floor((consecutive / 7) * 100)));

      this.setData({
        achievement: {
          currentTitleName: data.current_title_name || '-',
          currentLevel: data.current_level == null ? '-' : data.current_level,
          consecutiveHealthyDays: consecutive,
          totalHealthyDays: Number(data.total_healthy_days || 0),
          healthyToday: !!data.healthy_today
        },
        progressPercent: percent
      });
    } catch (e) {
      wx.showToast({ title: '康复成就加载失败', icon: 'none' });
      this.setData({ achievement: null, progressPercent: 0 });
    } finally {
      this.setData({ loading: false });
    }
  }
});
