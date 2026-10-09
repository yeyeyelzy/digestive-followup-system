import request from '../../api/requests';

const app = getApp();

Page({
  data: {
    loading: false,
    list: []
  },

  onShow() {
    this.loadData();
  },

  getPatientId() {
    const info = app.globalData.patientInfo || {};
    return info.patientId || null;
  },

  formatDateLabel(d) {
    const y = d.getFullYear();
    const m = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    return `${y}-${m}-${day}`;
  },

  toDistributionText(obj) {
    if (!obj || typeof obj !== 'object') return '-';
    return Object.keys(obj).map(k => `${k}: ${obj[k]}`).join(' | ');
  },

  getScopedMap(key) {
    return wx.getStorageSync(key) || {};
  },

  saveScopedMap(key, map) {
    wx.setStorageSync(key, map || {});
  },

  normalizeRiskLevel(level) {
    const text = String(level || '').toLowerCase();
    if (text.includes('high') || text.includes('高')) return 'high';
    if (text.includes('medium') || text.includes('mid') || text.includes('中')) return 'medium';
    return 'low';
  },

  riskLevelLabel(level) {
    const key = this.normalizeRiskLevel(level);
    if (key === 'high') return '高风险';
    if (key === 'medium') return '中风险';
    return '低风险';
  },

  formatDistributionValue(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return String(v);
    if (n >= 0 && n <= 1) return `${(n * 100).toFixed(2)}%`;
    return `${n}`;
  },

  toWarningText(obj) {
    if (!obj || typeof obj !== 'object') return '-';
    return Object.keys(obj).map(k => `${k}: ${this.formatDistributionValue(obj[k])}`).join(' | ');
  },

  async loadData() {
    const patientId = this.getPatientId();
    if (!patientId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    this.setData({ loading: true });
    try {
      const res = await request.getPatientRiskPredictHistory(patientId);
      const list = Array.isArray(res && res.data) ? res.data : [];
      const mapped = list.map((it, idx) => ({
        id: it.id || `${it.sourceDate || 'unknown'}_${idx}`,
        dateLabel: it.displayDate || '-',
        sourceDate: it.sourceDate || '-',
        fetchedLabel: it.displayDate || '-',
        riskLevel: this.riskLevelLabel(it.riskLevel),
        riskClass: `level-${this.normalizeRiskLevel(it.riskLevel)}`,
        heartRateDistributionText: this.toDistributionText(it.heartRateDistribution),
        warningDistributionText: this.toWarningText(it.warningDistribution),
        description: it.description || '-',
        unread: false
      }));
      this.setData({ list: mapped });
    } catch (e) {
      wx.showToast({ title: '风险预警加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  onTapItem() {}
});
