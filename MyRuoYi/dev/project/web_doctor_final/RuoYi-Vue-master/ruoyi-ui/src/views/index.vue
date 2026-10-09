<template>
  <div class="app-container">
    <el-card class="doctor-module-entry" shadow="never">
      <div slot="header">
        <span>医生端智能模块</span>
      </div>
      <el-row :gutter="12">
        <el-col :xs="24" :sm="8">
          <el-button type="danger" plain style="width: 100%;" @click="openRiskAlertAll">风险预警</el-button>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-button type="warning" plain style="width: 100%;" @click="openRehabPlanAll">康复方案</el-button>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-button type="success" plain style="width: 100%;" @click="openHealthReportAll">健康报告</el-button>
        </el-col>
      </el-row>
      <div class="doctor-module-note">支持按患者姓名或患者ID筛选，也可在下方患者列表按人进入对应模块。</div>
    </el-card>

    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="患者姓名" prop="patientName">
        <el-input
          v-model="queryParams.patientName"
          placeholder="请输入患者姓名"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>



    <el-table v-loading="loading" :data="patientList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="患者id" align="center" prop="patientId"></el-table-column>
      <el-table-column label="患者姓名" align="center" prop="patientName"></el-table-column>
      <el-table-column label="患者资料" align="center">
                <template slot-scope="scope">
                      <button @click="gethuanzhe(scope.row.patientName)">查看资料</button>
                </template>
      </el-table-column>
      <el-table-column label="出院小结" align="center">
                <template slot-scope="scope">
                      <button @click="getchuyuanxiaojie(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      <el-table-column label="医嘱" align="center">
                <template slot-scope="scope">
                      <button @click="getyizhu(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      <el-table-column label="复查计划" align="center">
                <template slot-scope="scope">
                      <button @click="getrecovery(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      
      <el-table-column label="随访记录" align="center">
                <template slot-scope="scope">
                      <button @click="getsuifang(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      


      <el-table-column label="行为日记" align="center">
                <template slot-scope="scope">
                      <button @click="getxingweiriji(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      <el-table-column label="饮食日记" align="center">
                <template slot-scope="scope">
                      <button @click="getyinshiriji(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      <el-table-column label="用药日记" align="center">
                <template slot-scope="scope">
                      <button @click="getmedicine(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>
      <el-table-column label="生活方式日记" align="center">
                      <template slot-scope="scope">
                            <button @click="getshenghuofangshi(scope.row.patientName)">查看</button>
                      </template>
      </el-table-column>


      <el-table-column label="聊天" align="center">
                <template slot-scope="scope">
                      <button @click="getchat(scope.row.patientName)">查看</button>
                </template>
      </el-table-column>

      <el-table-column label="风险预警" align="center">
            <template slot-scope="scope">
              <button @click="openRiskAlert(scope.row)">查看</button>
            </template>
      </el-table-column>

      <el-table-column label="康复方案" align="center">
            <template slot-scope="scope">
              <button @click="openRehabPlan(scope.row)">查看</button>
            </template>
      </el-table-column>

      <el-table-column label="健康报告" align="center">
            <template slot-scope="scope">
              <button @click="openHealthReport(scope.row)">查看</button>
            </template>
      </el-table-column>
      
      <el-table-column label="可视化" align="center">
                <template slot-scope="scope">
                      <button @click="getview(scope.row.patientName)">查看</button>
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

   
  </div>
</template>

<script>
import { listPatient, getPatient, delPatient, addPatient, updatePatient } from "@/api/system/patient";

export default {
  name: "Patient",
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
      // 患者管理表格数据
      patientList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        patientName: null,
        avatarUrl: null,
        phoneNumber: null,
        age: null,
        gender: null,
        weight: null,

      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        patientName: [
          { required: true, message: "患者姓名不能为空", trigger: "blur" }
        ],
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询患者管理列表 */
    getList() {
      this.loading = true;
      listPatient(this.queryParams).then(response => {
        this.patientList = response.rows;
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
        patientId: null,
        patientName: null,
        avatarUrl: null,
        phoneNumber: null,
        age: null,
        gender: null,
        weight: null
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
      this.ids = selection.map(item => item.patientId)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加患者管理";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const patientId = row.patientId || this.ids
      getPatient(patientId).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改患者管理";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.patientId != null) {
            updatePatient(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addPatient(this.form).then(response => {
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
      const patientIds = row.patientId || this.ids;
      this.$modal.confirm('是否确认删除患者管理编号为"' + patientIds + '"的数据项？').then(function() {
        return delPatient(patientIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/patient/export', {
        ...this.queryParams
      }, `patient_${new Date().getTime()}.xlsx`)
    },
    //*********************************************************** */
    /** 查看资料 */
    gethuanzhe(name){
      this.$router.push({
        name: "router-patient",
        params: {
          patientName: name
        }
      });
    },
    getrecovery(name){
      this.$router.push({
        name: "router-recovery",
        params: {
          patientName: name
        }
      });
    },
    getshenghuofangshi(name){
      this.$router.push({
        name: "router-living",
        params: {
          patientName: name
        }
      });
    },
    getyinshiriji(name){
      this.$router.push({
        name: "router-diet",
        params: {
          patientName: name
        }
      });
    },
    getchuyuanxiaojie(name){
      this.$router.push({
        name: "router-discharge",
        params: {
          patientName: name
        }
      });
    },
    getchat(name){
      this.$router.push({
        name: "router-chat",
        params: {
          patientName: name
        }
      });
    },
    getxingweiriji(name){
      this.$router.push({
        name: "router-behavior",
        params: {
          patientName: name
        }
      });
    },
    getyizhu(name){
      this.$router.push({
        name: "router-advice",
        params: {
          patientName: name
        }
      });
    },
    getview(name){
      this.$router.push({
        name: "router-visual",
        params: {
          patientName: name
        }
      });
    },
    getsuifang(name){
      this.$router.push({
        name: "router-follow_up",
        params: {
          patientName: name
        }
      });
    },
    getmedicine(name){
      this.$router.push({
        name: "router-medicine",
        params: {
          patientName: name
        }
      });
    },
    openRiskAlertAll() {
      this.$router.push({
        name: "router-doctor-risk-alert"
      })
    },
    openRehabPlanAll() {
      this.$router.push({
        name: "router-doctor-rehab-plan"
      })
    },
    openHealthReportAll() {
      this.$router.push({
        name: "router-doctor-health-report"
      })
    },
    openRiskAlert(row) {
      this.$router.push({
        name: "router-doctor-risk-alert",
        query: {
          patientId: row.patientId,
          patientName: row.patientName
        }
      })
    },
    openRehabPlan(row) {
      this.$router.push({
        name: "router-doctor-rehab-plan",
        query: {
          patientId: row.patientId,
          patientName: row.patientName
        }
      })
    },
    openHealthReport(row) {
      this.$router.push({
        name: "router-doctor-health-report",
        query: {
          patientId: row.patientId,
          patientName: row.patientName
        }
      })
    }
    //****************************************************************** */
 




  }
};
</script>

<style scoped>
.doctor-module-entry {
  margin-bottom: 14px;
}

.doctor-module-note {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}
</style>
