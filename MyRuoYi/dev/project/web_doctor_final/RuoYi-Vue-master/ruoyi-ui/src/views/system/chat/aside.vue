<template>
  <el-container>
      <!-- router是关键属性 -->
      <el-menu
        default-active="1"
        background-color="#53a8ff"
        text-color="#fff"
        active-text-color=white
      >
        <el-submenu index="1">
          <template slot="title">
            <i class="el-icon-chat-dot-round"></i>
            <span>聊天列表</span>
          </template>
<!--          <el-menu-item v-for="pn in queryParams.patientName">{{pn}}</el-menu-item>-->
          <el-menu-item
            v-for="pn in patientList"
            :key="pn.patientName"
            :index="pn.patientName"
            @click="jump(pn.patientName)"
          >
            <span slot="title">{{pn.patientName}}</span>
            </el-menu-item>

        </el-submenu>


      </el-menu>

  </el-container>
</template>


<script>
import { listPatient, getPatient, delPatient, addPatient, updatePatient } from "@/api/system/patient";
import chat from "@/views/system/chat/index";
// import {listPatient, namePatient} from "@/api/system/patient";

export default {
  name: "Aside",
  components:{
    chat
  },
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
      genderList:[{name:"男",id:1},{name:"女",id:2}],
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
    jump(name){
      // this.$router.push({
      //   name: "router-chat",
      //   params: {
      //     patientName: name
      //   }
      // });
      chat.methods.getList(name)
    },
    /** 查询患者管理列表 */
    getList() {
      this.loading = true;
      listPatient(this.queryParams).then(response => {
        response.rows.filter((r)=>{
          if (r.gender === 1)
            r.gender="男"
          else r.gender="女"
        })
        this.patientList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    }
  }
};
</script>

