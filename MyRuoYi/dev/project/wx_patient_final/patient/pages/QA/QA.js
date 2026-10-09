// pages/QA/QA.js
import { getAIAnswer } from '../../api/aiRequest.js';
const app = getApp();

Page({
  data: {
    messageList: [
      { sender: 'ai', content: '您好，我是您的智能健康助手，有什么可以帮您？' }
    ], // 聊天消息列表
    inputValue: '',  // 输入框内容
    scrollToView: '' // 用于控制滚动条位置
  },

  // 绑定输入框输入
  bindInput: function(e) {
    this.setData({
      inputValue: e.detail.value
    });
  },

  // 发送消息
  sendMessage: function() {
    const question = this.data.inputValue.trim();
    if (!question) {
      wx.showToast({ title: '请输入问题', icon: 'none' });
      return;
    }

    // 将用户消息添加到列表
    const userMessage = { sender: 'user', content: question };
    const newMessageList = [...this.data.messageList, userMessage];
    
    this.setData({
      messageList: newMessageList,
      inputValue: '', // 清空输入框
      scrollToView: `msg-${newMessageList.length - 1}` // 滚动到最新消息
    });

    // 调用AI接口获取答案
    getAIAnswer(question).then(answerString => {
      if (answerString) {
        const aiMessage = { sender: 'ai', content: answerString };
        const finalMessageList = [...this.data.messageList, aiMessage];
        
        this.setData({
          messageList: finalMessageList,
          scrollToView: `msg-${finalMessageList.length - 1}`
        });
      } else {
        this.addAIMessage('抱歉，AI没有找到相关答案。');
      }
    }).catch(() => {
        this.addAIMessage('无法连接到AI服务，请检查网络。');
    });
  },

  // 辅助函数，用于添加AI的错误提示
  addAIMessage: function(content) {
    const aiMessage = { sender: 'ai', content: content };
    const finalMessageList = [...this.data.messageList, aiMessage];
    this.setData({
      messageList: finalMessageList,
      scrollToView: `msg-${finalMessageList.length - 1}`
    });
  }
});
