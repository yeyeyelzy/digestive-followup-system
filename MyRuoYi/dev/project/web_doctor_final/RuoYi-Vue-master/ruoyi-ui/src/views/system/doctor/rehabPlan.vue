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
        <el-button type="primary" icon="el-icon-search" @click="loadPatients">查询</el-button>
        <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <div class="mapping-note">
      数据时间映射说明：2016-04-15 对齐 2026-03-10，之后按天顺延。当前模块默认展示映射“当日”方案。
      当前映射日期：{{ mappedToday.displayDate }}（源数据日期：{{ mappedToday.sourceDate }}）
      <span class="mapping-note-sub">超出数据范围时，自动按 2016-05-09（映射 2026-04-03）封顶。</span>
    </div>

    <el-table v-loading="loading" :data="patientRows" @row-click="selectPatient">
      <el-table-column label="患者ID" prop="patientId" width="90" />
      <el-table-column label="患者姓名" prop="patientName" width="140" />
      <el-table-column label="当前方案" min-width="300">
        <template slot-scope="scope">
          <span v-if="scope.row.plan">{{ scope.row.plan.planId }} / v{{ scope.row.plan.version }} / {{ scope.row.plan.status }}</span>
          <el-tag
            v-if="scope.row.plan && scope.row.plan.recommendationSource"
            size="mini"
            :type="scope.row.plan.recommendationSource === 'report' ? 'success' : 'info'"
            style="margin-left: 8px;"
          >
            来源: {{ scope.row.plan.recommendationSource === 'report' ? '报告' : '方案' }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="原始方案标识" min-width="220">
        <template slot-scope="scope">
          <span v-if="scope.row.plan && scope.row.plan.dispatchInfo">
            {{ scope.row.plan.dispatchInfo.sourcePlanId }} / v{{ scope.row.plan.dispatchInfo.sourceVersion }}
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template slot-scope="scope">
          <el-button type="text" @click.stop="openLast7Days(scope.row)">近7日</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-card v-if="currentPatient" style="margin-top: 16px;">
      <div slot="header">
        <span>患者 {{ currentPatient.patientName }}（{{ currentPatient.patientId }}）康复方案</span>
      </div>

      <el-row :gutter="12" style="margin-bottom: 12px;">
        <el-col :span="8">
          <el-button type="primary" @click="generatePlan">智能体生成方案</el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="success" @click="revisePlan">保存医生修改</el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="warning" @click="dispatchPlan">一键下发至患者端/家属端</el-button>
        </el-col>
      </el-row>

      <div v-if="isPatientMode" style="margin-bottom: 12px;">
        <el-button-group>
          <el-button
            :type="patientPlanViewMode === 'all' ? 'primary' : 'default'"
            @click="switchPatientPlanView('all')"
          >全部方案</el-button>
          <el-button
            :type="patientPlanViewMode === 'doctor' ? 'primary' : 'default'"
            @click="switchPatientPlanView('doctor')"
          >医生修改</el-button>
        </el-button-group>
      </div>

      <el-form label-width="120px" size="small">
        <el-form-item label="当前方案ID">
          <el-input :value="planIdDisplay" readonly />
        </el-form-item>
        <el-form-item label="方案状态">
          <el-input :value="planStatusDisplay" readonly />
        </el-form-item>
        <el-form-item label="原始方案标识">
          <el-input :value="sourceMarkerDisplay" readonly />
        </el-form-item>
        <el-form-item label="数据来源标识">
          <el-tag :type="recommendationSourceTagType">{{ recommendationSourceDisplay }}</el-tag>
        </el-form-item>
        <el-form-item :label="planContentLabel">
          <el-input type="textarea" :rows="12" v-model="revisedContentText" :readonly="isPatientMode" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog :title="historyTitle" :visible.sync="historyOpen" width="62%">
      <el-table :data="historyRows" size="mini">
        <el-table-column label="映射日期" prop="displayDate" width="120" />
        <el-table-column label="源数据日期" prop="sourceDate" width="120" />
        <el-table-column label="AI方案建议" min-width="280">
          <template slot-scope="scope">
            <span>{{ scope.row.aiText || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="医生修订建议" min-width="280">
          <template slot-scope="scope">
            <span>{{ scope.row.revisedText || '-' }}</span>
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
  getDoctorRehabPlan,
  getDoctorRehabPlanTrace,
  generateDoctorRehabPlan,
  reviseDoctorRehabPlan,
  dispatchDoctorRehabPlan,
  getPatientRehabPlanCurrent,
  getPatientRehabPlanHistory
} from '@/api/system/doctorCenter'

export default {
  name: 'DoctorRehabPlanCenter',
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
      patientRows: [],
      currentPatient: null,
      currentPlan: null,
      revisedContentText: '',
      patientPlanViewMode: 'all',
      historyOpen: false,
      historyTitle: '近7日康复方案',
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
    },
    planIdDisplay() {
      return this.currentPlan ? this.currentPlan.planId : ''
    },
    planStatusDisplay() {
      return this.currentPlan ? this.currentPlan.status : ''
    },
    sourceMarkerDisplay() {
      if (!this.currentPlan) return ''
      const info = this.currentPlan.dispatchInfo || {}
      const sourcePlanId = info.sourcePlanId || this.currentPlan.sourcePlanId || this.currentPlan.planId
      const sourceVersion = info.sourceVersion || this.currentPlan.sourceVersion || this.currentPlan.version
      if (!sourcePlanId && !sourceVersion) return ''
      return `${sourcePlanId || '-'} / v${sourceVersion || '-'}`
    },
    recommendationSourceDisplay() {
      if (!this.currentPlan) return '未知'
      if (this.currentPlan.recommendationSource === 'report') return '报告'
      if (this.currentPlan.recommendationSource === 'plan') return '方案'
      if (this.currentPlan.recommendationSource === 'report_unavailable') return '报告不可用'
      return '未知'
    },
    recommendationSourceTagType() {
      if (!this.currentPlan) return 'info'
      if (this.currentPlan.recommendationSource === 'report') return 'success'
      if (this.currentPlan.recommendationSource === 'plan') return 'info'
      if (this.currentPlan.recommendationSource === 'report_unavailable') return 'warning'
      return 'warning'
    },
    planContentLabel() {
      if (!this.isPatientMode) return '医生修改内容(文本)'
      return this.patientPlanViewMode === 'doctor' ? '医生修改方案(recommendations)' : '智能体方案(recommendations)'
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
      await this.loadPatients()
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
    mapSourceDateByDisplayOffset(offsetFromToday) {
      const displayToday = this.normalizeDisplayDate(new Date())
      const displayRaw = new Date(displayToday.getTime() - offsetFromToday * 24 * 3600 * 1000)
      const display = this.normalizeDisplayDate(displayRaw)
      const dayOffset = Math.floor((display.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const source = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)
      return {
        displayDate: this.formatDate(display),
        sourceDate: this.formatDate(source)
      }
    },
    normalizeDisplayDate(date) {
      if (date.getTime() < this.displayBase.getTime()) return new Date(this.displayBase.getTime())
      if (date.getTime() > this.displayEnd.getTime()) return new Date(this.displayEnd.getTime())
      return date
    },
    resolvePatientSourceCutoffDate() {
      const display = this.normalizeDisplayDate(new Date())
      const dayOffset = Math.floor((display.getTime() - this.displayBase.getTime()) / (24 * 3600 * 1000))
      const normalized = Math.max(0, dayOffset)
      const source = new Date(this.sourceBase.getTime() + normalized * 24 * 3600 * 1000)
      return this.formatDate(source)
    },
    summarizeRecommendations(plan) {
      if (!plan) {
        return { aiText: '-', revisedText: '-' }
      }

      if (Array.isArray(plan.recommendations) && plan.recommendations.length) {
        const recText = plan.recommendations.join('；')
        return {
          aiText: recText,
          revisedText: recText
        }
      }

      const ai = plan.aiPlan || {}
      const revised = (plan.doctorRevisedPlan && plan.doctorRevisedPlan.content) || {}

      const aiList = this.flattenRecommendations(ai)
      const revisedList = this.flattenRecommendations(revised)
      return {
        aiText: aiList.length ? aiList.join('；') : '-',
        revisedText: revisedList.length ? revisedList.join('；') : '-'
      }
    },
    flattenRecommendations(node) {
      const out = []
      const walk = (obj) => {
        if (!obj) return
        if (Array.isArray(obj)) {
          obj.forEach(it => walk(it))
          return
        }
        if (typeof obj !== 'object') return
        if (Array.isArray(obj.recommendations)) {
          obj.recommendations.forEach(it => {
            if (it != null && String(it).trim()) out.push(String(it).trim())
          })
        }
        Object.keys(obj).forEach(k => walk(obj[k]))
      }
      walk(node)
      return Array.from(new Set(out)).slice(0, 4)
    },
    getRecommendationList(plan) {
      if (!plan) return []

      if (Array.isArray(plan.recommendations) && plan.recommendations.length) {
        return plan.recommendations
          .map(it => String(it || '').trim())
          .filter(Boolean)
      }

      const ai = this.flattenRecommendations(plan.aiPlan || {})
      if (ai.length) return ai

      const revised = this.flattenRecommendations((plan.doctorRevisedPlan && plan.doctorRevisedPlan.content) || {})
      return revised
    },
    getDoctorRevisedRecommendationList(plan) {
      if (!plan) return []

      const fromField = Array.isArray(plan.doctorRevisedRecommendations)
        ? plan.doctorRevisedRecommendations.map(it => String(it || '').trim()).filter(Boolean)
        : []
      if (fromField.length) return fromField

      const fromContent = this.flattenRecommendations((plan.doctorRevisedPlan && plan.doctorRevisedPlan.content) || {})
      if (fromContent.length) return fromContent

      return []
    },
    buildRecommendationText(plan) {
      if (
        plan &&
        plan.recommendationSource === 'report' &&
        Array.isArray(plan.recommendations) &&
        plan.recommendations.length
      ) {
        return plan.recommendations
          .map(it => String(it || '').trim())
          .filter(Boolean)
          .join('\n')
      }
      const revisedList = this.getDoctorRevisedRecommendationList(plan)
      const list = revisedList.length ? revisedList : this.getRecommendationList(plan)
      return list.join('\n')
    },
    getPlanTexts(plan) {
      if (!plan) {
        return { aiText: '', doctorText: '' }
      }

      const normalize = (arr) => Array.isArray(arr)
        ? arr.map(it => String(it || '').trim()).filter(Boolean)
        : []

      const aiList = normalize(plan.aiRecommendations)
      let doctorList = normalize(plan.doctorRevisedRecommendations)
      if (!doctorList.length) {
        doctorList = this.flattenRecommendations((plan.doctorRevisedPlan && plan.doctorRevisedPlan.content) || {})
      }
      const fallback = normalize(plan.recommendations)

      return {
        aiText: (aiList.length ? aiList : fallback).join('\n'),
        doctorText: doctorList.join('\n')
      }
    },
    applyPatientPlanView(plan) {
      const texts = this.getPlanTexts(plan)
      if (this.patientPlanViewMode === 'doctor') {
        this.revisedContentText = texts.doctorText || '当前暂无医生修改方案'
        return
      }
      this.revisedContentText = texts.aiText
    },
    switchPatientPlanView(mode) {
      this.patientPlanViewMode = mode === 'doctor' ? 'doctor' : 'all'
      if (this.isPatientMode) {
        this.applyPatientPlanView(this.currentPlan)
      }
    },
    resetQuery() {
      this.query.patientId = ''
      this.query.patientName = ''
      this.loadPatients()
    },
    async resolvePatients() {
      const byId = this.query.patientId || undefined
      const byName = this.query.patientName || undefined
      const resp = await listDoctorAiPatients({ patientId: byId, patientName: byName })
      return resp.data || []
    },
    async loadPatients() {
      this.loading = true
      try {
        if (this.isPatientMode) {
          const cutoffSourceDate = this.resolvePatientSourceCutoffDate()
          const historyResp = await getPatientRehabPlanHistory(this.query.patientId || this.currentUserId || undefined)
          const history = (historyResp.data || [])
            .filter(item => !item.sourceDate || item.sourceDate <= cutoffSourceDate)
            .sort((a, b) => String(b.sourceDate || '').localeCompare(String(a.sourceDate || '')))

          let currentPlan = null
          try {
            const currentResp = await getPatientRehabPlanCurrent(this.query.patientId || this.currentUserId || undefined)
            currentPlan = currentResp.data || null
          } catch (e) {
            currentPlan = null
          }

          if (!currentPlan && history.length) {
            currentPlan = {
              planId: history[0].planId,
              version: history[0].version,
              status: history[0].status,
              recommendationSource: history[0].recommendationSource || 'report',
              recommendations: history[0].recommendations || []
            }
          }

          this.patientRows = [{
            patientId: this.currentUserId,
            patientName: this.currentUserName || '当前患者',
            plan: currentPlan
          }]
          this.currentPatient = this.patientRows[0]
          this.currentPlan = currentPlan
          this.applyPatientPlanView(currentPlan)

          this.historyRows = history.map(item => ({
            displayDate: item.displayDate,
            sourceDate: item.sourceDate,
            aiText: Array.isArray(item.aiRecommendations)
              ? item.aiRecommendations.join('；')
              : (Array.isArray(item.recommendations) ? item.recommendations.join('；') : '-'),
            revisedText: Array.isArray(item.doctorRevisedRecommendations) && item.doctorRevisedRecommendations.length
              ? item.doctorRevisedRecommendations.join('；')
              : '-'
          }))
          return
        }

        const rows = await this.resolvePatients()

        const out = []
        for (const r of rows) {
          try {
            const planResp = await getDoctorRehabPlan(r.patientId)
            out.push({ ...r, plan: planResp.data })
          } catch (e) {
            out.push({ ...r, plan: null })
          }
        }
        this.patientRows = out
      } finally {
        this.loading = false
      }
    },
    async selectPatient(row) {
      this.currentPatient = row
      if (row.plan) {
        this.currentPlan = row.plan
      } else {
        try {
          const planResp = await getDoctorRehabPlan(row.patientId)
          this.currentPlan = planResp.data
        } catch (e) {
          this.currentPlan = null
        }
      }
      if (!this.currentPlan) {
        this.revisedContentText = ''
        return
      }
      if (this.isPatientMode) {
        this.applyPatientPlanView(this.currentPlan)
      } else {
        this.revisedContentText = this.buildRecommendationText(this.currentPlan)
      }
    },
    async generatePlan() {
      if (this.isPatientMode) return this.$modal.msgWarning('患者端不支持生成方案')
      if (!this.currentPatient) return this.$modal.msgWarning('请先选择患者')
      await generateDoctorRehabPlan(this.currentPatient.patientId)
      const latest = await getDoctorRehabPlan(this.currentPatient.patientId)
      this.currentPlan = latest.data
      this.revisedContentText = this.buildRecommendationText(this.currentPlan)
      this.$modal.msgSuccess('已生成智能体方案')
      this.loadPatients()
    },
    async revisePlan() {
      if (this.isPatientMode) return this.$modal.msgWarning('患者端不支持修改方案')
      if (!this.currentPatient || !this.currentPlan) return this.$modal.msgWarning('请先选择患者并生成方案')
      let parsed
      const rawText = (this.revisedContentText || '').trim()

      if (!rawText) {
        return this.$modal.msgWarning('请至少填写一条 recommendations 内容')
      }

      if (rawText.startsWith('{') || rawText.startsWith('[')) {
        try {
          parsed = JSON.parse(rawText)
        } catch (e) {
          return this.$modal.msgError('JSON 格式无效，请检查后重试')
        }
      } else {
        const lines = rawText
          .split(/\r?\n/)
          .map(it => it.trim())
          .filter(Boolean)

        if (!lines.length) {
          return this.$modal.msgWarning('请至少填写一条 recommendations 内容')
        }
        parsed = { recommendations: lines }
      }

      if (Array.isArray(parsed)) {
        parsed = {
          recommendations: parsed
            .map(it => String(it || '').trim())
            .filter(Boolean)
        }
      } else if (typeof parsed === 'string') {
        const text = parsed.trim()
        parsed = { recommendations: text ? [text] : [] }
      }

      if (!parsed || typeof parsed !== 'object') {
        return this.$modal.msgError('医生修改内容格式无效')
      }

      const revisedRecommendations = this.flattenRecommendations(parsed)
      if (!revisedRecommendations.length) {
        return this.$modal.msgWarning('请在修改内容中提供 recommendations，确保患者端可查看医生修改方案')
      }

      if (!Array.isArray(parsed.recommendations) || !parsed.recommendations.length) {
        parsed = {
          ...parsed,
          recommendations: revisedRecommendations
        }
      }

      const resp = await reviseDoctorRehabPlan({
        patientId: this.currentPatient.patientId,
        planId: this.currentPlan.planId,
        revisedContent: parsed,
        sourcePlanId: this.currentPlan.planId,
        sourceVersion: this.currentPlan.version
      })
      this.currentPlan = resp.data
      this.revisedContentText = this.buildRecommendationText(this.currentPlan)
      this.$modal.msgSuccess('医生方案修改已保存')
      this.loadPatients()
    },
    async dispatchPlan() {
      if (this.isPatientMode) return this.$modal.msgWarning('患者端不支持下发方案')
      if (!this.currentPatient || !this.currentPlan) return this.$modal.msgWarning('请先选择患者并准备方案')
      const resp = await dispatchDoctorRehabPlan(this.currentPatient.patientId, this.currentPlan.planId)
      this.currentPlan = resp.data || this.currentPlan
      try {
        const traceResp = await getDoctorRehabPlanTrace(this.currentPatient.patientId, this.currentPlan.planId)
        const trace = traceResp.data || {}
        this.currentPlan.dispatchInfo = {
          sourcePlanId: trace.sourcePlanId,
          sourceVersion: trace.sourceVersion,
          dispatchedPlanId: trace.dispatchedPlanId,
          dispatchedVersion: trace.dispatchedVersion,
          dispatchTime: trace.dispatchTime,
          dispatchScene: trace.dispatchScene
        }
      } catch (e) {
        // Ignore trace API failures to avoid blocking dispatch success flow.
      }
      this.$modal.msgSuccess('已下发至患者端和家属端')
      this.loadPatients()
    },
    async openLast7Days(row) {
      if (this.isPatientMode) {
        this.historyTitle = '历史康复方案'
        this.historyOpen = true
        return
      }
      let plan = row.plan
      if (!plan) {
        try {
          const planResp = await getDoctorRehabPlan(row.patientId)
          plan = planResp.data
        } catch (e) {
          plan = null
        }
      }
      const summary = this.summarizeRecommendations(plan)
      const rows = []
      for (let i = 0; i < 7; i++) {
        rows.push({
          ...this.mapSourceDateByDisplayOffset(i),
          aiText: summary.aiText,
          revisedText: summary.revisedText
        })
      }
      this.historyTitle = `患者 ${row.patientName}（${row.patientId}）近7日康复方案`
      this.historyRows = rows
      this.historyOpen = true
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
