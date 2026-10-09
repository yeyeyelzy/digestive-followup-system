<template>
  <div class="app-container">
    <el-form :inline="true" size="small" label-width="80px">
      <el-form-item label="患者ID">
        <el-input v-model="query.patientId" placeholder="如: 10" clearable />
      </el-form-item>
      <el-form-item label="患者姓名">
        <el-input v-model="query.patientName" placeholder="请输入患者姓名" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" @click="loadReports">查询</el-button>
        <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-tabs v-model="activeTab" @tab-click="loadReports">
      <el-tab-pane label="日报" name="daily" />
      <el-tab-pane label="周报" name="weekly" />
      <el-tab-pane label="月报" name="monthly" />
    </el-tabs>

    <div class="mapping-note">
      数据时间映射说明：2016-04-15 对齐 2026-03-10，之后按天顺延。
      当前{{ activeTabLabel }}映射：{{ mappedPeriod.displayLabel }}（源数据：{{ mappedPeriod.sourceLabel }}）
      <span class="mapping-note-sub">超出数据范围时，自动按 2016-05-09（映射 2026-04-03）封顶。</span>
    </div>

    <el-table v-loading="loading" :data="reportRows">
      <el-table-column label="患者ID" prop="patientId" width="90" />
      <el-table-column label="患者姓名" prop="patientName" width="140" />
      <el-table-column label="报告类型" prop="reportType" width="100" />
      <el-table-column label="摘要" min-width="320">
        <template slot-scope="scope">
          <span>{{ scope.row.summary || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="时间" min-width="160">
        <template slot-scope="scope">
          <span>{{ scope.row.displayLabel }}</span>
        </template>
      </el-table-column>
      <el-table-column label="PDF" min-width="260">
        <template slot-scope="scope">
          <span>{{ scope.row.pdf || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template slot-scope="scope">
          <el-button type="text" :disabled="!scope.row.pdf" @click="openPdf(scope.row)">点击查看PDF</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="historyTitle" :visible.sync="historyOpen" width="62%">
      <el-table :data="historyRows" size="mini">
        <el-table-column label="映射日期" prop="displayDate" width="120" />
        <el-table-column label="源数据日期" prop="sourceDate" width="120" />
        <el-table-column label="摘要" prop="summary" min-width="260" />
        <el-table-column label="PDF" prop="pdf" min-width="220" />
        <el-table-column label="操作" width="100">
          <template slot-scope="scope">
            <el-button type="text" :disabled="!scope.row.pdf" @click="openHistoryPdf(scope.row)">查看PDF</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import {
  listDoctorAiPatients,
  getDoctorHealthReportDaily,
  getDoctorHealthReportWeekly,
  getDoctorHealthReportMonthly,
  getDoctorIndicatorChangeHistory,
  previewDoctorIndicatorHistoryPdf,
  previewDoctorHealthReportPdf,
  getPatientIndicatorChangeHistory,
  previewPatientIndicatorHistoryPdf
} from '@/api/system/doctorCenter'

export default {
  name: 'DoctorHealthReportCenter',
  data() {
    const sourceBase = new Date('2016-04-15T00:00:00')
    const sourceEnd = new Date('2016-05-09T00:00:00')
    const displayBase = new Date('2026-03-10T00:00:00')
    const daySpan = Math.floor((sourceEnd.getTime() - sourceBase.getTime()) / (24 * 3600 * 1000))
    const displayEnd = new Date(displayBase.getTime() + daySpan * 24 * 3600 * 1000)
    return {
      loading: false,
      sourceBase,
      sourceEnd,
      displayBase,
      displayEnd,
      activeTab: 'daily',
      query: {
        patientId: '',
        patientName: ''
      },
      isPatientMode: false,
      currentUserId: null,
      currentUserName: '',
      reportRows: [],
      historyOpen: false,
      historyTitle: '近7日健康报告',
      historyRows: []
    }
  },
  computed: {
    activeTabLabel() {
      if (this.activeTab === 'weekly') return '周报'
      if (this.activeTab === 'monthly') return '月报'
      return '日报'
    },
    mappedPeriod() {
      const today = this.normalizeDisplayDate(new Date())
      const dayOffset = Math.floor((today.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const sourceToday = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)

      if (this.activeTab === 'weekly') {
        const displayStart = new Date(today.getTime() - 6 * 24 * 3600 * 1000)
        const sourceStart = new Date(sourceToday.getTime() - 6 * 24 * 3600 * 1000)
        return {
          displayLabel: `${this.formatDate(displayStart)} ~ ${this.formatDate(today)}`,
          sourceLabel: `${this.formatDate(sourceStart)} ~ ${this.formatDate(sourceToday)}`
        }
      }

      if (this.activeTab === 'monthly') {
        return {
          displayLabel: `${today.getFullYear()}-${`${today.getMonth() + 1}`.padStart(2, '0')}`,
          sourceLabel: `${sourceToday.getFullYear()}-${`${sourceToday.getMonth() + 1}`.padStart(2, '0')}`
        }
      }

      return {
        displayLabel: this.formatDate(today),
        sourceLabel: this.formatDate(sourceToday)
      }
    }
  },
  created() {
    this.query.patientId = this.$route.query.patientId || ''
    this.query.patientName = this.$route.query.patientName || ''
    this.initializePage()
  },
  methods: {
    async initializePage() {
      await this.detectMode()
      await this.loadReports()
    },
    async detectMode() {
      try {
        const info = await request({ url: '/getInfo', method: 'get' })
        this.currentUserId = info && info.user ? info.user.userId : null
        this.currentUserName = info && info.user ? info.user.userName : ''
      } catch (e) {
        this.currentUserId = null
        this.currentUserName = ''
      }

      const routePath = this.$route && this.$route.path ? this.$route.path : ''
      const routeName = this.$route && this.$route.name ? String(this.$route.name) : ''
      const isDoctorRoute = routePath.indexOf('/system/doctor') === 0 || routePath.indexOf('/doctor-') === 0 || routeName.indexOf('router-doctor') === 0
      if (isDoctorRoute) {
        this.isPatientMode = false
        return
      }

      try {
        const p = await request({ url: '/api/patient/getInfo', method: 'get' })
        this.isPatientMode = !!p
        if (p && p.data && p.data.patientName) {
          this.currentUserName = p.data.patientName
        }
      } catch (e) {
        this.isPatientMode = false
      }
    },
    normalizeDisplayDate(date) {
      if (date.getTime() < this.displayBase.getTime()) return new Date(this.displayBase.getTime())
      if (date.getTime() > this.displayEnd.getTime()) return new Date(this.displayEnd.getTime())
      return date
    },
    selectReportApi(period) {
      if (period === 'weekly') return getDoctorHealthReportWeekly
      if (period === 'monthly') return getDoctorHealthReportMonthly
      return getDoctorHealthReportDaily
    },
    formatDate(d) {
      const y = d.getFullYear()
      const m = `${d.getMonth() + 1}`.padStart(2, '0')
      const day = `${d.getDate()}`.padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    resolvePatientSourceCutoffDate() {
      const display = this.normalizeDisplayDate(new Date())
      const dayOffset = Math.floor((display.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const source = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)
      return this.formatDate(source)
    },
    resetQuery() {
      this.query.patientId = ''
      this.query.patientName = ''
      this.loadReports()
    },
    async resolvePatients() {
      const resp = await listDoctorAiPatients({
        patientId: this.query.patientId || undefined,
        patientName: this.query.patientName || undefined
      })
      return resp.data || []
    },
    async loadReports() {
      this.loading = true
      try {
        if (this.isPatientMode) {
          const maxSourceDate = this.resolvePatientSourceCutoffDate()
          const resp = await getPatientIndicatorChangeHistory(this.query.patientId || this.currentUserId || undefined, this.activeTab)
          const rows = (resp.data || [])
            .filter(item => !item.sourceDate || item.sourceDate <= maxSourceDate)
            .map(item => ({
              patientId: item.patientId || this.currentUserId,
              patientName: this.currentUserName || '当前患者',
              reportType: this.activeTab,
              summary: Array.isArray(item.recommendations) && item.recommendations.length
                ? item.recommendations.join('；')
                : (item.pdf ? '已生成PDF报告' : '暂无可用PDF报告'),
              displayLabel: item.displayDate || item.reportDate || '-',
              sourceDate: item.sourceDate,
              pdf: item.pdf,
              indicator: item
            }))
            .sort((a, b) => String(b.sourceDate || '').localeCompare(String(a.sourceDate || '')))
          this.reportRows = rows
          return
        }

        const patients = await this.resolvePatients()
        const reportApi = this.selectReportApi(this.activeTab)

        const rows = []
        for (const p of patients) {
          let indicator = {}
          try {
            const resp = await reportApi(p.patientId)
            indicator = resp.data || {}
          } catch (e) {
            continue
          }

          const summary = indicator.pdf ? '已生成PDF报告，可用于健康报告中心展示' : '暂无可用PDF报告'

          rows.push({
            patientId: p.patientId,
            patientName: p.patientName,
            reportType: this.activeTab,
            summary,
            displayLabel: this.mappedPeriod.displayLabel,
            sourceLabel: this.mappedPeriod.sourceLabel,
            pdf: indicator.pdf,
            indicator
          })
        }
        this.reportRows = rows
      } finally {
        this.loading = false
      }
    },
    async openPdf(row) {
      try {
        const fileData = this.isPatientMode
          ? await previewPatientIndicatorHistoryPdf(row.patientId, row.sourceDate, row.reportType)
          : await previewDoctorHealthReportPdf(row.patientId, row.reportType)
        const blob = fileData instanceof Blob ? fileData : new Blob([fileData], { type: 'application/pdf' })

        if (blob.type && blob.type.indexOf('application/json') >= 0) {
          const text = await blob.text()
          let msg = 'PDF预览失败'
          try {
            const err = JSON.parse(text)
            msg = err.msg || msg
          } catch (e) {
            // Ignore parse errors and use fallback message.
          }
          this.$modal.msgError(msg)
          return
        }

        const pdfUrl = URL.createObjectURL(blob)
        const win = window.open(pdfUrl, '_blank')
        if (!win) {
          this.$modal.msgWarning('浏览器阻止了新窗口，请允许弹窗后重试')
          URL.revokeObjectURL(pdfUrl)
          return
        }
        setTimeout(() => URL.revokeObjectURL(pdfUrl), 60000)
      } catch (e) {
        this.$modal.msgError('PDF预览失败，请稍后重试')
      }
    },
    async openLast7Days(row) {
      this.historyTitle = `患者 ${row.patientName}（${row.patientId}）近7日健康报告`
      try {
        let rows = []
        if (this.isPatientMode) {
          const resp = await getPatientIndicatorChangeHistory(row.patientId, this.activeTab)
          rows = resp.data || []
        } else {
          const resp = await getDoctorIndicatorChangeHistory(row.patientId, this.activeTab)
          rows = resp.data || []
        }

        this.historyRows = rows
          .map(item => ({
            patientId: row.patientId,
            patientName: row.patientName,
            reportType: this.activeTab,
            displayDate: item.displayDate || item.reportDate || '-',
            sourceDate: item.sourceDate || '-',
            summary: Array.isArray(item.recommendations) && item.recommendations.length
              ? item.recommendations.join('；')
              : (item.pdf ? '已生成PDF报告' : '暂无可用PDF报告'),
            pdf: item.pdf
          }))
          .sort((a, b) => String(b.sourceDate || '').localeCompare(String(a.sourceDate || '')))
          .slice(0, 7)
        this.historyOpen = true
      } catch (e) {
        this.$modal.msgError('近7日记录加载失败')
      }
    },
    async openHistoryPdf(row) {
      try {
        const fileData = this.isPatientMode
          ? await previewPatientIndicatorHistoryPdf(row.patientId, row.sourceDate, row.reportType)
          : await previewDoctorIndicatorHistoryPdf(row.patientId, row.sourceDate, row.reportType)
        const blob = fileData instanceof Blob ? fileData : new Blob([fileData], { type: 'application/pdf' })

        if (blob.type && blob.type.indexOf('application/json') >= 0) {
          const text = await blob.text()
          let msg = 'PDF预览失败'
          try {
            const err = JSON.parse(text)
            msg = err.msg || msg
          } catch (e) {
            // Ignore parse errors and use fallback message.
          }
          this.$modal.msgError(msg)
          return
        }

        const pdfUrl = URL.createObjectURL(blob)
        const win = window.open(pdfUrl, '_blank')
        if (!win) {
          this.$modal.msgWarning('浏览器阻止了新窗口，请允许弹窗后重试')
          URL.revokeObjectURL(pdfUrl)
          return
        }
        setTimeout(() => URL.revokeObjectURL(pdfUrl), 60000)
      } catch (e) {
        this.$modal.msgError('PDF预览失败，请稍后重试')
      }
    }
  }
}
</script>

<style scoped>
.mapping-note {
  margin: 8px 0 12px;
  font-size: 12px;
  color: #909399;
}

.mapping-note-sub {
  margin-left: 6px;
}
</style>
