// pages/chat/chat.js
import request from '../../api/requests'
const app = getApp();
const BASE_URL = 'http://localhost:8080';

Page({
  data: {
    isLogin: false,
    words: [],
    rawWords: [],
    allChats: [],
    users: [], // 这里将存储 SysUser 对象列表
    conversationList: [],
    filteredConversationList: [],
    userNameList: [], 
    form: {
      patientId: null,      
      patientName: null,    
      doctorId: null,       // 【修改】对方用户的 userId
      doctorName: null,     // 【修改】对方用户的 nickName
    },
    content: null,
    avatarUrl: '', // 当前登录用户的头像
    otherUserAvatarUrl: '', // 对方用户的头像
    theIndex: -1,
    title: '请选择医生',
    focus: false,
    bottomHeight: 0,
    searchDoctorKeyword: '',
    historyKeyword: '',
    historyDate: '',
    lastReadMap: {},
    pollingTimer: null,
  },
  // 获取焦点 唤起软键盘
  bindfocus(e) {
    this.setData({
      focus: true,
      bottomHeight: e.detail.height //将键盘的高度设置为comment容器与page容器下边界之间的距离。
    })

  },
  // 输入内容
  bindinput(e) {
    this.setData({
      'content': e.detail.value
    })
  },
  // 失去焦点 
  bindblur(e) {
    this.setData({
      bottomHeight: 0,
      focus: false
    })
  },
  /**
   * 获取所有普通用户列表 (SysUser 列表)
   */
  getUserList() {
    request.getAllNormalUsers().then((res) => {
      if (res.code === 200 && res.data) {
        // 后端返回的是标准的 SysUser 列表
        const userList = res.data;

        this.setData({
          users: userList
        }, () => {
          this.refreshConversationSummary();
        });
      }
    })
  },

  normalizeUrl(url) {
    if (!url) return '/images/tabs/my-grey.png';
    if (url.startsWith('/images/')) return url;
    if (url.startsWith('images/')) return '/' + url;
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    if (url.startsWith('/')) return BASE_URL + url;
    return BASE_URL + '/' + url;
  },

  getReadStorageKey() {
    return 'chat_last_read_' + (this.data.form.patientId || 'unknown');
  },

  parseTimeMillis(timeText) {
    if (!timeText) return 0;
    if (typeof timeText === 'number') return timeText;
    const normalized = String(timeText).trim().replace(/-/g, '/');
    const millis = Date.parse(normalized);
    return Number.isNaN(millis) ? 0 : millis;
  },

  parseMessage(content) {
    const text = content || '';
    if (text.indexOf('[img]') === 0) {
      const msgUrl = text.substring(5);
      return { type: 'image', text: '[图片]', url: msgUrl, fileName: '' };
    }
    if (text.indexOf('[video]') === 0) {
      const msgUrl = text.substring(7);
      return { type: 'video', text: '[视频]', url: msgUrl, fileName: '' };
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
    return { type: 'text', text: text, url: '', fileName: '' };
  },

  getMessagePreview(content) {
    const parsed = this.parseMessage(content);
    if (parsed.type === 'file') {
      return '[文件] ' + (parsed.fileName || '附件');
    }
    return parsed.text;
  },

  syncDropdownOptions() {
    const options = (this.data.filteredConversationList || []).map((user) => {
      const unread = user.unreadCount > 0 ? ` (${user.unreadCount})` : '';
      return {
        text: (user.nickName || '未知用户') + unread,
        value: user.userId
      };
    });
    this.setData({ userNameList: options });
  },

  filterConversations() {
    const keyword = (this.data.searchDoctorKeyword || '').trim().toLowerCase();
    let list = this.data.conversationList || [];
    if (keyword) {
      list = list.filter((item) => (item.nickName || '').toLowerCase().includes(keyword));
    }
    this.setData({ filteredConversationList: list }, () => {
      this.syncDropdownOptions();
    });
  },

  refreshConversationSummary() {
    const patientId = this.data.form.patientId;
    if (!patientId) return;

    request.get({ patientId: patientId }, 'chat').then((res) => {
      const rows = (res && res.rows) ? res.rows : [];
      const readMap = this.data.lastReadMap || {};
      const summaryMap = {};

      rows.forEach((item) => {
        const doctorId = item.doctorId;
        if (!doctorId) return;
        const time = item.time || '';
        if (!summaryMap[doctorId]) {
          summaryMap[doctorId] = {
            latestTime: '',
            latestPreview: '',
            unreadCount: 0
          };
        }
        if (!summaryMap[doctorId].latestTime || this.parseTimeMillis(time) >= this.parseTimeMillis(summaryMap[doctorId].latestTime)) {
          summaryMap[doctorId].latestTime = time;
          summaryMap[doctorId].latestPreview = this.getMessagePreview(item.content);
        }

        if (item.direction === 1) {
          const readTime = readMap[doctorId];
          if (!readTime || this.parseTimeMillis(time) > this.parseTimeMillis(readTime)) {
            summaryMap[doctorId].unreadCount += 1;
          }
        }
      });

      const merged = (this.data.users || []).map((user) => {
        const summary = summaryMap[user.userId] || {};
        const userAvatar = user.avatar || user.avatarUrl || '';
        return {
          ...user,
          avatar: this.normalizeUrl(userAvatar),
          latestTime: summary.latestTime || '',
          lastPreview: summary.latestPreview || '',
          unreadCount: summary.unreadCount || 0
        };
      });

      merged.sort((a, b) => {
        const ta = a.latestTime ? this.parseTimeMillis(a.latestTime) : 0;
        const tb = b.latestTime ? this.parseTimeMillis(b.latestTime) : 0;
        if (tb !== ta) return tb - ta;
        return (a.nickName || '').localeCompare(b.nickName || '');
      });

      this.setData({
        allChats: rows,
        conversationList: merged
      }, () => {
        this.filterConversations();
      });
    });
  },

  markConversationRead(doctorId) {
    if (!doctorId) return;
    const latestDoctorMessage = (this.data.allChats || [])
      .filter(item => item.doctorId === doctorId && item.direction === 1)
      .sort((a, b) => this.parseTimeMillis(b.time) - this.parseTimeMillis(a.time))[0];
    if (!latestDoctorMessage) return;

    const map = { ...(this.data.lastReadMap || {}) };
    map[doctorId] = latestDoctorMessage.time;
    wx.setStorageSync(this.getReadStorageKey(), map);
    this.setData({ lastReadMap: map }, () => {
      this.refreshConversationSummary();
    });
  },

  onDoctorSearchInput(e) {
    const keyword = e.detail;
    this.setData({ searchDoctorKeyword: keyword }, () => {
      this.filterConversations();
    });
  },

  onSelectConversation(e) {
    const doctorId = Number(e.currentTarget.dataset.doctorid);
    this.selectDoctorById(doctorId);
  },

  selectDoctorById(doctorId) {
    const selectedUser = (this.data.users || []).find(user => Number(user.userId) === Number(doctorId));
    if (!selectedUser) return;

    const avatar = encodeURIComponent(this.normalizeUrl(selectedUser.avatar || selectedUser.avatarUrl || ''));
    const doctorName = encodeURIComponent(selectedUser.nickName || '医生');
    wx.navigateTo({
      url: `/pages/chat/detail?doctorId=${selectedUser.userId}&doctorName=${doctorName}&doctorAvatar=${avatar}`
    });
  },

 /**
   * 当选择一个用户时
   */
  change(e) {
    console.log("完整的事件对象e:", e);
    console.log("--- 1. change() 方法被触发 ---");

    // 【【【 关键修改：直接使用 e.detail.value 作为索引，因为它传递了正确的值 】】】
    // 强制将 e.detail.value 转换为数字，确保后续数组索引正确
    const selectedIndex = Number(e.detail); 
    
    // **注意：在某些 Vant 版本中，e.detail 可能直接是 value 值。
    // 我们需要通过打印来确认 e.detail 的结构**
    
    // 假设 Vant 确实把索引值放在了 e.detail 中（这是最常见的非标准 Vant 行为）
    // 如果 e.detail.value 是 undefined，我们尝试用 e.detail 本身
    let finalIndex = e.detail; 
    if (typeof finalIndex !== 'number') {
        finalIndex = Number(e.detail.value); // 再次尝试 value
    }
    if (typeof finalIndex !== 'number' || isNaN(finalIndex)) {
        console.error("致命错误：无法从事件中解析出有效的索引值！");
        return;
    }

    if (typeof finalIndex === 'number' && !isNaN(finalIndex)) {
      const foundById = (this.data.users || []).find(user => Number(user.userId) === Number(finalIndex));
      if (foundById) {
        this.selectDoctorById(foundById.userId);
        return;
      }
    }

    const selectedUser = this.data.users[finalIndex]; // 根据索引获取完整的用户对象

    console.log("最终选中的索引:", finalIndex);
    console.log("选中的用户对象:", selectedUser);

    if (!selectedUser) {
      console.error("错误：无法根据索引找到用户对象！请检查 this.data.users 是否正确。");
      return;
    }

    // 设置数据
    this.setData({
      theIndex: selectedUser.userId,
      title: selectedUser.nickName,
      'form.doctorName': selectedUser.nickName,
      'form.doctorId': selectedUser.userId,
      otherUserAvatarUrl: this.normalizeUrl(selectedUser.avatar)
    });

    console.log("--- 2. setData 完成，准备调用 load() ---");

    // 选中用户后，加载聊天记录
    if (this.data.theIndex !== -1) {
      this.load();
    }
  },

  /**
   * 加载聊天记录
   */
  load() {
    console.log("--- 3. load() 方法被触发 ---");
    console.log("加载聊天记录的参数 form:", this.data.form);

    request.get(this.data.form, 'chat').then((res) => {
      console.log("--- 4. 收到聊天记录响应 ---", res);
      
      if (!res || !res.rows) {
        console.error("后端返回的聊天记录格式不正确！", res);
        return;
      }
      
      const words = [];
      // ... (省略 for 循环，保持原样)
      for (let index = 0; index < res.rows.length; index++) {
        const element = res.rows[index];
        const parsed = this.parseMessage(element.content);
        let aU = '';
        let n = '';
        if (element.direction == 2) {
          aU = this.normalizeUrl(this.data.avatarUrl);
          n = this.data.form.patientName;
        } else {
          aU = this.normalizeUrl(this.data.otherUserAvatarUrl);
          n = this.data.form.doctorName;
        }
        words.push({
          name: n,
          avatarUrl: aU,
          time: element.time,
          content: parsed.text,
          rawContent: element.content,
          msgType: parsed.type,
          msgUrl: parsed.url,
          fileName: parsed.fileName,
          flag: element.direction,
          id: element.id || `${element.time}_${index}`
        });
      }
      this.setData({
        rawWords: words
      }, () => {
        this.applyHistoryFilter();
        this.markConversationRead(this.data.form.doctorId);
      });
      console.log("--- 5. 聊天记录渲染完成 ---");
    }).catch(err => {
      console.error("加载聊天记录的网络请求失败:", err);
    });
  },

  applyHistoryFilter() {
    const keyword = (this.data.historyKeyword || '').trim();
    const date = this.data.historyDate;
    let list = [...(this.data.rawWords || [])];

    if (keyword) {
      list = list.filter(item => {
        return (item.content || '').includes(keyword)
          || (item.fileName || '').includes(keyword)
          || (item.rawContent || '').includes(keyword);
      });
    }

    if (date) {
      list = list.filter(item => (item.time || '').startsWith(date));
    }

    this.setData({ words: list });
  },

  onHistoryKeywordInput(e) {
    this.setData({ historyKeyword: e.detail.value }, () => {
      this.applyHistoryFilter();
    });
  },

  onHistoryDateChange(e) {
    this.setData({ historyDate: e.detail.value }, () => {
      this.applyHistoryFilter();
    });
  },

  clearHistoryFilter() {
    this.setData({ historyKeyword: '', historyDate: '' }, () => {
      this.applyHistoryFilter();
    });
  },

  startPolling() {
    this.stopPolling();
    const timer = setInterval(() => {
      if (!this.data.isLogin || !this.data.form.patientId) return;
      this.refreshConversationSummary();
    }, 5000);
    this.setData({ pollingTimer: timer });
  },

  stopPolling() {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer);
      this.setData({ pollingTimer: null });
    }
  },

  sendMessageContent(messageContent) {
    if (!messageContent || !this.data.form.doctorId) return;
    request.chat({
      ...this.data.form,
      content: messageContent,
      direction: 2
    }).then(res => {
      if (res) {
        this.setData({ content: "" });
        this.load();
        this.refreshConversationSummary();
      }
    }).catch((error) => {
      wx.showToast({
        title: '发送失败',
        icon: 'error',
        duration: 2000
      })
      console.error(error);
    });
  },

  uploadAndSend(filePath, type, fileName = '') {
    const token = wx.getStorageSync('token');
    wx.uploadFile({
      url: BASE_URL + '/common/upload',
      filePath: filePath,
      name: 'file',
      header: token ? { Authorization: 'Bearer ' + token } : {},
      success: (uploadRes) => {
        let result = {};
        try {
          result = JSON.parse(uploadRes.data);
        } catch (err) {
          wx.showToast({ title: '上传响应解析失败', icon: 'none' });
          return;
        }

        if (result.code !== 200 || !result.url) {
          wx.showToast({ title: '上传失败', icon: 'none' });
          return;
        }

        const url = this.normalizeUrl(result.url);
        let payload = '';
        if (type === 'image') {
          payload = '[img]' + url;
        } else if (type === 'video') {
          payload = '[video]' + url;
        } else {
          const name = fileName || '附件';
          payload = '[file]' + url + '|' + name;
        }
        this.sendMessageContent(payload);
      },
      fail: () => {
        wx.showToast({ title: '上传失败', icon: 'none' });
      }
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
    if (this.data.theIndex === -1) return;
    if (wx.canIUse && wx.canIUse('chooseMedia')) {
      wx.chooseMedia({
        count: 1,
        mediaType: ['image'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const file = res.tempFiles && res.tempFiles[0];
          if (!file) return;
          this.uploadAndSend(file.tempFilePath, 'image');
        },
        fail: (err) => this.handlePickerFail(err, '选择图片')
      });
      return;
    }

    wx.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      success: (res) => {
        const path = res.tempFilePaths && res.tempFilePaths[0];
        if (!path) return;
        this.uploadAndSend(path, 'image');
      },
      fail: (err) => this.handlePickerFail(err, '选择图片')
    });
  },

  chooseVideo() {
    if (this.data.theIndex === -1) return;
    if (wx.canIUse && wx.canIUse('chooseMedia')) {
      wx.chooseMedia({
        count: 1,
        mediaType: ['video'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const file = res.tempFiles && res.tempFiles[0];
          if (!file) return;
          this.uploadAndSend(file.tempFilePath, 'video');
        },
        fail: (err) => this.handlePickerFail(err, '选择视频')
      });
      return;
    }

    wx.chooseVideo({
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      success: (res) => {
        if (!res || !res.tempFilePath) return;
        this.uploadAndSend(res.tempFilePath, 'video');
      },
      fail: (err) => this.handlePickerFail(err, '选择视频')
    });
  },

  chooseFile() {
    if (this.data.theIndex === -1) return;
    if (!(wx.canIUse && wx.canIUse('chooseMessageFile'))) {
      wx.showToast({ title: '当前基础库不支持文件选择', icon: 'none' });
      return;
    }

    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0];
        if (!file) return;
        this.uploadAndSend(file.path, 'file', file.name || '附件');
      },
      fail: (err) => this.handlePickerFail(err, '选择文件')
    });
  },

  //
  sendOut() {
    const text = (this.data.content || '').trim();
    if (!text) return;
    this.sendMessageContent(text);
  },
    /**
   * 生命周期函数--监听页面加载
   */
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    // onLoad 中保持为空，所有逻辑移到 onShow 中
  },

  onShow: function () {
    const loginPatientInfo = app.globalData.patientInfo; 
    
    // 【修改】判断条件改为 patientId
    if (loginPatientInfo && loginPatientInfo.patientId) {
        this.setData({
          isLogin: true,
          // 【修改】从 Patient 对象中读取数据
          'form.patientId': loginPatientInfo.patientId,
          'form.patientName': loginPatientInfo.patientName,
          // 【注意】如果 Patient 对象没有头像字段，这里需要给个默认值
          'avatarUrl': this.normalizeUrl(loginPatientInfo.avatarUrl || '/images/svg/user.svg'),
          'lastReadMap': wx.getStorageSync('chat_last_read_' + loginPatientInfo.patientId) || {}
        });
        // 确认登录后，加载【其他用户(SysUser)】列表
        this.getUserList();
        this.startPolling();
    } else {
      // 未登录
      wx.showToast({ title: '请先登录', icon: 'none', duration: 1500 });
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/login/login' });
      }, 1500);
    }
  },

 
  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },



  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {
    this.stopPolling();
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {
    this.stopPolling();
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {
    this.refreshConversationSummary();
    if (this.data.theIndex != -1) {
      this.load()
    }
    wx.stopPullDownRefresh();
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  }
})