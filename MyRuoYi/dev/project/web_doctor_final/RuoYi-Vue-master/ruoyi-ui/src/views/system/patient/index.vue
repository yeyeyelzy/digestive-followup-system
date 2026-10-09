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
<!--      <el-form-item label="头像" prop="avatarUrl">-->
<!--        <el-input-->
<!--          v-model="queryParams.avatarUrl"-->
<!--          placeholder="请输入头像"-->
<!--          clearable-->
<!--          @keyup.enter.native="handleQuery"-->
<!--        />-->
<!--      </el-form-item>-->
      <el-form-item label="电话" prop="phoneNumber">
        <el-input
          v-model="queryParams.phoneNumber"
          placeholder="请输入电话"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
<!--      <el-form-item label="年龄" prop="age">-->
<!--        <el-input-->
<!--          v-model="queryParams.age"-->
<!--          placeholder="请输入年龄"-->
<!--          clearable-->
<!--          @keyup.enter.native="handleQuery"-->
<!--        />-->
<!--      </el-form-item>-->
<!--      <el-form-item label="性别" prop="gender">-->
<!--        <template slot-scope="scope">-->
<!--          <el-select v-model="queryParams.gender" placeholder="请输入性别" >-->
<!--            <el-option value=1 label="男"/>-->
<!--            <el-option value=2 label="女"/>-->
<!--          </el-select>-->
<!--        </template>-->

<!--        &lt;!&ndash;        <el-input&ndash;&gt;-->
<!--        &lt;!&ndash;          v-model="queryParams.gender"&ndash;&gt;-->
<!--        &lt;!&ndash;          placeholder="请输入性别"&ndash;&gt;-->
<!--        &lt;!&ndash;          clearable&ndash;&gt;-->
<!--        &lt;!&ndash;          @keyup.enter.native="handleQuery"&ndash;&gt;-->
<!--        &lt;!&ndash;        />&ndash;&gt;-->
<!--      </el-form-item>-->
<!--      <el-form-item label="体重" prop="weight">-->
<!--        <el-input-->
<!--          v-model="queryParams.weight"-->
<!--          placeholder="请输入体重"-->
<!--          clearable-->
<!--          @keyup.enter.native="handleQuery"-->
<!--        />-->
<!--      </el-form-item>-->
      <el-form-item style="padding-left: 30px">
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

    <el-table v-loading="loading" :data="patientList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="患者id" align="center" prop="patientId" />
      <el-table-column label="患者姓名" align="center" prop="patientName" />
<!--      <el-table-column label="头像" align="center" prop="avatarUrl" />-->
      <el-table-column label="电话" align="center" prop="phoneNumber" />
      <el-table-column label="年龄" align="center" prop="age" />
      <el-table-column label="性别" align="center" prop="gender" />
      <el-table-column label="体重" align="center" prop="weight" />
<!--      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">-->
<!--        <template slot-scope="scope">-->
<!--          <el-button-->
<!--            size="mini"-->
<!--            type="text"-->
<!--            icon="el-icon-edit"-->
<!--            @click="handleUpdate(scope.row)"-->
<!--            v-hasPermi="['system:patient:edit']"-->
<!--          >修改</el-button>-->
<!--          <el-button-->
<!--            size="mini"-->
<!--            type="text"-->
<!--            icon="el-icon-delete"-->
<!--            @click="handleDelete(scope.row)"-->
<!--            v-hasPermi="['system:patient:remove']"-->
<!--          >删除</el-button>-->
<!--        </template>-->
<!--      </el-table-column>-->
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改患者管理对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="420px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="患者姓名" prop="patientName">
          <el-input v-model="form.patientName" placeholder="请输入患者姓名" />
        </el-form-item>
<!--        <el-form-item label="头像" prop="avatarUrl">-->
<!--          <el-input v-model="form.avatarUrl" placeholder="请输入头像" />-->
<!--        </el-form-item>-->
        <el-form-item label="电话" prop="phoneNumber">
          <el-input v-model="form.phoneNumber" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input v-model="form.age" placeholder="请输入年龄" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <template slot-scope="scope">
            <el-select v-model="form.gender" placeholder="请输入性别" style="width:300px;height: 38px;">
              <el-option :value="0" label="男"/>
              <el-option :value="1" label="女"/>
            </el-select>
          </template>
        </el-form-item>
        <el-form-item label="体重" prop="weight">
          <el-input v-model="form.weight" placeholder="请输入体重" />
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
        weight: null
      },
      genderList:[{name:"男",id:0},{name:"女",id:1}],
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

      //*********************************************************************** */
      // this.queryParams.patientName=this.$route.params.patientName
      //******************************************************************** */
      this.loading = true;
      listPatient(this.queryParams).then(response => {
        response.rows.filter((r)=>{
          if (r.gender === 0 || r.gender === "0") {
            r.gender="男"
          } else if (r.gender === 1 || r.gender === "1") {
            r.gender="女"
          } else {
            r.gender="未知"
          }
        })
        this.patientList = response.rows;
        // console.log(this.patientList)
        this.total = response.total;
        this.loading = false;
      });
      // console.log(this.patientList)
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
    }
  }
};
</script>
