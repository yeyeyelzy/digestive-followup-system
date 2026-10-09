// pages/detail/index.js
import request from '../../api/requests'
import recipeRequest from '../../api/recipe'
import commentRequest from '../../api/comment'
import fileRequest from '../../api/file'
Page({

  /**
   * 页面的初始数据
   */
  data: {
    recipe: {},
    comment: [],
    comment_pid: null,
    comment_oid: null,
    placeholder: '发一条友善的评论~',
    focus: false,
    content: '', //文本类容
    bottomHeight: 0, //定义comment容器与page容器下边界之间的距离
    type: {
      'M': '主料',
      'S': '辅料',
      'F': '调料',
    },
    flag: 0,
    colBool: false, // true 数据库为收藏
    likeBool: false, // true 数据库为点赞
    likedNum: 0,
    collectedNum: 0,
    recommend: [],
    onFold: false,
    showFold: false,
    onReady: false,

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    let app = getApp()
    request.getOne(options.id,'recipe').then(res => {
      if (res) {
        console.log(res)
        this.setData({
          recipe: res.data,
        }, () => {
          this.setData({
            'recipe.createTime': this.data.recipe.createTime.substring(5, 10).replace('-', '/')
          })
          // commentRequest.countLikeR(this.data.recipe.recipeId).then(res => {
          //   if (res) {
          //     this.setData({
          //       likedNum: res.data,
          //     })
          //   }
          // })
          // commentRequest.countColR(this.data.recipe.recipeId).then(res => {
          //   if (res) {
          //     this.setData({
          //       collectedNum: res.data,
          //     })
          //   }
          // })
          // commentRequest.isCol({
          //   recipeId: this.data.recipe.recipeId,
          //   userId: app.globalData.userId
          // }).then(res => {
          //   if (res) {
          //     console.log(res)
          //     this.setData({
          //       colBool: res.data
          //     })
          //   }
          // })
          // commentRequest.isLike({
          //   recipeId: this.data.recipe.recipeId,
          //   userId: app.globalData.userId
          // }).then(res => {
          //   if (res) {
          //     this.setData({
          //       likeBool: res.data
          //     })
          //   }
          // })
          // this.loadComment()
          // this.loadRec().then(() => {
          //   for (let i = 0; i < 6; i++) {
          //     this.setData({
          //         ['recommend[' + i + '].createTime']: this.data.recommend[i].createTime.substring(5, 10).replace('-', '/')
          //       }

          //     )
          //   }

          // })

        })
      }
    }).catch((error) => {
      console.error(error);
    })

  },

  loadComment: function () {
    commentRequest.findTree(this.data.recipe.recipeId).then(res => {
      if (res) {
        // that.data.tagData = res.data;
        this.setData({
          comment: res.data
        });
      }
    }).catch((error) => {
      console.error(error);
    })
  },

  loadRec: function () {
    return recipeRequest.findRand().then(res => {
      if (res) {
        this.setData({
          recommend: res.data
        })
      }
    }).catch((error) => {
      console.error(error);
    })


  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
    this.checkFold()
    this.data.onReady = true
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

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
      content: e.detail.value
    })
  },
  // 失去焦点 
  bindblur(e) {
    this.setData({
      bottomHeight: 0,
      comment_pid: null,
      comment_oid: null,
      placeholder: '发一条友善的评论~',
      focus: false
    })
  },


  reply(e) {
    console.log(e)
    let id = e.currentTarget.dataset.id
    let name = e.currentTarget.dataset.name
    this.setData({
      placeholder: '回复 ' + name + ':',
      comment_pid: id,
      comment_oid: id,
      focus: true
    })
    console.log(this.data.comment_oid)
    console.log(this.data.comment_pid)


  },


  //
  sendOut() {
    var app = getApp()
    //调用发送接口
    console.log(this.data.comment_pid)
    commentRequest.saveComment({
      content: this.data.content,
      userId: app.globalData.userId,
      recipeId: this.data.recipe.recipeId,
      pid: this.data.comment_pid,
      originId: this.data.comment_oid,
    }).then(res => {
      if (res) {
        wx.showToast({
          title: '发送成功',
          icon: 'success',
          duration: 2000
        })
        this.setData({
          content: ""
        })
        this.loadComment()

      }
    }).catch((error) => {
      wx.showToast({
        title: '发送失败',
        icon: 'error',
        duration: 2000
      })
      console.error(error);
    })

  },

  scrollToInfo() {
    this.setData({
      flag: 0,
    })
    wx.createSelectorQuery().select('.info').boundingClientRect(res => {


      wx.pageScrollTo({
        selector: ".info",
        duration: 1000
      })
    }).exec()
  },

  scrollToRemarks() {
    this.setData({
      flag: 1,
    })
    wx.createSelectorQuery().select('.remarks').boundingClientRect(res => {

      wx.pageScrollTo({
        selector: ".remarks",
        duration: 1000
      })

    }).exec()
  },

  scrollToRecommend() {
    this.setData({
      flag: 2,
    })
    wx.createSelectorQuery().select('.recommend').boundingClientRect(res => {


      wx.pageScrollTo({
        selector: ".recommend",
        duration: 1000
      })
    }).exec()
  },

  checkFold() {
    const query = wx.createSelectorQuery().in(this);
    query.selectAll(".showArea, .hideArea").boundingClientRect(res => {
      this.setData({
        showFold: res[0].height < res[1].height
      })
    }).exec()
  },
  handleFold() {
    this.setData({
      onFold: !this.onFold,
      showFold: false
    })
  },

  collect(e) {
    var app = getApp()
    commentRequest.col({
      userId: app.globalData.userId,
      recipeId: this.data.recipe.recipeId,
      status: !this.data.colBool,
    }).then((res) => {
      console.log(res)
      commentRequest.countColR(this.data.recipe.recipeId).then(res => {
        if (res) {
          this.setData({
            colBool: !this.data.colBool,
            collectedNum: res.data,
          })
        }
      })
    }).then(() => {
      wx.showToast({
        title: '操作成功！',
        content: '成功',
      })
    })
  },

  like(e) {
    var app = getApp()
    commentRequest.like({
      userId: app.globalData.userId,
      recipeId: this.data.recipe.recipeId,
      status: !this.data.likeBool,
    }).then((res) => {
      console.log(res)
      commentRequest.countLikeR(this.data.recipe.recipeId).then(res => {
        if (res) {
          this.setData({
            likeBool: !this.data.likeBool,
            likedNum: res.data,
          })
        }
      })
    }).then(() => {
      wx.showToast({
        title: '操作成功！',
        content: '成功',
      })
    })
  },
  upload() {
    recipeRequest.getFile(this.data.recipe.recipeId).then(res => {
      console.log(res.data)
      wx.downloadFile({
        url: res.data,
        success(res) {
          console.log(res)
          let data = res.tempFilePath;
          wx.openDocument({
            filePath: data,
            showMenu: true //表示右上角是否有转发按钮
          })
        }
      })
      // fileRequest.download(res.data)
    })
  }
})