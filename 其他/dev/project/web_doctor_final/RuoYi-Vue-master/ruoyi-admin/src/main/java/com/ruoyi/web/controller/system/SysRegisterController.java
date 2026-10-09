package com.ruoyi.web.controller.system;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.model.RegisterBody;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.framework.web.service.SysRegisterService;
import com.ruoyi.system.service.ISysConfigService;

/**
 * 注册验证 (公开)
 *
 * @author ruoyi
 */
@RestController
public class SysRegisterController extends BaseController
{
    @Autowired
    private SysRegisterService registerService;

    @Autowired
    private ISysConfigService configService;

    /**
     * 公开的注册接口，用于任何用户（例如：患者）注册
     */
    @PostMapping("/register")
    public AjaxResult register(@RequestBody RegisterBody user)
    {

        // 调用 Service 层执行注册逻辑
        String msg = registerService.register(user);

        // 根据 Service 返回的结果，给前端对应的响应
        // 如果 msg 是空的，说明成功了
        return StringUtils.isEmpty(msg) ? success() : error(msg);
    }
}

