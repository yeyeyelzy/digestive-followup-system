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
        <el-button type="primary" icon="el-icon-search" @click="loadRiskList">查询</el-button>
        <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-alert title="风险预警排序规则：高风险置顶，中风险居中，低风险置底" type="warning" :closable="false" />
    <div class="mapping-note">
      数据时间映射说明：2016-04-15 对齐 2026-03-10，之后按天顺延。当前页面默认展示映射“当日”风险。
      当前映射日期：{{ mappedToday.displayDate }}（源数据日期：{{ mappedToday.sourceDate }}）
      <span class="mapping-note-sub">超出数据范围时，自动按 2016-05-09（映射 2026-04-03）封顶。</span>
    </div>

    <el-table v-loading="loading" :data="riskRows" style="margin-top: 12px;">
      <el-table-column label="患者ID" prop="patientId" width="90" />
      <el-table-column label="患者姓名" prop="patientName" width="140" />
      <el-table-column label="映射日期" prop="displayDate" width="120" />
      <el-table-column label="源数据日期" prop="sourceDate" width="120" />
      <el-table-column label="风险等级" width="120">
        <template slot-scope="scope">
          <el-tag :type="riskTagType(scope.row.riskLevel)">{{ scope.row.riskLevel }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="心率分布" min-width="220">
        <template slot-scope="scope">
          <span>{{ formatDistribution(scope.row.heartRateDistribution) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="预警占比" min-width="220">
        <template slot-scope="scope">
          <span>{{ formatDistribution(scope.row.warningDistribution) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="说明" prop="description" min-width="260" />
      <el-table-column label="操作" width="120">
        <template slot-scope="scope">
          <el-button type="text" @click="openLast7Days(scope.row)">近7日</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="historyTitle" :visible.sync="historyOpen" width="62%">
      <el-table :data="historyRows" size="mini">
        <el-table-column label="映射日期" prop="displayDate" width="120" />
        <el-table-column label="源数据日期" prop="sourceDate" width="120" />
        <el-table-column label="风险等级" width="100">
          <template slot-scope="scope">
            <el-tag :type="riskTagType(scope.row.riskLevel)">{{ scope.row.riskLevel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="心率分布" min-width="180">
          <template slot-scope="scope">
            <span>{{ formatDistribution(scope.row.heartRateDistribution) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="预警占比" min-width="180">
          <template slot-scope="scope">
            <span>{{ formatDistribution(scope.row.warningDistribution) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="说明" prop="description" min-width="220" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import { getDoctorRiskPredict, getPatientRiskPredictHistory, listDoctorAiPatients } from '@/api/system/doctorCenter'

export default {
  name: 'DoctorRiskAlert',
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
      query: {
        patientId: '',
        patientName: ''
      },
      isPatientMode: false,
      currentUserId: null,
      currentUserName: '',
      riskRows: [],
      historyOpen: false,
      historyTitle: '近7日风险预警',
      historyRows: []
    }
  },
  computed: {
    mappedToday() {
      const today = new Date()
      const dayOffset = Math.floor((today.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const source = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)
      return {
        displayDate: this.formatDate(today),
        sourceDate: this.formatDate(source)
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
      await this.loadRiskList()
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
    formatDate(d) {
      const y = d.getFullYear()
      const m = `${d.getMonth() + 1}`.padStart(2, '0')
      const day = `${d.getDate()}`.padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    normalizeRiskLevel(level) {
      const text = level == null ? '' : String(level).trim().toLowerCase()
      if (text === 'high' || text === '高' || text === '高风险') return 'high'
      if (text === 'medium' || text === 'mid' || text === '中' || text === '中风险') return 'medium'
      if (text === 'low' || text === '低' || text === '低风险') return 'low'
      return text || 'low'
    },
    normalizeDisplayDate(date) {
      if (date.getTime() < this.displayBase.getTime()) return new Date(this.displayBase.getTime())
      if (date.getTime() > this.displayEnd.getTime()) return new Date(this.displayEnd.getTime())
      return date
    },
    mapSourceDateByDisplayOffset(offsetFromToday) {
      const anchor = this.normalizeDisplayDate(new Date())
      const displayRaw = new Date(anchor.getTime() - offsetFromToday * 24 * 3600 * 1000)
      const display = this.normalizeDisplayDate(displayRaw)
      const dayOffset = Math.floor((display.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const source = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)
      return {
        displayDate: this.formatDate(display),
        sourceDate: this.formatDate(source)
      }
    },
    resolvePatientSourceCutoffDate() {
      const display = this.normalizeDisplayDate(new Date())
      const dayOffset = Math.floor((display.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const source = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)
      return this.formatDate(source)
    },
    riskTagType(level) {
      const normalized = this.normalizeRiskLevel(level)
      if (normalized === 'high') return 'danger'
      if (normalized === 'medium') return 'warning'
      return 'success'
    },
    formatDistribution(obj) {
      if (!obj) return '-'
      return Object.keys(obj).map(k => `${k}: ${obj[k]}`).join(' | ')
    },
    resetQuery() {
      this.query.patientId = ''
      this.query.patientName = ''
      this.loadRiskList()
    },
    async resolvePatients() {
      const byId = this.query.patientId || undefined
      const byName = this.query.patientName || undefined
      const resp = await listDoctorAiPatients({ patientId: byId, patientName: byName })
      return resp.data || []
    },
    async loadRiskList() {
      this.loading = true
      try {
        if (this.isPatientMode) {
          const maxSourceDate = this.resolvePatientSourceCutoffDate()
          const resp = await getPatientRiskPredictHistory(this.query.patientId || this.currentUserId || undefined)
          const history = (resp.data || [])
            .filter(row => !row.sourceDate || row.sourceDate <= maxSourceDate)
            .map(row => ({
              ...row,
              patientId: row.patientId || this.currentUserId,
              patientName: this.currentUserName || row.patientName || '当前患者',
              riskLevel: this.normalizeRiskLevel(row.riskLevel)
            }))
            .sort((a, b) => String(b.sourceDate || '').localeCompare(String(a.sourceDate || '')))

          this.riskRows = history
          return
        }

        const patients = await this.resolvePatients()
        const calls = patients.map(p => getDoctorRiskPredict(p.patientId))
        const settled = await Promise.allSettled(calls)

        const rows = []
        settled.forEach((item, idx) => {
          if (item.status !== 'fulfilled') {
            return
          }
          const p = patients[idx]
          const mapped = this.mapSourceDateByDisplayOffset(0)
          const rowData = item.value.data || {}
          const level = this.normalizeRiskLevel(rowData.riskLevel)
          rows.push({
            patientId: p.patientId,
            patientName: p.patientName,
            ...mapped,
            ...rowData,
            riskLevel: level
          })
        })

        const order = { high: 3, medium: 2, low: 1 }
        rows.sort((a, b) => (order[b.riskLevel] || 0) - (order[a.riskLevel] || 0))
        this.riskRows = rows
      } finally {
        this.loading = false
      }
    },
    openLast7Days(row) {
      if (this.isPatientMode) {
        this.historyTitle = '历史风险预警'
        this.historyRows = this.riskRows.slice(0, 30)
        this.historyOpen = true
        return
      }
      this.historyTitle = `患者 ${row.patientName}（${row.patientId}）近7日风险预警`
      const list = []
      for (let i = 0; i < 7; i++) {
        const mapped = this.mapSourceDateByDisplayOffset(i)
        list.push({
          ...row,
          ...mapped
        })
      }
      this.historyRows = list
      this.historyOpen = true
    }
  }
}
</script>

<style scoped>
.mapping-note {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.mapping-note-sub {
  margin-left: 6px;
}
</style>
