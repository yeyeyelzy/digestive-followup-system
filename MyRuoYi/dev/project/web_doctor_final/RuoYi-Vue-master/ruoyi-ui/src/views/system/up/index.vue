<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="患者id" prop="patientId">
        <el-input
          v-model="queryParams.patientId"
          placeholder="请输入患者id"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="患者姓名" prop="patientName">
        <el-input
          v-model="queryParams.patientName"
          placeholder="请输入患者姓名"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="日期" prop="date">
        <el-date-picker clearable
          v-model="queryParams.date"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="请选择日期">
        </el-date-picker>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="handleAdd"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="el-icon-edit"
          size="mini"
          :disabled="single"
          @click="handleUpdate"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
        >导出</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="upList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="随访记录id" align="center" prop="followUpId" />
      <el-table-column label="患者id" align="center" prop="patientId" />
      <el-table-column label="患者姓名" align="center" prop="patientName" />
      <el-table-column label="日期" align="center" prop="date" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.date, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="上次健康教育内容" align="center" prop="lastHealthEducation" />
      <el-table-column label="自我报告" align="center" prop="patientConclusion" />
      <el-table-column label="患者症状" align="center" prop="patientSymptom" />
      <el-table-column label="患者压力" align="center" prop="patientPressure" />
      <el-table-column label="患者照护者" align="center" prop="patientSupport" />
      <el-table-column label="临床治疗计划" align="center" prop="clinicalTreatmentPlan" />
      <el-table-column label="随访小结" align="center" prop="summary" />
      <el-table-column label="当前主要护理诊断" align="center" prop="currentPrimaryCareDiagnosis" />
      <el-table-column label="健康指标情况" align="center" prop="healthIndicator" />
      <el-table-column label="更新护理目标" align="center" prop="newNursingGoal" />
      <el-table-column label="护理指导内容" align="center" prop="guidance" />
      <el-table-column label="其他" align="center" prop="note" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
          >修改</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改随访记录管理对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="患者id" prop="patientId">
          <el-input v-model="form.patientId" placeholder="请输入患者id" />
        </el-form-item>
        <el-form-item label="患者姓名" prop="patientName">
          <el-input v-model="form.patientName" placeholder="请输入患者姓名" />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker clearable
            v-model="form.date"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="请选择日期">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="上次健康教育内容" prop="lastHealthEducation">
          <el-input v-model="form.lastHealthEducation" placeholder="请输入上次健康教育内容" />
        </el-form-item>
        <el-form-item label="自我报告" prop="patientConclusion">
          <el-input v-model="form.patientConclusion" placeholder="请输入自我报告" />
        </el-form-item>
        <el-form-item label="患者症状" prop="patientSymptom">
          <el-input v-model="form.patientSymptom" placeholder="请输入患者症状" />
        </el-form-item>
        <el-form-item label="患者压力" prop="patientPressure">
          <el-input v-model="form.patientPressure" placeholder="请输入患者压力" />
        </el-form-item>
        <el-form-item label="患者照护者" prop="patientSupport">
          <el-input v-model="form.patientSupport" placeholder="请输入患者照护者" />
        </el-form-item>
        <el-form-item label="临床治疗计划" prop="clinicalTreatmentPlan">
          <el-input v-model="form.clinicalTreatmentPlan" placeholder="请输入临床治疗计划" />
        </el-form-item>
        <el-form-item label="随访小结" prop="summary">
          <el-input v-model="form.summary" placeholder="请输入随访小结" />
        </el-form-item>
        <el-form-item label="当前主要护理诊断" prop="currentPrimaryCareDiagnosis">
          <el-input v-model="form.currentPrimaryCareDiagnosis" placeholder="请输入当前主要护理诊断" />
        </el-form-item>
        <el-form-item label="健康指标情况" prop="healthIndicator">
          <el-input v-model="form.healthIndicator" placeholder="请输入健康指标情况" />
        </el-form-item>
        <el-form-item label="更新护理目标" prop="newNursingGoal">
          <el-input v-model="form.newNursingGoal" placeholder="请输入更新护理目标" />
        </el-form-item>
        <el-form-item label="护理指导内容" prop="guidance">
          <el-input v-model="form.guidance" placeholder="请输入护理指导内容" />
        </el-form-item>
        <el-form-item label="其他" prop="note">
          <el-input v-model="form.note" placeholder="请输入其他" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { listUp, getUp, delUp, addUp, updateUp } from "@/api/system/up";

export default {
  name: "Up",
  data() {
    return {
      // 遮罩层
      loading: true,
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 随访记录管理表格数据
      upList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        patientId: null,
        patientName: null,
        date: null,
        lastHealthEducation: null,
        patientConclusion: null,
        patientSymptom: null,
        patientPressure: null,
        patientSupport: null,
        clinicalTreatmentPlan: null,
        summary: null,
        currentPrimaryCareDiagnosis: null,
        healthIndicator: null,
        newNursingGoal: null,
        guidance: null,
        note: null
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        patientId: [
          { required: true, message: "患者id不能为空", trigger: "blur" }
        ],
        date: [
          { required: true, message: "日期不能为空", trigger: "blur" }
        ],
      }
    };
  },
  created() {
    this.applyRoutePatientNameOnce();
    this.getList();
  },
  methods: {
    applyRoutePatientNameOnce() {
      const routeName = this.$route && this.$route.params ? this.$route.params.patientName : ''
      if (routeName && !this.queryParams.patientName) {
        this.queryParams.patientName = routeName
      }
    },
    /** 查询随访记录管理列表 */
    getList() {
      this.loading = true;
      listUp(this.queryParams).then(response => {
        this.upList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        followUpId: null,
        patientId: null,
        patientName: null,
        date: null,
        lastHealthEducation: null,
        patientConclusion: null,
        patientSymptom: null,
        patientPressure: null,
        patientSupport: null,
        clinicalTreatmentPlan: null,
        summary: null,
        currentPrimaryCareDiagnosis: null,
        healthIndicator: null,
        newNursingGoal: null,
        guidance: null,
        note: null
      };
      this.resetForm("form");
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.followUpId)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加随访记录管理";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const followUpId = row.followUpId || this.ids
      getUp(followUpId).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改随访记录管理";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.followUpId != null) {
            updateUp(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addUp(this.form).then(response => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const followUpIds = row.followUpId || this.ids;
      this.$modal.confirm('是否确认删除随访记录管理编号为"' + followUpIds + '"的数据项？').then(function() {
        return delUp(followUpIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/up/export', {
        ...this.queryParams
      }, `up_${new Date().getTime()}.xlsx`)
    }
  }
};
</script>
