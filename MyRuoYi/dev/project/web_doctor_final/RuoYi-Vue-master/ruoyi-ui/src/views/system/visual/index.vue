<template>
  <div class="ml20 mr20 mb20 colorFOp">
    <div class="app-container">
      <el-form
        :model="queryParams"
        ref="queryForm"
        size="small"
        :inline="true"
        v-show="showSearch"
        label-width="68px"
      >
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

        <el-form-item label="NT_proBNP" prop="ntProbnp">
          <el-input
            v-model="queryParams.ntProbnp"
            placeholder="请输入NT_proBNP"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="LVEF" prop="lvef">
          <el-input
            v-model="queryParams.lvef"
            placeholder="请输入LVEF"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="峰值公斤摄氧量" prop="cpet1">
          <el-input
            v-model="queryParams.cpet1"
            placeholder="请输入峰值公斤摄氧量"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="无氧公斤摄氧量" prop="cpet2">
          <el-input
            v-model="queryParams.cpet2"
            placeholder="请输入无氧公斤摄氧量"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="峰值血压" prop="peakBloodPressure">
          <el-input
            v-model="queryParams.peakBloodPressure"
            placeholder="请输入峰值血压"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="峰值心率" prop="peakHeartRate">
          <el-input
            v-model="queryParams.peakHeartRate"
            placeholder="请输入峰值心率"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="无氧阈血压" prop="anaerobicThresholdBloodPressure">
          <el-input
            v-model="queryParams.anaerobicThresholdBloodPressure"
            placeholder="请输入无氧阈血压"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="无氧阈心率" prop="anaerobicThresholdHeartRate">
          <el-input
            v-model="queryParams.anaerobicThresholdHeartRate"
            placeholder="请输入无氧阈心率"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            icon="el-icon-search"
            size="mini"
            @click="handleQuery"
            >搜索</el-button
          >
          <el-button icon="el-icon-refresh" size="mini" @click="resetQuery"
            >重置</el-button
          >
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="recoveryList"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="复查id" align="center" prop="recoveryId" />
        <el-table-column label="患者id" align="center" prop="patientId" />
        <el-table-column label="患者姓名" align="center" prop="patientName" />
        <el-table-column label="日期" align="center" prop="date" width="180">
          <template slot-scope="scope">
            <span>{{ parseTime(scope.row.date, "{y}-{m}-{d}") }}</span>
          </template>
        </el-table-column>
        <el-table-column label="NT_proBNP" align="center" prop="ntProbnp" />
        <el-table-column label="LVEF" align="center" prop="lvef" />
        <el-table-column label="峰值公斤摄氧量" align="center" prop="cpet1" />
        <el-table-column label="无氧公斤摄氧量" align="center" prop="cpet2" />
        <el-table-column
          label="峰值血压"
          align="center"
          prop="peakBloodPressure"
        />
        <el-table-column label="峰值心率" align="center" prop="peakHeartRate" />
        <el-table-column
          label="无氧阈血压"
          align="center"
          prop="anaerobicThresholdBloodPressure"
        />
        <el-table-column
          label="无氧阈心率"
          align="center"
          prop="anaerobicThresholdHeartRate"
        />
        <el-table-column
          label="操作"
          align="center"
          class-name="small-padding fixed-width"
        >
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              >修改</el-button
            >
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="getList"
      />
    </div>
    <!--为echarts准备一个具备大小的容器dom-->
    <div id="main" style="margin-top:20px;width: 100%; height: 900px"></div>
  </div>
