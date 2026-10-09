import request from '../../api/requests'

const app = getApp();

function toTypeLabel(type) {
  if (type === 1 || type === '1') return '有氧运动';
  if (type === 2 || type === '2') return '抗阻运动';
  if (type === 3 || type === '3') return '综合性运动';
  return '其他';
}

Page({
  data: {
    list: [],
    loading: false,
  },

  onShow() {
    const selectedPatientId = wx.getStorageSync('selectedPatientId');
    if (selectedPatientId) {
      this.loadList();
    } else {
      wx.showToast({ title: '请先绑定并选择患者', icon: 'none', duration: 1500 });
    }
  },

  loadList() {
    this.setData({ loading: true });
    request.getBehavior({ pageNum: 1, pageSize: 200 }).then((res) => {
      const rows = (res && res.rows) ? res.rows : [];
      rows.sort((a, b) => new Date(b.date) - new Date(a.date));
      rows.forEach(item => {
        item.typeText = toTypeLabel(item.type);
      });
      this.setData({ list: rows, loading: false });
    }).catch(() => {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    });
  },
});
