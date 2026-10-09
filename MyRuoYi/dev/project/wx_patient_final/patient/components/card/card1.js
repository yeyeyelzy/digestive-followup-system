// components/card/card1.js
import commentRequest from '../../api/comment'
Component({
  /**
   * 组件的属性列表
   */

  options: {
    addGlobalClass: true, // 基础库2.2.3开始支持
  },

  properties: {
    data: {
      type: Object,
      value: { }
    },

    ratio: {
      type: Number,
      value: 1
    },

  },

  /**
   * 组件的初始数据
   */
  data: {
    likedNum:0,
    collectedNum:0,
  },
attached:function(){
  
  // commentRequest.countLikeR(this.properties.data.recipeId).then(res => {
  //   if (res) {
  //     this.setData({
  //       likedNum: res.data,
  //     })
  //   }
  // })
  // commentRequest.countColR(this.properties.data.recipeId).then(res => {
  //   if (res) {
  //     this.setData({
  //       collectedNum: res.data,
  //     })
  //   }
  // })
},
  /**
   * 组件的方法列表
   */
  methods: {

  }
})