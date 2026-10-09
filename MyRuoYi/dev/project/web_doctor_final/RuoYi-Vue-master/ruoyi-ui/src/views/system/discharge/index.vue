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
      <el-form-item label="入院时间" prop="admissionDate">
        <el-date-picker clearable
          v-model="queryParams.admissionDate"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="请选择入院时间">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="出院时间" prop="dischargeDate">
        <el-date-picker clearable
          v-model="queryParams.dischargeDate"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="请选择出院时间">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="出院诊断" prop="dischargeDiagnosis">
        <el-input
          v-model="queryParams.dischargeDiagnosis"
          placeholder="请输入出院诊断"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="主要化验结果" prop="majorTestResult">
        <el-input
          v-model="queryParams.majorTestResult"
          placeholder="请输入主要化验结果"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="医嘱号" prop="doctorsAdviceId">
        <el-input
          v-model="queryParams.doctorsAdviceId"
          placeholder="请输入医嘱号"
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
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="handleOcr"
        >出院图片识别</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="dischargeList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="住院号" align="center" prop="admissionNumber" />
      <el-table-column label="患者id" align="center" prop="patientId" />
      <el-table-column label="患者姓名" align="center" prop="patientName" />
      <el-table-column label="入院时间" align="center" prop="admissionDate" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.admissionDate, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="出院时间" align="center" prop="dischargeDate" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.dischargeDate, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="出院诊断" align="center" prop="dischargeDiagnosis" />
      <el-table-column label="主要化验结果" align="center" prop="majorTestResult" />
      <el-table-column label="医嘱号" align="center" prop="doctorsAdviceId" @click="$router.push('/tool/advice')">
                <template slot-scope="scope">
<!--                  <router-link to="{path:'/tool/advice', params:{patientName:111}">{{scope.row.doctorsAdviceId}}</router-link>-->
                      <button @click="getAdvice(scope.row.patientName)">查看医嘱</button>
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

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <el-dialog :title="title" :visible.sync="ocropen" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="上传图片" required>
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            name="file"
            :headers="headers"
            ref="upload"
            :show-file-list="false"
            :on-error="handleUploadError"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <i class="el-icon-plus"></i>
          </el-upload>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- 添加或修改出院小结管理对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="患者id" prop="patientId">
          <el-input v-model="form.patientId" placeholder="请输入患者id" />
        </el-form-item>
        <el-form-item label="患者姓名" prop="patientName">
          <el-input v-model="form.patientName" placeholder="请输入患者姓名" />
        </el-form-item>
        <el-form-item label="入院时间" prop="admissionDate">
          <el-date-picker clearable
            v-model="form.admissionDate"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="请选择入院时间">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="出院时间" prop="dischargeDate">
          <el-date-picker clearable
            v-model="form.dischargeDate"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="请选择出院时间">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="出院诊断" prop="dischargeDiagnosis">
          <el-input v-model="form.dischargeDiagnosis" placeholder="请输入出院诊断" />
        </el-form-item>
        <el-form-item label="主要化验结果" prop="majorTestResult">
          <el-input v-model="form.majorTestResult" placeholder="请输入主要化验结果" />
        </el-form-item>
        <el-form-item label="医嘱号" prop="doctorsAdviceId">
          <el-input v-model="form.doctorsAdviceId" placeholder="请输入医嘱号" />
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
import { listDischarge, getDischarge, delDischarge, addDischarge, updateDischarge } from "@/api/system/discharge";
import {getToken} from "@/utils/auth";

export default {
  name: "Discharge",
  data() {
    return {
      uploadUrl: process.env.VUE_APP_BASE_API + "/system/discharge/ocr", // 上传的图片识别地址
      headers: {
        Authorization: "Bearer " + getToken()
      },
      ocropen : false,
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
      // 出院小结管理表格数据
      dischargeList: [],
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
        admissionDate: null,
        dischargeDate: null,
        dischargeDiagnosis: null,
        majorTestResult: null,
        doctorsAdviceId: null
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        patientId: [
          { required: true, message: "患者id不能为空", trigger: "blur" }
        ],
        admissionDate: [
          { required: true, message: "入院时间不能为空", trigger: "blur" }
        ],
        dischargeDate: [
          { required: true, message: "出院时间不能为空", trigger: "blur" }
        ],
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    handleAvatarSuccess(res, file) {
      if(res.code==200){
        this.ocropen=false;
        this.handleAdd();
        this.form = res.data;
      }else{
        this.$message.error("图片识别失败");
      }
    },
    // 图片上传前的判断
    beforeAvatarUpload(file) {
      let imgType = ['jpg','jpeg','png']
      let judge = false // 后缀
      let type = file.name.split('.')[file.name.split('.').length - 1]
      for (let k = 0; k < imgType.length; k++) {
        if (imgType[k].toUpperCase() === type.toUpperCase()) {
          judge = true
          break
        }
      }
      // 验证图片格式
      if (!judge) {
        this.$message.error('图片格式只支持：JPG、JPEG、PNG')
        return false
      }
      return true
    },
    /** 查询出院小结管理列表 */
    getList() {
      //*********************************************************************** */
      // this.queryParams.patientName=this.$route.params.patientName
      //******************************************************************** */
      this.loading = true;
      listDischarge(this.queryParams).then(response => {
        this.dischargeList = response.rows;
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
        admissionNumber: null,
        patientId: null,
        patientName: null,
        admissionDate: null,
        dischargeDate: null,
        dischargeDiagnosis: null,
        majorTestResult: null,
        doctorsAdviceId: null
      };
      this.resetForm("form");
    },
    handleUploadError() {
      this.$message.error("图片识别失败");
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
      this.ids = selection.map(item => item.admissionNumber)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** ocr按钮操作 */
    handleOcr() {
      this.reset();
      this.ocropen = true;
      this.title = "出院小结识别";
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加出院小结管理";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const admissionNumber = row.admissionNumber || this.ids
      getDischarge(admissionNumber).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改出院小结管理";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.admissionNumber != null) {
            updateDischarge(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addDischarge(this.form).then(response => {
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
      const admissionNumbers = row.admissionNumber || this.ids;
      this.$modal.confirm('是否确认删除出院小结管理编号为"' + admissionNumbers + '"的数据项？').then(function() {
        return delDischarge(admissionNumbers);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/discharge/export', {
        ...this.queryParams
      }, `discharge_${new Date().getTime()}.xlsx`)
    },
    /** 查看医嘱 */
    getAdvice(name){
      this.$router.push({
        name: "router-advice",
        params: {
          patientName: name
        }
      });
    }
  }
};
</script>
