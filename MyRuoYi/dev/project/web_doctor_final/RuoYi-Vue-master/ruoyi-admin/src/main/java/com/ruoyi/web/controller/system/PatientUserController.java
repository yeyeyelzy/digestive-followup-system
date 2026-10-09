package com.ruoyi.web.controller.system;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.core.domain.model.LoginBody;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.framework.web.service.PatientLoginService;
import com.ruoyi.system.service.IPatientUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;

/**
 * 患者端认证与用户信息接口。
 */
@RestController
@RequestMapping("/api/patient")
public class PatientUserController extends BaseController {

    @Autowired
    private IPatientUserService patientUserService;

    @Autowired
    private PatientLoginService patientLoginService;

    @Anonymous
    @PostMapping("/login")
    public AjaxResult login(@RequestBody LoginBody loginBody) {
        String token = patientLoginService.login(loginBody.getUsername(), loginBody.getPassword());
        HashMap<String, String> result = new HashMap<>();
        result.put("token", token);
        return AjaxResult.success(result);
    }

    @Anonymous
    @PostMapping("/register")
    public AjaxResult register(@Validated @RequestBody PatientUser patientUser) {
        if (StringUtils.isEmpty(patientUser.getPhonenumber())) {
            return AjaxResult.error("手机号不能为空");
        }

        if (StringUtils.isEmpty(patientUser.getPassword())) {
            return AjaxResult.error("密码不能为空");
        }

        if (patientUserService.selectPatientUserByPhonenumber(patientUser.getPhonenumber()) != null) {
            return AjaxResult.error("该手机号已注册");
        }

        if (StringUtils.isEmpty(patientUser.getPatientName())) {
            patientUser.setPatientName(patientUser.getPhonenumber());
        }

        boolean success = patientUserService.registerUserAndCreatePatientProfile(patientUser);
        return success ? AjaxResult.success("注册成功") : AjaxResult.error("注册失败，账号可能已存在");
    }

    @GetMapping("/getInfo")
    public AjaxResult getInfo() {
        LoginUser loginUser = getLoginUser();
        Long patientId = loginUser.getUserId();
        PatientUser patient = patientUserService.selectPatientUserByPatientId(patientId);
        if (patient == null) {
            return AjaxResult.error(404, "用户档案信息未找到");
        }

        patient.setPassword(null);
        return AjaxResult.success(patient);
    }
}
