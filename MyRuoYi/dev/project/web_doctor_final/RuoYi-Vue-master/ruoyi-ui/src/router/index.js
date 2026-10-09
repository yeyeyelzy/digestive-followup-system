import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: 路由配置项
 *
 * hidden: true                     // 当设置 true 的时候该路由不会再侧边栏出现 如401，login等页面，或者如一些编辑页面/edit/1
 * alwaysShow: true                 // 当你一个路由下面的 children 声明的路由大于1个时，自动会变成嵌套的模式--如组件页面
 *                                  // 只有一个时，会将那个子路由当做根路由显示在侧边栏--如引导页面
 *                                  // 若你想不管路由下面的 children 声明的个数都显示你的根路由
 *                                  // 你可以设置 alwaysShow: true，这样它就会忽略之前定义的规则，一直显示根路由
 * redirect: noRedirect             // 当设置 noRedirect 的时候该路由在面包屑导航中不可被点击
 * name:'router-name'               // 设定路由的名字，一定要填写不然使用<keep-alive>时会出现各种问题
 * query: '{"id": 1, "name": "ry"}' // 访问路由的默认传递参数
 * roles: ['admin', 'common']       // 访问路由的角色权限
 * permissions: ['a:a:a', 'b:b:b']  // 访问路由的菜单权限
 * meta : {
    noCache: true                   // 如果设置为true，则不会被 <keep-alive> 缓存(默认 false)
    title: 'title'                  // 设置该路由在侧边栏和面包屑中展示的名字
    icon: 'svg-name'                // 设置该路由的图标，对应路径src/assets/icons/svg
    breadcrumb: false               // 如果设置为false，则不会在breadcrumb面包屑中显示
    activeMenu: '/system/user'      // 当路由设置了该属性，则会高亮相对应的侧边栏。
  }
 */

// 公共路由
export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: () => import('@/views/redirect')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error/401'),
    hidden: true
  },
  {
    path: '',
    component: Layout,
    redirect: 'index',
    meta: { title: '基础管理', icon: 'dashboard', affix: true },
    children: [
      {
        path: 'index',
        component: () => import('@/views/index'),
        name: 'Index',
        meta: { title: '首页', icon: 'dashboard', affix: true }
      },
      {
        path: 'patient',
        component: () => import('@/views/system/patient/index'),
        name: 'router-patient',
        meta: { title: '患者', icon: 'dashboard', affix: true }
      },
      {
        path: 'doctor',
        component: () => import('@/views/system/doctor/index'),
        name: 'router-doctor',
        meta: { title: '医生', icon: 'dashboard', affix: true }
      },
      {
        path: 'doctor-risk-alert',
        component: () => import('@/views/system/doctor/riskAlert'),
        name: 'router-doctor-risk-alert',
        meta: { title: '风险预警', icon: 'dashboard', affix: true }
      },
      {
        path: 'doctor-rehab-plan',
        component: () => import('@/views/system/doctor/rehabPlan'),
        name: 'router-doctor-rehab-plan',
        meta: { title: '康复方案', icon: 'dashboard', affix: true }
      },
      {
        path: 'doctor-health-report',
        component: () => import('@/views/system/doctor/healthReport'),
        name: 'router-doctor-health-report',
        meta: { title: '健康报告', icon: 'dashboard', affix: true }
      },
      {
        path: 'advice',
        component: () => import('@/views/system/advice/index'),
        name: 'router-advice',
        meta: { title: '医嘱', icon: 'dashboard', affix: true }
      },
      {
        path: 'discharge',
        component: () => import('@/views/system/discharge/index'),
        name: 'router-discharge',
        meta: { title: '出院小结', icon: 'dashboard', affix: true }
      },
      {
        path: 'chat',
        component: () => import('@/views/system/chat/index'),
        name: 'router-chat',
        meta: { title: '聊天', icon: 'dashboard', affix: true },
      },
      // {
      //   path: 'files',
      //   component: () => import('@/views/system/files/index'),
      //   name: 'router-files',
      //   meta: { title: '文件管理', icon: 'dashboard', affix: true }
      // },
      {
        path: 'recovery',
        component: () => import('@/views/system/recovery/index'),
        name: 'router-recovery',
        meta: { title: '复查管理', icon: 'dashboard', affix: true }
      },
      {
        path: 'up',
        component: () => import('@/views/system/up/index'),
        name: 'router-follow_up',
        meta: { title: '随访管理', icon: 'dashboard', affix: true }
      },
      {
        path: 'visual',
        component: () => import('@/views/system/visual/index'),
        name: 'router-visual',
        meta: { title: '可视化', icon: 'dashboard', affix: true }
      }
    ]
  },
  {
    path: '/diary',
    component: Layout,
    redirect: 'diary',
    meta: { title: '日记管理', icon: 'dashboard', affix: true },
    children: [
      {
        path: '/diary/behavior',
        component: () => import('@/views/system/behavior/index'),
        name: 'router-behavior',
        meta: { title: '行为日记', icon: 'dashboard', affix: true }
      },
      {
        path: '/diary/diet',
        component: () => import('@/views/system/diet/index'),
        name: 'router-diet',
        meta: { title: '饮食日记', icon: 'dashboard', affix: true }
      },
      {
        path: '/diary/medicine',
        component: () => import('@/views/system/medicine/index'),
        name: 'router-medicine',
        meta: { title: '服药日记', icon: 'dashboard', affix: true }
      },
      {
        path: '/diary/living',
        component: () => import('@/views/system/living/index'),
        name: 'router-living',
        meta: { title: '生活方式日记', icon: 'dashboard', affix: true }
      }
    ]
  },
  {
    path: '/user',
    component: Layout,
    hidden: true,
    redirect: 'noredirect',
    children: [
      {
        path: 'profile',
        component: () => import('@/views/system/user/profile/index'),
        name: 'Profile',
        meta: { title: '个人中心', icon: 'user' }
      }
    ]
  }
]

