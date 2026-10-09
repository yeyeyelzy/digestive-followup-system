package com.ruoyi.web.controller.system;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.core.domain.model.LoginBody;
import com.ruoyi.framework.web.service.PatientLoginService;
import com.ruoyi.framework.web.service.SysLoginService;
import com.ruoyi.system.service.IPatientUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import com.ruoyi.common.core.domain.model.LoginUser; // 引入 LoginUser
import com.ruoyi.framework.web.service.TokenService; // 引入 TokenService
import java.util.HashMap;
import com.ruoyi.common.utils.StringUtils;

/**
 * 病人信息操作处理 (小程序端API)
 *
 * @author ruoyi
 */
@RestController
@RequestMapping("/api/patient")
public class PatientUserController extends BaseController{
    // LoginService可以复用或创建一个PatientLoginService
//    @Autowired
//    private SysLoginService loginService;

    @Autowired
    private IPatientUserService patientUserService;

    @Autowired
    private PatientLoginService patientLoginService;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private TokenService tokenService;

    /**
     * 登录方法
     * @param loginBody 登录信息 (可复用LoginBody，或创建PatientLoginBody)
     * @return 结果
     */
    @Anonymous
    @PostMapping("/login")
    public AjaxResult login(@RequestBody LoginBody loginBody) {
        // 1. 调用登录服务获取 token
        String token = patientLoginService.login(loginBody.getUsername(), loginBody.getPassword());

        // 2. 创建一个 map 来存放 token
        HashMap<String, String> result = new HashMap<>();
        result.put("token", token);

        // 3. 将这个 map 作为成功数据返回
        return AjaxResult.success(result);
    }

    /**
     * 注册方法
     * @param patientUser 注册信息
     * @return
     */
    @Anonymous
    @PostMapping("/register")
    public AjaxResult register(@Validated @RequestBody PatientUser patientUser) {

        if (StringUtils.isEmpty(patientUser.getPhonenumber())) {
            return AjaxResult.error("手机号不能为空");
        }

        if (patientUserService.selectPatientUserByPhonenumber(patientUser.getPhonenumber()) != null) {
            return AjaxResult.error("该手机号已注册");
        }

        if (StringUtils.isEmpty(patientUser.getPatientName())) {
            patientUser.setPatientName(patientUser.getPhonenumber());
        }

        // 【修改点】: 直接调用封装了事务的 service 方法
        boolean success = patientUserService.registerUserAndCreatePatientProfile(patientUser);

        if (success) {
            return AjaxResult.success("注册成功");
        } else {
            return AjaxResult.error("注册失败，账号可能已存在");
        }
    }

    /**
     * 获取病人详细信息
     * (这个接口可以在登录后，前端根据token获取用户信息时调用)
     */
    @GetMapping("/getInfo")
    public AjaxResult getInfo()
    {
        // 1. 使用 BaseController 提供的 getLoginUser() 方法获取当前登录的用户信息。
        // 因为是病人登录的，所以这个 LoginUser 是由 PatientUserDetailsServiceImpl 创建的。
        LoginUser loginUser = getLoginUser();

        // 2. 从 LoginUser 对象中安全地获取用户ID。
        // 这个ID就是我们在登录时存进去的 patient_id。
        Long patientId = loginUser.getUserId();

        // 3. 使用这个ID去数据库查询完整的病人信息。
        PatientUser patient = patientUserService.selectPatientUserByPatientId(patientId);

        // 4. 为了安全，返回给前端前，将密码字段设置为空。
        if (patient == null) {
            return AjaxResult.error(404, "用户档案信息未找到");
        }

        patient.setPassword(null);

        return AjaxResult.success(patient);
    }
}
