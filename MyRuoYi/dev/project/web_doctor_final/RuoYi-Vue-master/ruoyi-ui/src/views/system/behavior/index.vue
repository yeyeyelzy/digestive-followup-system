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
<!--      <el-col :span="1.5">-->
<!--        <el-button-->
<!--          type="primary"-->
<!--          plain-->
<!--          icon="el-icon-plus"-->
<!--          size="mini"-->
<!--          @click="handleAdd"-->
<!--          v-hasPermi="['system:behavior:add']"-->
<!--        >新增</el-button>-->
<!--      </el-col>-->
<!--      <el-col :span="1.5">-->
<!--        <el-button-->
<!--          type="success"-->
<!--          plain-->
<!--          icon="el-icon-edit"-->
<!--          size="mini"-->
<!--          :disabled="single"-->
<!--          @click="handleUpdate"-->
<!--          v-hasPermi="['system:behavior:edit']"-->
<!--        >修改</el-button>-->
<!--      </el-col>-->
<!--      <el-col :span="1.5">-->
<!--        <el-button-->
<!--          type="danger"-->
<!--          plain-->
<!--          icon="el-icon-delete"-->
<!--          size="mini"-->
<!--          :disabled="multiple"-->
<!--          @click="handleDelete"-->
<!--          v-hasPermi="['system:behavior:remove']"-->
<!--        >删除</el-button>-->
<!--      </el-col>-->
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
          v-hasPermi="['system:behavior:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="behaviorList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="行为日记id" align="center" prop="behaviorId" />
      <el-table-column label="患者id" align="center" prop="patientId" />
      <el-table-column label="患者姓名" align="center" prop="patientName" />
      <el-table-column label="日期" align="center" prop="date" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.date, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="频率" align="center" prop="frequency" />
      <el-table-column label="分级" align="center" prop="strength" />
      <el-table-column label="时长" align="center" prop="duration">
        <template slot-scope="scope">
          <span>{{ formatDuration(scope.row.duration) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="类型" align="center" prop="type" />

      <el-table-column label="感受" align="center" prop="feel" />
      <el-table-column label="每周复盘" align="center" prop="replay" />
      <el-table-column label="运动管理问题" align="center" prop="question" />
<!--      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">-->
<!--        <template slot-scope="scope">-->
<!--          <el-button-->
<!--            size="mini"-->
<!--            type="text"-->
<!--            icon="el-icon-edit"-->
<!--            @click="handleUpdate(scope.row)"-->
<!--            v-hasPermi="['system:behavior:edit']"-->
<!--          >修改</el-button>-->
<!--          <el-button-->
<!--            size="mini"-->
<!--            type="text"-->
<!--            icon="el-icon-delete"-->
<!--            @click="handleDelete(scope.row)"-->
<!--            v-hasPermi="['system:behavior:remove']"-->
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

    <!-- 添加或修改行为日记管理对话框 -->
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
        <el-form-item label="频率" prop="frequency">
          <el-input v-model="form.frequency" placeholder="请输入频率" />
        </el-form-item>
        <el-form-item label="分级" prop="strength">
          <el-input v-model="form.strength" placeholder="请输入分级" />
        </el-form-item>
        <el-form-item label="时长" prop="duration">
          <el-input v-model="form.duration" placeholder="请输入时长" />
        </el-form-item>
        <el-form-item label="感受" prop="feel">
          <el-input v-model="form.feel" placeholder="请输入感受" />
        </el-form-item>
        <el-form-item label="每周复盘" prop="replay">
          <el-input v-model="form.replay" placeholder="请输入每周复盘" />
        </el-form-item>
        <el-form-item label="运动管理问题" prop="question">
          <el-input v-model="form.question" placeholder="请输入运动管理问题" />
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
import { listBehavior, getBehavior, delBehavior, addBehavior, updateBehavior } from "@/api/system/behavior";

export default {
  name: "Behavior",
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
      // 行为日记管理表格数据
      behaviorList: [],
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
        frequency: null,
        strength: null,
        duration: null,
        type: null,
        feel: null,
        replay: null,
        question: null
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
    formatDuration(value) {
      const n = Number(value)
      if (!Number.isFinite(n) || n <= 0) {
        return "-"
      }
      // 历史数据统一按分钟展示，避免歧义。
      return `${Math.round(n)} 分钟`
    },
    /** 查询行为日记管理列表 */
    getList() {
      this.loading = true;
      listBehavior(this.queryParams).then(response => {
        response.rows.filter((r)=>{
          if (r.type === 0)
            r.type="其他"
          else if (r.type === 1)
            r.type="有氧运动"
          else if (r.type === 2)
            r.type="抗阻运动"
          else r.type="综合性运动"
        })
        this.behaviorList = response.rows;
        console.log(this.behaviorList)
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
        behaviorId: null,
        patientId: null,
        patientName: null,
        date: null,
        frequency: null,
        strength: null,
        duration: null,
        type: null,
        feel: null,
        replay: null,
        question: null
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
      this.ids = selection.map(item => item.behaviorId)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加行为日记管理";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const behaviorId = row.behaviorId || this.ids
      getBehavior(behaviorId).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改行为日记管理";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.behaviorId != null) {
            updateBehavior(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addBehavior(this.form).then(response => {
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
      const behaviorIds = row.behaviorId || this.ids;
      this.$modal.confirm('是否确认删除行为日记管理编号为"' + behaviorIds + '"的数据项？').then(function() {
        return delBehavior(behaviorIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/behavior/export', {
        ...this.queryParams
      }, `behavior_${new Date().getTime()}.xlsx`)
    }
  }
};
</script>
