// index.js
Page({
  async getPhoneNumber(e) {
    const {
      cloudID
    } = e.detail;
    if (cloudID) {
      let {
        result
      } = await this.step(cloudID);
      console.log(result);
    }
  },

});