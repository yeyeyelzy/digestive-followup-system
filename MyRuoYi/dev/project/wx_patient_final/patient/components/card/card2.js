// components/card/card2.js
Component({
  /**
   * 组件的属性列表
   */
  properties: {
    data: {
      type: Object,
      value: {
      }
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
      height:'', 
  },

  attached: function() {
    // 在组件实例进入页面节点树时执行
    var that = this
    var query = this.createSelectorQuery()
    query.select(".imgs2").boundingClientRect(function(res) {
      that.setData({
        height: res.width  + 'px'
      })
    }).exec()
    console.log(this.properties)
  },

  /**
   * 组件的方法列表
   */
  methods: {

  }
})