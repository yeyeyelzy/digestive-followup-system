import request from '../../api/requests';

const app = getApp();
const REPORT_CACHE_TTL = 60 * 1000;

Page({
  data: {
    activeTab: 'daily',
    tabList: [
      { key: 'daily', label: '日报' },
      { key: 'weekly', label: '周报' },
      { key: 'monthly', label: '月报' }
    ],
    loading: false,
    list: [],
    trendRows: [],
    sourceDateLabel: ''
  },

  onShow() {
    if (!this.reportCache) {
      this.reportCache = {};
    }
    this.loadIndicator(this.data.activeTab);
  },

  getPatientId() {
    const info = app.globalData.patientInfo || {};
    return info.patientId || null;
  },

  formatDate(d) {
    const y = d.getFullYear();
    const m = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    return `${y}-${m}-${day}`;
  },

  buildSourceDateLabel(reportDate, period) {
    if (!reportDate) return '-';
    if (period === 'weekly') {
      return `源数据周期: ${reportDate}`;
    }
    if (period === 'monthly') {
      return `源数据月份: ${reportDate}`;
    }
    return `源数据日期: ${reportDate}`;
  },

  parseSourceDateFromReportDate(reportDate, period) {
    if (!reportDate) return '';
    const text = String(reportDate).trim();
    if (!text) return '';

    if (period === 'weekly') {
      const start = text.split('~')[0].trim();
      return /^\d{4}-\d{2}-\d{2}$/.test(start) ? start : '';
    }

    if (period === 'monthly') {
      if (/^\d{4}-\d{2}$/.test(text)) {
        return `${text}-01`;
      }
      if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
        return text;
      }
      return '';
    }

    return /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : '';
  },

  async loadHealthReportFallback(patientId, period) {
    let req = null;
    if (period === 'weekly') req = request.getPatientHealthReportWeekly;
    if (period === 'monthly') req = request.getPatientHealthReportMonthly;
    if (!req) return [];

    const res = await req(patientId);
    const data = (res && res.data) || {};
    const reportDate = data.reportDate || '';
    const sourceDate = this.parseSourceDateFromReportDate(reportDate, period);
    return [{
      id: `${period}_${sourceDate || reportDate || 'latest'}_fallback`,
      period,
      fetchedAt: Date.now(),
      reportDate: reportDate || '-',
      sourceDate,
      sourceDateLabel: this.buildSourceDateLabel(reportDate || sourceDate || '-', period),
      pdf: data.pdf || '',
      recommendations: Array.isArray(data.recommendations) ? data.recommendations : []
    }];
  },

  rebuildList(source) {
    const list = (Array.isArray(source) ? source : [])
      .filter(it => (it.period || 'daily') === this.data.activeTab)
      .sort((a, b) => (b.fetchedAt || 0) - (a.fetchedAt || 0));
    this.setData({ list });
  },

  buildSparkline(values) {
    const blocks = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
    const arr = (Array.isArray(values) ? values : []).map(n => Number(n)).filter(n => Number.isFinite(n));
    if (!arr.length) return '-';
    const min = Math.min(...arr);
    const max = Math.max(...arr);
    if (max === min) return blocks[3].repeat(Math.min(12, arr.length));
    return arr.slice(-12).map(v => {
      const idx = Math.max(0, Math.min(7, Math.round(((v - min) / (max - min)) * 7)));
      return blocks[idx];
    }).join('');
  },

  async loadTrendFallback(patientId) {
    try {
      const res = await request.zhexian(patientId);
      const data = (res && res.data) || {};
      const rows = [
        { key: 'NtProbnpList', label: 'NT-proBNP', values: data.NtProbnpList || [] },
        { key: 'LVEFList', label: 'LVEF', values: data.LVEFList || [] },
        { key: 'CPET1List', label: '峰值公斤摄氧量', values: data.CPET1List || [] },
        { key: 'CPET2List', label: '无氧公斤摄氧量', values: data.CPET2List || [] },
        { key: 'PeakHeartRateList', label: '峰值心率', values: data.PpeakHeartRateList || [] }
      ].map(item => ({
        ...item,
        latest: item.values.length ? item.values[item.values.length - 1] : '-',
        trend: this.buildSparkline(item.values)
      }));
      this.setData({ trendRows: rows });
    } catch (e) {
      this.setData({ trendRows: [] });
    }
  },

  onSwitchTab(e) {
    const key = e.currentTarget.dataset.key;
    if (!key || key === this.data.activeTab) return;
    this.setData({ activeTab: key });
    this.loadIndicator(key);
  },

  async loadIndicator(period) {
    const patientId = this.getPatientId();
    if (!patientId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    this.setData({ loading: true });
    try {
      if (period === 'weekly' || period === 'monthly') {
        const cached = this.reportCache && this.reportCache[period];
        if (cached && (Date.now() - cached.timestamp) < REPORT_CACHE_TTL) {
          this.rebuildList(cached.rows || []);
          this.loadTrendFallback(patientId);
          return;
        }

        const res = await request.getPatientIndicatorChangeHistory(patientId, period);
        const rows = Array.isArray(res && res.data) ? res.data : [];
        let mapped = rows.map((it, idx) => ({
          id: `${period}_${it.sourceDate || it.reportDate || 'unknown'}_${idx}`,
          period,
          fetchedAt: it.sourceDate ? new Date(`${it.sourceDate}T12:00:00`).getTime() : Date.now(),
          reportDate: it.displayDate || it.reportDate || '-',
          sourceDate: it.sourceDate || this.parseSourceDateFromReportDate(it.displayDate || it.reportDate || '', period),
          sourceDateLabel: this.buildSourceDateLabel(it.displayDate || it.reportDate || it.sourceDate || '-', period),
          pdf: it.pdf || '',
          recommendations: Array.isArray(it.recommendations) ? it.recommendations : []
        }));

        if (!mapped.length) {
          mapped = await this.loadHealthReportFallback(patientId, period);
        }

        this.reportCache[period] = {
          timestamp: Date.now(),
          rows: mapped
        };
        this.rebuildList(mapped);
        this.loadTrendFallback(patientId);
        return;
      }

      const res = await request.getPatientIndicatorChangeHistory(patientId, period);
      const rows = Array.isArray(res && res.data) ? res.data : [];
      const mapped = rows.map((it, idx) => ({
        id: `${period}_${it.sourceDate || 'unknown'}_${idx}`,
        period,
        fetchedAt: it.sourceDate ? new Date(`${it.sourceDate}T12:00:00`).getTime() : Date.now(),
        reportDate: it.displayDate || '-',
        sourceDate: it.sourceDate || '',
        sourceDateLabel: `源数据日期: ${it.sourceDate || '-'}`,
        pdf: it.pdf || '',
        recommendations: Array.isArray(it.recommendations) ? it.recommendations : []
      }));
      this.rebuildList(mapped);
      this.loadTrendFallback(patientId);
    } catch (err) {
      this.rebuildList([]);
      this.loadTrendFallback(patientId);
      wx.showToast({ title: '报告加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  resolvePdfUrl(pdfPath) {
    if (!pdfPath) return '';
    if (pdfPath.startsWith('http://') || pdfPath.startsWith('https://')) {
      return pdfPath;
    }
    if (pdfPath.startsWith('/')) {
      return `http://localhost:8080${pdfPath}`;
    }
    return '';
  },

  buildHistoryPdfUrl(item) {
    if (!item || !item.sourceDate) return '';
    const period = encodeURIComponent(item.period || this.data.activeTab || 'daily');
    const sourceDate = encodeURIComponent(item.sourceDate);
    return `http://localhost:8080/system/indicator/change/history/pdf?period=${period}&sourceDate=${sourceDate}`;
  },

  openPdf(e) {
    const item = (e && e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.item) || {};
    const pdfPath = item.pdf;
    if (!pdfPath) {
      wx.showModal({
        title: '暂无PDF预览',
        content: '该记录暂无PDF。已在下方展示“图表替代视图”，可直接查看关键指标趋势。',
        showCancel: false
      });
      return;
    }

    let url = this.resolvePdfUrl(pdfPath);
    if (!url) {
      url = this.buildHistoryPdfUrl(item);
    }
    if (!url) {
      wx.showModal({
        title: 'PDF无法直接打开',
        content: '当前PDF路径不可直接下载。请查看下方“图表替代视图”获取同类趋势信息。',
        showCancel: false
      });
      return;
    }

    wx.showLoading({ title: '正在打开', mask: true });
    const token = wx.getStorageSync('token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    wx.downloadFile({
      url,
      header: headers,
      success: (res) => {
        if (res.statusCode !== 200) {
          wx.showToast({ title: 'PDF下载失败', icon: 'none' });
          return;
        }
        wx.openDocument({
          filePath: res.tempFilePath,
          fileType: 'pdf',
          fail: () => wx.showToast({ title: 'PDF打开失败', icon: 'none' })
        });
      },
      fail: () => wx.showToast({ title: 'PDF下载失败', icon: 'none' }),
      complete: () => wx.hideLoading()
    });
  }
});