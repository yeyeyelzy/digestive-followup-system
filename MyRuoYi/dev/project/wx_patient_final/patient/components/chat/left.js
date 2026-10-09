// components/chat/left.js
Component({
  /**
   * 组件的属性列表
   */
  properties: {
    item: {
      type: Object,
      value: {
        name:'',
        avatarUrl:'',
        time:'',
        content:''
      }
    },
  },

  /**
   * 组件的初始数据
   */
  data: {
    displayAvatar: '/images/tabs/my-grey.png'
  },

  observers: {
    item(newItem) {
      const avatar = (newItem && newItem.avatarUrl) ? newItem.avatarUrl : '/images/tabs/my-grey.png';
      this.setData({ displayAvatar: avatar });
    }
  },

  /**
   * 组件的方法列表
   */
  methods: {
    onAvatarError(e) {
      console.warn('chat-left avatar load failed', {
        src: this.data.displayAvatar,
        name: this.data.item && this.data.item.name,
        detail: e && e.detail
      });
      this.setData({ displayAvatar: '/images/tabs/my-grey.png' });
    },
    previewImage() {
      if (!this.data.item.msgUrl) return;
      wx.previewImage({
        urls: [this.data.item.msgUrl],
        current: this.data.item.msgUrl
      });
    },
    openFile() {
      if (!this.data.item.msgUrl) return;
      wx.downloadFile({
        url: this.data.item.msgUrl,
        success: (res) => {
          if (res.statusCode === 200) {
            wx.openDocument({
              filePath: res.tempFilePath,
              showMenu: true
            });
          } else {
            wx.showToast({ title: '文件下载失败', icon: 'none' });
          }
        },
        fail: () => {
          wx.showToast({ title: '文件打开失败', icon: 'none' });
        }
      });
    }
  }
})