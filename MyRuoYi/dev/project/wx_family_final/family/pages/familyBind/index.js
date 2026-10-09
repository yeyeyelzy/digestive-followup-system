import request from '../../api/requests'

Page({
  data: {
    patientPhone: '',
    relationship: '',
    list: [],
    loading: false
  },

  onShow() {
    this.loadList();
  },

  onInputPhone(e) {
    this.setData({ patientPhone: e.detail.value });
  },

  onInputRelation(e) {
    this.setData({ relationship: e.detail.value });
  },

  loadList() {
    this.setData({ loading: true });
    request.getBoundPatients().then(res => {
      this.setData({
        list: (res && res.data) ? res.data : [],
        loading: false
      });
    }).catch(() => {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    });
  },

  submitBind() {
    const { patientPhone, relationship } = this.data;
    if (!/^\d{11}$/.test(patientPhone)) {
      wx.showToast({ title: '请输入11位患者手机号', icon: 'none' });
      return;
    }

    request.bindPatient({ patientPhone, relationship }).then(res => {
      if (res.code === 200) {
        wx.showToast({ title: '绑定成功', icon: 'success' });
        this.setData({ patientPhone: '', relationship: '' });
        this.loadList();
      } else {
        wx.showToast({ title: res.msg || '绑定失败', icon: 'none' });
      }
    }).catch(() => {
      wx.showToast({ title: '绑定失败', icon: 'none' });
    });
  },

  unbind(e) {
    const patientId = e.currentTarget.dataset.id;
    wx.showModal({
      title: '提示',
      content: '确认解绑该患者吗？',
      success: (res) => {
        if (!res.confirm) return;
        request.unbindPatient(patientId).then(resp => {
          if (resp.code === 200) {
            if (Number(wx.getStorageSync('selectedPatientId')) === Number(patientId)) {
              wx.removeStorageSync('selectedPatientId');
            }
            wx.showToast({ title: '解绑成功', icon: 'success' });
            this.loadList();
          } else {
            wx.showToast({ title: resp.msg || '解绑失败', icon: 'none' });
          }
        });
      }
    });
  }
});
