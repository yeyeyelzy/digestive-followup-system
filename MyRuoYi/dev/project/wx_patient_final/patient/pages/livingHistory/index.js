import request from '../../api/requests'

const app = getApp();

function improvedText(value) {
  if (value === 1 || value === '1' || value === true) return '有改善';
  if (value === 0 || value === '0' || value === false) return '无改善';
  return '—';
}

Page({
  data: {
    list: [],
    loading: false,
  },

  onShow() {
    const patientInfo = app.globalData.patientInfo;
    if (patientInfo && patientInfo.patientId) {
      this.loadList();
    } else {
      wx.showToast({ title: '请先登录', icon: 'none', duration: 1500 });
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/login/login' });
      }, 1500);
    }
  },

  loadList() {
    this.setData({ loading: true });
    request.getLiving({ pageNum: 1, pageSize: 200 }).then((res) => {
      const rows = (res && res.rows) ? res.rows : [];
      rows.sort((a, b) => new Date(b.date) - new Date(a.date));
      rows.forEach(item => {
        item.improvedText = improvedText(item.isImproved);
      });
      this.setData({ list: rows, loading: false });
    }).catch(() => {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    });
  },
});
