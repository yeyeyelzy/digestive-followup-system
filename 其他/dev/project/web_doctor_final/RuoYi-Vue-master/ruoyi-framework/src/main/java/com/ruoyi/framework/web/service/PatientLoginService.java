package com.ruoyi.framework.web.service;

import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.exception.user.UserPasswordNotMatchException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 病人登录服务 (手动认证版本)
 */
@Component
public class PatientLoginService {

    @Autowired
    private TokenService tokenService;

    // 1. 注入我们自定义的 PatientUserDetailsServiceImpl
    @Autowired
    @Qualifier("patientUserDetailsService")
    private UserDetailsService patientUserDetailsService;

    // 2. 注入密码编码器
    @Autowired
    private PasswordEncoder passwordEncoder;

    /**
     * 登录验证 (手动完成认证全过程)
     *
     * @param username 用户名
     * @param password 密码
     * @return 结果 token
     */
    public String login(String username, String password) {
        // 步骤 1: 使用 PatientUserDetailsServiceImpl 从数据库加载用户信息
        // loadUserByUsername 方法在找不到用户时会抛出 UsernameNotFoundException
        UserDetails userDetails;
        try {
            userDetails = patientUserDetailsService.loadUserByUsername(username);
        } catch (Exception e) {
            // 捕获所有异常（包括 UsernameNotFoundException），统一处理为业务异常
            throw new ServiceException("登录用户：" + username + " 不存在");
        }

        // 步骤 2: 使用 PasswordEncoder 校验密码
        if (!passwordEncoder.matches(password, userDetails.getPassword())) {
            // 抛出密码不匹配异常
            throw new UserPasswordNotMatchException();
        }

        // 步骤 3: 认证成功, userDetails 就是我们的 LoginUser 对象
        LoginUser loginUser = (LoginUser) userDetails;

        // 步骤 4: 使用 TokenService 创建并返回 Token
        return tokenService.createToken(loginUser);
    }
}

