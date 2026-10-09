<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="患者姓名" prop="patientName">
        <el-input
          v-model="queryParams.patientName"
          placeholder="请输入患者姓名"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="用药方案" prop="medicationRegimen">
        <el-input
          v-model="queryParams.medicationRegimen"
          placeholder="请输入用药方案"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="复查计划" prop="reviewPlan">
        <el-input
          v-model="queryParams.reviewPlan"
          placeholder="请输入复查计划"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="注意事项" prop="notice">
        <el-input
          v-model="queryParams.notice"
          placeholder="请输入注意事项"
          clearable
          @keyup.enter.native="handleQuery"
        />
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

    <el-table v-loading="loading" :data="adviceList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="医嘱id" align="center" prop="doctorsAdviceId" />
      <el-table-column label="患者姓名" align="center" prop="patientName" />
      <el-table-column label="用药方案" align="center" prop="medicationRegimen" />
      <el-table-column label="复查计划" align="center" prop="reviewPlan" />
<!--      <el-table-column label="注意事项" align="center" prop="notice" />-->
      <el-table-column label="注意事项" align="center">
        <template slot-scope="scope">
          <el-button @click="openDrawer(scope.row)" size="mini" type="text" icon="el-icon-edit">
            查看注意事项
          </el-button>
        </template>
      </el-table-column>
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

    <el-drawer
      title="详细注意事项"
      :visible.sync="drawer"
      :direction="direction"
      :before-close="handleDrawerClose">
      <div>
        <el-table :data="noticeData" style="width: 100%">
          <el-table-column prop="priority" label="优先级"></el-table-column>
          <el-table-column prop="content" label="内容"></el-table-column>
        </el-table>
      </div>
    </el-drawer>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改医嘱管理对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="患者姓名" prop="patientName">
          <el-input v-model="form.patientName" placeholder="请输入患者姓名" />
        </el-form-item>
        <el-form-item label="用药方案" prop="medicationRegimen">
          <el-input v-model="form.medicationRegimen" placeholder="请输入用药方案" />
        </el-form-item>
        <el-form-item label="复查计划" prop="reviewPlan">
          <el-input v-model="form.reviewPlan" placeholder="请输入复查计划" />
        </el-form-item>
        <el-form-item label="注意事项" prop="notice">
          <el-input v-model="form.notice" placeholder="请输入注意事项" />
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
import { listAdvice, getAdvice, delAdvice, addAdvice, updateAdvice } from "@/api/system/advice";

export default {
  name: "Advice",
  data() {
    return {

      drawer: false,
      direction: 'rtl',
      noticeData:[],
      statements:"",

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
      // 医嘱管理表格数据
      adviceList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        patientName: null,
        medicationRegimen: null,
        reviewPlan: null,
        notice: null
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
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
    handleDrawerClose(){
      this.drawer=false
      this.noticeData=[]
    },
    openDrawer(row){
      this.noticeData = []
      const noticeText = (row && row.notice ? row.notice : "").trim()
      this.statements = noticeText ? noticeText.split(/[；;]+/) : []

      for(let i=0;i<this.statements.length;i++){
        let jsonObj={
          priority:i+1,
          content:this.statements[i]
        }
        this.noticeData.push(jsonObj)
      }
      this.drawer=true
      // console.log(this.statements.length)
      // console.log(this.statements)
    },

    /** 查询医嘱管理列表 */
    getList() {
      this.loading = true;
      listAdvice(this.queryParams).then(response => {
        this.adviceList = response.rows;
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
        doctorsAdviceId: null,
        patientName: null,
        medicationRegimen: null,
        reviewPlan: null,
        notice: null
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
      this.ids = selection.map(item => item.doctorsAdviceId)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加医嘱管理";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const doctorsAdviceId = row.doctorsAdviceId || this.ids
      getAdvice(doctorsAdviceId).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改医嘱管理";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.doctorsAdviceId != null) {
            updateAdvice(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addAdvice(this.form).then(response => {
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
      const doctorsAdviceIds = row.doctorsAdviceId || this.ids;
      this.$modal.confirm('是否确认删除医嘱管理编号为"' + doctorsAdviceIds + '"的数据项？').then(function() {
        return delAdvice(doctorsAdviceIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/advice/export', {
        ...this.queryParams
      }, `advice_${new Date().getTime()}.xlsx`)
    }
  }
};
</script>
