// pages/my/profile/profile.js
import request from '../../api/requests'
import { getInfo } from '../../api/user'
const app = getApp();

Page({
    data: {
        form: {
            phoneNumber: '',
            gender: null,
            age: null,
            avatarUrl: ''
        },
        avatarPreview: '/images/svg/user.svg'
    },

    onLoad: function() {
        this.loadFamilyProfile();
    },

    loadFamilyProfile() {
        getInfo().then(res => {
            if (res.code === 200 && res.data) {
                const info = res.data;
                this.setData({
                    'form.phoneNumber': info.phoneNumber || '',
                    'form.gender': info.gender !== undefined ? Number(info.gender) : null,
                    'form.age': info.age || null,
                    'form.avatarUrl': info.avatar || '',
                    avatarPreview: this.normalizeAvatarUrl(info.avatar)
                });

                app.setGlobalPatientInfo(info);
            }
        }).catch(() => {
            wx.showToast({ title: '加载失败', icon: 'none' });
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
        this.setData({'form.age': Number(e.detail.value)});
    },

    submitForm() {
        const { phoneNumber, age, gender, avatarUrl } = this.data.form;

        if (!/^\d{11}$/.test(phoneNumber)) {
            wx.showToast({ title: '手机号格式错误', icon: 'none' });
            return;
        }

        if (gender === null || !age) {
            wx.showToast({ title: '请填写完整信息', icon: 'none' });
            return;
        }

        const data = {
            phoneNumber: phoneNumber,
            gender: gender,
            age: age,
            avatar: avatarUrl
        };

        request.updateFamilyProfile(data).then(res => {
            if (res.code === 200) {
                wx.showToast({ title: '信息修改成功', icon: 'success' });
                setTimeout(() => { wx.navigateBack(); }, 1000);
            } else {
                wx.showToast({ title: res.msg || '修改失败', icon: 'error' });
            }
        }).catch(() => {
            wx.showToast({ title: '网络请求失败', icon: 'error' });
        });
    }
});
