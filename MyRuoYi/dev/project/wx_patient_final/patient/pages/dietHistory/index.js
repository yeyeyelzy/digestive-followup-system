import request from '../../api/requests'

const app = getApp();

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
    request.getDiet({ pageNum: 1, pageSize: 200 }).then((res) => {
      const rows = (res && res.rows) ? res.rows : [];
      rows.sort((a, b) => new Date(b.date) - new Date(a.date));
      this.setData({ list: rows, loading: false });
    }).catch(() => {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    });
  },
});
