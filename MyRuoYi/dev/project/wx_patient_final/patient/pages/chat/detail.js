import request from '../../api/requests'
const app = getApp();
const BASE_URL = 'http://localhost:8080';
const DEFAULT_AVATAR = '/images/tabs/my-grey.png';

Page({
  data: {
    words: [],
    rawWords: [],
    content: '',
    focus: false,
    bottomHeight: 0,
    scrollTop: 0,
    historyKeyword: '',
    historyDate: '',
    pollingTimer: null,
    form: {
      patientId: null,
      patientName: null,
      doctorId: null,
      doctorName: null,
    },
    avatarUrl: '',
    otherUserAvatarUrl: '',
    lastToolTapAt: 0,
  },

  onToolTap(e) {
    const type = (e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.type) || '';
    const now = Date.now();
    const last = this.data.lastToolTapAt || 0;
    if (now - last < 350) return;
    this.setData({ lastToolTapAt: now });

    const tipMap = {
      image: '已点击图片',
      video: '已点击视频',
      file: '已点击文件'
    };
    wx.showToast({ title: tipMap[type] || '已点击', icon: 'none', duration: 600 });

    if (type === 'image') {
      this.chooseImage();
      return;
    }
    if (type === 'video') {
      this.chooseVideo();
      return;
    }
    if (type === 'file') {
      this.chooseFile();
    }
  },

  bindfocus(e) {
    this.setData({ focus: true, bottomHeight: e.detail.height || 0 });
  },

  bindblur() {
    this.setData({ focus: false, bottomHeight: 0 });
  },

  bindinput(e) {
    this.setData({ content: e.detail.value });
  },

  normalizeUrl(url) {
    if (!url) return DEFAULT_AVATAR;
    if (url.startsWith('/images/')) return url;
    if (url.startsWith('images/')) return '/' + url;
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    if (url.startsWith('/')) return BASE_URL + url;
    return BASE_URL + '/' + url;
  },

  resolveAvatar(rawAvatar) {
    return this.normalizeUrl(rawAvatar || DEFAULT_AVATAR);
  },

  parseMessage(content) {
    const text = content || '';
    if (text.indexOf('[img]') === 0) {
      return { type: 'image', text: '[图片]', url: text.substring(5), fileName: '' };
    }
    if (text.indexOf('[video]') === 0) {
      return { type: 'video', text: '[视频]', url: text.substring(7), fileName: '' };
    }
    if (text.indexOf('[file]') === 0) {
      const payload = text.substring(6);
      const splitIndex = payload.indexOf('|');
      if (splitIndex > -1) {
        return {
          type: 'file',
          text: '[文件]',
          url: payload.substring(0, splitIndex),
          fileName: payload.substring(splitIndex + 1)
        };
      }
      return { type: 'file', text: '[文件]', url: payload, fileName: '附件' };
    }
    return { type: 'text', text, url: '', fileName: '' };
  },

  getReadStorageKey() {
    return 'chat_last_read_' + (this.data.form.patientId || 'unknown');
  },

  markConversationRead() {
    const doctorId = this.data.form.doctorId;
    if (!doctorId) return;
    const latestDoctorMessage = (this.data.rawWords || [])
      .filter(item => item.flag === 1)
      .sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())[0];
    if (!latestDoctorMessage) return;

    const map = wx.getStorageSync(this.getReadStorageKey()) || {};
    map[doctorId] = latestDoctorMessage.time;
    wx.setStorageSync(this.getReadStorageKey(), map);
  },

  getChatQueryParams() {
    return {
      patientId: this.data.form.patientId,
      doctorId: this.data.form.doctorId
    };
  },

  normalizeName(name) {
    return String(name || '').trim().toLowerCase();
  },

  isTargetDoctorRow(row) {
    if (!row) return false;
    const targetDoctorId = this.data.form.doctorId;
    if (targetDoctorId && Number(row.doctorId) === Number(targetDoctorId)) {
      return true;
    }

    const targetDoctorName = this.normalizeName(this.data.form.doctorName);
    const rowDoctorName = this.normalizeName(row.doctorName);
    if (!targetDoctorName || !rowDoctorName) return false;
    return targetDoctorName === rowDoctorName;
  },

  alignDoctorInfoByRows(rows) {
    if (!Array.isArray(rows) || rows.length === 0) return;
    const latest = rows[rows.length - 1] || {};
    const correctedDoctorId = latest.doctorId || this.data.form.doctorId;
    const correctedDoctorName = latest.doctorName || this.data.form.doctorName;
    if (Number(correctedDoctorId) !== Number(this.data.form.doctorId)
      || correctedDoctorName !== this.data.form.doctorName) {
      this.setData({
        'form.doctorId': correctedDoctorId,
        'form.doctorName': correctedDoctorName
      });
    }
  },

  fetchChatRows() {
    const primaryQuery = this.getChatQueryParams();
    return request.get(primaryQuery, 'chat').then((res) => {
      const primaryRows = (res && Array.isArray(res.rows)) ? res.rows : [];
      if (primaryRows.length > 0) {
        return primaryRows;
      }

      // Fallback for inconsistent doctor ID sources: fetch patient history and match target doctor.
      return request.get({ patientId: this.data.form.patientId }, 'chat').then((fallbackRes) => {
        const fallbackRows = (fallbackRes && Array.isArray(fallbackRes.rows)) ? fallbackRes.rows : [];
        return fallbackRows.filter((row) => this.isTargetDoctorRow(row));
      });
    });
  },

  load() {
    this.fetchChatRows().then((rows) => {
      if (!Array.isArray(rows)) {
        this.setData({ rawWords: [], words: [] });
        return;
      }

      this.alignDoctorInfoByRows(rows);

      const words = rows.map((element, index) => {
        const parsed = this.parseMessage(element.content);
        const fromDoctor = Number(element.direction) === 1;
        return {
          name: fromDoctor ? this.data.form.doctorName : this.data.form.patientName,
          avatarUrl: fromDoctor ? this.resolveAvatar(this.data.otherUserAvatarUrl) : this.resolveAvatar(this.data.avatarUrl),
          time: element.time,
          content: parsed.text,
          rawContent: element.content,
          msgType: parsed.type,
          msgUrl: parsed.url,
          fileName: parsed.fileName,
          flag: element.direction,
          id: element.id || `${element.time}_${index}`
        };
      });

      this.setData({ rawWords: words }, () => {
        this.applyHistoryFilter();
        this.markConversationRead();
        this.setData({ scrollTop: 999999 });
      });
    }).catch(() => {
      this.setData({ rawWords: [], words: [] });
      wx.showToast({ title: '历史消息加载失败', icon: 'none' });
    });
  },

  applyHistoryFilter() {
    const keyword = (this.data.historyKeyword || '').trim();
    const date = this.data.historyDate;
    let list = [...(this.data.rawWords || [])];

    if (keyword) {
      list = list.filter(item => (item.content || '').includes(keyword)
        || (item.fileName || '').includes(keyword)
        || (item.rawContent || '').includes(keyword));
    }

    if (date) {
      list = list.filter(item => (item.time || '').startsWith(date));
    }

    this.setData({ words: list });
  },

  onHistoryKeywordInput(e) {
    this.setData({ historyKeyword: e.detail.value }, () => this.applyHistoryFilter());
  },

  onHistoryDateChange(e) {
    this.setData({ historyDate: e.detail.value }, () => this.applyHistoryFilter());
  },

  clearHistoryFilter() {
    this.setData({ historyKeyword: '', historyDate: '' }, () => this.applyHistoryFilter());
  },

  sendMessageContent(messageContent) {
    if (!messageContent) return;
    request.chat({
      ...this.data.form,
      content: messageContent,
      direction: 2
    }).then(() => {
      this.setData({ content: '' });
      this.load();
    }).catch(() => {
      wx.showToast({ title: '发送失败', icon: 'none' });
    });
  },

  sendOut() {
    const text = (this.data.content || '').trim();
    if (!text) return;
    this.sendMessageContent(text);
  },

  uploadAndSend(filePath, type, fileName = '') {
    const token = wx.getStorageSync('token');
    wx.uploadFile({
      url: BASE_URL + '/common/upload',
      filePath,
      name: 'file',
      header: token ? { Authorization: 'Bearer ' + token } : {},
      success: (uploadRes) => {
        let result = {};
        try {
          result = JSON.parse(uploadRes.data);
        } catch (e) {
          wx.showToast({ title: '上传失败', icon: 'none' });
          return;
        }
        if (result.code !== 200 || !result.url) {
          wx.showToast({ title: '上传失败', icon: 'none' });
          return;
        }
        const url = this.normalizeUrl(result.url);
        if (type === 'image') {
          this.sendMessageContent('[img]' + url);
        } else if (type === 'video') {
          this.sendMessageContent('[video]' + url);
        } else {
          this.sendMessageContent('[file]' + url + '|' + (fileName || '附件'));
        }
      },
      fail: () => wx.showToast({ title: '上传失败', icon: 'none' })
    });
  },

  handlePickerFail(err, pickerName) {
    const msg = (err && err.errMsg) ? err.errMsg : '';
    if (msg.includes('cancel')) return;
    if (msg.includes('auth deny') || msg.includes('authorize no response')) {
      wx.showModal({
        title: '需要授权',
        content: '请在设置中允许访问相册/相机后重试',
        showCancel: false
      });
      return;
    }
    if (msg.includes('can not be invoked in IDE') || msg.includes('not supported')) {
      wx.showToast({ title: pickerName + '当前环境不支持', icon: 'none' });
      return;
    }
    wx.showToast({ title: pickerName + '失败', icon: 'none' });
  },

  chooseImage() {
    wx.showLoading({ title: '打开图片选择', mask: false });
    if (wx.canIUse && wx.canIUse('chooseMedia')) {
      wx.chooseMedia({
        count: 1,
        mediaType: ['image'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const file = res.tempFiles && res.tempFiles[0];
          if (!file) return;
          wx.hideLoading();
          this.uploadAndSend(file.tempFilePath, 'image');
        },
        fail: (err) => {
          wx.hideLoading();
          this.handlePickerFail(err, '选择图片');
        },
        complete: () => wx.hideLoading()
      });
      return;
    }

    wx.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      success: (res) => {
        const path = res.tempFilePaths && res.tempFilePaths[0];
        if (!path) return;
        wx.hideLoading();
        this.uploadAndSend(path, 'image');
      },
      fail: (err) => {
        wx.hideLoading();
        this.handlePickerFail(err, '选择图片');
      },
      complete: () => wx.hideLoading()
    });
  },

  chooseVideo() {
    wx.showLoading({ title: '打开视频选择', mask: false });
    if (wx.canIUse && wx.canIUse('chooseMedia')) {
      wx.chooseMedia({
        count: 1,
        mediaType: ['video'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const file = res.tempFiles && res.tempFiles[0];
          if (!file) return;
          wx.hideLoading();
          this.uploadAndSend(file.tempFilePath, 'video');
        },
        fail: (err) => {
          wx.hideLoading();
          this.handlePickerFail(err, '选择视频');
        },
        complete: () => wx.hideLoading()
      });
      return;
    }

    wx.chooseVideo({
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      success: (res) => {
        if (!res || !res.tempFilePath) return;
        wx.hideLoading();
        this.uploadAndSend(res.tempFilePath, 'video');
      },
      fail: (err) => {
        wx.hideLoading();
        this.handlePickerFail(err, '选择视频');
      },
      complete: () => wx.hideLoading()
    });
  },

  chooseFile() {
    wx.showLoading({ title: '打开文件选择', mask: false });
    if (!(wx.canIUse && wx.canIUse('chooseMessageFile'))) {
      wx.hideLoading();
      wx.showToast({ title: '当前基础库不支持文件选择', icon: 'none' });
      return;
    }

    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0];
        if (!file) return;
        wx.hideLoading();
        this.uploadAndSend(file.path, 'file', file.name || '附件');
      },
      fail: (err) => {
        wx.hideLoading();
        this.handlePickerFail(err, '选择文件');
      },
      complete: () => wx.hideLoading()
    });
  },

  startPolling() {
    this.stopPolling();
    const timer = setInterval(() => this.load(), 5000);
    this.setData({ pollingTimer: timer });
  },

  stopPolling() {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer);
      this.setData({ pollingTimer: null });
    }
  },

  onLoad(options) {
    const loginPatientInfo = app.globalData.patientInfo;
    if (!loginPatientInfo || !loginPatientInfo.patientId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => wx.reLaunch({ url: '/pages/login/login' }), 1000);
      return;
    }

    const doctorId = Number(options.doctorId || 0);
    const doctorName = decodeURIComponent(options.doctorName || '医生');
    const doctorAvatar = decodeURIComponent(options.doctorAvatar || '');

    this.setData({
      'form.patientId': loginPatientInfo.patientId,
      'form.patientName': loginPatientInfo.patientName,
      'form.doctorId': doctorId,
      'form.doctorName': doctorName,
      avatarUrl: this.resolveAvatar(loginPatientInfo.avatarUrl || loginPatientInfo.avatar),
      otherUserAvatarUrl: this.resolveAvatar(doctorAvatar)
    });

    wx.setNavigationBarTitle({ title: doctorName });
    this.load();
    this.startPolling();
  },

  onHide() {
    this.stopPolling();
  },

  onUnload() {
    this.stopPolling();
  },

  onPullDownRefresh() {
    this.load();
    wx.stopPullDownRefresh();
  }
});
