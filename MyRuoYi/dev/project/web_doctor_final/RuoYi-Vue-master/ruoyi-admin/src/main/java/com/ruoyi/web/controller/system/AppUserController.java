package com.ruoyi.web.controller.system;

import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.system.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * App端/小程序用户相关接口。
 */
@RestController
@RequestMapping("/app/user")
public class AppUserController extends BaseController
{
    @Autowired
    private ISysUserService sysUserService;

    /**
     * 获取所有非管理员的普通用户列表。
     */
    @GetMapping("/listAllNormal")
    public AjaxResult listAllNormal()
    {
        List<SysUser> list = sysUserService.selectAllNormalUsers();
        return AjaxResult.success(list);
    }
}