</template>
 <script>
     import * as echarts from 'echarts';
     import { listRecovery, getRecovery, delRecovery, addRecovery, updateRecovery,selectStatisics,
        getNtProbnp ,getLVEF,getCPET1,getCPET2,getPeakBloodPressure,zhexian,
        getPpeakHeartRate,getAnaerobicThresholdBloodPressure,getAnaerobicThresholdHeartRate
    } from "@/api/system/recovery";

     export default {
        name: "Recovery",
         data() {
             return {
                 charts: '',
       /*    opinion: ["1", "3", "3", "4", "5"],*/
         xdata: [],
         NT_proBN:[],
         lvef: [],
         峰值公斤摄氧量: [],
         无氧公斤摄氧量: [],
         峰值血压: [],
         峰值心率: [],
         无氧阈血压: [],
         无氧阈心率: [],

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
      // 复查管理表格数据
      recoveryList: [],
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
        ntProbnp: null,
        lvef: null,
        cpet1: null,
        cpet2: null,
        peakBloodPressure: null,
        peakHeartRate: null,
        anaerobicThresholdBloodPressure: null,
        anaerobicThresholdHeartRate: null
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
             }
     },
     created() {
      this.getList();
      this.showChart();
  },

         methods: {

            showChart() {
              // this.queryParams.patientName=this.$route.params.patientName;
              console.log(this.queryParams.patientName);
          zhexian(this.queryParams.patientName)
          .then(response =>{
            this.xdata = response.data.dayList
            this.NT_proBNP = response.data.NtProbnpList
            this.lvef = response.data.LVEFList
            this.峰值公斤摄氧量 = response.data.CPET1List
            this.无氧公斤摄氧量 = response.data.CPET2List
            this.峰值血压 = response.data.PeakBloodPressureList
            this.峰值心率 = response.data.PpeakHeartRateList
            this.无氧阈血压 = response.data.AnaerobicThresholdBloodPressureList
            this.无氧阈心率 = response.data.AnaerobicThresholdHeartRateList

            this.drawLine('main')   //获取到数据后调用图表参数进行显示
          })

        },
             drawLine(id) {
                 this.charts = echarts.init(document.getElementById(id))
                 this.charts.setOption({
                     tooltip: {
                         trigger: 'axis'
                     },
                     legend: {
                         data: ['NT_proBNP/6','LVEF','峰值公斤摄氧量','无氧公斤摄氧量','峰值血压','峰值心率','无氧阈血压','无氧阈心率']//图例
                     },
                     grid: {
                         left: '3%',
                         right: '4%',
                         bottom: '3%',
                         containLabel: true
                     },

                     toolbox: {
                         feature: {
                             saveAsImage: {}
                         }
                     },
                     xAxis: {//横坐标
                          name: "日期",
                         type: 'category',
                         boundaryGap: false,
                           data: this.xdata

                     },
                     yAxis: {
                          name: "指标值",
                         type: 'value'
                     },
                     //三条折线就有三种series，可以更改type以改变是否为折线
                     series: [{
                         name: 'NT_proBNP/6',
                         type: 'line',
                         data: this.NT_proBNP.map(a=>{
                          return (a/6).toFixed(2);
                         }),
                     },{
                         name: 'LVEF',
                         type: 'line',
                         data: this.lvef
                     },{
                         name: '峰值公斤摄氧量',
                         type: 'line',
                         data: this.峰值公斤摄氧量,
                         color:'#cfa068'
                     },{
                         name: '无氧公斤摄氧量',
                         type: 'line',
                         data: this.无氧公斤摄氧量,
                     },{
                         name: '峰值血压',
                         type: 'line',
                         data: this.峰值血压,
                         color:'#9f7fac'
                     },{
                         name: '峰值心率',
                         type: 'line',
                         data: this.峰值心率,
                         color:'#9f7fac'
                     },{
                         name: '无氧阈血压',
                         type: 'line',
                         data: this.无氧阈血压,
                         color:'#9f7fac'
                     },{
                         name: '无氧阈心率',
                         type: 'line',
                         data: this.无氧阈心率,
                         color:'#fad64e'
                     }]
                 })
             },

              /** 查询复查管理列表 */
    getList() {
      //*********************************************************************** */
      // this.queryParams.patientName=this.$route.params.patientName
      //******************************************************************** */
      this.loading = true;
      listRecovery(this.queryParams).then(response => {
        this.recoveryList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
      this.showChart()
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        recoveryId: null,
        patientId: null,
        patientName: null,
        date: null,
        ntProbnp: null,
        lvef: null,
        cpet1: null,
        cpet2: null,
        peakBloodPressure: null,
        peakHeartRate: null,
        anaerobicThresholdBloodPressure: null,
        anaerobicThresholdHeartRate: null
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
      this.ids = selection.map(item => item.recoveryId)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加复查管理";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const recoveryId = row.recoveryId || this.ids
      getRecovery(recoveryId).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改复查管理";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.recoveryId != null) {
            updateRecovery(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addRecovery(this.form).then(response => {
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
      const recoveryIds = row.recoveryId || this.ids;
      this.$modal.confirm('是否确认删除复查管理编号为"' + recoveryIds + '"的数据项？').then(function() {
        return delRecovery(recoveryIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/recovery/export', {
        ...this.queryParams
      }, `recovery_${new Date().getTime()}.xlsx`)
    }
         },
         //调用

     }
 </script>
 <style scoped>
* {
  margin: 0;
  padding: 0;
  list-style: none;
}
.box {
  margin: 0 auto;
  padding-top: 80px;
  height: 100px;
  width: 100%;
}
.searchBox {
  margin: 0 auto;
  width: 60%;
  position: relative;
}
.searchInput {
  display: inline-block;
  width: 85%;
  height: 38px;
  border: 1px solid #cccccc;
  float: left;
  box-sizing: border-box;
  -moz-box-sizing: border-box; /* Firefox */
  -webkit-box-sizing: border-box; /* Safari */
  border-bottom-left-radius: 5px;
  border-top-left-radius: 5px;
}
.searchButton {
  display: inline-block;
  width: 15%;
  height: 38px;
  line-height: 40px;
  float: left;
  background-color: #00a0e9;
  font-size: 16px;
  cursor: pointer;
  border-bottom-right-radius: 5px;
  border-top-right-radius: 5px;
  border: none;
  color: #fff;
}
</style>
