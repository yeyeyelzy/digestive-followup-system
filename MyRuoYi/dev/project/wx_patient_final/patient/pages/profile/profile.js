// pages/my/profile/profile.js
import request from '../../api/requests' // 确保路径正确
const app = getApp();

Page({
    data: {
        form: {
            phoneNumber: '',
            gender: null, // 0:男, 1:女
            birthday: '',
            weight: null, // double
            avatarUrl: ''
        },
        patientId: null,
        currentDate: new Date().toISOString().slice(0, 10),
        avatarPreview: '/images/svg/user.svg'
    },

    onLoad: function() {
        // 1. 获取当前患者ID
        const loginInfo = app.globalData.patientInfo;
        if (loginInfo && loginInfo.patientId) {
            this.setData({
                patientId: loginInfo.patientId,
                'form.phoneNumber': loginInfo.phonenumber || '' // 预填手机号
            });
            this.loadPatientProfile(loginInfo.patientId);
        } else {
            wx.showToast({ title: '未登录', icon: 'error' });
            setTimeout(() => { wx.reLaunch({ url: '/pages/login/login' }); }, 1000);
        }
    },

    // 加载详细档案信息
    loadPatientProfile(patientId) {
        // 假设你有一个 API 来获取 Patient 详情
        request.getOne(patientId, 'patient').then(res => {
            if (res.code === 200 && res.data) {
                this.setData({
                    'form.gender': res.data.gender,
                    // birthday 可能需要后端提供，这里假设后端不直接提供 DOB，只提供了 age
                    'form.weight': res.data.weight,
                    'form.avatarUrl': res.data.avatarUrl || '',
                    avatarPreview: this.normalizeAvatarUrl(res.data.avatarUrl)
                });
            }
        });
    },

    normalizeAvatarUrl(path) {
        if (!path) return '/images/svg/user.svg';
        if (path.startsWith('http://') || path.startsWith('https://')) return path;
        return `http://localhost:8080${path}`;
    },

    chooseAvatar() {
        wx.chooseImage({
            count: 1,
            sizeType: ['compressed'],
            sourceType: ['album', 'camera'],
            success: (res) => {
                const tempFilePath = res.tempFilePaths[0];
                this.uploadAvatar(tempFilePath);
            }
        });
    },

    uploadAvatar(filePath) {
        const token = wx.getStorageSync('token');
        wx.showLoading({ title: '上传中', mask: true });
        wx.uploadFile({
            url: 'http://localhost:8080/common/upload',
            filePath: filePath,
            name: 'file',
            header: token ? { Authorization: 'Bearer ' + token } : {},
            success: (res) => {
                try {
                    const data = JSON.parse(res.data || '{}');
                    if (data.code === 200 && data.fileName) {
                        this.setData({
                            'form.avatarUrl': data.fileName,
                            avatarPreview: data.url || this.normalizeAvatarUrl(data.fileName)
                        });
                        wx.showToast({ title: '头像上传成功', icon: 'success' });
                    } else {
                        wx.showToast({ title: data.msg || '上传失败', icon: 'none' });
                    }
                } catch (e) {
                    wx.showToast({ title: '上传返回异常', icon: 'none' });
                }
            },
            fail: () => {
                wx.showToast({ title: '头像上传失败', icon: 'none' });
            },
            complete: () => wx.hideLoading()
        });
    },

    bindPhoneNumberInput(e) {
        this.setData({'form.phoneNumber': e.detail.value});
    },
    bindGenderChange(e) {
        // 0=男, 1=女
        this.setData({'form.gender': Number(e.detail.value)});
    },
    bindDateChange(e) {
        this.setData({'form.birthday': e.detail.value});
    },
    bindWeightInput(e) {
        this.setData({'form.weight': Number(e.detail.value)});
    },

    submitForm() {
        const { phoneNumber, birthday, weight, gender, avatarUrl } = this.data.form;

        // 1. 手机号校验 (11位数字)
        if (!/^\d{11}$/.test(phoneNumber)) {
            wx.showToast({ title: '手机号格式错误', icon: 'none' });
            return;
        }

        // 2. 基本校验
        if (gender === null || !birthday || !weight) {
            wx.showToast({ title: '请填写完整信息', icon: 'none' });
            return;
        }

        // 3. 构建请求体 (注意：我们只需要发前端填写的字段)
        const data = {
            phoneNumber: phoneNumber,
            gender: gender,
            birthday: birthday, // 后端 Java 会计算年龄
            weight: weight,
            avatarUrl: avatarUrl
        };

        // 【新增调试】打印你实际要发送的数据
        console.log("准备发送的数据：", data); 
        // 检查：如果所有字段都是 null/undefined/空字符串，后端会认为 body 为空
        if (Object.values(data).every(x => x === null || x === '' || x === undefined)) {
           wx.showToast({ title: '没有信息需要修改', icon: 'none' });
        return;
  }

        // 4. 调用后端 API
        // 假设你在 requests.js 中定义了 updatePatientProfile
        request.updatePatientProfile(data).then(res => {
            if (res.code === 200) {
                wx.showToast({ title: '信息修改成功', icon: 'success' });
                // 刷新 my 页面或返回
                setTimeout(() => { wx.navigateBack(); }, 1000);
            } else {
                wx.showToast({ title: res.msg || '修改失败', icon: 'error' });
            }
        }).catch(() => {
            wx.showToast({ title: '网络请求失败', icon: 'error' });
        });
    }
});
