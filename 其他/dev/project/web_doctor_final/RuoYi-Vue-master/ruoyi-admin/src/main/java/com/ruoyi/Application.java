package com.ruoyi;

import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.system.domain.SysUserRole;
import com.ruoyi.system.mapper.SysUserRoleMapper;
import com.ruoyi.system.service.ISysRoleService;
import com.ruoyi.system.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.context.annotation.ComponentScan;

/**
 * 启动程序
 *
 * @author ruoyi
 */
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
//@ComponentScan({"com.ruoyi", "com.ruoyi.framework"})
public class Application implements CommandLineRunner
{
    @Autowired
    private ISysUserService userService;

    @Autowired
    private ISysRoleService roleService;

    @Autowired
    private SysUserRoleMapper userRoleMapper;

    public static void main(String[] args)
    {
        // System.setProperty("spring.devtools.restart.enabled", "false");
        SpringApplication.run(Application.class, args);
        System.out.println("  ***************************启动成功****************************** ");
    }

    @Override
    public void run(String... args) throws Exception {
        // 1. 检查是否已有管理员账号
        SysUser admin = userService.selectUserByUserName("admin");
        if (admin == null) {

            // 2. 检查并创建管理员角色
            SysRole adminRole = roleService.selectRoleByRoleKey("admin");
            if (adminRole == null) {
                adminRole = new SysRole();
                adminRole.setRoleName("超级管理员");
                adminRole.setRoleKey("admin");
                adminRole.setStatus("0");
                roleService.insertRole(adminRole);
            }
            // 3. 创建管理员用户
            admin = new SysUser();
            admin.setUserName("admin");
            admin.setPassword(SecurityUtils.encryptPassword("admin123")); // 加密密码
            admin.setNickName("超级管理员");
            admin.setStatus("0"); // 启用
            admin.setCreateBy("system");
            admin.setUserId(1L);
            admin.setRoleId(1L);
            userService.insertUser(admin);
            userService.insertUserAuth(admin.getUserId(), admin.getRoleIds());

            // 4. 直接使用Mapper关联用户与角色
            SysUserRole userRole = new SysUserRole();
            userRole.setUserId(admin.getUserId());
            userRole.setRoleId(adminRole.getRoleId());
            userRoleMapper.insertUserRoleInfo(userRole); // 直接调用Mapper的插入方法


            System.out.println("默认管理员账号创建成功：用户名admin，密码admin123");
        }
    }
}
