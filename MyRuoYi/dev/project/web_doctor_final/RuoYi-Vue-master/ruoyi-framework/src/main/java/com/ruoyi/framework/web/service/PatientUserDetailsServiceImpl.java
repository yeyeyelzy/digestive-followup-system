package com.ruoyi.framework.web.service;

import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.enums.UserStatus;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.system.service.IPatientUserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Set;

/**
 * 患者用户验证处理。
 */
@Service("patientUserDetailsService")
public class PatientUserDetailsServiceImpl implements UserDetailsService {

    private static final Logger log = LoggerFactory.getLogger(PatientUserDetailsServiceImpl.class);

    @Autowired
    private IPatientUserService patientUserService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        PatientUser patientUser = patientUserService.selectPatientUserByPhonenumber(username);
        if (patientUser == null) {
            log.info("登录患者：{} 不存在.", username);
            throw new UsernameNotFoundException("登录患者：" + username + " 不存在");
        }
        if (UserStatus.DELETED.getCode().equals(patientUser.getDelFlag())) {
            log.info("登录患者：{} 已被删除.", username);
            throw new ServiceException("对不起，您的账号：" + username + " 已被删除");
        }
        if (UserStatus.DISABLE.getCode().equals(patientUser.getStatus())) {
            log.info("登录患者：{} 已被停用.", username);
            throw new ServiceException("对不起，您的账号：" + username + " 已停用");
        }

        return createLoginUser(patientUser);
    }

    public UserDetails createLoginUser(PatientUser patientUser) {
        Set<String> permissions = new HashSet<>();
        permissions.add("*:*:*");

        SysUser user = new SysUser();
        user.setUserId(patientUser.getPatientId());
        user.setUserName(patientUser.getPhonenumber());
        user.setNickName(patientUser.getPatientName());
        user.setPhonenumber(patientUser.getPhonenumber());
        user.setSex(patientUser.getSex());
        user.setAvatar(patientUser.getAvatar());
        user.setPassword(patientUser.getPassword());
        user.setStatus(patientUser.getStatus());
        user.setDelFlag(patientUser.getDelFlag());

        return new LoginUser(patientUser.getPatientId(), null, user, permissions);
    }
}