// 动态路由，基于用户权限动态去加载
export const dynamicRoutes = [
  {
    path: '/system/user-auth',
    component: Layout,
    hidden: true,
    permissions: ['system:user:edit'],
    children: [
      {
        path: 'role/:userId(\\d+)',
        component: () => import('@/views/system/user/authRole'),
        name: 'AuthRole',
        meta: { title: '分配角色', activeMenu: '/system/user' }
      }
    ]
  },
  {
    path: '/system/role-auth',
    component: Layout,
    hidden: true,
    permissions: ['system:role:edit'],
    children: [
      {
        path: 'user/:roleId(\\d+)',
        component: () => import('@/views/system/role/authUser'),
        name: 'AuthUser',
        meta: { title: '分配用户', activeMenu: '/system/role' }
      }
    ]
  },
  {
    path: '/system/dict-data',
    component: Layout,
    hidden: true,
    permissions: ['system:dict:list'],
    children: [
      {
        path: 'index/:dictId(\\d+)',
        component: () => import('@/views/system/dict/data'),
        name: 'Data',
        meta: { title: '字典数据', activeMenu: '/system/dict' }
      }
    ]
  },
  {
    path: '/monitor/job-log',
    component: Layout,
    hidden: true,
    permissions: ['monitor:job:list'],
    children: [
      {
        path: 'index/:jobId(\\d+)',
        component: () => import('@/views/monitor/job/log'),
        name: 'JobLog',
        meta: { title: '调度日志', activeMenu: '/monitor/job' }
      }
    ]
  },
  {
    path: '/tool/gen-edit',
    component: Layout,
    hidden: true,
    permissions: ['tool:gen:edit'],
    children: [
      {
        path: 'index/:tableId(\\d+)',
        component: () => import('@/views/tool/gen/editTable'),
        name: 'GenEdit',
        meta: { title: '修改生成配置', activeMenu: '/tool/gen' }
      }
    ]
  }
]

// 防止连续点击多次路由报错
let routerPush = Router.prototype.push;
let routerReplace = Router.prototype.replace;
// push
Router.prototype.push = function push(location) {
  return routerPush.call(this, location).catch(err => err)
}
// replace
Router.prototype.replace = function push(location) {
  return routerReplace.call(this, location).catch(err => err)
}

export default new Router({
  mode: 'history', // 去掉url中的#
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})
