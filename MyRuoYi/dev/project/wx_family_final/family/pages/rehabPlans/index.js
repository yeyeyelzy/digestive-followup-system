import request from '../../api/requests';

const app = getApp();

Page({
  data: {
    loading: false,
    activeTab: 'all',
    tabs: [
      { key: 'all', label: '全部方案' },
      { key: 'doctor', label: '医生修改' }
    ],
    list: []
  },

  onShow() {
    this.loadData();
  },

  getPatientId() {
    const selectedPatientId = Number(wx.getStorageSync('selectedPatientId'));
    return Number.isFinite(selectedPatientId) && selectedPatientId > 0 ? selectedPatientId : null;
  },

  formatDateLabel(d) {
    const y = d.getFullYear();
    const m = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    return `${y}-${m}-${day}`;
  },

  formatDateTime(ts) {
    if (!ts) return '-';
    const d = new Date(ts);
    const h = `${d.getHours()}`.padStart(2, '0');
    const mm = `${d.getMinutes()}`.padStart(2, '0');
    const s = `${d.getSeconds()}`.padStart(2, '0');
    return `${this.formatDateLabel(d)} ${h}:${mm}:${s}`;
  },

  collectRecommendationsFromNode(node, sink) {
    if (!node) return;
    if (Array.isArray(node)) {
      node.forEach(it => this.collectRecommendationsFromNode(it, sink));
      return;
    }
    if (typeof node === 'object') {
      const rec = node.recommendations;
      if (Array.isArray(rec)) {
        rec.forEach(it => {
          const text = String(it || '').trim();
          if (text) sink.push(text);
        });
      }
      Object.keys(node).forEach(k => this.collectRecommendationsFromNode(node[k], sink));
      return;
    }
  },

  extractRecommendations(data) {
    const primary = Array.isArray(data.recommendations) ? data.recommendations : [];
    const ai = Array.isArray(data.aiRecommendations) ? data.aiRecommendations : [];
    const doctor = Array.isArray(data.doctorRevisedRecommendations) ? data.doctorRevisedRecommendations : [];
    const bag = [];

    [...primary, ...doctor, ...ai].forEach(it => {
      const text = String(it || '').trim();
      if (text) bag.push(text);
    });

    this.collectRecommendationsFromNode(data.aiPlan, bag);
    this.collectRecommendationsFromNode(data.doctorRevisedPlan, bag);

    const dedup = [];
    const seen = new Set();
    bag.forEach(it => {
      if (!seen.has(it)) {
        seen.add(it);
        dedup.push(it);
      }
    });
    return dedup;
  },

  isDoctorModified(plan) {
    const status = String(plan.status || '').toLowerCase();
    if (status.includes('revised') || status.includes('dispatch')) return true;
    if (plan.sourcePlanId || plan.sourceVersion) return true;
    return false;
  },

  rebuildList(source) {
    let list = (Array.isArray(source) ? source : []).slice().sort((a, b) => (b.fetchedAt || 0) - (a.fetchedAt || 0));
    if (this.data.activeTab === 'doctor') {
      list = list.filter(it => this.isDoctorModified(it));
    }

    const mapped = list.map(it => ({
      ...it,
      fetchedLabel: this.formatDateTime(it.fetchedAt),
      statusClass: this.isDoctorModified(it) ? 'status-doctor' : 'status-ai',
      unread: false
    }));

    this.setData({ list: mapped });
  },

  async loadData() {
    const patientId = this.getPatientId();
    if (!patientId) {
      wx.showToast({ title: '请先绑定并选择患者', icon: 'none' });
      return;
    }

    this.setData({ loading: true });
    try {
      const res = await request.getFamilyRehabPlanHistory(patientId);
      const list = Array.isArray(res && res.data) ? res.data : [];
      const mapped = list.map((data, idx) => {
        const recommendations = this.extractRecommendations(data);
        const sourceDate = data.sourceDate || '';
        const displayDate = data.displayDate || sourceDate || '-';
        return {
          id: data.id || `${sourceDate || 'unknown'}_${idx}`,
          dateLabel: displayDate,
          sourceDate: sourceDate || '-',
          fetchedAt: sourceDate ? new Date(`${sourceDate}T12:00:00`).getTime() : Date.now(),
          planId: data.planId || '',
          version: data.version || 1,
          status: data.status || '',
          recommendationSource: data.recommendationSource || '',
          sourcePlanId: data.sourcePlanId || (data.dispatchInfo && data.dispatchInfo.sourcePlanId) || '',
          sourceVersion: data.sourceVersion || (data.dispatchInfo && data.dispatchInfo.sourceVersion) || '',
          recommendations
        };
      });
      this.rebuildList(mapped);
    } catch (e) {
      wx.showToast({ title: '康复方案加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  onSwitchTab(e) {
    const key = e.currentTarget.dataset.key;
    if (!key || key === this.data.activeTab) return;
    this.setData({ activeTab: key });
    this.loadData();
  },

  onTapItem() {}
});
